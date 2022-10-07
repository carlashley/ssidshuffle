#!/usr/bin/env python3
"""This is a basic utility to re-order SSIDs that have been configured on a specific
network interface.

Inspired by and adapted from: https://gist.github.com/pudquick/fcbdd3924ee230592ab4


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
SOFTWARE."""
import argparse
import sys
import CoreWLAN

from collections import OrderedDict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from CoreWLAN import CWInterface  # for type hinting neatness
    from CoreWLAN import CWConfiguration  # for type hinting neatness
    from CoreWLAN import CWMutableConfiguration  # for type hinting neatness
    from Foundation import NSOrderedSet
    from PyObjCTools import Conversion
except ModuleNotFoundError:
    print("Error: Could not find required PyObjC packages for importing.\n"
          "       Please run: 'pip install pyobjc'", file=sys.stderr)
    sys.exit(667)


NAME = Path(__file__).name.replace("./", "")  # for custom arg errors
VERSION = "1.0.20221007"


def _o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html

    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)


def _get_interface() -> Optional[CWInterface]:
    """Internal method to get the default Wi-Fi interface."""
    return CoreWLAN.CWInterface.interface()


def _get_available_interfaces() -> Optional[Dict[str, CWInterface]]:
    """Internal method to get all available wireless network interfaces.

    Note: The dictionary returned (if there are wireless interfaces) will contain a string representing
          the interface name as the key, this _should_ be the equivalent of the BSD name of the interface,
          for example: 'en0' on modern Mac laptops post USB-C is typically the wireless interface.
          The value for the key is a dynamic PyObjC class type '<objective-c class CWInterface>' and does
          not appear to have a directly importable class that can be used for typing"""
    return _o2p(CoreWLAN.CWInterface.interfaceNames())


def _get_interface_config(iface: str, mutable: bool = False) -> Optional[CWConfiguration | CWMutableConfiguration]:
    """Get the current configuration for an interface.

    :param iface: interface name, for example: 'en0' - this interface must exist and be available
    :param mutable: return a mutable instance of the configuration (default is False)"""
    iface = CoreWLAN.CWInterface.interfaceWithName_(iface)

    if mutable:
        return CoreWLAN.CWMutableConfiguration.alloc().initWithConfiguration_(iface.configuration())
    else:
        return CoreWLAN.CWConfiguration.alloc().initWithConfiguration_(iface.configuration())


def _get_interface_profiles(conf: CWConfiguration | CWMutableConfiguration) -> Optional[Any]:
    """Get interface profiles.

    Note: Not entirely sure what 'profile' means in this context...

    :param conf: either a 'CWConfiguration' or 'CWMutableConfiguration' object"""
    return list(conf.networkProfiles().array())


def _get_ssid_ordered_dict(ssids: List[str]) -> OrderedDict:
    """Create an ordered dictionary of SSIDs, with their position as the key, the SSID name as the value.

    :param ssids: list of SSIDs to convert to an OrderedDict."""
    result = OrderedDict()

    for ssid in ssids:
        result[ssid] = ssids.index(ssid)

    return result


def _check_all_ssids_exist(ssids: Dict[str, int], current_ssids: Dict[str, int]) -> None:
    """Check's all the provied SSIDs for re-ordering exist in the current set of configured
    SSIDs.

    :param ssids: a dictionary with ssid name as the key, and the position (int) as the value
                  to use for ordering the SSID
    :param current_ssids: a dictionary of the current configured SSIDs with ssid name as the
                          key, and the position (int)"""
    if not all([ssid in current_ssids for ssid, posn in ssids.items()]):
        missing_ssids = ", ".join([f"{s!r}" for s, _ in sorted(ssids.items(), key=lambda x: x[1])
                                   if s not in current_ssids])
        print("Cannot re-order the specified SSIDs as one or more SSID is not configured.", file=sys.stderr)
        print(f"SSIDs not configured on the specified interface: {missing_ssids}.", file=sys.stderr)
        sys.exit(2)


def _dry_run_output(ssids: Dict[str, int], current_ssids: Dict[str, int]) -> None:
    """Prints the output of a dry run operation.

    :param ssids: a dictionary with ssid name as the key, and the position (int) as the value
                  to use for ordering the SSID
    :param current_ssids: a dictionary of the current configured SSIDs with ssid name as the
                          key, and the position (int)"""
    old = [f" {s!r}" for s, p in current_ssids.items()]
    new = [f" {s!r}" for s, p in ssids.items()]
    new.extend([ssid for ssid in old if ssid not in new.copy()])
    old = "\n".join(old)
    new = "\n".join(new)

    print("Old SSID order:")
    print(f"{old}")
    print("New SSID order:")
    print(f"{new}")


def _list_current(current_ssids: Dict[str, int], iface: str) -> None:
    """Prints the output of a list current SSIDs operation.

    :param current_ssids: a dictionary of the current configured SSIDs with ssid name as the
                          key, and the position (int)
    :param iface: the wireless network interface to reorder SSIDs on; this should be the
                  BSD name of the interfoace, for example: 'en0'. By default this is not
                  required as this operation defaults to getting the current wireless
                  interface"""
    current_ssids = [ssid for ssid, _ in current_ssids.copy().items()]

    if len(current_ssids) > 0:
        print(f"Current SSIDs for interface {iface!r}")

        for ssid in current_ssids:
            print(f" {current_ssids.index(ssid)}:{ssid}")

        sys.exit(0)
    else:
        print(f"Wirless interface {iface!r} does not have any configured SSIDs", file=sys.stderr)
        sys.exit(44)


def _has_configured_ssids(current_ssids: Dict[str, int], iface: str) -> None:
    """Checks if there are any configured SSIDs for the wireless interface.

    :param current_ssids: a dictionary of the current configured SSIDs with ssid name as the
                          key, and the position (int)
    :param iface: the wireless network interface to reorder SSIDs on; this should be the
                  BSD name of the interfoace, for example: 'en0'. By default this is not
                  required as this operation defaults to getting the current wireless
                  interface"""
    if not len(current_ssids) > 0:
        print(f"Wirless interface {iface!r} does not have any configured SSIDs", file=sys.stderr)
        sys.exit(44)


def reorder_ssids(ssids: Optional[Dict[str, int]] = dict(),
                  iface: Optional[str] = None,
                  list_ssids: Optional[bool] = False,
                  dry_run: Optional[bool] = False) -> None:
    """Reorder the SSIDs for a given Wi-Fi interface.

    Note: This performs a check to ensure that all the SSIDs provided have been configured on the
          specified interface to avoid possible issues with applying empty configurations.
          Additionally, if an SSID in the new ordering does not exist, it will be skipped.

          It seems that post macOS Big Sur (11.0), committing changes to the configuration now
          requires elevating priviliges with 'sudo', not running this with 'sudo' will generate
          an error like the one below:
            'Error Domain=com.apple.wifi.apple80211API.error Code=-3930 "(null)"'
          This error correlates to 'kCWOperationNotPermittedErr' and seems to be a result of Apple
          enforcing higher level access requirements on network related changes that are _not_ made
          via System Preferences/System Settings.

    :param ssids: a dictionary with ssid name as the key, and the position (int) as the value
                  to use for ordering the SSID
    :param iface: the wireless network interface to reorder SSIDs on; this should be the
                  BSD name of the interfoace, for example: 'en0'. By default this is not
                  required as this operation defaults to getting the current wireless
                  interface
    :param list_ssids: list current SSIDs
    :param dry_run: perform a dry run"""
    reordered = list()
    nso = NSOrderedSet.orderedSetWithArray_
    commit = CoreWLAN.CWInterface.interfaceWithName_(iface).commitConfiguration_authorization_error_

    iface = iface or _get_interface().interfaceName()  # use provided param value or default to current iface
    config = _get_interface_config(iface=iface, mutable=True)

    if not config:
        print(f"Error: No configuration found for {iface!r}", file=sys.stderr)
        sys.exit(99)

    current_ssids = _get_ssid_ordered_dict([profile.ssid() for profile in _get_interface_profiles(config)])

    if list_ssids:
        _list_current(current_ssids=current_ssids, iface=iface)

    # Check that all SSIDs being re-ordered have been configured
    _check_all_ssids_exist(ssids=ssids, current_ssids=current_ssids)

    # Check that the wireless interface actually has SSIDs that can be re-ordered
    _has_configured_ssids(current_ssids=current_ssids, iface=iface)

    if not dry_run:
        completed = list()  # used for tracking what has been shuffled and what hasn't

        # Do the shuffle...
        for ssid, posn in ssids.items():
            try:
                current_index = current_ssids[ssid]
                reordered.append(config.networkProfiles().array()[current_index])
                completed.append(ssid)
            except IndexError:
                print(f"Warning: {ssid!r} is not configured on {iface!r}, skipping this change.")
                pass

        # Check for any SSIDs that weren't in the new order dictionary and re-add them back at the bottom.
        for wifi_profile in config.networkProfiles().array():
            if _o2p(wifi_profile.ssid()) not in completed:
                reordered.append(wifi_profile)

        # Update the configuration
        config.setNetworkProfiles_(nso(reordered))

        # Commit the configuration
        committed = commit(config, None, None)

        if not committed[0]:
            print(f"Error committing change: {committed[1]} - you may need to run this with 'sudo'.", file=sys.stderr)
            sys.exit(1)
        else:
            print("Success!")
    else:
        _dry_run_output(ssids=ssids, current_ssids=current_ssids)


def arguments() -> None:
    """Construct command line arguments."""
    parser = argparse.ArgumentParser(description=("A command line utility to quickly re-order "
                                                  "SSIDs for a specific wireless network interface."),
                                     formatter_class=argparse.RawTextHelpFormatter)
    a = parser.add_argument
    e = parser.add_mutually_exclusive_group().add_argument

    e("-n", "--dry-run",
      action="store_true",
      dest="dry_run",
      help="performs a dry run",
      required=False)

    e("-l", "--list-current",
      action="store_true",
      dest="list_current",
      help="list current SSIDs for the interface",
      required=False)

    a("-s, --ssids",
      nargs="*",
      dest="ssids",
      metavar="[ssid]",
      help="SSID names in the order they need to be re-shuffled into",
      required=False)

    a("-i", "--interface",
      dest="interface",
      metavar="[interface]",
      help=("the wireless network interface, for example: 'en0'; defaults\n"
            "to the current wirless interface"),
      required=False)

    a("-v", "--version",
      action="version",
      version=f"{NAME} v{VERSION}")

    args = parser.parse_args()
    valid_interfaces = _get_available_interfaces()

    if args.interface and args.interface not in valid_interfaces:
        parser.print_usage(sys.stderr)
        iface = _get_interface().interfaceName()
        msg = f"{NAME}: error: the specified interface {args.interface!r} is not a valid wireless interface"

        # Offer up interface as a hint
        if iface:
            msg = f"{msg}; perhaps you meant {iface!r}?"

        print(msg, file=sys.stdout)
        sys.exit(1)

    if not args.list_current and not args.ssids:
        parser.print_usage(sys.stderr)
        msg = f"{NAME}: error: the following arguments are required: -s, --ssids"
        print(msg, file=sys.stdout)
        sys.exit(1)

    if args.ssids:
        args.ssids = {ssid: args.ssids.index(ssid) for ssid in args.ssids.copy()}

    return args


if __name__ == "__main__":
    args = arguments()

    reorder_ssids(ssids=args.ssids,
                  iface=args.interface,
                  list_ssids=args.list_current,
                  dry_run=args.dry_run)
