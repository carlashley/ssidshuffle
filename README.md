# ssidshuffle
Re-order SSIDs connected on a specific wireless network interface.
Inspired by a gist from @pudquick - https://gist.github.com/pudquick/fcbdd3924ee230592ab4

## Requirements
Requires `pyobjc` and Python 3.10+.
Tested with Python v3.10.7 and PyObjC v8.5 on macOS 12.4+.

# License
```
MIT License

Copyright (c) 2022 Carl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

# Support
This is provided as is. No support provided.

# Notes
- **Use this at your own risk, no support/warranty is provided!**
- When run on macOS 12 or newer, `sudo` is required to make configuration changes
- When run on macOS 13 or newer, `networksetup -removeallpreferredwirelessnetworks` is used to remove all configured wireless networks from the relevant wireless interface, and `networksetup -addpreferredwirelessnetworkatindex` is then used to re-add them back in the new order.
- - This is a _nuclear_ method to use as if the 'add' method fails, all the configured wireless networks will have been removed, manually re-connecting to the wireless networks may be required
 - - It appears that the ability to re-order SSIDs with CoreWLAN is no longer available in macOS 13 public previews (even though developer notes do not indicate any deprecation); the CoreWLAN framework still returns a success value when the re-order commit is made. If this is an issue you will need to raise feedback with Apple about this, stating the reason why re-ordering SSIDs is critical for your needs. Feedback can be raised via https://feedbackassistant.apple.com by signing in with a developer account, or an ASM/ABM account that is participating in Apple Seed.

# Distribution
A compressed zipfile is built in the `./dist/` folder, this is built with `#!/usr/bin/env python3` as the interpreter path, this interpreter must be able to import various `pyobjc` packages (`CoreWLAN`, `Foundation`, and `PyObjCTools.Conversion`).


# Usage
```
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -h
usage: ssidshuffle [-h] [-n] [-l] [-s, --ssids [[ssid] ...]] [-i [interface]] [--power-cycle] [-v]

A command line utility to quickly re-order SSIDs for a specific wireless network interface.

options:
  -h, --help            show this help message and exit
  -n, --dry-run         performs a dry run
  -l, --list-current    list current SSIDs for the interface
  -s, --ssids [[ssid] ...]
                        SSID names in the order they need to be re-shuffled into; if
                        only one SSID is provided, it will be moved to the first
                        position in the existing preferred connection order, with all
                        other SSIDs being added after in their current order; note:
                        this falls back to using 'networksetup' on macOS 13+, you will
                        need to perform this option as root or by using 'sudo'.
                        when 'networksetup' is used, the SSIDs automatically get the
                        auto-join state enabled, you will need to change this manually
                        if auto-join is not desired
  -i [interface], --interface [interface]
                        the wireless network interface, for example: 'en1'; defaults
                        to the current wirless interface ('en1') when this argument is not
                        supplied
  --power-cycle         power cycles the wireless interface with a 5 second wait
                        between off/on states
  -v, --version         show program's version number and exit
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -l
Current SSID order:
 0: 'Dartanian'
 1: 'Pismo'
 2: 'Mercury'
 3: 'Mac Man'
 4: 'Columbus'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -n -s Columbus Dartanian Pismo Mercury "Mac Man"
Old SSID order:
 0: 'Dartanian'
 1: 'Pismo'
 2: 'Mercury'
 3: 'Mac Man'
 4: 'Columbus'
New SSID order:
 0: 'Columbus'
 1: 'Dartanian'
 2: 'Pismo'
 3: 'Mercury'
 4: 'Mac Man'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -s Columbus Dartanian Pismo Mercury "Mac Man" --power-cycle
Password:
Successfully applied configuration change.
Power cycling wireless interface 'en1'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -n -s "Mac Man"
Old SSID order:
 0: 'Columbus'
 1: 'Dartanian'
 2: 'Pismo'
 3: 'Mercury'
 4: 'Mac Man'
New SSID order:
 0: 'Mac Man'
 1: 'Columbus'
 2: 'Dartanian'
 3: 'Pismo'
 4: 'Mercury'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -s Columbus Dartanian Pismo Mercury "Mac Man"
You must be root to apply these changes.
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -i en1 -s Dartanian Pismo Mercury "Mac Man" Columbus
Successfully applied configuration change.
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -i en1 -s Dartanian Pismo Mercury "Mac Man" Columbus Kaleidoscope
Cannot re-order the specified SSIDs as one or more SSID is not configured.
SSIDs not configured on 'en1': 'Kaleidoscope'.
Current SSID order:
 0: 'Columbus'
 1: 'Dartanian'
 2: 'Pismo'
 3: 'Mercury'
 4: 'Mac Man'
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle --power-cycle
Power cycling wireless interface 'en1'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
```
