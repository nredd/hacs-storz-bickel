"""End-to-end setup tests for the Storz & Bickel integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_setup_creates_entities(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
) -> None:
    entry = await setup_entry()
    assert entry.state is ConfigEntryState.LOADED

    # Climate reflects the device's current/target temperature.
    climate_states = hass.states.async_all("climate")
    assert len(climate_states) == 1
    assert climate_states[0].attributes["temperature"] == 180.0
    assert climate_states[0].attributes["current_temperature"] == 40.0

    # The Volcano exposes heater, pump, vibration, auto-shutoff, and
    # Fahrenheit-display switches.
    assert len(hass.states.async_all("switch")) == 5
    # Heater + pump + connectivity binary sensors.
    assert len(hass.states.async_all("binary_sensor")) == 3
    # Full-session, fill-balloon, and stop-workflow buttons.
    assert len(hass.states.async_all("button")) == 3
    # Temperature + total_runtime (enabled by default) plus the 5 session
    # sensors (last_session, total_sessions, total_pump_time, favorite_temperature,
    # session_history); several other sensors exist but are disabled by default.
    assert len(hass.states.async_all("sensor")) == 7

    # The companion card resolves entities by translation_key (see
    # card/src/entities.ts); every platform must set it, including climate.
    registry = er.async_get(hass)
    climate_entry = registry.async_get(climate_states[0].entity_id)
    assert climate_entry is not None
    assert climate_entry.translation_key == "heater"


async def test_unload(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
) -> None:
    entry = await setup_entry()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
