"""Number platform for Storz & Bickel settings (brightness, auto-shutoff, boost)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature, UnitOfTime

from custom_components.storz_bickel.config_flow_handler.options_flow import (
    MAX_PUMP_COOLDOWN_SECONDS,
    MAX_PUMP_FAILSAFE_SECONDS,
)
from custom_components.storz_bickel.const import (
    CONF_PUMP_COOLDOWN_SECONDS,
    CONF_PUMP_FAILSAFE_SECONDS,
    CONF_TEMP_STEP,
    DEFAULT_PUMP_COOLDOWN_SECONDS,
    DEFAULT_PUMP_FAILSAFE_SECONDS,
    DEFAULT_TEMP_STEP,
    PARALLEL_UPDATES as _PARALLEL_UPDATES,
)
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.api import SBDevice, SBDeviceState
    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )
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


@dataclass(frozen=True, kw_only=True)
class StorzBickelOptionNumberEntityDescription(NumberEntityDescription):
    """Describes a number entity backed by a config entry option.

    Unlike :class:`StorzBickelNumberEntityDescription`, this never talks to the
    device: the value configures integration-side behavior (pump protections,
    the climate entity's temperature step) read once at coordinator
    construction (see ``coordinator/base.py``). Writing a new value updates
    ``config_entry.options``, which triggers the entry's existing update
    listener to reload the entry (the same path the options flow itself
    uses), rather than issuing a BLE write.
    """

    conf_key: str
    default: float
    capability: str | None = None


OPTION_NUMBERS: tuple[StorzBickelOptionNumberEntityDescription, ...] = (
    StorzBickelOptionNumberEntityDescription(
        key="pump_failsafe_seconds",
        translation_key="pump_failsafe_seconds",
        capability="pump",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=MAX_PUMP_FAILSAFE_SECONDS,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-alert-outline",
        conf_key=CONF_PUMP_FAILSAFE_SECONDS,
        default=DEFAULT_PUMP_FAILSAFE_SECONDS,
    ),
    StorzBickelOptionNumberEntityDescription(
        key="pump_cooldown_seconds",
        translation_key="pump_cooldown_seconds",
        capability="pump",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=MAX_PUMP_COOLDOWN_SECONDS,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-sand",
        conf_key=CONF_PUMP_COOLDOWN_SECONDS,
        default=DEFAULT_PUMP_COOLDOWN_SECONDS,
    ),
    StorzBickelOptionNumberEntityDescription(
        key="temp_step",
        translation_key="temp_step",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0.5,
        native_max_value=5,
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-lines",
        conf_key=CONF_TEMP_STEP,
        default=DEFAULT_TEMP_STEP,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    async_add_entities(
        [
            StorzBickelNumber(coordinator, description)
            for description in NUMBERS
            if getattr(capabilities, description.capability)
        ]
        + [
            StorzBickelOptionNumber(coordinator, description)
            for description in OPTION_NUMBERS
            if description.capability is None
            or getattr(capabilities, description.capability)
        ]
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


class StorzBickelOptionNumber(StorzBickelEntity, NumberEntity):
    """A capability-gated setting backed by a config entry option."""

    entity_description: StorzBickelOptionNumberEntityDescription

    def __init__(
        self,
        coordinator: StorzBickelDataUpdateCoordinator,
        entity_description: StorzBickelOptionNumberEntityDescription,
    ) -> None:
        """Initialize with the coordinator's config entry."""
        super().__init__(coordinator, entity_description)
        self._entry = coordinator.config_entry

    @property
    def available(self) -> bool:
        """Option-backed settings don't depend on a live BLE connection."""
        return True

    @property
    def native_value(self) -> float:
        """Return the current option value, falling back to the default."""
        return self._entry.options.get(
            self.entity_description.conf_key, self.entity_description.default
        )

    async def async_set_native_value(self, value: float) -> None:
        """Persist the new option value; the entry reloads to pick it up."""
        self.hass.config_entries.async_update_entry(
            self._entry,
            options={**self._entry.options, self.entity_description.conf_key: value},
        )
