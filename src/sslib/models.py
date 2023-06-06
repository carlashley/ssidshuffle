from dataclasses import dataclass, field


@dataclass
class AirportConnectionInfo:
    """Dataclass representing connection information from the output of an 'airport --getinfo' call."""
    auth_80211: str = field(default=None)
    auth_lower: int = field(default=None)
    auth_upper: int = field(default=None)
    bssid: str = field(default=None)
    channel: int = field(default=None)
    channel_extension: int = field(default=None)
    channel_flags: int = field(default=None)
    guard_interval: int = field(default=None)
    last_assoc_status: int = field(default=None)
    last_tx_rate: int | float = field(default=None)
    link_auth: int = field(default=None)
    max_rate: int | float = field(default=None)
    mcs_index: int | float = field(default=None)
    noise_ctl_agr: int | float = field(default=None)
    noise_unit: int | float = field(default=None)
    nss: int | float = field(default=None)
    op_mode: str = field(default=None)
    phymode_active: int = field(default=None)
    phymode_supported: int = field(default=None)
    rssi_ctl_agr: int | float = field(default=None)
    rssi_unit: int | float = field(default=None)
    ssid: str = field(default=None)
    state: str = field(default=None)


# @dataclass
# class WirelessBroadcastNetwork:
#     ap_mode: int | str = field(default=None)
#     bssid: str = field(default=None)
#     country_code: str = field(default=None)
#     channel: int = field(default=None)
#     noise: int | float = field(default=None)
#     rssi: int | float = field(default=None)
#     second_channel_offset: int = field(default=None)
#     ssid: str = field(default=None)
# 
#     def __post_init__(self):
#         self.ap_mode = OPERATING_MODES.get(self.ap_mode, self.ap_mode)
#         self.ssid = self.ssid.decode("utf-8")


