from dataclasses import dataclass, field, make_dataclass  # NOQA
from pprint import pformat  # NOQA
from typing import Any, Callable, List, Optional

from CoreWLAN import CWConfiguration, CWInterface, CWMutableConfiguration, CWWiFiClient
from PyObjCTools import Conversion

from .models import InterfaceConnection


def o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    Note: Not all ObjC types can be converted to native Python data types by this method.

    PyObjC Documentation: https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html


    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)


class WiFiAdapterException(Exception):
    """WiFiAdapter Exception"""
    pass


class WiFiAdapterCommitConfigurationException(Exception):
    """WiFiAdapter Commit Configuration Exception"""
    pass


class WiFiAdapter:
    def __init__(self,
                 client: CWWiFiClient = CWWiFiClient.sharedWiFiClient(),
                 iface: Optional[str] = None) -> None:
        self._client = client
        self._iface = iface or self.interface

    def _get_configuration(self,
                           mutable: Optional[bool] = False) -> Optional[CWConfiguration | CWMutableConfiguration]:
        """Gets the current configuration for a wireless interface.

        :param iface: interface name (string), for example 'en0'
        :param mutable: boolean value to return a mutable version of the configuration that will
                        allow modifications to the configuration if the param is True; default is False"""
        conf = CWConfiguration if not mutable else CWMutableConfiguration
        iface = self._client.interfaceWithName_(self._iface)

        return conf.alloc().initWithConfiguration_(iface.configuration())

    @property
    def _interface(self) -> Optional[CWInterface]:
        """Return the current interface as an object."""
        return self._client.interface()

    def _interface_with_name(self) -> Optional[CWInterface]:
        """Return the interface as a 'CWInterface' object."""
        return self._client.interfaceWithName_(self._iface)

    @property
    def interface(self) -> str:
        """Return the default wireless interface name."""
        return o2p(self._client.interface().interfaceName())

    @property
    def interfaces(self) -> str:
        """Return a list of available and valid wireless interface names."""
        return [o2p(iface.interfaceName()) for iface in self._client.interfaces()]

    @property
    def configuration(self) -> Optional[CWConfiguration]:
        """Return an immutable configuration for the wireless interface."""
        return self._get_configuration(iface=self._iface)

    @property
    def mutable_configuration(self) -> Optional[CWMutableConfiguration]:
        """Return a mutable configuration for the wireless interface."""
        return self._get_configuration(iface=self._iface, mutable=True)

    @property
    def network_profiles(self) -> Optional[List[CWConfiguration | CWMutableConfiguration]]:
        """Gets the current configuration for a wireless interface. The items in the
        result are in the order in which macOS will prefer to join to."""
        return list(self._get_configuration().networkProfiles().array())

    def commit_configuration(self, config: CWMutableConfiguration) -> None:
        """Commit a configuration change. The returned result from the 'commit' action is a tuple
        containing the result state ('True' for success, 'False' for failure) and any error message.

        :param config: mutable configuration object containing the updated changes"""
        committer = self._interface_with_name(self._iface).commitConfiguration_interfaceName_authorization_error_
        success, error_msg = committer(config, None, None)

        if not success:
            raise WiFiAdapterCommitConfigurationException(error_msg)

    def current_connection(self) -> InterfaceConnection:
        """Get current connection details and return an instance of 'InterfaceConnection'."""
        ip_monitor = self._interface.ipMonitor()

        data = {"auto_join_history": self._interface.autoJoinHistory(),
                "bssid": self._interface.bssid(),  # Note, this won't return anything in 10.15+ because location data
                "busy": self._interface.busy(),
                "cached_scan_results": list(self._interface.cachedScanResults()),  # Last network scan results
                "capabilities": o2p(self._interface.capabilities()),
                "channel": self._interface.channel(),
                "channel_band": self._interface.channel(),
                "device": self._interface.device(),
                "device_Attached": self._interface.deviceAttached(),
                "eapo_client": self._interface.eapolClient(),
                "entity_name": self._interface.entityName(),
                "hardware_address": self._interface.hardwareAddress(),
                "interface_mode": self._interface.interfaceMode(),
                "interface_state": self._interface.interfaceState(),
                "ipv4_addresses": o2p(ip_monitor.ipv4Addresses()),
                "ipv4_available": ip_monitor.ipv4Available(),
                "ipv4_global_setup_config": o2p(ip_monitor.ipv4GlobalSetupConfig()),
                "ipv4_global_setup_key": o2p(ip_monitor.ipv4GlobalSetupKey()),
                "ipv4_global_state_config": o2p(ip_monitor.ipv4GlobalStateConfig()),
                "ipv4_global_state_key": ip_monitor.ipv4GlobalStateKey(),
                "ipv4_primary_interface": ip_monitor.ipv4PrimaryInterface(),
                "ipv4_primary_service_id": ip_monitor.ipv4PrimaryServiceID(),
                "ipv4_routable": ip_monitor.ipv4Routable(),
                "ipv4_router": ip_monitor.ipv4Router(),
                "ipv4_setup_config": o2p(ip_monitor.ipv4SetupConfig()),
                "ipv4_state_config": o2p(ip_monitor.ipv4StateConfig()),
                "ipv4_wifi_global_setup_config": o2p(ip_monitor.ipv4WiFiGlobalSetupConfig()),
                "ipv4_wifi_global_state_config": o2p(ip_monitor.ipv4WiFiGlobalStateConfig()),
                "ipv4_wifi_setup_config": o2p(ip_monitor.ipv4WiFiSetupConfig()),
                "ipv4_wifi_setup_key": ip_monitor.ipv4WiFiSetupKey(),
                "ipv4_wifi_state_config": o2p(ip_monitor.ipv4WiFiStateConfig()),
                "ipv4_wifi_state_key": ip_monitor.ipv4WiFiStateKey(),
                "ipv6_addresses": o2p(ip_monitor.ipv6Addresses()),
                "ipv6_available": ip_monitor.ipv6Available(),
                "ipv6_global_setup_config": o2p(ip_monitor.ipv6GlobalSetupConfig()),
                "ipv6_global_setup_key": ip_monitor.ipv6GlobalSetupKey(),
                "ipv6_global_state_config": o2p(ip_monitor.ipv6GlobalStateConfig()),
                "ipv6_global_state_key": ip_monitor.ipv6GlobalStateKey(),
                "ipv6_primary_interface": ip_monitor.ipv6PrimaryInterface(),
                "ipv6_primary_service_id": ip_monitor.ipv6PrimaryServiceID(),
                "ipv6_routable": ip_monitor.ipv6Routable(),
                "ipv6_router": ip_monitor.ipv6Router(),
                "ipv6_setup_config": o2p(ip_monitor.ipv6SetupConfig()),
                "ipv6_state_config": o2p(ip_monitor.ipv6StateConfig()),
                "ipv6_wifi_global_setup_config": o2p(ip_monitor.ipv6WiFiGlobalSetupConfig()),
                "ipv6_wifi_global_state_config": o2p(ip_monitor.ipv6WiFiGlobalStateConfig()),
                "ipv6_wifi_setup_config": o2p(ip_monitor.ipv6WiFiSetupConfig()),
                "ipv6_wifi_setup_key": ip_monitor.ipv6WiFiSetupKey(),
                "ipv6_wifi_state_config": o2p(ip_monitor.ipv6WiFiStateConfig()),
                "ipv6_wifi_state_key": ip_monitor.ipv6WiFiStateKey(),
                "is_airplay_in_progress": self._interface.isAirPlayInProgress(),
                "join_history": self._interface.joinHistory(),
                "last_network_joined": self._interface.lastNetworkJoined(),
                "last_power_state": self._interface.lastPowerState(),
                "last_preferred_network_joined": self._interface.lastPreferredNetworkJoined(),
                "last_tether_device_joined": self._interface.lastTetherDeviceJoined(),
                "max_nss_supported_for_ap": self._interface.maxNSSSupportedForAP(),
                "maximum_link_speed": self._interface.maximumLinkSpeed(),
                "monitor_mode": self._interface.monitorMode(),
                "name": self._interface.name(),
                "network_interface_available": self._interface.networkInterfaceAvailable(),
                "network_service_ids": o2p(self._interface.networkServiceIDs()),
                "noise": self._interface.noise(),
                "noise_measurement": self._interface.noiseMeasurement(),
                "num_tx_streams": self._interface.numTXStreams(),
                "number_of_spatial_streams": self._interface.numberOfSpatialStreams(),
                "observation_info": self._interface.observationInfo(),
                "op_mode": self._interface.opMode(),
                "parent_interface_name": self._interface.parentInterfaceName(),
                "physical_mode": self._interface.phyMode(),
                "physical_layer_mode": self._interface.physicalLayerMode(),
                "power": self._interface.power(),
                "power_debug_info": o2p(self._interface.powerDebugInfo()),
                "power_save_mode_enabled": self._interface.powerSaveModeEnabled(),
                "roam_history": self._interface.roamHistory(),
                "rssi": self._interface.rssi(),
                "rssi_value": self._interface.rssiValue(),
                "security": self._interface.security(),
                "security_mode": self._interface.securityMode(),
                "security_type": self._interface.securityType(),
                "service_active": self._interface.serviceActive(),
                "ssid_name": self._interface.ssid(),
                "state_info": self._interface.stateInfo(),
                "supported_ism_channels": list(self._interface.supportedISMChannels()),
                "supported_physical_layer_modes": self._interface.supportedPhysicalLayerModes(),
                "supported_wlan_channels": list(self._interface.supportedWLANChannels()),
                "supported_bsxpc_secure_coding": self._interface.supportsBSXPCSecureCoding(),
                "supported_rbsxpc_secure_coding": self._interface.supportsRBSXPCSecureCoding(),
                "supports_short_gi_40mhz": self._interface.supportsShortGI40MHz(),
                "transmit_power": self._interface.transmitPower(),
                "transmit_rate": self._interface.transmitRate(),
                "tx_rate": self._interface.txRate(),
                "virtual_interface_role": self._interface.virtualInterfaceRole(),
                "wake_on_wireless_enabled": self._interface.wakeOnWirelessEnabled(),
                "wlan_channel": self._interface.wlanChannel(),
                "zone": self._interface.zone()}

        return InterfaceConnection(**data)
