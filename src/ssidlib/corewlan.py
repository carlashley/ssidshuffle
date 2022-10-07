import sys

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional

import CoreWLAN

from CoreWLAN import CWInterface  # for type hinting neatness
from CoreWLAN import CWConfiguration  # for type hinting neatness
from CoreWLAN import CWMutableConfiguration  # for type hinting neatness
from Foundation import NSOrderedSet
from PyObjCTools import Conversion


def o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html

    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)


def get_interface() -> Optional[CWInterface]:
    """Internal method to get the default Wi-Fi interface."""
    return CoreWLAN.CWInterface.interface()


def get_available_interfaces() -> Optional[Dict[str, CWInterface]]:
    """Internal method to get all available wireless network interfaces.

    Note: The dictionary returned (if there are wireless interfaces) will contain a string representing
          the interface name as the key, this _should_ be the equivalent of the BSD name of the interface,
          for example: 'en0' on modern Mac laptops post USB-C is typically the wireless interface.
          The value for the key is a dynamic PyObjC class type '<objective-c class CWInterface>' and does
          not appear to have a directly importable class that can be used for typing"""
    return o2p(CoreWLAN.CWInterface.interfaceNames())


def get_interface_config(iface: str, mutable: bool = False) -> Optional[CWConfiguration | CWMutableConfiguration]:
    """Get the current configuration for an interface.

    :param iface: interface name, for example: 'en0' - this interface must exist and be available
    :param mutable: return a mutable instance of the configuration (default is False)"""
    iface = CoreWLAN.CWInterface.interfaceWithName_(iface)

    if mutable:
        return CoreWLAN.CWMutableConfiguration.alloc().initWithConfiguration_(iface.configuration())
    else:
        return CoreWLAN.CWConfiguration.alloc().initWithConfiguration_(iface.configuration())


def get_interface_profiles(conf: CWConfiguration | CWMutableConfiguration) -> Optional[Any]:
    """Get interface profiles.

    Note: Not entirely sure what 'profile' means in this context...

    :param conf: either a 'CWConfiguration' or 'CWMutableConfiguration' object"""
    return list(conf.networkProfiles().array())


def get_ssid_ordered_dict(ssids: List[str]) -> OrderedDict:
    """Create an ordered dictionary of SSIDs, with their position as the key, the SSID name as the value.

    :param ssids: list of SSIDs to convert to an OrderedDict."""
    result = OrderedDict()

    for ssid in ssids:
        result[ssid] = ssids.index(ssid)

    return result


def check_all_ssids_exist(ssids: Dict[str, int], current_ssids: Dict[str, int]) -> None:
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


def dry_run_output(ssids: Dict[str, int], current_ssids: Dict[str, int]) -> None:
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


def list_current_ssids(current_ssids: Dict[str, int], iface: str) -> None:
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


def has_configured_ssids(current_ssids: Dict[str, int], iface: str) -> None:
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


def commit_change(config: CWConfiguration | CWMutableConfiguration,
                  new_ssids: List[Any],
                  iface: str) -> None:
    """Commits the change to the SSID order.

    :param config: configuration object
    :param new_ssids: list of new SSID in the order to be committed
    :param iface: the wireless network interface to reorder SSIDs on; this should be the
                  BSD name of the interfoace, for example: 'en0'. By default this is not
                  required as this operation defaults to getting the current wireless
                  interface"""
    nso = NSOrderedSet.orderedSetWithArray_
    commit = CoreWLAN.CWInterface.interfaceWithName_(iface).commitConfiguration_authorization_error_

    config.setNetworkProfiles_(nso(new_ssids))
    # Commit the configuration
    committed = commit(config, None, None)

    if not committed[0]:
        print(f"Error committing change: {committed[1]} - you may need to run this with 'sudo'.", file=sys.stderr)
        sys.exit(1)
    else:
        print("Success!")
