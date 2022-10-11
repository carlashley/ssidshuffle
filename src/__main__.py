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

from os import geteuid
from ssidlib.airport import WiFiAdapter
from ssidlib.utils import major_os_version


NAME = "ssidshuffle"  # for custom arg errors
VERSION = "1.0.20221009"


def _print_arg_err(msg: str, parser: argparse.Namespace, returncode: int = 1) -> None:
    """Print an argument error message and exit.

    :param msg: message to print
    :param parser: the argument parser namespace for usage printing
    :param returncode: the exit code to use when exiting"""
    parser.print_usage(sys.stderr)
    print(msg, file=sys.stderr)
    sys.exit(returncode)


def _arguments() -> None:
    """Construct command line arguments."""
    iface = WiFiAdapter().interface
    valid_interfaces = WiFiAdapter().interfaces
    parser = argparse.ArgumentParser(description=("A command line utility to quickly re-order "
                                                  "SSIDs for a specific wireless network interface."),
                                     formatter_class=argparse.RawTextHelpFormatter)
    a = parser.add_argument

    a("-n", "--dry-run",
      action="store_true",
      dest="dry_run",
      help="performs a dry run",
      required=False)

    a("-l", "--list-current",
      action="store_true",
      dest="list_current",
      help="list current SSIDs for the interface",
      required=False)

    a("-s, --ssids",
      nargs="*",
      dest="ssids",
      metavar="[ssid]",
      help=("SSID names in the order they need to be re-shuffled into; if\n"
            "only one SSID is provided, it will be moved to the first\n"
            "position in the existing preferred connection order, with all\n"
            "other SSIDs being added after in their current order; note:\n"
            "this falls back to using 'networksetup' on macOS 13+, you will\n"
            "need to perform this option as root or by using 'sudo'.\n"
            "when 'networksetup' is used, the SSIDs automatically get the\n"
            "auto-join state enabled, you will need to change this manually\n"
            "if auto-join is not desired"),
      required=False)

    a("-i", "--interface",
      dest="interface",
      metavar="[interface]",
      help=(f"the wireless network interface, for example: {iface!r}; defaults\n"
            f"to the current wirless interface ({iface!r}) when this argument is not\n"
            "supplied"),
      required=False)

    a("--power-cycle",
      action="store_true",
      dest="power_cycle",
      help=("power cycles the wireless interface with a 5 second wait\n"
            "between off/on states"),
      required=False)

    a("--networksetup",
      action="store_true",
      dest="use_networksetup",
      help=argparse.SUPPRESS,
      required=False)

    a("-v", "--version",
      action="version",
      version=f"{NAME} v{VERSION}")

    args = parser.parse_args()

    if args.ssids and major_os_version() >= 12 and not geteuid() == 0 and not args.dry_run:
        print("You must be root to apply these changes.", file=sys.stderr)
        sys.exit(1)

    if args.ssids and args.list_current:
        msg = f"{NAME}: error: argument -s, --ssids: not allowed with argument -l/--list-current"
        _print_arg_err(msg=msg, parser=parser)

    if args.list_current and args.power_cycle:
        msg = f"{NAME}: error: argument -l, --list-current: not allowed with argument --power-cycle"
        _print_arg_err(msg=msg, parser=parser)

    if args.interface and args.interface not in valid_interfaces:
        msg = f"{NAME}: error: the specified interface {args.interface!r} is not a valid wireless interface"

        # Offer up interface as a hint
        if iface:
            msg = f"{msg}; perhaps you meant {iface!r}?"

        _print_arg_err(msg=msg, parser=parser)

    if not args.ssids:
        if not (args.list_current or args.power_cycle):
            msg = f"{NAME}: error: the following arguments are required: -s, --ssids"
            _print_arg_err(msg=msg, parser=parser)

    if args.use_networksetup and not args.ssids:
        msg = f"{NAME}: error: the following arguments are required: -s, --ssids when using --networksetup"
        _print_arg_err(msg=msg, parser=parser)

    return args


def main():
    """Main"""
    args = _arguments()
    wifi = WiFiAdapter(iface=args.interface, dry_run=args.dry_run)

    if args.list_current:
        wifi.print_current_ssid_order()

    if args.ssids:
        wifi.reorder(new_order=args.ssids, use_networksetup=args.use_networksetup)

    if args.power_cycle:
        if not args.dry_run:
            print(f"Power cycling wireless interface {wifi.interface!r}")
            wifi.power_cycle()
        else:
            print(f"Would power cycle wireless interface {wifi.interface!r}")


if __name__ == "__main__":
    main()
