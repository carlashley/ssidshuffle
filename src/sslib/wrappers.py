"""Wrappers of system binaries."""
import subprocess
import sys

from .utils import is_root


def airport(*args, **kwargs) -> subprocess.CompletedProcess:
    """Wraps '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'.
    Note: this system binary does not consistently return error messages to 'stderr', so
          additional processing by the calling function/method will need to be done.
    :param *args: arguments to pass to the system binary
    :param **kwargs: arguments to pass to the subprocess call"""
    root_args = ["-I", "--info", "-s", "--scan", "-z", "--disassociate"]
    ap = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    cmd = [ap, *args]

    if any(arg in root_args for arg in args) and not is_root():
        print(f"Error: you must be root to run {ap!r}.", file=sys.stderr)
        sys.exit(1)

    return subprocess.run(cmd, **kwargs)


def networksetup(*args, **kwargs) -> subprocess.CompletedProcess:
    """Wraps '/usr/sbin/networksetup'.
    Note: this system binary does not consistently return error messages to 'stderr', so
          additional processing by the calling function/method will need to be done.
    :param *args: arguments to pass to the system binary
    :param **kwargs: arguments to pass to the subprocess call"""
    cmd = ["/usr/sbin/networksetup", *args]
    return subprocess.run(cmd, **kwargs)
