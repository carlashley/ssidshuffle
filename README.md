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

# Distribution
A compressed zipfile is built in the `./dist/` folder, this is built with `#!/usr/bin/env python3` as the interpreter path, this interpreter must be able to import various `pyobjc` packages (`CoreWLAN`, `Foundation`, and `PyObjCTools.Conversion`).


# Usage
```
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -h
usage: ssidshuffle [-h] [-n | -l] [-s, --ssids [[ssid] ...]] [-i [interface]] [-v]

A command line utility to quickly re-order SSIDs for a specific wireless network interface.

options:
  -h, --help            show this help message and exit
  -n, --dry-run         performs a dry run
  -l, --list-current    list current SSIDs for the interface
  -s, --ssids [[ssid] ...]
                        SSID names in the order they need to be re-shuffled into
  -i [interface], --interface [interface]
                        the wireless network interface, for example: 'en0'; defaults
                        to the current wirless interface when this argument is not
                        supplied
  -v, --version         show program's version number and exit
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -l
Current SSIDs for interface 'en1' (in order):
 'Dartanian'
 'Pismo'
 'Mercury'
 'Mac Man'
 'Columbus'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -n -s Columbus Dartanian Pismo Mercury "Mac Man"
Old SSID order:
 'Dartanian'
 'Pismo'
 'Mercury'
 'Mac Man'
 'Columbus'
New SSID order:
 'Columbus'
 'Dartanian'
 'Pismo'
 'Mercury'
 'Mac Man'
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -s Columbus Dartanian Pismo Mercury "Mac Man"
Success!
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # ./dist/ssidshuffle -s Columbus Dartanian Pismo Mercury "Mac Man"
Error committing change: Error Domain=com.apple.wifi.apple80211API.error Code=-3930 "(null)" - you may need to run this with 'sudo'.
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -i en1 -s Dartanian Pismo Mercury "Mac Man" Columbus
Success!
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle #
[jappleseed@infiniteloop]:ssidshuffle # sudo ./dist/ssidshuffle -i en1 -s Dartanian Pismo Mercury "Mac Man" Columbus Kaleidoscope
Cannot re-order the specified SSIDs as one or more SSID is not configured.
SSIDs not configured on 'en1': 'Kaleidoscope'.
```
