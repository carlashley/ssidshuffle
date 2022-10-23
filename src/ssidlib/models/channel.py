from CoreWLAN import (CWChannel,
                      kCWChannelBand2GHz,
                      kCWChannelBand5GHz,
                      kCWChannelBandUnknown,
                      kCWChannelWidth160MHz,
                      kCWChannelWidth20MHz,
                      kCWChannelWidth40MHz,
                      kCWChannelWidth80MHz,
                      kCWChannelWidthUnknown)

from ..utils.pyobjc import o2p


CHANNEL_BANDS = {kCWChannelBand2GHz: "2.4Ghz",
                 kCWChannelBand5GHz: "5GHz",
                 kCWChannelBandUnknown: "Unknown"}

CHANNEL_WIDTH = {kCWChannelWidth160MHz: "160MHz",
                 kCWChannelWidth80MHz: "80MHz",
                 kCWChannelWidth40MHz: "40MHz",
                 kCWChannelWidth20MHz: "20MHz",
                 kCWChannelWidthUnknown: "Unknown"}


class ChannelBand:
    def __init__(self, cb: CWChannel) -> None:
        self.channel = o2p(cb.channelNumber())
        self.channel_band = CHANNEL_BANDS.get(o2p(cb.channelBand()))
        self.channel_properties = o2p(cb.channelProperties())
        self.channel_width = CHANNEL_WIDTH.get(o2p(cb.channelWidth()))

    def __repr__(self):
        attrvals = [f"{k}={v!r}" for k, v in self.__dict__.items() if not (k.startswith("_") or k.startswith("__"))]
        return f"{type(self).__name__}({', '.join(attrvals)})"
