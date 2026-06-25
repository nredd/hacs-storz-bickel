"""Sensor platform for Storz & Bickel telemetry and device metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature, UnitOfTime

from custom_components.storz_bickel.const import PARALLEL_UPDATES as _PARALLEL_UPDATES
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.api import SBDeviceState
    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PARALLEL_UPDATES = _PARALLEL_UPDATES

_UNIT_HOURS = UnitOfTime.HOURS
_DIAGNOSTIC = EntityCategory.DIAGNOSTIC


@dataclass(frozen=True, kw_only=True)
class StorzBickelSensorEntityDescription(SensorEntityDescription):
    """Describes a Storz & Bickel sensor entity."""

    value_fn: Callable[[SBDeviceState], float | int | str | None]
    capability: str | None = None


SENSORS: tuple[StorzBickelSensorEntityDescription, ...] = (
    StorzBickelSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda state: state.current_temperature,
    ),
    StorzBickelSensorEntityDescription(
        key="battery",
        translation_key="battery",
        capability="battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda state: state.battery_level,
    ),
    StorzBickelSensorEntityDescription(
        key="total_runtime",
        translation_key="total_runtime",
        capability="hours_of_operation",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=_UNIT_HOURS,
        suggested_display_precision=1,
        icon="mdi:timer-sand",
        value_fn=lambda state: state.total_runtime_hours,
    ),
    StorzBickelSensorEntityDescription(
        key="hours_of_operation",
        translation_key="hours_of_operation",
        capability="hours_of_operation",
        entity_category=_DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=_UNIT_HOURS,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.hours_of_operation,
    ),
    StorzBickelSensorEntityDescription(
        key="minutes_of_operation",
        translation_key="minutes_of_operation",
        capability="hours_of_operation",
        entity_category=_DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.minutes_of_operation,
    ),
    StorzBickelSensorEntityDescription(
        key="heater_runtime",
        translation_key="heater_runtime",
        capability="heater_runtime",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-sand",
        value_fn=lambda state: state.heater_runtime_minutes,
    ),
    StorzBickelSensorEntityDescription(
        key="battery_charge_time",
        translation_key="battery_charge_time",
        capability="heater_runtime",
        entity_category=_DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.battery_charge_time_minutes,
    ),
    StorzBickelSensorEntityDescription(
        key="serial_number",
        translation_key="serial_number",
        entity_category=_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.serial_number,
    ),
    StorzBickelSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        entity_category=_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.firmware_version,
    ),
    StorzBickelSensorEntityDescription(
        key="ble_firmware_version",
        translation_key="ble_firmware_version",
        entity_category=_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda state: state.ble_firmware_version,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor entities supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    async_add_entities(
        StorzBickelSensor(coordinator, description)
        for description in SENSORS
        if description.capability is None or getattr(capabilities, description.capability)
    )


class StorzBickelSensor(StorzBickelEntity, SensorEntity):
    """A capability-gated telemetry or metadata sensor."""

    entity_description: StorzBickelSensorEntityDescription

    @property
    def native_value(self) -> float | int | str | None:
        """Return the current sensor value."""
        return self.entity_description.value_fn(self.data)
