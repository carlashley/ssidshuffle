# ssidshuffle
Re-order SSIDs connected on a specific wireless network interface.
Inspired by a gist from @pudquick - https://gist.github.com/pudquick/fcbdd3924ee230592ab4

## Requirements
Requires `pyobjc` and Python 3.8+.
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
There is a Python file in the `src` folder that can be used on Mac systems that have had Python 3 installed.

Note: The Python 3 path is referenced by calling the `#!/usr/bin env python3` shebang, so ensure that the version of Python this shebang points to has the `pyobjc` package installed.
You can of course do things with `virtualenv` at your leisure.

Alternatively, there are self contained binary bundles in the `./dist` folder for `arm64` and `x86_64` architecture; these can be used _without_ a Python 3 interpreter installed, but there is an added penalty hit as this requires some magical decompression on each run.


# Usage
```
usage: ssidshuffle.py [-h] [-n | -l] [-s, --ssids [[ssid] ...]] [-i [interface]] [-v]

A command line utility to quickly re-order SSIDs for a specific wireless network interface.

options:
  -h, --help            show this help message and exit
  -n, --dry-run         performs a dry run
  -l, --list-current    list current SSIDs for the interface
  -s, --ssids [[ssid] ...]
                        SSID names in the order they need to be re-shuffled into
  -i [interface], --interface [interface]
                        the wireless network interface, for example: 'en0'; defaults
                        to the current wirless interface
  -v, --version         show program's version number and exit
[jappleseed@infiniteloop]: ~#
```
