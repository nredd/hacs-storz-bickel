"""Switch platform for Storz & Bickel on/off controls (pump, vibration, auto-shutoff)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory

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
class StorzBickelSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Storz & Bickel switch entity."""

    capability: str
    is_on_fn: Callable[[SBDeviceState], bool | None]
    set_fn: Callable[[SBDevice, bool], Coroutine[Any, Any, None]]


SWITCHES: tuple[StorzBickelSwitchEntityDescription, ...] = (
    StorzBickelSwitchEntityDescription(
        key="heater",
        translation_key="heater",
        capability="heater",
        icon="mdi:fire",
        is_on_fn=lambda state: state.heater_on,
        set_fn=lambda device, on: device.async_set_heater(on=on),
    ),
    StorzBickelSwitchEntityDescription(
        key="pump",
        translation_key="pump",
        capability="pump",
        icon="mdi:fan",
        is_on_fn=lambda state: state.pump_on,
        set_fn=lambda device, on: device.async_set_pump(on=on),
    ),
    StorzBickelSwitchEntityDescription(
        key="vibration",
        translation_key="vibration",
        capability="vibration",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:vibrate",
        is_on_fn=lambda state: state.vibration,
        set_fn=lambda device, on: device.async_set_vibration(on=on),
    ),
    StorzBickelSwitchEntityDescription(
        key="auto_shutoff_enabled",
        translation_key="auto_shutoff_enabled",
        capability="auto_shutoff_toggle",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:timer-off-outline",
        is_on_fn=lambda state: state.auto_shutoff_enabled,
        set_fn=lambda device, on: device.async_set_auto_shutoff(on=on),
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch entities supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    async_add_entities(
        StorzBickelSwitch(coordinator, description)
        for description in SWITCHES
        if getattr(capabilities, description.capability)
    )


class StorzBickelSwitch(StorzBickelEntity, SwitchEntity):
    """A capability-gated on/off control."""

    entity_description: StorzBickelSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return whether the control is currently on."""
        return self.entity_description.is_on_fn(self.data)

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the control on."""
        await self.entity_description.set_fn(self.device, True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the control off."""
        await self.entity_description.set_fn(self.device, False)
