from CoreWLAN import (CWNetwork,
                      CWNetworkProfile)

from .channel import ChannelBand
from .interface import SECURITY_MODES
from ..utils.pyobjc import o2p


class NetworkProfile:
    def __init__(self, np: CWNetworkProfile) -> None:
        self.ssid = o2p(np.ssid())

    def __repr__(self):
        attrvals = [f"{k}={v!r}" for k, v in self.__dict__.items() if not (k.startswith("_") or k.startswith("__"))]
        return f"{type(self).__name__}({', '.join(attrvals)})"


class WirelessNetwork:
    def __init__(self, wn: CWNetwork) -> None:
        self._cb = ChannelBand(cb=wn.wlanChannel())
        self.channel = self._cb.channel
        self.channel_band = self._cb.channel_band
        self.channel_properties = o2p(self._cb.channel_properties)
        self.channel_width = self._cb.channel_width
        self.country_code = None
        self.bssid = o2p(wn.bssid())
        self.rssi = o2p(wn.rssi())
        self.security = SECURITY_MODES.get(o2p(wn.securityMode()), "Unknown")
        self.ssid = o2p(wn.ssid())
        self.is_hidden = self.ssid is None

    def __repr__(self):
        attrvals = [f"{k}={v!r}" for k, v in self.__dict__.items() if not (k.startswith("_") or k.startswith("__"))]
        print(f"{type(self).__name__}({', '.join(attrvals)})")
        return f"{type(self).__name__}({', '.join(attrvals)})"

    def __str__(self):
        return (f"{self.ssid!r} ({self.channel_band}), channel {self.channel} ({self.channel_width} width),"
                f" RSSI {self.rssi}dBm, {self.security}")
