# kconfig-menu-dump.py - v0.5.4
kconfig-menu-dump.py: Copies your current menuconfig to a series of text files and directory tree.
Co-author: genBTC
Co-author: chatGPT
October, 2026

```
# time ./kconfig-menu-dump.py --debug --width 125 --height 90
> starting:
> tmux new-session -d -s kconfig-dump-26766 -x 125 -y 90 -c /usr/src/linux-5.10 -- make menuconfig
> capture: tmux capture-pane -p -t kconfig-dump-26766 -S -
> capture returned 10773 bytes
----- initial pane -----
----- end initial pane -----
[walker] ENTER MENU: /
Initial screen is here
[walker] selection=0 visible_entries=23 known_entries=0
> capture: tmux capture-pane -p -t kconfig-dump-26766 -S -
> capture returned 10773 bytes
[walker] POSITIONING FOR [0]: 'General setup'
> capture: tmux capture-pane -p -t kconfig-dump-26766 -S -
> capture returned 10773 bytes
[walker] POSITIONED SCREEN FOR [0] by moving: last0 curr0 delta0 'General setup'
> KEY TAB
> KEY ENTER
> capture: tmux capture-pane -p -t kconfig-dump-23128 -S -
> capture returned 5943 bytes
> capture: tmux capture-pane -p -t kconfig-dump-23128 -S -
> capture returned 10773 bytes
[walker] RETURNED FROM [22]: 'Gentoo Linux'
 .config - Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration
 → Gentoo Linux ────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ┌──────────────────────────────────────────────────── Gentoo Linux ────────────────────────────────────────────────────┐
  │  Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----).  Highlighted letters are     │
  │  hotkeys.  Pressing <Y> includes, <N> excludes, <M> modularizes features.  Press <Esc><Esc> to exit, <?> for Help,   │
  │  </> for Search.  Legend: [*] built-in  [ ] excluded  <M> module  < > module capable                                 │
  │                                                                                                                      │
  │ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
  │ │                      [*] Gentoo Linux support                                                                    │ │
  │ │                      [*]   Linux dynamic and persistent device naming (userspace devfs) support                  │ │
  │ │                      [*]   Select options required by Portage features                                           │ │
  │ │                          Support for init systems, system and service managers  --->                             │ │
  │ │                      [ ] Kernel Self Protection Project  ----                                                    │ │
  │ │                      [*] Print firmware information that the kernel attempts to load                             │ │
  │ │                                                                                                                  │ │
  │ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │                               <Select>    < Exit >    < Help >    < Save >    < Load >                               │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


Dumped 150 menus to kconfig-dump/
```
real	0m22.870s
user	0m2.149s
sys	0m2.530s

# Saved Files and Directories:
```
gentoo /usr/src/linux # ls kconfig-dump/
drwxr-xr-x. 24 root root    4096 Oct  2 09:15 menus
-rw-r--r--.  1 root root  121133 Oct  2 09:15 kconfig-tree.txt
-rw-r--r--.  1 root root  770541 Oct  2 09:15 menuconfig-dump.txt
```
## all the menus have been dumped to .txt and numbered
```
gentoo /usr/src/linux # ls kconfig-dump/menus/
drwxr-xr-x. 10 root root   4096 Oct  2 09:15 '0001- General setup'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0011- Processor type and features'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0013- ___ Mitigations for CPU vulnerabilities'
drwxr-xr-x.  5 root root   4096 Oct  2 09:15 '0014- Power management and ACPI options'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0018- Bus options _PCI etc._'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0019- Binary Emulations'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0020- Firmware Drivers'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0022- ___ Virtualization'
drwxr-xr-x.  4 root root   4096 Oct  2 09:15 '0023- General architecture-dependent options'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0026- ___ Enable loadable module support'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0027- -_- Enable the block layer'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0029- IO Schedulers'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0030- Executable file formats'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0031- Memory Management options'
drwxr-xr-x.  4 root root   4096 Oct  2 09:15 '0032- ___ Networking support'
drwxr-xr-x. 38 root root   4096 Oct  2 09:15 '0042- Device Drivers'
drwxr-xr-x.  9 root root   4096 Oct  2 09:15 '0120- File systems'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0128- Security options'
drwxr-xr-x.  2 root root   4096 Oct  2 09:15 '0131- -_- Cryptographic API'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0132- Library routines'
drwxr-xr-x. 14 root root   4096 Oct  2 09:15 '0134- Kernel hacking'
drwxr-xr-x.  3 root root   4096 Oct  2 09:15 '0148- Gentoo Linux'
-rw-r--r--.  1 root root  12721 Oct  2 09:15  menu.txt
```
### menu.txt = Top level menu
```
 .config - Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration                                                                                                                                                                                                             
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────                                                                                                                                                    
  ┌────────────────────────────── Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration ──────────────────────────────┐                                                                                                                                                      
  │  Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----).  Highlighted letters are     │                                                                                                                                                      
  │  hotkeys.  Pressing <Y> includes, <N> excludes, <M> modularizes features.  Press <Esc><Esc> to exit, <?> for Help,   │                                                                                                                                                      
  │  </> for Search.  Legend: [*] built-in  [ ] excluded  <M> module  < > module capable                                 │                                                                                                                                                      
  │                                                                                                                      │                                                                                                                                                      
  │ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │                                                                                                                                                      
  │ │                          General setup  --->                                                                     │ │                                                                                                                                                      
  │ │                      [*] 64-bit kernel                                                                           │ │                                                                                                                                                      
  │ │                          Processor type and features  --->                                                       │ │                                                                                                                                                      
  │ │                      [*] Mitigations for CPU vulnerabilities  --->                                               │ │                                                                                                                                                      
  │ │                          Power management and ACPI options  --->                                                 │ │                                                                                                                                                      
  │ │                          Bus options (PCI etc.)  --->                                                            │ │                                                                                                                                                      
  │ │                          Binary Emulations  --->                                                                 │ │                                                                                                                                                      
  │ │                          Firmware Drivers  --->                                                                  │ │                                                                                                                                                      
  │ │                      [*] Virtualization  --->                                                                    │ │                                                                                                                                                      
  │ │                          General architecture-dependent options  --->                                            │ │                                                                                                                                                      
  │ │                      [*] Enable loadable module support  --->                                                    │ │                                                                                                                                                      
  │ │                      -*- Enable the block layer  --->                                                            │ │                                                                                                                                                      
  │ │                          IO Schedulers  --->                                                                     │ │                                                                                                                                                      
  │ │                          Executable file formats  --->                                                           │ │                                                                                                                                                      
  │ │                          Memory Management options  --->                                                         │ │                                                                                                                                                      
  │ │                      [*] Networking support  --->                                                                │ │                                                                                                                                                      
  │ │                          Device Drivers  --->                                                                    │ │                                                                                                                                                      
  │ │                          File systems  --->                                                                      │ │                                                                                                                                                      
  │ │                          Security options  --->                                                                  │ │                                                                                                                                                      
  │ │                      -*- Cryptographic API  --->                                                                 │ │                                                                                                                                                      
  │ │                          Library routines  --->                                                                  │ │                                                                                                                                                      
  │ │                          Kernel hacking  --->                                                                    │ │                                                                                                                                                      
  │ │                          Gentoo Linux  --->                                                                      │ │                                                                                                                                                      
  │ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
  ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │                               <Select>    < Exit >    < Help >    < Save >    < Load >                               │
  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### kconfig-tree.txt = Summary Overview of Every Item

### menuconfig-dump.txt = Entire Dump in 1 file
```
================================================================================
MENU: /Power management and ACPI options/CPU Idle
================================================================================                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                
 .config - Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration
 → Power management and ACPI options → CPU Idle ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────────── CPU Idle ────────────────────────────────────────────────────────────────────────┐
  │  Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----).  Highlighted letters are hotkeys.  Pressing <Y> includes, <N>   │
  │  excludes, <M> modularizes features.  Press <Esc><Esc> to exit, <?> for Help, </> for Search.  Legend: [*] built-in  [ ] excluded  <M> module  < >      │
  │  module capable                                                                                                                                         │
  │                                                                                                                                                         │
  │ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
  │ │                                       -*- CPU idle PM support                                                                                       │ │
  │ │                                       [ ]   Ladder governor (for periodic timer tick)                                                               │ │
  │ │                                       -*-   Menu governor (for tickless system)                                                                     │ │
  │ │                                       [ ]   Timer events oriented (TEO) governor (for tickless systems)                                             │ │
  │ └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │                                                <Select>    < Exit >    < Help >    < Save >    < Load >                                                 │
  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

================================================================================
MENU: /Bus options (PCI etc.)
================================================================================

 .config - Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration
 → Bus options (PCI etc.) ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ┌──────────────────────────────────────────────────────────────── Bus options (PCI etc.) ─────────────────────────────────────────────────────────────────┐
  │  Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----).  Highlighted letters are hotkeys.  Pressing <Y> includes, <N>   │
  │  excludes, <M> modularizes features.  Press <Esc><Esc> to exit, <?> for Help, </> for Search.  Legend: [*] built-in  [ ] excluded  <M> module  < >      │
  │  module capable                                                                                                                                         │
  │                                                                                                                                                         │
  │ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
  │ │                                       [*] Support mmconfig PCI config space access                                                                  │ │
  │ │                                       [ ] Mark VGA/VBE/EFI FB as generic system framebuffer                                                         │ │
  │ └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
  ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │                                                <Select>    < Exit >    < Help >    < Save >    < Load >                                                 │
  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

================================================================================
MENU: /Binary Emulations
================================================================================

 .config - Linux/x86 5.10.270-gentoo-hardened1 Kernel Configuration
 → Binary Emulations ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────────── Binary Emulations ───────────────────────────────────────────────────────────────────┐
  │  Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----).  Highlighted letters are hotkeys.  Pressing <Y> includes, <N>   │
  │  excludes, <M> modularizes features.  Press <Esc><Esc> to exit, <?> for Help, </> for Search.  Legend: [*] built-in  [ ] excluded  <M> module  < >      │
  │  module capable                                                                                                                                         │
  │                                                                                                                                                         │
  │ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
  │ │                                       [*] IA32 Emulation                                                                                            │ │
  │ │                                       [ ] x32 ABI for 64-bit mode                                                                                   │ │
  │ └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
```
