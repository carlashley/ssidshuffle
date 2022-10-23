import plistlib
import subprocess
import sys

from dataclasses import dataclass, field  # make_dataclass
from os import geteuid
from typing import List, Optional

from CoreWLAN import (kCWOpModeHostAP,
                      kCWOpModeIBSS,
                      kCWOpModeMonitorMode,
                      kCWOpModeStation,
                      kCWOpNotPermitted)


OPERATING_MODES = {kCWOpModeStation: "Station",
                   kCWOpModeIBSS: "IBSS",
                   kCWOpModeHostAP: "Host AP",
                   kCWOpModeMonitorMode: "Monitor Mode",
                   kCWOpNotPermitted: "Not Permitted"}


@dataclass
class WirelessSettings:
    auth_80211: str = field(default=None)
    auth_lower: int = field(default=None)
    auth_upper: int = field(default=None)
    bssid: str = field(default=None)
    channel: int = field(default=None)
    channel_extension: int = field(default=None)
    channel_flags: int = field(default=None)
    last_assoc_status: int = field(default=None)
    last_tx_rate: int | float = field(default=None)
    link_auth: int = field(default=None)
    max_rate: int | float = field(default=None)
    op_mode: str = field(default=None)
    ssid: str = field(default=None)
    state: str = field(default=None)


@dataclass
class WirelessBroadcastNetwork:
    ap_mode: int | str = field(default=None)
    bssid: str = field(default=None)
    country_code: str = field(default=None)
    channel: int = field(default=None)
    noise: int | float = field(default=None)
    rssi: int | float = field(default=None)
    second_channel_offset: int = field(default=None)
    ssid: str = field(default=None)

    def __post_init__(self):
        self.ap_mode = OPERATING_MODES.get(self.ap_mode, self.ap_mode)
        self.ssid = self.ssid.decode("utf-8")


def _airport(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Wrapper around the 'airport' binary in the 802.11 framework.

    :param args: list of string arguments to pass on to 'airport'
    :param **kwargs: dictionary of arguments to pass on to the 'subprocess' call"""
    root_args = ["-I", "--info",
                 "-s", "--scan",
                 "-z", "--disassociate"]

    if any([arg in root_args for arg in args]):
        if not geteuid() == 0:
            root_req_args = ", ".join([f"'{arg}'" for arg in args if arg in root_args])
            print(f"Error: root required for these arguments: {root_req_args}", file=sys.stderr)
            sys.exit(1)

    cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"]
    cmd.extend(args)
    kwargs = kwargs or {"capture_output": True, "encoding": "utf-8"}
    return subprocess.run(cmd, **kwargs)


def disassociate() -> None:
    """Disassociate from any network. 'root' access is required."""
    args = ["--disassociate"]
    return _airport(args)


def getinfo() -> Optional[WirelessSettings]:
    """Get current wireless status info. Requires root to get BSSID.

    Note: The output of "--getinfo" changes if "--xml" is used, with data relating to "BSSID" and other
          items not included in the xml output, so this function merges data from the '--getinfo' output
          and the '--getinfo --xml' output into one result

          This info is a 'mapping' of the '--getinfo' "keys" against the actual key's from the output of
          '--getinfo --xml':
          xml_key_map = {"agrCtlRSSI": "RSSI_CTL_AGR",
                         "agrExtRSSI": "RSSI_EXT_AGR",
                         "agrCtlNoise": "NOISE_CTL_AGR",
                         "agrExtNoise": "NOISE_EXT_AGR",  # unsure of actual xml key name
                         "MCS": "MCS_INDEX",
                         "guardInterval": "GI",
                         "NSS": "NSS",
                         "channel": "CHANNEL"}

          The 'channel' value from the '--getinfo' output includes the extension channel info from
          802.11n standard, for example: '149,1' is '149,+1'"""
    args = ["--getinfo"]
    # Include these values from the non-xml output in the xml output, the key is the "key" from
    # the non-xml output, and the value is the key name to use in the xml output
    inc_from_std_out = {"state": "STATE",  # not in xml
                        "op mode": "OP_MODE",  # not in xml
                        "lastTxRate": "LAST_TX_RATE",  # not in xml
                        "maxRate": "MAX_RATE",  # not in xml
                        "lastAssocStatus": "LAST_ASSOC_STATUS",  # not in xml
                        "802.11 auth": "AUTH_80211",  # not in xml
                        "link auth": "LINK_AUTH",  # not in xml
                        "BSSID": "BSSID",  # not in xml
                        "SSID": "SSID"}  # not in xml
    int_std_out_vals = ["lastTxRate",
                        "maxRate",
                        "lastAssocStatus"]
    p = _airport(args + ["--xml"], **{"capture_output": True})

    if p.returncode == 0:
        result = plistlib.loads(p.stdout.strip())
        p = _airport(args)

        if p.returncode == 0:
            for ln in p.stdout.strip().split("\n"):
                _ln = ln.split(": ")

                if len(_ln) == 2:
                    key, val = [x.strip() for x in _ln]
                else:
                    key, val = _ln[0].strip(), None

                if key in int_std_out_vals:
                    val = int(val)

                # Add channel extension value
                if key == "channel" and val and "," in val:
                    result["CHANNEL_EXTENSION"] = int("".join(val.split(",")[1:]))
                else:
                    result["CHANNEL_EXTENSION"] = None

                if key in inc_from_std_out:
                    result[inc_from_std_out[key]] = val

        if result:
            result = {k.lower(): v for k, v in result.items()}  # lower case keys
            result.update({k: None for k, v in result.items() if v == ""})  # set empty strings to None
            result = WirelessSettings(**result)

        return result


def scan(ssid: Optional[str] = None) -> Optional[List[WirelessBroadcastNetwork]]:
    """Perform a wireless broadcast scan.

    :param ssid: provide the SSID of the network to scan for specifically"""
    if ssid:
        args = [f"--scan={ssid}", "--xml"]
    else:
        args = ["--scan", "--xml"]

    p = _airport(args, **{"capture_output": True})
    fieldnames = ["AP_MODE",
                  "BSSID",
                  "CHANNEL",
                  "NOISE",
                  "RSSI",
                  "SSID"]

    if p.returncode == 0:
        result = list()
        data = plistlib.loads(p.stdout.strip())

        for network in data:
            attrs = dict()
            IE_80211D = network.get("80211D_IE")
            HT_IE = network.get("HT_IE")

            if IE_80211D:
                attrs["country_code"] = IE_80211D.get("IE_KEY_80211D_COUNTRY_CODE", None)
            else:
                attrs["country_code"] = None

            if HT_IE:
                attrs["second_channel_offset"] = HT_IE.get("HT_SECONDARY_CHAN_OFFSET", None)

            for attr in fieldnames:
                attrs[attr.lower()] = network.get(attr)

            result.append(WirelessBroadcastNetwork(**attrs))

        return result
