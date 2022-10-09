import subprocess
import sys

from collections import OrderedDict
from os import geteuid
from platform import mac_ver
from time import sleep
from typing import Any, Dict, List, Optional

from CoreWLAN import (CWConfiguration,
                      CWInterface,
                      CWMutableConfiguration,
                      CWNetwork,
                      CWWiFiClient)
from Foundation import NSOrderedSet

from .models.interface import InterfaceConnection
from .utils import o2p


class WiFiAdapterException(Exception):
    """WiFiAdapter Exception"""
    pass


class WiFiAdapter:
    def __init__(self,
                 client: CWWiFiClient = CWWiFiClient.sharedWiFiClient(),
                 iface: Optional[str] = None,
                 dry_run: Optional[bool] = False) -> None:
        self._client = client
        self._iface = iface or self.interface
        self._dry_run = dry_run

    def _commit_change(self, config: CWConfiguration | CWMutableConfiguration) -> None:
        """Commits changes made to the configuration of a wireless interface.
        Note: It seems that post macOS Big Sur (11.0), committing changes to the configuration now
              requires elevating priviliges with 'sudo', not running this with 'sudo' will generate
              an error like the one below:
                'Error Domain=com.apple.wifi.apple80211API.error Code=-3930 "(null)"'
              This error correlates to 'kCWOperationNotPermittedErr' and seems to be a result of Apple
              enforcing higher level access requirements on network related changes that are _not_ made
              via System Preferences/System Settings.

        A tuple is returned, the tuple value at index 0 is the success/error result, 'True' indicates a
        successful commit, while 'False' indicates an error, and the tuple value at index 1 is the error
        message.

        :param config: configuration object"""
        commit = self._interface_with_name().commitConfiguration_authorization_error_

        return commit(config, None, None)

    def _get_configuration(self,
                           mutable: Optional[bool] = False) -> Optional[CWConfiguration | CWMutableConfiguration]:
        """Gets the current configuration for a wireless interface.

        :param iface: interface name (string), for example 'en0'
        :param mutable: boolean value to return a mutable version of the configuration that will
                        allow modifications to the configuration if the param is True; default is False"""
        conf = CWConfiguration if not mutable else CWMutableConfiguration
        iface = self._client.interfaceWithName_(self._iface)

        return conf.alloc().initWithConfiguration_(iface.configuration())

    def _interface_with_name(self) -> Optional[CWInterface]:
        """Return the interface as a 'CWInterface' object."""
        return self._client.interfaceWithName_(self._iface)

    def _major_os_version(self) -> int:
        """Return the major OS version."""
        return int(mac_ver()[0].split(".")[0])

    @property
    def _interface(self) -> Optional[CWInterface]:
        """Return the current interface as an 'CWInterface' object.

        Note: Used internally."""
        return self._client.interface()

    @property
    def interface(self) -> str:
        """Return the default wireless interface name.

        Note: this is NOT the interface as a 'CWInterface' object."""
        return o2p(self._client.interface().interfaceName())

    @property
    def interfaces(self) -> str:
        """Return a list of available and valid wireless interface names."""
        return [o2p(iface.interfaceName()) for iface in self._client.interfaces()]

    @property
    def configuration(self) -> Optional[CWConfiguration]:
        """Return an immutable configuration for the wireless interface."""
        return self._get_configuration()

    @property
    def mutable_configuration(self) -> Optional[CWMutableConfiguration]:
        """Return a mutable configuration for the wireless interface."""
        return self._get_configuration(mutable=True)

    @property
    def network_profiles(self) -> Optional[List[CWConfiguration | CWMutableConfiguration]]:
        """Gets the current configuration for a wireless interface. The items in the
        result are in the order in which macOS will prefer to join to."""
        return list(self._get_configuration().networkProfiles().array())

    @property
    def current_ssid_order(self) -> Optional[OrderedDict]:
        """Returns an ordered dictionary of the current SSID preferred join position.

        Note: the value of the '.ssid()' method returns an 'objc.unicode' encoded value,
              so this is converted to a 'utf-8' encoded value to avoid mixed text encoding
              causing errors with value comparison as 'utf-8' does not necessarily equal
              'objc.unicode'"""
        result = OrderedDict()

        for profile in self.network_profiles:
            result[o2p(profile.ssid())] = self.network_profiles.index(profile)

        return result

    def associate(self, ssid: str, password: Optional[str] = None) -> Optional[bool]:
        """Associate to an SSID.

        Note: This has not been tested for associating with 802.1x networks, or other enterprise network types.
              A network scan for networks matching the specified SSID is done as the associate method requires
              a 'CWNetwork' object passed in as the first parameter.
              If the network is already associated, nothing happens.

        :param ssid: SSID to associate to
        :param password: optional password (string) to use when associating, if the SSID has previously been
                         associated with and credentials are stored, then this will automatically reconnect"""
        network = self.scan_for_networks(ssid=ssid)

        if network:
            success, result_msg = self._interface.associateToNetwork_password_error_(network, password, None)

            if not success:
                domain, code = result_msg.domain(), result_msg.code()
                print(f"Error associating to {ssid!r}: {domain()}, code: {code!r}", file=sys.stderr)

            return success

    def disassociate(self) -> None:
        """Disconnects from the currently connected SSID."""
        self._interface.disassociate()

    def current_connection(self) -> Optional["InterfaceConnection"]:
        """Get current connection details"""
        ip_monitor = self._interface.ipMonitor()
        data = {"aggregate_noise": self._interface.aggregateNoise(),
                "aggregate_rssi": self._interface.aggregateRSSI(),
                "airplay_statistics": self._interface.airplayStatistics(),
                "auto_content_accessing_proxy": self._interface.autoContentAccessingProxy(),
                "auto_join_history": self._interface.autoJoinHistory(),
                "awdl_operating_mode": self._interface.awdlOperatingMode(),
                "available_wlan_channels": list(self._interface.availableWLANChannels()),
                "bssid": self._interface.bssid(),  # Note, this won't return anything in 10.15+ because location data
                "busy": self._interface.busy(),
                "cached_scan_results": list(self._interface.cachedScanResults()),  # Last network scan results
                "capabilities": o2p(self._interface.capabilities()),
                "caused_last_wake": self._interface.causedLastWake(),
                "channel": self._interface.channel(),
                "channel_band": self._interface.channel(),
                "configuration": self._interface.configuration(),
                "country_code": self._interface.countryCode(),
                "device": self._interface.device(),
                "device_attached": self._interface.deviceAttached(),
                "eapo_client": self._interface.eapolClient(),
                "entity_name": self._interface.entityName(),
                "hardware_address": self._interface.hardwareAddress(),
                "interface_capabilities": self._interface.interfaceCapabilities(),
                "interface_mode": self._interface.interfaceMode(),
                "interface_state": self._interface.interfaceState(),
                "io_80211_controller_info": o2p(self._interface.IO80211ControllerInfo()),
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

    def print_current_ssid_order(self, header: str = "Current SSID order:") -> None:
        """Print the current SSID order."""
        print(header)

        for ssid, posn in self.current_ssid_order.items():
            print(f" {posn}: {ssid!r}")

    def reorder(self, order: List[str] | Dict[str, int]) -> Any:
        """Reorder the current SSID preferred join order.

        :param new_order: a list of SSID names (string) in order that the current SSIDs will be reordered to, or a
                          dictionary object where the SSID (string) is the key, and the order/position
                          (int) is the value, if a dictionary is provided, the first SSID must have a position
                          value of 0"""
        added_ssids = list()  # Empty list to track all the SSIDs that have been added to the new config
        reordered_ssids = list()  # Empty list for the new order of items to be inserted into
        current_config = self.mutable_configuration
        current_ssids = self.network_profiles  # Note, this is an immutable configuration
        current_order = self.current_ssid_order
        current_order_as_list = [ssid for ssid, _ in current_order.items()]

        if not all([ssid in current_order_as_list for ssid in order]):
            missing_ssids = [ssid for ssid in order if ssid not in current_order_as_list]
            missing_ssids_str = ", ".join([f"{ssid!r}" for ssid in missing_ssids])
            print("Cannot re-order the specified SSIDs as one or more SSID is not configured.", file=sys.stderr)
            print(f"SSIDs not configured on {self._iface!r}: {missing_ssids_str}.", file=sys.stderr)
            sys.exit(2)

        # Convert a dictionary of SSID orders into a list
        if isinstance(order, dict):
            order = [ssid for ssid, _ in sorted(order.items(), key=lambda x: x[1])]

        # Reorder the profiles
        for ssid in order:
            try:
                index = current_order[ssid]  # The index of the SSID in the "old/current" order
            except (IndexError, KeyError):
                print(f"Warning: {ssid!r} is not configured on {self._iface!r}, skipping this SSID.", file=sys.stderr)
                pass
            else:
                reordered_ssids.append(current_ssids[index])
                added_ssids.append(ssid)  # Track we've added the SSID to the new order

        # Check for any SSIDs that weren't in the new order and re-add them back to the bottom of the
        # new ordering.
        # Note: 'profile.ssid()' returns an objc unicode value, so convert to
        #        normal 'utf-8' encoding to avoid mixed encoding causing errors with
        #        value comparisons
        for profile in current_ssids:
            if o2p(profile.ssid() not in added_ssids):
                reordered_ssids.append(profile)
                added_ssids.append(o2p(profile.ssid()))

        if not self._dry_run:
            nso = NSOrderedSet.orderedSetWithArray_
            current_config.setNetworkProfiles_(nso(reordered_ssids))
            success, result_msg = self._commit_change(config=current_config)

            if not success:
                domain, code = result_msg.domain(), result_msg.code()
                print(f"Error applying change: {domain!r}, code: {code!r}")

                if result_msg.code() == -3930 and not geteuid() == 0:
                    print("You may need to run this with 'sudo' to apply this configuration change.", file=sys.stderr)
            else:
                print("Successfully applied configuration change.")

                if self._major_os_version() >= 13:
                    print("Note: macOS 13+ appears to no longer allow SSIDs to be manually re-ordered even when the\n"
                          "      CoreWLAN configuration change returns a success value.\n"
                          "      Please file feedback with Apple to ask for this feature to be added back to macOS and.\n"
                          "      raise it with your Apple SE. If you're a member of the Mac Admins Slack, please raise\n"
                          "      the feedback then provide the feedback number to the right people in the right channel.\n"
                          "       - https://feedbackassistant.apple.com/")

            return success
        elif self._dry_run:
            self.print_current_ssid_order(header="Old SSID order:")

            print("New SSID order:")

            for ssid in added_ssids:
                print(f" {added_ssids.index(ssid)}: {ssid!r}")

    def networksetup(self, args: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run the '/usr/sbin/networksetup' command with arguments.

        Note: this will exit if you do not run this command with 'sudo' or as root user.

        :param args: list (strings) of arguments to pass to '/usr/sbin/networksetup'
        :param **kwargs: args dict to pass to 'subprocess'"""
        cmd = ["/usr/sbin/networksetup"]
        cmd.extend([str(arg) for arg in args])

        if self._major_os_version() > 12:
            print(f"You must be root to run {' '.join(cmd)!r}", file=sys.stderr)
            sys.exit(1)

        return subprocess.run(cmd, **kwargs)

    def power_cycle(self, wait: str | int = 5) -> None:
        """Power cycles the wireless network interface off then on.

        :param wait: number of seconds to wait between power off and on"""
        self.set_power_off()
        sleep(int(wait))
        self.set_power_on()

    def scan_for_networks(self,
                          ssid: Optional[str] = None,
                          include_hidden: Optional[bool] = True) -> Optional[CWNetwork | List[CWNetwork]]:
        """Scan for all networks.

        :param ssid: optional SSID name (string) to scan for
        :param include_hidden: optional param (bool) to include hidden networks in results"""
        networks, err = self._interface.scanForNetworksWithName_includeHidden_error_(ssid, include_hidden, None)

        if networks:
            networks = list(networks)

            if ssid:
                for network in networks:
                    if o2p(network.ssid()) == ssid:
                        return network
            else:
                return networks

    def set_power_off(self) -> None:
        """Set the wirless interface power off."""
        self._interface.setPower_error_(False, None)

    def set_power_on(self) -> None:
        """Set the wirless interface power on."""
        self._interface.setPower_error_(True, None)
