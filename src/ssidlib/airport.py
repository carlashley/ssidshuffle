from typing import Any, Callable, List, Optional

from CoreWLAN import CWConfiguration
from CoreWLAN import CWInterface
from CoreWLAN import CWMutableConfiguration
from CoreWLAN import CWWiFiClient
from PyObjCTools import Conversion


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
