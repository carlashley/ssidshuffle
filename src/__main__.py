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

from typing import Dict, Optional

from ssidlib.corewlan import check_all_ssids_exist
from ssidlib.corewlan import commit_change
from ssidlib.corewlan import dry_run_output
from ssidlib.corewlan import get_available_interfaces
from ssidlib.corewlan import get_interface
from ssidlib.corewlan import get_interface_config
from ssidlib.corewlan import get_interface_profiles
from ssidlib.corewlan import get_ssid_ordered_dict
from ssidlib.corewlan import has_configured_ssids
from ssidlib.corewlan import list_current_ssids
from ssidlib.corewlan import o2p

NAME = "ssidshuffle"  # for custom arg errors
VERSION = "1.0.20221007"


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

    iface = iface or get_interface().interfaceName()  # use provided param value or default to current iface
    config = get_interface_config(iface=iface, mutable=True)

    if not config:
        print(f"Error: No configuration found for {iface!r}", file=sys.stderr)
        sys.exit(99)

    current_ssids = get_ssid_ordered_dict([profile.ssid() for profile in get_interface_profiles(config)])

    if list_ssids:
        list_current_ssids(current_ssids=current_ssids, iface=iface)

    # Check that all SSIDs being re-ordered have been configured
    check_all_ssids_exist(ssids=ssids, current_ssids=current_ssids)

    # Check that the wireless interface actually has SSIDs that can be re-ordered
    has_configured_ssids(current_ssids=current_ssids, iface=iface)

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
            if o2p(wifi_profile.ssid()) not in completed:
                reordered.append(wifi_profile)

        # Update the configuration
        commit_change(config=config, new_ssids=reordered, iface=iface)
    else:
        dry_run_output(ssids=ssids, current_ssids=current_ssids)


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
            "to the current wirless interface when this argument is not\n"
            "supplied"),
      required=False)

    a("-v", "--version",
      action="version",
      version=f"{NAME} v{VERSION}")

    args = parser.parse_args()
    valid_interfaces = get_available_interfaces()

    if args.interface and args.interface not in valid_interfaces:
        parser.print_usage(sys.stderr)
        iface = get_interface().interfaceName()
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
