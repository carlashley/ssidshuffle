import sys

from os import geteuid
from time import sleep
from typing import Any, Dict, List, Optional, TextIO  # NOQA

from CoreWLAN import (CWConfiguration,
                      CWWiFiClient,
                      CWMutableConfiguration,
                      CWNetworkProfile)
from Foundation import NSOrderedSet

from .models.interface import WirelessInterface
from .utils import networksetup
from .utils.pyobjc import o2p


class WLan:
    """Parent class containing CoreWLAN wrappers and other various methods relating to CoreWLAN.
    Note, this parent class only operates on the current available interface."""
    def __init__(self, iface: Optional[str] = None):
        """Initialise."""
        self._client = CWWiFiClient.sharedWiFiClient()
        self._interface = self._client.interface()  # Raw interface object

    def __repr__(self):
        attrvals = [f"{k}={v!r}" for k, v in self.__dict__.items() if not (k.startswith("_") or k.startswith("__"))]
        return f"{type(self).__name__}({', '.join(attrvals)})"

    # ------------------- Properties via decorated functions ----------------------------------------------------------
    @property
    def interface(self) -> Optional[WirelessInterface]:
        """Return a WirelessInterface object as a property."""
        return WirelessInterface(client=self._client, iface=self._interface)

    @property
    def interfaces(self) -> Optional[List[WirelessInterface]]:
        """Return a list of WirelessInterface objects."""
        return [WirelessInterface(client=self._client, iface=_iface) for _iface in self._client.interfaces()]

    @property
    def valid_interfaces(self) -> Optional[List[str]]:
        """Return a list of valid interface names."""
        return [iface.name for iface in self.interfaces]

    # ------------------- Functions -----------------------------------------------------------------------------------
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
        domain, code = None, None

        if network:
            success, result_msg = self._interface.associateToNetwork_password_error_(network, password, None)

            if not success:
                domain, code = result_msg.domain(), result_msg.code()

            return (success, domain, code)

    def commit(self, new_order: List[CWNetworkProfile], use_networksetup: bool = False) -> None:
        """Commit changes to the ordering of the preferred networks.

        :param new_order: the new order of network profiles to apply"""
        # Check we can reorder all specified SSIDs
        if not use_networksetup:
            nso = NSOrderedSet.orderedSetWithArray_
            commit = self._interface.commitConfiguration_authorization_error_
            config = self.interface.mutable_configuration
            config.setNetworkProfiles_(nso(new_order))
            success, result = commit(config, None, None)

            if not success:
                domain, code = result.domain(), result.code()
                print(f"Error applying change: {domain!r}, code {code!r}", file=sys.stderr)

                if code == -3930 and not geteuid() == 0:
                    print("You may need to run this with 'sudo' to apply this configuration change.", file=sys.stderr)

                sys.exit(1)
            else:
                print("Successfully applied configuration change.")
        else:
            ssids_added = list()
            security_map = self.interface.networksetup_security_types_map
            removed = networksetup.remove_ssids(iface=self.interface.name)

            if removed.returncode == 0:
                for profile in new_order:
                    ssid = o2p(profile.ssid())
                    st = security_map.get(ssid)
                    index = new_order.index(profile)

                    if not st == "Unknown":
                        added = networksetup.add_ssids(iface=self.interface.name,
                                                       ssid=ssid,
                                                       index=index,
                                                       security_type=st)

                        if added.returncode == 0:
                            ssids_added.append(ssid)

                            if all([o2p(profile.ssid()) in ssids_added for profile in new_order]):
                                print("Successfully applied configuration change.")

    def current_ssid_order(self, output: Optional[TextIO] = sys.stdout) -> None:
        """Display the current SSID order."""
        for profile in self.interface.network_profiles:
            index = self.interface.network_profiles.index(profile)
            print(f" {index}: {profile.ssid()!r}", file=output)

    def power_cycle(self, wait: str | int = 5) -> None:
        """Power cycles the wireless network interface off then on.

        :param wait: number of seconds to wait between power off and on"""
        self.set_power_off()
        sleep(int(wait))
        self.set_power_on()

    def reorder(self, new_order: List[str]) -> List[CWConfiguration | CWMutableConfiguration]:
        """Reorder the current list of network profiles.

        :param new_order: a list of SSID names (as strings) in the order they will be organised into"""
        old_order = [o2p(profile.ssid()) for profile in self.interface.network_profiles]

        if not all([ssid in old_order for ssid in new_order]):
            missing = ", ".join([f"{ssid!r}" for ssid in new_order if ssid not in old_order])
            msg = f"Error: Cannot re-order the SSIDs as one or more SSID is not configured on {self.interface.name!r}"
            print(msg, file=sys.stderr)
            print(f"SSIDs not configured on {self.interface.name!r}: {missing}", file=sys.stderr)
            print("Current SSID order:", file=sys.stderr)
            self.current_ssid_order(output=sys.stderr)
            sys.exit(2)

        reordered = list()
        tracking = list()

        # Process all SSIDs in the 'new_order' param first
        for ssid in new_order:
            old_index = old_order.index(ssid)
            profile = self.interface.network_profiles[old_index]
            reordered.append(profile)
            tracking.append(ssid)

        # Now process any SSIDs from the current profiles that was not included in
        # the 'new_order' param so existing SSIDs are not arbitrarily removed.
        for profile in self.interface.network_profiles:
            ssid = o2p(profile.ssid())

            if ssid not in tracking:
                reordered.append(profile)
                tracking.append(ssid)

        return reordered

    def set_power_off(self) -> None:
        """Set the wirless interface power off."""
        self._interface.setPower_error_(False, None)

    def set_power_on(self) -> None:
        """Set the wirless interface power on."""
        self._interface.setPower_error_(True, None)
