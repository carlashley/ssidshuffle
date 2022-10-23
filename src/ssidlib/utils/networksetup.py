import subprocess

from dataclasses import dataclass, field
from typing import List, Optional


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


def _networksetup(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Run the '/usr/sbin/networksetup' command with arguments.

    :param args: a list of strings to include in the 'networksetup' argument list
    :param **kwargs: **kwargs to pass on to 'subprocess'"""
    cmd = ["/usr/sbin/networksetup"] + args
    kwargs = kwargs or {"capture_output": True, "encoding": "utf-8"}
    return subprocess.run(cmd, **kwargs)


def _parse_completed_process(p: subprocess.CompletedProcess, success_str: str) -> NetworkSetupOutput:
    """Parse the completed subprocess object of the internal '_networksetup' function.

    :param p: the completed subprocess object
    :param success_str: the string value that indicates the subprocess completed successfully"""
    returncode = p.returncode
    stdout = p.stdout.strip() if not p.stdout == "" else None
    stderr = p.stderr.strip() if not p.stderr == "" else None

    if p.returncode == 0:
        if stdout.splitlines()[-1].startswith(success_str):
            return NetworkSetupOutput(returncode=returncode, stdout=stdout, stderr=stderr)
        else:
            return NetworkSetupOutput(returncode=1, stdout=None, stderr=stdout or stderr)
    else:
        return NetworkSetupOutput(returncode=returncode, stdout=None, stderr=stdout or stderr)


def add_ssids(iface: str,
              ssid: str,
              index: int | str,
              security_type: str,
              password: Optional[str] = None) -> NetworkSetupOutput:
    """Run the '/usr/sbin/networksetup' command with arguments.
    Note: Apple does not correctly return output on stdout/stderr when errors
          are raised, so this uses a dataclass to resolve this.

    :param iface: wireless interface to add the preferred network to, for example: 'en1'
    :param ssid: the SSID name (string) to add, for example: 'Pismo'
    :param index: the index position to add the SSID into (offset starts at 0), for example: 12
    :praam security_type: the security type to use when adding the interface, default 'networksetup'
                          behaviour is to use 'OPEN' as the default security in certain circumstances
    :param password: password (as plaintext string) of the SSID being added, this is plaintext, so it
                     is not recommended to use this as a means of configuring the SSID, use other
                     methods instead, also note, no username can be provided for SSIDs that require
                     a username and password credential to be provided"""
    cmd = ["-addpreferredwirelessnetworkatindex", iface, ssid, str(index), security_type]

    # Only append if password is there
    if password:
        cmd.append(password)

    return _parse_completed_process(p=_networksetup(args=cmd), success_str=f"Added {ssid}")


def remove_ssids(iface: str, ssid: Optional[str] = None) -> NetworkSetupOutput:
    """Run the '/usr/sbin/networksetup' command with arguments.
    Note: Apple does not correctly return output on stdout/stderr when errors
          are raised, so this uses a dataclass to resolve this.

    :param iface: wireless interface to remove the preferred network from, for example: 'en1'
    :param ssid: the optional SSID name (string) to remove, for example: 'Pismo'; if no SSID is
                 provided, then all existing preferred wireless networks are removed"""
    if ssid:
        cmd = ["-removepreferredwirelessnetwork", iface, ssid]
    else:
        cmd = ["-removeallpreferredwirelessnetworks", iface]
    # When removing all the stdout msg doesn't include the SSID name, so use generic success string value
    return _parse_completed_process(p=_networksetup(args=cmd), success_str="Removed ")
