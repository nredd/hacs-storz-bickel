"""Number platform for Storz & Bickel settings (brightness, auto-shutoff, boost)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature, UnitOfTime

from custom_components.storz_bickel.const import PARALLEL_UPDATES as _PARALLEL_UPDATES
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.api import SBDevice, SBDeviceState
    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PARALLEL_UPDATES = _PARALLEL_UPDATES


@dataclass(frozen=True, kw_only=True)
class StorzBickelNumberEntityDescription(NumberEntityDescription):
    """Describes a Storz & Bickel number entity."""

    capability: str
    value_fn: Callable[[SBDeviceState], float | None]
    set_fn: Callable[[SBDevice, float], Coroutine[Any, Any, None]]


NUMBERS: tuple[StorzBickelNumberEntityDescription, ...] = (
    StorzBickelNumberEntityDescription(
        key="led_brightness",
        translation_key="led_brightness",
        capability="led_brightness",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:brightness-6",
        value_fn=lambda state: state.led_brightness,
        set_fn=lambda device, value: device.async_set_led_brightness(int(value)),
    ),
    StorzBickelNumberEntityDescription(
        key="auto_shutoff_minutes",
        translation_key="auto_shutoff_minutes",
        capability="auto_shutoff",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=720,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
        value_fn=lambda state: state.auto_shutoff_minutes,
        set_fn=lambda device, value: device.async_set_auto_shutoff_minutes(int(value)),
    ),
    StorzBickelNumberEntityDescription(
        key="boost_temperature",
        translation_key="boost_temperature",
        capability="boost_temperature",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-plus",
        value_fn=lambda state: state.boost_temperature,
        set_fn=lambda device, value: device.async_set_boost_temperature(value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 - required platform signature
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    async_add_entities(
        StorzBickelNumber(coordinator, description)
        for description in NUMBERS
        if getattr(capabilities, description.capability)
    )


class StorzBickelNumber(StorzBickelEntity, NumberEntity):
    """A capability-gated numeric setting."""

    entity_description: StorzBickelNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value of the setting."""
        return self.entity_description.value_fn(self.data)

    async def async_set_native_value(self, value: float) -> None:
        """Write a new value to the device."""
        await self.entity_description.set_fn(self.device, value)
