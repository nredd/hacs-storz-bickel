"""Storz & Bickel Bluetooth Low Energy API.

This package contains the BLE transport, per-device protocol adapters, data
models, and discovery helpers used by the integration. Entities and the
coordinator interact with a :class:`SBDevice` instance; they never touch
``bleak`` directly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.storz_bickel.api.devices import CraftyDevice, SBDevice, VeazyDevice, VentyDevice, VolcanoDevice
from custom_components.storz_bickel.api.discovery import detect_device_type
from custom_components.storz_bickel.api.exceptions import (
    StorzBickelCharacteristicError,
    StorzBickelConnectionError,
    StorzBickelError,
    StorzBickelNotConnectedError,
)
from custom_components.storz_bickel.api.models import DeviceCapabilities, DeviceType, SBDeviceState

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice

_DEVICE_CLASSES: dict[DeviceType, type[SBDevice]] = {
    DeviceType.VOLCANO: VolcanoDevice,
    DeviceType.VENTY: VentyDevice,
    DeviceType.VEAZY: VeazyDevice,
    DeviceType.CRAFTY: CraftyDevice,
}


def create_device(device_type: DeviceType, ble_device: BLEDevice) -> SBDevice:
    """Instantiate the protocol adapter for a device family.

    Args:
        device_type: The detected Storz & Bickel device family.
        ble_device: The connectable ``BLEDevice`` handle.

    Returns:
        A concrete :class:`SBDevice` for the given family.
    """
    return _DEVICE_CLASSES[device_type](ble_device)


def capabilities_for(device_type: DeviceType) -> DeviceCapabilities:
    """Return the capability flags for a device family without instantiating it."""
    return _DEVICE_CLASSES[device_type].capabilities


__all__ = [
    "CraftyDevice",
    "DeviceCapabilities",
    "DeviceType",
    "SBDevice",
    "SBDeviceState",
    "StorzBickelCharacteristicError",
    "StorzBickelConnectionError",
    "StorzBickelError",
    "StorzBickelNotConnectedError",
    "VeazyDevice",
    "VentyDevice",
    "VolcanoDevice",
    "capabilities_for",
    "create_device",
    "detect_device_type",
]
