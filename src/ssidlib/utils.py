import subprocess

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from PyObjCTools import Conversion


@dataclass
class NetworkSetupOutput:
    """Basic dataclass to improve the handling of output from
    the '/usr/sbin/networksetup' binary; this binary is notorious
    for incorrectly outputting error messages to standard output,
    rather than to standard error, and for returncodes that don't
    correspond to actual errors when certain arguments fail."""
    returncode: int = field(default=None)
    stdout: str = field(default=None)
    stderr: str = field(default=None)

    # In this post init processing, eliminate any output that is
    # empty string output, then if the returncode is not a success
    # code (0), and if the stddout == stderr output, then this is
    # an error, so handle it accordingly.
    def __post_init__(self):
        self.stdout = None if self.stdout == "" else self.stdout
        self.stderr = None if self.stderr == "" else self.stderr

        if not self.returncode == 0:
            if self.stdout == self.stderr:
                self.stdout = None


def networksetup(args, **kwargs) -> subprocess.CompletedProcess:
    """Run the '/usr/sbin/networksetup' command with arguments.

    :param args: a list of strings to include in the 'networksetup' argument list
    :param **kwargs: **kwargs to pass on to 'subprocess'"""
    cmd = ["/usr/sbin/networksetup"] + args
    kwargs = {"capture_output": True, "encoding": "utf-8"} or kwargs
    return subprocess.run(cmd, **kwargs)


def remove_ssid(iface: str, ssid: Optional[str] = None, remove_all: Optional[bool] = False) -> NetworkSetupOutput:
    """Run the '/usr/sbin/networksetup' command with arguments.
    Note: Apple does not correctly return output on stdout/stderr when errors
          are raised, so this uses a dataclass to resolve this.

    :param iface: wireless interface to remove the preferred network from, for example: 'en1'
    :param ssid: the SSID name (string) to remove, for example: 'Pismo'; required if 'remove_all' is 'False'
    :param remove_all: boolean param to remove all existing preferred wireless networks on the specified
                       wireless interface, default is 'False'
                       when this param is supplied, the client may briefly experience a complete disconnect
                       from the wireless network it may be currently connected to"""
    if not remove_all and not ssid:
        raise TypeError("remove_ssid() missing 2 required positional arguments: 'iface' and 'ssid'")

    if remove_all:
        cmd = ["-removeallpreferredwirelessnetworks", iface]
    else:
        cmd = ["-removepreferredwirelessnetwork", iface, ssid]

    p = networksetup(args=cmd)
    returncode = p.returncode
    stdout = p.stdout.strip() if not p.stdout == "" else None
    stderr = p.stderr.strip() if not p.stderr == "" else None

    if p.returncode == 0:
        if stdout.startswith("Removed "):  # When removing all the stdout msg doesn't include the SSID name
            return NetworkSetupOutput(returncode=returncode, stdout=stdout, stderr=stderr)
        else:
            return NetworkSetupOutput(returncode=1, stdout=None, stderr=stdout or stderr)
    else:
        return NetworkSetupOutput(returncode=returncode, stdout=None, stderr=stdout or stderr)


def add_ssid_at_index(iface: str, ssid: str, index: int | str, security_type: str) -> NetworkSetupOutput:
    """Run the '/usr/sbin/networksetup' command with arguments.
    Note: Apple does not correctly return output on stdout/stderr when errors
          are raised, so this uses a dataclass to resolve this.

    :param iface: wireless interface to add the preferred network to, for example: 'en1'
    :param ssid: the SSID name (string) to add, for example: 'Pismo'
    :param index: the index position to add the SSID into (offset starts at 0), for example: 12"""
    cmd = ["-addpreferredwirelessnetworkatindex", iface, ssid, str(index), security_type]
    p = networksetup(args=cmd)
    returncode = p.returncode
    stdout = p.stdout.strip() if not p.stdout == "" else None
    stderr = p.stderr.strip() if not p.stderr == "" else None

    if p.returncode == 0:
        if stdout.splitlines()[-1].startswith(f"Added {ssid}"):
            return NetworkSetupOutput(returncode=returncode, stdout=stdout, stderr=stderr)
        else:
            return NetworkSetupOutput(returncode=1, stdout=None, stderr=stdout or stderr)
    else:
        return NetworkSetupOutput(returncode=returncode, stdout=None, stderr=stdout or stderr)


def o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    Note: Not all ObjC types can be converted to native Python data types by this method.

    PyObjC Documentation: https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html


    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)
