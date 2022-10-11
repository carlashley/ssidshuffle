import subprocess

from collections import OrderedDict
from dataclasses import dataclass, field
from platform import mac_ver
from typing import Dict, Any, Callable, List, Optional

from CoreWLAN import CWInterface
from CoreWLAN import CWConfiguration
from CoreWLAN import CWMutableConfiguration
from PyObjCTools import Conversion


ListNetworkConfigurationTypes = List[CWConfiguration | CWMutableConfiguration]


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


def networksetup(args, **kwargs) -> subprocess.CompletedProcess:
    """Run the '/usr/sbin/networksetup' command with arguments.

    :param args: a list of strings to include in the 'networksetup' argument list
    :param **kwargs: **kwargs to pass on to 'subprocess'"""
    cmd = ["/usr/sbin/networksetup"] + args
    kwargs = {"capture_output": True, "encoding": "utf-8"} or kwargs
    return subprocess.run(cmd, **kwargs)


def remove_ssid(iface: str, ssid: Optional[str] = None, remove_all: Optional[bool] = False) -> NetworkSetupOutput:
    """Run the '/usr/sbin/networksetup' command with arguments.
    Note: Apple does not correctly return output on stdout/stderr when errors
          are raised, so this uses a dataclass to resolve this.

    :param iface: wireless interface to remove the preferred network from, for example: 'en1'
    :param ssid: the SSID name (string) to remove, for example: 'Pismo'; required if 'remove_all' is 'False'
    :param remove_all: boolean param to remove all existing preferred wireless networks on the specified
                       wireless interface, default is 'False'
                       when this param is supplied, the client may briefly experience a complete disconnect
                       from the wireless network it may be currently connected to"""
    if not remove_all and not ssid:
        raise TypeError("remove_ssid() missing 2 required positional arguments: 'iface' and 'ssid'")

    if remove_all:
        cmd = ["-removeallpreferredwirelessnetworks", iface]
    else:
        cmd = ["-removepreferredwirelessnetwork", iface, ssid]

    p = networksetup(args=cmd)
    returncode = p.returncode
    stdout = p.stdout.strip() if not p.stdout == "" else None
    stderr = p.stderr.strip() if not p.stderr == "" else None

    if p.returncode == 0:
        if stdout.startswith("Removed "):  # When removing all the stdout msg doesn't include the SSID name
            return NetworkSetupOutput(returncode=returncode, stdout=stdout, stderr=stderr)
        else:
            return NetworkSetupOutput(returncode=1, stdout=None, stderr=stdout or stderr)
    else:
        return NetworkSetupOutput(returncode=returncode, stdout=None, stderr=stdout or stderr)


def add_ssid_at_index(iface: str,
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

    p = networksetup(args=cmd)
    returncode = p.returncode
    stdout = p.stdout.strip() if not p.stdout == "" else None
    stderr = p.stderr.strip() if not p.stderr == "" else None

    if p.returncode == 0:
        if stdout.splitlines()[-1].startswith(f"Added {ssid}"):
            return NetworkSetupOutput(returncode=returncode, stdout=stdout, stderr=stderr)
        else:
            return NetworkSetupOutput(returncode=1, stdout=None, stderr=stdout or stderr)
    else:
        return NetworkSetupOutput(returncode=returncode, stdout=None, stderr=stdout or stderr)


def o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    Note: Not all ObjC types can be converted to native Python data types by this method.

    PyObjC Documentation: https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html


    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)


def reorder_ssids(new_order: List[str],
                  old_order: OrderedDict,
                  current_profiles: ListNetworkConfigurationTypes) -> ListNetworkConfigurationTypes:
    """Reorder a list of CoreWLAN configurations (mutable or immutable) and return the reordered list.

    :param new_order: a list of SSID names (as strings) in the order they will be organised into
    :param old_order: an ordered dictionary of the SSIDs with the SSID name as the key and the position
                      as the value
    :param current_profiles: a list of mutable/immutable network profiles that will be reordered"""
    reordered = list()
    tracking = list()

    # Process all SSIDs in the 'new_order' param first
    for ssid in new_order:
        old_index = old_order[ssid]
        profile = current_profiles[old_index]
        reordered.append(profile)
        tracking.append(ssid)

    # Now process any SSIDs from the current profiles that was not included in
    # the 'new_order' param so existing SSIDs are not arbitrarily removed.
    for profile in current_profiles:
        ssid = o2p(profile.ssid())

        if ssid not in tracking:
            reordered.append(profile)
            tracking.append(ssid)

    return reordered


def major_os_version() -> int:
    """Return the major OS version."""
    return int(mac_ver()[0].split(".")[0])


def mac_corewlan_framework_warning() -> None:
    """Print a message about macOS 13+ and CoreWLAN, aka throw shade at Apple."""
    print("Note: macOS 13+ appears to no longer allow SSIDs to be manually re-ordered even when the\n"
          "      CoreWLAN configuration change returns a success value.\n"
          "      Please file feedback with Apple to ask for this feature to be added back to macOS and.\n"
          "      raise it with your Apple SE. If you're a member of the Mac Admins Slack, please raise\n"
          "      the feedback then provide the feedback number to the right people in the right channel.\n"
          "       - https://feedbackassistant.apple.com/")


def get_current_connection_properties(iface: CWInterface) -> Optional[Dict[Any, Any]]:
    """Get all the property values from a 'CWInterface' object and return a dictionary object.

    :param iface: a 'CWInterface' object to parse property values from"""
    ip_monitor = iface.ipMonitor()
    data = {"aggregate_noise": iface.aggregateNoise(),
            "aggregate_rssi": iface.aggregateRSSI(),
            "airplay_statistics": iface.airplayStatistics(),
            "auto_content_accessing_proxy": iface.autoContentAccessingProxy(),
            "auto_join_history": iface.autoJoinHistory(),
            "awdl_operating_mode": iface.awdlOperatingMode(),
            "available_wlan_channels": list(iface.availableWLANChannels()),
            "bssid": iface.bssid(),  # Note, this won't return anything in 10.15+ because location data
            "busy": iface.busy(),
            "cached_scan_results": list(iface.cachedScanResults()),  # Last network scan results
            "capabilities": o2p(iface.capabilities()),
            "caused_last_wake": iface.causedLastWake(),
            "channel": iface.channel(),
            "channel_band": iface.channel(),
            "configuration": iface.configuration(),
            "country_code": iface.countryCode(),
            "device": iface.device(),
            "device_attached": iface.deviceAttached(),
            "eapo_client": iface.eapolClient(),
            "entity_name": iface.entityName(),
            "hardware_address": iface.hardwareAddress(),
            "interface_capabilities": iface.interfaceCapabilities(),
            "interface_mode": iface.interfaceMode(),
            "interface_state": iface.interfaceState(),
            "io_80211_controller_info": o2p(iface.IO80211ControllerInfo()),
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
            "is_airplay_in_progress": iface.isAirPlayInProgress(),
            "join_history": iface.joinHistory(),
            "last_network_joined": iface.lastNetworkJoined(),
            "last_power_state": iface.lastPowerState(),
            "last_preferred_network_joined": iface.lastPreferredNetworkJoined(),
            "last_tether_device_joined": iface.lastTetherDeviceJoined(),
            "max_nss_supported_for_ap": iface.maxNSSSupportedForAP(),
            "maximum_link_speed": iface.maximumLinkSpeed(),
            "monitor_mode": iface.monitorMode(),
            "name": iface.name(),
            "network_interface_available": iface.networkInterfaceAvailable(),
            "network_service_ids": o2p(iface.networkServiceIDs()),
            "noise": iface.noise(),
            "noise_measurement": iface.noiseMeasurement(),
            "num_tx_streams": iface.numTXStreams(),
            "number_of_spatial_streams": iface.numberOfSpatialStreams(),
            "observation_info": iface.observationInfo(),
            "op_mode": iface.opMode(),
            "parent_interface_name": iface.parentInterfaceName(),
            "physical_mode": iface.phyMode(),
            "physical_layer_mode": iface.physicalLayerMode(),
            "power": iface.power(),
            "power_debug_info": o2p(iface.powerDebugInfo()),
            "power_save_mode_enabled": iface.powerSaveModeEnabled(),
            "roam_history": iface.roamHistory(),
            "rssi": iface.rssi(),
            "rssi_value": iface.rssiValue(),
            "security": iface.security(),
            "security_mode": iface.securityMode(),
            "security_type": iface.securityType(),
            "service_active": iface.serviceActive(),
            "ssid_name": iface.ssid(),
            "state_info": iface.stateInfo(),
            "supported_ism_channels": list(iface.supportedISMChannels()),
            "supported_physical_layer_modes": iface.supportedPhysicalLayerModes(),
            "supported_wlan_channels": list(iface.supportedWLANChannels()),
            "supported_bsxpc_secure_coding": iface.supportsBSXPCSecureCoding(),
            "supported_rbsxpc_secure_coding": iface.supportsRBSXPCSecureCoding(),
            "supports_short_gi_40mhz": iface.supportsShortGI40MHz(),
            "transmit_power": iface.transmitPower(),
            "transmit_rate": iface.transmitRate(),
            "tx_rate": iface.txRate(),
            "virtual_interface_role": iface.virtualInterfaceRole(),
            "wake_on_wireless_enabled": iface.wakeOnWirelessEnabled(),
            "wlan_channel": iface.wlanChannel(),
            "zone": iface.zone()}

    return data
