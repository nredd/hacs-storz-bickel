"""Base entity for the Storz & Bickel integration.

All platform entities inherit from :class:`StorzBickelEntity`, which wires up the
coordinator, device info (keyed on the BLE address), unique IDs, and availability
that follows the live BLE connection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.storz_bickel.const import ATTRIBUTION, DOMAIN, MANUFACTURER
from custom_components.storz_bickel.coordinator import StorzBickelDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription

    from custom_components.storz_bickel.api import SBDevice, SBDeviceState


class StorzBickelEntity(CoordinatorEntity[StorzBickelDataUpdateCoordinator]):
    """Base class for all Storz & Bickel entities."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StorzBickelDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity with its coordinator and description."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        device = coordinator.device
        self._attr_unique_id = f"{device.address}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, device.address)},
            identifiers={(DOMAIN, device.address)},
            manufacturer=MANUFACTURER,
            model=device.device_type.model_name,
            name=device.name,
            serial_number=device.state.serial_number,
            sw_version=device.state.firmware_version,
        )

    @property
    def device(self) -> SBDevice:
        """Return the device adapter for this entity."""
        return self.coordinator.device

    @property
    def data(self) -> SBDeviceState:
        """Return the latest device state snapshot."""
        return self.coordinator.data

    @property
    def available(self) -> bool:
        """Return availability, requiring a live BLE connection."""
        return super().available and self.coordinator.device.connected
