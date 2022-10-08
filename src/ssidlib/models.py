from dataclasses import dataclass, field
from typing import Any

from CoreWLAN import (kCWSecurityDynamicWEP,
                      kCWSecurityEnterprise,
                      kCWSecurityModeDynamicWEP,
                      kCWSecurityModeOpen,
                      kCWSecurityModeWEP,
                      kCWSecurityModeWPA2_Enterprise,
                      kCWSecurityModeWPA2_PSK,
                      kCWSecurityModeWPA_Enterprise,
                      kCWSecurityModeWPA_PSK,
                      kCWSecurityModeWPS,
                      kCWSecurityNone,
                      kCWSecurityPersonal,
                      kCWSecurityUnknown,
                      kCWSecurityWEP,
                      kCWSecurityWPA2Enterprise,
                      kCWSecurityWPA2Personal,
                      kCWSecurityWPA3Enterprise,
                      kCWSecurityWPA3Personal,
                      kCWSecurityWPA3Transition,
                      kCWSecurityWPAEnterprise,
                      kCWSecurityWPAEnterpriseMixed,
                      kCWSecurityWPAPersonal,
                      kCWSecurityWPAPersonalMixed)


SECURITY_TYPES = {kCWSecurityDynamicWEP: "Dynamic WEP",
                  kCWSecurityEnterprise: "Enterprise",
                  kCWSecurityNone: "Open/No Security",
                  kCWSecurityPersonal: "Personal",
                  kCWSecurityUnknown: "Unknown",
                  kCWSecurityWEP: "WEP",
                  kCWSecurityWPA2Enterprise: "WPA2 Enterprise",
                  kCWSecurityWPA2Personal: "WPA2 Personal",
                  kCWSecurityWPA3Enterprise: "WPA3 Enterprise",
                  kCWSecurityWPA3Personal: "WPA3 Personal",
                  kCWSecurityWPA3Transition: "WPA3 Transition (WPA3/WPA2 Personal)",
                  kCWSecurityWPAEnterprise: "WPA Enterprise",
                  kCWSecurityWPAEnterpriseMixed: "WPA/WPA2 Enterprise",
                  kCWSecurityWPAPersonal: "WPA Personal",
                  kCWSecurityWPAPersonalMixed: "WPA/WPA2 Personal Mixed"}

SECURITY_MODES = {kCWSecurityModeDynamicWEP: "Dynamic WEP Mode",
                  kCWSecurityModeOpen: "Open Mode",
                  kCWSecurityModeWEP: "WEP Mode",
                  kCWSecurityModeWPA2_Enterprise: "WPA2 Enterprise Mode",
                  kCWSecurityModeWPA2_PSK: "WPA2 PSK Mode",
                  kCWSecurityModeWPA_Enterprise: "WPA Enterprise Mode",
                  kCWSecurityModeWPA_PSK: "WPA PSK Mode",
                  kCWSecurityModeWPS: "WPS Mode"}


@dataclass
class InterfaceConnection:
    auto_join_history: Any = field(default=None)
    bssid: Any = field(default=None)
    busy: Any = field(default=None)
    cached_scan_results: Any = field(default=None)
    capabilities: Any = field(default=None)
    channel: Any = field(default=None)
    channel_band: Any = field(default=None)
    device: Any = field(default=None)
    device_Attached: Any = field(default=None)
    eapo_client: Any = field(default=None)
    entity_name: Any = field(default=None)
    hardware_address: Any = field(default=None)
    interface_mode: Any = field(default=None)
    interface_state: Any = field(default=None)
    ipv4_addresses: Any = field(default=None)
    ipv4_available: Any = field(default=None)
    ipv4_global_setup_config: Any = field(default=None)
    ipv4_global_setup_key: Any = field(default=None)
    ipv4_global_state_config: Any = field(default=None)
    ipv4_global_state_key: Any = field(default=None)
    ipv4_primary_interface: Any = field(default=None)
    ipv4_primary_service_id: Any = field(default=None)
    ipv4_routable: Any = field(default=None)
    ipv4_router: Any = field(default=None)
    ipv4_setup_config: Any = field(default=None)
    ipv4_state_config: Any = field(default=None)
    ipv4_wifi_global_setup_config: Any = field(default=None)
    ipv4_wifi_global_state_config: Any = field(default=None)
    ipv4_wifi_setup_config: Any = field(default=None)
    ipv4_wifi_setup_key: Any = field(default=None)
    ipv4_wifi_state_config: Any = field(default=None)
    ipv4_wifi_state_key: Any = field(default=None)
    ipv6_addresses: Any = field(default=None)
    ipv6_available: Any = field(default=None)
    ipv6_global_setup_config: Any = field(default=None)
    ipv6_global_setup_key: Any = field(default=None)
    ipv6_global_state_config: Any = field(default=None)
    ipv6_global_state_key: Any = field(default=None)
    ipv6_primary_interface: Any = field(default=None)
    ipv6_primary_service_id: Any = field(default=None)
    ipv6_routable: Any = field(default=None)
    ipv6_router: Any = field(default=None)
    ipv6_setup_config: Any = field(default=None)
    ipv6_state_config: Any = field(default=None)
    ipv6_wifi_global_setup_config: Any = field(default=None)
    ipv6_wifi_global_state_config: Any = field(default=None)
    ipv6_wifi_setup_config: Any = field(default=None)
    ipv6_wifi_setup_key: Any = field(default=None)
    ipv6_wifi_state_config: Any = field(default=None)
    ipv6_wifi_state_key: Any = field(default=None)
    is_airplay_in_progress: Any = field(default=None)
    join_history: Any = field(default=None)
    last_network_joined: Any = field(default=None)
    last_power_state: Any = field(default=None)
    last_preferred_network_joined: Any = field(default=None)
    last_tether_device_joined: Any = field(default=None)
    max_nss_supported_for_ap: Any = field(default=None)
    maximum_link_speed: Any = field(default=None)
    monitor_mode: Any = field(default=None)
    name: Any = field(default=None)
    network_interface_available: Any = field(default=None)
    network_service_ids: Any = field(default=None)
    noise: Any = field(default=None)
    noise_measurement: Any = field(default=None)
    num_tx_streams: Any = field(default=None)
    number_of_spatial_streams: Any = field(default=None)
    observation_info: Any = field(default=None)
    op_mode: Any = field(default=None)
    parent_interface_name: Any = field(default=None)
    physical_mode: Any = field(default=None)
    physical_layer_mode: Any = field(default=None)
    power: Any = field(default=None)
    power_debug_info: Any = field(default=None)
    power_save_mode_enabled: Any = field(default=None)
    roam_history: Any = field(default=None)
    rssi: Any = field(default=None)
    rssi_value: Any = field(default=None)
    security: Any = field(default=None)
    security_mode: Any = field(default=None)
    security_type: Any = field(default=None)
    service_active: Any = field(default=None)
    ssid_name: Any = field(default=None)
    state_info: Any = field(default=None)
    supported_ism_channels: Any = field(default=None)
    supported_physical_layer_modes: Any = field(default=None)
    supported_wlan_channels: Any = field(default=None)
    supported_bsxpc_secure_coding: Any = field(default=None)
    supported_rbsxpc_secure_coding: Any = field(default=None)
    supports_short_gi_40mhz: Any = field(default=None)
    transmit_power: Any = field(default=None)
    transmit_rate: Any = field(default=None)
    tx_rate: Any = field(default=None)
    virtual_interface_role: Any = field(default=None)
    wake_on_wireless_enabled: Any = field(default=None)
    wlan_channel: Any = field(default=None)
    zone: Any = field(default=None)

    def __post_init__(self):
        self.security = SECURITY_TYPES[self.security]
        self.security_mode = SECURITY_MODES[self.security_mode]
