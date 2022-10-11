import sys

from collections import OrderedDict
from os import geteuid
from time import sleep
from typing import Any, Dict, List, Optional

from CoreWLAN import (CWConfiguration,
                      CWInterface,
                      CWMutableConfiguration,
                      CWNetwork,
                      CWWiFiClient)
from Foundation import NSOrderedSet

from .models.interface import InterfaceConnection
from .models.interface import NETWORK_SETUP_MAP_SECURITY_TYPES as NS_MST
from .utils import get_current_connection_properties
from .utils import major_os_version
from .utils import o2p
from .utils import add_ssid_at_index
from .utils import remove_ssid
from .utils import reorder_ssids


ListNetworkConfigurationTypes = List[CWConfiguration | CWMutableConfiguration]


class WiFiAdapterException(Exception):
    """WiFiAdapter Exception"""
    pass


class WiFiAdapter:
    def __init__(self,
                 iface: Optional[str] = None,
                 dry_run: Optional[bool] = False) -> None:
        self._client = CWWiFiClient.sharedWiFiClient()
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

    def _has_configured_ssids(self) -> bool:
        return len(self.current_ssid_order) > 0

    def _interface_with_name(self) -> Optional[CWInterface]:
        """Return the interface as a 'CWInterface' object."""
        return self._client.interfaceWithName_(self._iface)

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
    def network_profiles(self) -> Optional[ListNetworkConfigurationTypes]:
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
        """Get current connection details and returns a dataclass of values."""
        data = get_current_connection_properties(iface=self._interface)
        return InterfaceConnection(**data)

    def print_current_ssid_order(self, header: str = "Current SSID order:") -> None:
        """Print the current SSID order.

        :param header: the header message string to print"""
        if self._has_configured_ssids():
            print(header)

            for ssid, posn in self.current_ssid_order.items():
                print(f" {posn}: {ssid!r}")
        else:
            print(f"No SSIDs found configured for {self._iface!r}", file=sys.stderr)

    def print_updated_ssid_order(self,
                                 reordered_ssids: List[ListNetworkConfigurationTypes],
                                 header: str = "Updated SSID order:") -> None:
        """Print the updated SSID order.

        :param reordered_ssids: a list of mutable/immutable network profiles that has been reordered
        :param header: the header message string to print"""
        print(header)

        for profile in reordered_ssids:
            ssid = o2p(profile.ssid())
            print(f" {reordered_ssids.index(profile)}: {ssid!r}")

    def reorder(self, new_order: List[str] | Dict[str, int], use_networksetup: Optional[bool] = False) -> Any:
        """Reorder the current SSID preferred join order.

        :param new_order: a list of SSID names (string) in order that the current SSIDs will be reordered to, or a
                          dictionary object where the SSID (string) is the key, and the order/position
                          (int) is the value, if a dictionary is provided, the first SSID must have a position
                          value of 0
        :param use_networksetup: forcibly use 'networksetup' instead of CoreWLAN"""
        # Check there are SSIDs to configure
        if not self._has_configured_ssids():
            print(f"No SSIDs found configured for {self._iface!r}", file=sys.stderr)
            sys.exit()

        # Convert a dictionary of SSID orders into a list
        if isinstance(new_order, dict):
            new_order = [ssid for ssid, _ in sorted(new_order.items(), key=lambda x: x[1])]

        # Check all SSIDs in the new order can be iterated on
        check_list = [ssid for ssid, _ in self.current_ssid_order.items()]

        if not all([ssid in check_list for ssid in new_order]):
            missing = ", ".join([f"{ssid!r}" for ssid in new_order if ssid not in check_list])

            msg = f"Error: Cannot re-order the SSIDs as one or more SSID is not configured on {self._iface!r}"
            print(msg, file=sys.stderr)
            print(f"SSIDs not configured on {self._iface}: {missing}", file=sys.stderr)
            self.print_current_ssid_order()
            sys.exit(2)

        # Reorder the SSIDs into a new order
        reordered_ssids = reorder_ssids(new_order=new_order,
                                        old_order=self.current_ssid_order,
                                        current_profiles=self.network_profiles)

        if self._dry_run:
            self.print_current_ssid_order(header="Old SSID order:")
            self.print_updated_ssid_order(reordered_ssids=reordered_ssids, header="New SSID order:")
            sys.exit()

        # macOS Ventura 13.0 and newer appear unable to use the CoreWLAN framework to reorder SSIDs,
        # so use the CoreWLAN framework for macOS versions prior to macOS Ventura
        if not self._dry_run and major_os_version() <= 12 and not use_networksetup:
            nso = NSOrderedSet.orderedSetWithArray_

            current_config = self.mutable_configuration
            current_config.setNetworkProfiles_(nso(reordered_ssids))
            success, result_msg = self._commit_change(config=current_config)

            if not success:
                domain, code = result_msg.domain(), result_msg.code()
                print(f"Error applying change: {domain!r}, code: {code!r}")

                if result_msg.code() == -3930 and not geteuid() == 0:
                    print("You may need to run this with 'sudo' to apply this configuration change.", file=sys.stderr)
                sys.exit(1)
            else:
                print("Successfully applied configuration change.")
        elif not self._dry_run and major_os_version() >= 13 or use_networksetup:  # Use 'networksetup' for macOS 13+
            print("Falling back to 'networksetup'")
            adding_ssids = [o2p(profile.ssid()) for profile in reordered_ssids]
            security_types_map = {o2p(profile.ssid()): NS_MST[profile.security()] for profile in reordered_ssids}
            removed = remove_ssid(iface=self._iface, remove_all=True)
            added_ssids = list()

            if removed.returncode == 0:
                for profile in reordered_ssids:
                    index = reordered_ssids.index(profile)
                    ssid = o2p(profile.ssid())
                    security_type = security_types_map[ssid]
                    added = add_ssid_at_index(iface=self._iface,
                                              ssid=ssid,
                                              index=index,
                                              security_type=security_type)

                    if added.returncode == 0:
                        added_ssids.append(ssid)

                if sorted(added_ssids) == sorted(adding_ssids):
                    print("Successfully applied configuration change.")
                else:
                    missing = ", ".join([f"{ssid!r}" for ssid in adding_ssids if ssid not in added_ssids])
                    print(f"Error: The following SSIDs were not re-sorted:\n  {missing}", file=sys.stderr)
                    sys.exit(99)
            else:
                print(f"Error: {removed.stdout or removed.stderr}", file=sys.stderr)
                print("Please check Wi-Fi settings and re-add Wi-Fi networks if necessary.")
                sys.exit(removed.returncode)

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
