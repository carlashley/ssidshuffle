"""Parsers of things."""
import plistlib

from dataclasses import fields
from functools import partial
from typing import Optional
from .models import AirportConnectionInfo
from .wrappers import airport

# This is maps stdout of the 'airport --getinfo' utility (for values not in the '--xml' output).
AIRPORT_STDOUT_INFO_MAP: dict[str, (str, type)] = {
    "state": ("state", str),
    "op mode": ("op_mode", str),
    "lastTxRate": ("last_tx_rate", int),
    "maxRate": ("max_rate", int),
    "lastAssocStatus": ("last_assoc_status", int),
    "802.11 auth": ("auth_80211", str),
    "link auth": ("link_auth", str),
    "BSSID": ("bssid", str),
    "SSID": ("ssid", str),
    "guardInterval": ("guard_interval", int),
}


def parse_airport_info() -> Optional[AirportConnectionInfo]:
    """Parses information out of the 'airport --getinfo' and 'airport --getinfo --xml' calls."""
    stdout = partial(
        airport, *["--getinfo"], **{"capture_output": True, "encoding": "utf-8"}
    )
    xmlout = partial(airport, *["--getinfo", "--xml"], **{"capture_output": True})
    reqd_fields = [fn.name for fn in fields(AirportConnectionInfo)]
    del_fields = ["gi"]
    result = {fn: None for fn in reqd_fields}  # all fields exist
    xml_data = plistlib.loads(xmlout().stdout)

    if xml_data:
        result.update(
            {
                k.lower(): v if not v == "" else None
                for k, v in xml_data.items()
                if k.lower() not in del_fields
            }
        )

    for ln in stdout().stdout.strip().splitlines():
        key, *val = [x.strip() for x in ln.strip().split(": ")]
        val = val[0] if val else None

        km = AIRPORT_STDOUT_INFO_MAP.get(key)

        if km:
            new_key, val_type = km
            result[new_key] = val_type(val) if not isinstance(val, val_type) else val

    if result:
        return AirportConnectionInfo(**result)
