from typing import Optional

from CoreWLAN import (CWConfiguration,
                      CWWiFiClient,
                      CWInterface,
                      CWMutableConfiguration,
                      kCWInterfaceModeHostAP,
                      kCWInterfaceModeIBSS,
                      kCWInterfaceModeNone,
                      kCWInterfaceModeStation,
                      kCWInterfaceStateAssociating,
                      kCWInterfaceStateAuthenticating,
                      kCWInterfaceStateInactive,
                      kCWInterfaceStateScanning,
                      kCWInterfaceStateRunning,
                      kCWOpModeHostAP,
                      kCWOpModeIBSS,
                      kCWOpModeMonitorMode,
                      kCWOpModeStation,
                      kCWOpNotPermitted,
                      kCWPHYMode11a,
                      kCWPHYMode11ac,
                      kCWPHYMode11ax,
                      kCWPHYMode11b,
                      kCWPHYMode11g,
                      kCWPHYMode11n,
                      kCWPHYModeNone,
                      kCWSecurityDynamicWEP,
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

from .channel import ChannelBand
from ..utils import airport
from ..utils.pyobjc import o2p

INTERFACE_MODES = {kCWInterfaceModeHostAP: "Host AP",
                   kCWInterfaceModeIBSS: "IBSS",
                   kCWInterfaceModeNone: "No Mode",
                   kCWInterfaceModeStation: "Station"}

INTERFACE_STATES = {kCWInterfaceStateAssociating: "Associating",
                    kCWInterfaceStateAuthenticating: "Authenticating",
                    kCWInterfaceStateInactive: "Inactive",
                    kCWInterfaceStateScanning: "Scanning",
                    kCWInterfaceStateRunning: "Running"}

NETWORKSETUP_SECURITY_MAP = {kCWSecurityDynamicWEP: "8021XWEP",  # This is a guess...
                             kCWSecurityEnterprise: "8021XWEP",  # This is a guess...
                             kCWSecurityNone: "OPEN",
                             kCWSecurityPersonal: "WPA",  # This is a guess...
                             kCWSecurityUnknown: "OPEN",  # networksetup defaults to open if sec type unknown
                             kCWSecurityWEP: "WEP",
                             kCWSecurityWPA2Enterprise: "WPA2E",
                             kCWSecurityWPA2Personal: "WPA2",
                             kCWSecurityWPA3Enterprise: "WPA2E",  # WPA3 is not an option for networksetup
                             kCWSecurityWPA3Personal: "WPA2",  # WPA3 is not an option for networksetup
                             kCWSecurityWPA3Transition: "WPA2",  # WPA3 is not an option for networksetup
                             kCWSecurityWPAEnterprise: "WPAE",
                             kCWSecurityWPAEnterpriseMixed: "WPAE/WPA2E",
                             kCWSecurityWPAPersonal: "WPA",
                             kCWSecurityWPAPersonalMixed: "WPA/WPA2"}

OPERATING_MODES = {kCWOpModeStation: "Station",
                   kCWOpModeIBSS: "IBSS",
                   kCWOpModeHostAP: "Host AP",
                   kCWOpModeMonitorMode: "Monitor Mode",
                   kCWOpNotPermitted: "Not Permitted"}

PHYSICAL_MODES = {kCWPHYMode11a: "802.11a",
                  kCWPHYMode11b: "802.11b",
                  kCWPHYMode11g: "802.11g",
                  kCWPHYMode11n: "802.11n",
                  kCWPHYMode11ac: "802.11ac",
                  kCWPHYMode11ax: "802.11ax",
                  kCWPHYModeNone: "Unknown"}

SECURITY_TYPES = {kCWSecurityDynamicWEP: "WEP/Dynamic",
                  kCWSecurityEnterprise: "WPA",
                  kCWSecurityNone: "Open",
                  kCWSecurityPersonal: "PSK",
                  kCWSecurityUnknown: "Unknown",
                  kCWSecurityWEP: "WEP",
                  kCWSecurityWPA2Enterprise: "WPA2",
                  kCWSecurityWPA2Personal: "WPA2 PSK",
                  kCWSecurityWPA3Enterprise: "WPA3",
                  kCWSecurityWPA3Personal: "WPA3",
                  kCWSecurityWPA3Transition: "WPA2/WPA3",
                  kCWSecurityWPAEnterprise: "WPA",
                  kCWSecurityWPAEnterpriseMixed: "WPA/Mix",
                  kCWSecurityWPAPersonal: "WPA PSK",
                  kCWSecurityWPAPersonalMixed: "WPA PSK/Mix"}

SECURITY_MODES = {kCWSecurityModeDynamicWEP: "Dynamic WEP",
                  kCWSecurityModeOpen: "Open",
                  kCWSecurityModeWEP: "WEP",
                  kCWSecurityModeWPA2_Enterprise: "WPA2 Enterprise",
                  kCWSecurityModeWPA2_PSK: "WPA2 Personal",
                  kCWSecurityModeWPA_Enterprise: "WPA Enterprise",
                  kCWSecurityModeWPA_PSK: "WPA Personal",
                  kCWSecurityModeWPS: "WPS"}


class WirelessInterface:
    def __init__(self, iface: CWInterface, client: CWWiFiClient) -> None:
        self.active_physical_mode = PHYSICAL_MODES.get(o2p(iface.activePHYMode()), "Unknown")
        self.available = iface.networkInterfaceAvailable()
        self.hardware_address = o2p(iface.hardwareAddress())
        self.ip_monitor = iface.ipMonitor()
        self.last_network_joined = iface.lastNetworkJoined()
        self.last_preferred_network_joined = iface.lastPreferredNetworkJoined()
        self.last_tether_device_joined = iface.lastTetherDeviceJoined()
        self.mode = INTERFACE_MODES.get((o2p(iface.interfaceMode())), "Unknown")
        self.name = o2p(iface.interfaceName())
        self.op_mode = OPERATING_MODES.get(o2p(iface.opMode()), "Unknown")
        self.physical_mode = PHYSICAL_MODES.get(o2p(iface.phyMode()), "Unknown")
        self.power = iface.power()
        self.security_mode = SECURITY_MODES.get(o2p(iface.securityMode()), "Unknown")
        self.service_active = iface.serviceActive()
        self.ssid = iface.ssid()
        self.state = INTERFACE_STATES.get(o2p(iface.interfaceState()), "Unknown")
        self.transmit_power = o2p(iface.transmitPower())
        self.tx_rate = o2p(iface.txRate())
        self.wlan_channel = ChannelBand(iface.wlanChannel())

        # Items that need to init after various standard 'interface' properties
        self.configuration = self._configuration(client=client)
        self.ipv4_addresses = o2p(self.ip_monitor.ipv4Addresses())
        self.ipv4_router = o2p(self.ip_monitor.ipv4Router())
        self.ipv6_addresses = o2p(self.ip_monitor.ipv6Addresses())
        self.ipv6_router = o2p(self.ip_monitor.ipv6Router())
        self.mutable_configuration = self._configuration(client=client, mutable=True)
        self.network_profiles = list(self.configuration.networkProfiles().array())

    def __repr__(self):
        attrvals = [f"{k}={v!r}" for k, v in self.__dict__.items() if not (k.startswith("_") or k.startswith("__"))]
        return f"{type(self).__name__}({', '.join(attrvals)})"

    # ------------------- Properties (as decorated functions) ---------------------------------------------------------
    @property
    def bssid(self) -> Optional[str]:
        """Return the BSSID of the currently connected SSID."""
        return airport.getinfo().bssid

    @property
    def channel(self) -> Optional[int | str]:
        """Return the current channel number."""
        return self.wlan_channel().channel

    @property
    def channel_band(self) -> Optional[str]:
        """Return the current channel band, for example: '5GHz'."""
        try:
            return self.wlan_channel().channel_band
        except KeyError:
            return "Unknown"

    @property
    def channel_width(self) -> Optional[str]:
        """Return the current channel width, for example: '40MHz'."""
        try:
            return self.wlan_channel().channel_width
        except KeyError:
            return "Unknown"

    @property
    def networksetup_security_types_map(self):
        """Map the raw security value for all network profiles on this interface for use
        with the 'networksetup' based re-ordering process if required."""
        return {o2p(p.ssid()): NETWORKSETUP_SECURITY_MAP.get(o2p(p.security()), "Unknown")
                for p in self.network_profiles}

    # ------------------- "Private" Functions -------------------------------------------------------------------------
    def _configuration(self,
                       client: CWWiFiClient,
                       mutable: bool = False) -> Optional[CWConfiguration | CWMutableConfiguration]:
        """Return the current interface configuration as either an immutable or mutable configuration object.

        :param mutable: boolean flag to return an immutable (False) or mutable (True) configuration object"""
        conf = CWConfiguration if not mutable else CWMutableConfiguration
        return conf.alloc().initWithConfiguration_(client.interface().configuration())
