#!/usr/bin/env python3

"""
Walk Linux Kconfig's mconf UI and dump its rendered menus.

The program deliberately drives mconf as a user would, rather than
parsing Kconfig files directly.

Requirements:
    - tmux
    - Linux kernel source tree containing scripts/kconfig/mconf

The initial implementation is intentionally conservative.  The screen
parser and menu-entry identification should be adjusted against actual
mconf output rather than assuming a particular ncurses implementation.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_KERNEL = "/usr/src/linux"
DEFAULT_WIDTH = 160
DEFAULT_HEIGHT = 60


@dataclass
class MenuEntry:
    """One logical entry in a Kconfig menu."""

    index: int
    text: str
    raw: str
    submenu: bool = False
    empty_submenu: bool = False


@dataclass
class Menu:
    """One complete logical menu."""

    path: tuple[str, ...]
    title: str
    entries: list[MenuEntry] = field(default_factory=list)
    rendered_screen: str = ""


class MenuConfigSession:
    """Owns the tmux session and communicates with mconf."""

    def __init__(
        self,
        kernel: Path,
        width: int,
        height: int,
        debug: bool = False,
    ):
        self.kernel = kernel
        self.width = width
        self.height = height
        self.debug = debug

        self.session = f"kconfig-dump-{os.getpid()}"

    def log(self, message):
        if self.debug:
            print(f"> {message}", file=sys.stderr)

    def session_exists(self):
        return subprocess.run(
            [
                "tmux",
                "has-session",
                "-t",
                self.session,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0

    def run(self):
        cmd = [
            "tmux",
            "new-session",
            "-d",
            "-s",
            self.session,
            "-x",
            str(self.width),
            "-y",
            str(self.height),
            "-c",
            str(self.kernel),
            "--",
            "make",
            "menuconfig",
        ]

        self.log("starting:")
        self.log(" ".join(map(str, cmd)))

        subprocess.run(cmd, check=True)

        # Give make/Kconfig a chance to establish the environment and
        # launch mconf before we attempt to drive the terminal.
        time.sleep(0.2)

        if not self.session_exists():
            raise RuntimeError(
                "menuconfig exited before the tmux session became usable"
            )

    def kill(self):
        subprocess.run(
            ["tmux", "kill-session", "-t", self.session],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

    def wait_for_menu(self, timeout=5.0):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            screen = self.capture()

            if "Kernel Configuration" in screen:
                return screen

            time.sleep(0.1)

        screen = self.capture()

        raise RuntimeError(
            "Timed out waiting for mconf menu to appear.\n"
            f"Last capture ({len(screen)} bytes):\n"
            f"{screen}"
        )

    def capture(self):
        cmd = [
            "tmux",
            "capture-pane",
            "-p",
            "-t",
            self.session,
            "-S",
            "-",
        ]

        self.log("capture: " + " ".join(cmd))

        result = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "capture-pane failed:\n"
                f"command: {' '.join(cmd)}\n"
                f"stdout: {result.stdout!r}\n"
                f"stderr: {result.stderr!r}"
            )

        self.log(
            f"capture returned {len(result.stdout)} bytes"
        )

        return result.stdout

    def key(self, key):
        self.log(f"KEY {key}")

        subprocess.run(
            [
                "tmux",
                "send-keys",
                "-t",
                self.session,
                key,
            ],
            check=True,
        )


class ScreenParser:
    """
    Parse the visible mconf screen.

    This intentionally does NOT inspect terminal attributes or cursor
    position.

    The first version recognizes Kconfig menu rows primarily by their
    visible checkbox/menu syntax and submenu suffixes.
    """

    MENU_HEADING_RE = re.compile(
        r"^\s*---\s+.+\S\s*$"
    )

    ITEM_RE = re.compile(
        r"^\s*(?:"
        r"\[[ *M]\]"          # [ ], [*], [M]
        r"|<[*M ]>"           # < >, <*>, <M>
        r"|-\*-"              # -*- forced built-in
        r"|-\s*M\s-"          # -M- forced module
        r"|\(\([^()\r\n]*\)\)"  # ((value))
        r"|\([^()\r\n]*\)"    # (), (value), (20), (GENR8TOO), ...
        r").*\S$"
    )

    SUBMENU_RE = re.compile(
        r"^\s*(?P<text>.*?)\s+(?P<suffix>--->|----)\s*$"
    )

    def __init__(self, debug=False):
        self.debug = debug

    def log(self, message):
        if self.debug:
            print(f"[parser] {message}", file=sys.stderr)

    def parse(self, screen):
        lines = screen.splitlines()
        result = []

        for lineno, line in enumerate(lines):
            stripped = line.rstrip()
            if not stripped:
                continue

            content = self._remove_border(stripped)

            if self.ITEM_RE.match(content):
                result.append((lineno, content))
                continue

            if self.SUBMENU_RE.match(content):
                result.append((lineno, content))

            if self.MENU_HEADING_RE.match(content):
                result.append((lineno, content))

        return result

    @staticmethod
    def _remove_border(line):
        return line.strip(" │")


class MenuWalker:
    """
    Recursively walk mconf.

    Important invariant:

        selected_index

    is maintained by us.  We do NOT determine the selected row by looking
    at terminal cursor state or terminal attributes.
    """

    def __init__(self, session, parser, debug=False):
        self.session = session
        self.parser = parser
        self.debug = debug

        self.menus = []

    def log(self, message):
        if self.debug:
            print(f"[walker] {message}", file=sys.stderr)

    @staticmethod
    def menu_breadcrumb(screen):
        for line in screen.splitlines():
            line = line.strip()
            if line.startswith("→"):
                return line
        return ""

#    def wait_for_stable_screen(self):
#        time.sleep(0.05)
#        return self.session.capture()

    def wait_for_stable_screen(self):
        previous = self.session.capture()
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            time.sleep(0.01)
            current = self.session.capture()
            if current == previous:
                return current
            previous = current
        return previous

    def walk(self, path=(), initial_screen=None):
        """
        Walk the current menu and recursively descend into submenus.
        """

        self.log(f"ENTER MENU: /{'/'.join(path)}")

        if initial_screen is None:
#            self.session.key("HOME")
            print("Initial screen is none")
            screen = self.wait_for_stable_screen()
        else:
            print("Initial screen is here")
            screen = initial_screen

        menu = Menu(
            path=path,
            title=self.find_menu_title(screen),
        )

        # This is the canonical top-of-menu rendering.
        menu.rendered_screen = screen

        selected_index = 0
        known_entries = []

        while True:
            visible = self.parser.parse(screen)

            self.log(
                f"selection={selected_index} "
                f"visible_entries={len(visible)} "
                f"known_entries={len(known_entries)}"
            )

            self.merge_entries(
                known_entries,
                visible,
                selected_index,
            )

            new_screen = self.session.capture()
            old_count = len(known_entries)

            new_visible = self.parser.parse(new_screen)

            self.merge_entries(
                known_entries,
                new_visible,
                selected_index + 1,
            )

            screen = new_screen
            selected_index += 1
            break

        menu.entries = known_entries

        self.menus.append(menu)

        current_index = 0
        last_index = 0
#        #debug
#        print(menu.entries)

        # Now recursively visit submenu entries.
        for entry in menu.entries:
            if not entry.submenu:
                continue

            if entry.empty_submenu:
                continue

            self.log(
                f"POSITIONING FOR [{entry.index}]: {entry.text!r}"
            )

            delta = entry.index - current_index

            for _ in range(delta):
                self.session.key("DOWN")
#                time.sleep(0.1)

            current_index = last_index + delta

            positioned_screen = self.wait_for_stable_screen()

            self.log(
                f"POSITIONED SCREEN FOR [{entry.index}] by moving: last{last_index} curr{current_index} delta{delta} "
                f"{entry.text!r}\n{positioned_screen}"
            )

            last_index = entry.index

            before = self.menu_breadcrumb(positioned_screen)

            self.session.key("ENTER")
            time.sleep(0.05)
            child_screen = self.wait_for_stable_screen()

            after = self.menu_breadcrumb(child_screen)

            self.log(
                f"CHILD SCREEN AFTER ENTER [{entry.index}]: "
                f"{entry.text!r}\n{child_screen}"
            )

            child_title = self.find_menu_title(child_screen)

            child_breadcrumb = self.menu_breadcrumb(child_screen)

            if self.is_choice_dialog(child_screen):
                self.log(
                    f"SUBMENU [{entry.index}] opened an item dialog: "
                    f"{entry.text!r}; - closing with exit_current_menu()"
                )
                screen = self.exit_current_menu(child_title, True)

            current_breadcrumb = self.menu_breadcrumb(screen)

            if child_breadcrumb == current_breadcrumb:
#                raise RuntimeError(
#                    f"REFUSING RECURSION: child menu did not change "
#                    f"for {entry.text!r}: {child_breadcrumb!r}"
#                )
                continue

            self.walk(path + (entry.text,), child_screen)

            #exit when done walking
            screen = self.exit_current_menu(child_title, False)

            if child_title == menu.title:
                self.log(
                    f"SUBMENU [{entry.index}] stayed in same menu: "
                    f"{entry.text}\n{child_screen}"
                )
            else:
                self.log(
                    f"RETURNED FROM [{entry.index}]: "
                    f"{entry.text!r}\n{child_screen}"
                )
#            self.wait_for_stable_screen()

    def merge_entries(self, known, visible, selected_index):
        if not visible:
            return False

        changed = False

        for _, raw in visible:
            if any(entry.raw == raw for entry in known):
                continue

            entry = self.make_entry(
                len(known),
                raw,
            )

            known.append(entry)
            changed = True

        return changed

    @staticmethod
    def make_entry(index, raw):
        match = ScreenParser.SUBMENU_RE.match(raw)

        if match:
            text = match.group("text").strip()
            suffix = match.group("suffix")

            return MenuEntry(
                index=index,
                text=text,
                raw=raw,
                submenu=suffix == "--->",
                empty_submenu=suffix == "----",
            )

        text = re.sub(
            r"^\s*(?:"
            r"\[[ *M]\]"
            r"|<[*M ]>"
            r"|-\*-"
            r"|-\s*M\s-"
            r"|\([^()\r\n]*\)"
            r")\s*",
            "",
            raw
        ).strip()

        return MenuEntry(
            index=index,
            text=text,
            raw=raw,
        )

    @staticmethod
    def find_menu_title(screen):
        for line in screen.splitlines():
            line = line.strip()

            if (
                line.startswith("┌")
                or line.startswith("│")
                or line.startswith("└")
                or not line
            ):
                continue

            if "Kernel Configuration" in line:
                continue

            return line

        return ""

    @staticmethod
    def is_choice_dialog(screen):
        return (
            "Use the arrow keys to navigate this window" in screen
            and "followed by the <SPACE" in screen
        )

    @staticmethod
    def is_exitable(screen):
        return ("< Exit >" in screen)

    def exit_current_menu(self, parent_title, is_choice_dialog):
        if not is_choice_dialog:
            self.log(f"EXIT MENU: waiting for parent {parent_title!r}")
#            self.session.key("x")
#"Exiting with the x key is not reliable if theres an entry starting with an X it will jump to it"
            self.session.key("TAB")
            self.session.key("ENTER")

            screen = self.wait_for_stable_screen()

            if self.find_menu_title(screen) == parent_title:
                self.log("EXIT MENU: x to Exit, succeeded")

        else:
            screen = self.wait_for_stable_screen()

            self.log("EXIT DIALOG: {self.find_menu_title(screen)}")

            self.close_choice_dialog(screen, parent_title)

        return screen

    def close_choice_dialog(self, screen, parent_title):
        self.log("CLOSE CHOICE DIALOG: sending ESC")
        self.session.key("Escape")
        self.session.key("Escape")
        screen = self.wait_for_stable_screen()
        self.log("CLOSE CHOICE DIALOG: closed OK.")
        if self.find_menu_title(screen) == parent_title:
            return

        if self.is_exitable(screen):
#            self.session.key("x")
            self.session.key("TAB")
            self.session.key("ENTER")

            screen = self.wait_for_stable_screen()
            self.log("EXIT MENU: x to Exit, succeeded")

        if self.is_choice_dialog(screen):
            raise RuntimeError(
                "Failed to CLOSE CHOICE dialog"
            )

        if self.is_exitable(screen):
            raise RuntimeError(
                "Failed to CLOSE exitable screen"
            )

        if self.find_menu_title(screen) != parent_title:
            raise RuntimeError(
                f"Failed to exit menu: expected {parent_title!r}, "
                f"got {self.find_menu_title(screen)!r}"
            )

        return screen


class Dumper:
    def __init__(self, menus, output):
        self.menus = menus
        self.output = output

    def write(self):
        self.output.mkdir(parents=True, exist_ok=True)

        self.write_tree()
        self.write_transcript()
        self.write_individual_menus()

    def write_tree(self):
        path = self.output / "kconfig-tree.txt"

        with path.open("w", encoding="utf-8") as f:
            for menu in self.menus:
                logical_path = "/" + "/".join(menu.path)

                f.write("=" * 80 + "\n")
                f.write(logical_path + "\n")
                f.write("=" * 80 + "\n")

                for entry in menu.entries:
                    suffix = ""

                    if entry.submenu:
                        suffix = " --->"
                    elif entry.empty_submenu:
                        suffix = " ----"

                    f.write(
                        f"{entry.index:4d} "
                        f"{entry.text}{suffix}\n"
                    )

                f.write("\n")

    def write_transcript(self):
        path = self.output / "menuconfig-dump.txt"

        with path.open("w", encoding="utf-8") as f:
            for menu in self.menus:
                logical_path = "/" + "/".join(menu.path)

                f.write("=" * 80 + "\n")
                f.write(f"MENU: {logical_path}\n")
                f.write("=" * 80 + "\n\n")
                f.write(re.sub(r"^  │ │ *│ │\n", "", menu.rendered_screen.rstrip('\n'), flags=re.MULTILINE))
                f.write("\n\n")


    def write_individual_menus(self):
        root = self.output / "menus"

        # Map each menu path to its number.
        menu_numbers = {
            tuple(menu.path): number
            for number, menu in enumerate(self.menus)
        }

        for number, menu in enumerate(self.menus):
            directory = root

            # Build the complete numbered path.
            for depth, component in enumerate(menu.path):
                path = tuple(menu.path[:depth + 1])
                component_number = menu_numbers.get(path)

                if component_number is not None:
                    component = f"{component_number:04d}- {component}"

                directory /= self.safe_filename(component)

            directory.mkdir(parents=True, exist_ok=True)

            filename = directory / "menu.txt"

            filename.write_text(
                menu.rendered_screen.rstrip("\n") + "\n",
                encoding="utf-8",
            )

    @staticmethod
    def safe_filename(name):
        name = re.sub(r"[^\w .+-]", "_", name)
        name = re.sub(r"\s+", " ", name)
        return name.strip() or "_"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dump the rendered Linux Kconfig menu tree."
    )

    parser.add_argument(
        "--kernel",
        type=Path,
        default=Path(DEFAULT_KERNEL),
        help=f"Linux source tree (default: {DEFAULT_KERNEL})",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"virtual terminal width (default: {DEFAULT_WIDTH})",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help=f"virtual terminal height (default: {DEFAULT_HEIGHT})",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("kconfig-dump"),
        help="output directory",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="print traversal diagnostics",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    kernel = args.kernel.resolve()

    mconf = kernel / "scripts/kconfig/mconf"
    kconfig = kernel / "Kconfig"

    if not mconf.is_file():
        raise SystemExit(f"mconf not found: {mconf}")

    if not os.access(mconf, os.X_OK):
        raise SystemExit(f"mconf is not executable: {mconf}")

    if not kconfig.is_file():
        raise SystemExit(f"Kconfig not found: {kconfig}")

    if subprocess.run(
        ["tmux", "-V"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        raise SystemExit("tmux is required")

    session = MenuConfigSession(
        kernel=kernel,
        width=args.width,
        height=args.height,
        debug=args.debug,
    )

    parser = ScreenParser(debug=args.debug)
    walker = MenuWalker(
        session=session,
        parser=parser,
        debug=args.debug,
    )

    try:
        session.run()

        # Let mconf finish its initial draw.
        time.sleep(1.5)

        initial_screen = session.wait_for_menu()

        if args.debug:
            print("----- initial pane -----", file=sys.stderr)
            print(initial_screen, file=sys.stderr)
            print("----- end initial pane -----", file=sys.stderr)

        if not initial_screen.strip():
            raise RuntimeError(
                "Initial tmux capture is empty; "
                "refusing to start menu walker"
            )

        walker.walk(initial_screen=initial_screen)

        dumper = Dumper(
            menus=walker.menus,
            output=args.output,
        )

        dumper.write()

        print(
            f"Dumped {len(walker.menus)} menus to "
            f"{args.output}"
        )

    finally:
        session.kill()


if __name__ == "__main__":
    main()
