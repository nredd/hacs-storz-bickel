"""Binary sensor platform for Storz & Bickel state (heater, pump, connectivity)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from custom_components.storz_bickel.const import PARALLEL_UPDATES as _PARALLEL_UPDATES
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.api import SBDeviceState
    from custom_components.storz_bickel.coordinator import StorzBickelDataUpdateCoordinator
    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PARALLEL_UPDATES = _PARALLEL_UPDATES


@dataclass(frozen=True, kw_only=True)
class StorzBickelBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Storz & Bickel binary sensor entity."""

    is_on_fn: Callable[[SBDeviceState], bool | None]
    capability: str | None = None


BINARY_SENSORS: tuple[StorzBickelBinarySensorEntityDescription, ...] = (
    StorzBickelBinarySensorEntityDescription(
        key="heater",
        translation_key="heater",
        device_class=BinarySensorDeviceClass.HEAT,
        is_on_fn=lambda state: state.heater_on,
    ),
    StorzBickelBinarySensorEntityDescription(
        key="pump",
        translation_key="pump",
        capability="pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        is_on_fn=lambda state: state.pump_on,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 - required platform signature
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    entities: list[BinarySensorEntity] = [
        StorzBickelBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
        if description.capability is None or getattr(capabilities, description.capability)
    ]
    entities.append(StorzBickelConnectivitySensor(coordinator))
    async_add_entities(entities)


class StorzBickelBinarySensor(StorzBickelEntity, BinarySensorEntity):
    """A capability-gated binary state sensor."""

    entity_description: StorzBickelBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the current binary state."""
        return self.entity_description.is_on_fn(self.data)


class StorzBickelConnectivitySensor(StorzBickelEntity, BinarySensorEntity):
    """Reports whether Home Assistant currently holds the BLE connection."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: StorzBickelDataUpdateCoordinator) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, BinarySensorEntityDescription(key="connection", translation_key="connection"))

    @property
    def available(self) -> bool:
        """The connectivity sensor stays available even while disconnected."""
        return True

    @property
    def is_on(self) -> bool:
        """Return whether the BLE connection is currently established."""
        return self.coordinator.device.connected
