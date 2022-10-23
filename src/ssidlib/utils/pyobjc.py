from typing import Any, Callable, Optional

from PyObjCTools import Conversion


def o2p(obj: Any, helper: Optional[Callable] = None) -> Any:
    """Converts an NSArray/NSDictionary to 'native' Python data types.
    Note: Not all ObjC types can be converted to native Python data types by this method.

    PyObjC Documentation: https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.Conversion.html


    :param obj: NS* object to convert
    :param helper: conversion helper function to pass to the conversion call if the PyObjC conversion fails"""
    return Conversion.pythonCollectionFromPropertyList(obj, conversionHelper=helper)
