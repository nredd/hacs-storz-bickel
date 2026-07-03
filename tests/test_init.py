"""End-to-end setup tests for the Storz & Bickel integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState

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

    # The Volcano exposes heater, pump, vibration, and auto-shutoff switches.
    assert len(hass.states.async_all("switch")) == 4
    # Heater + pump + connectivity binary sensors.
    assert len(hass.states.async_all("binary_sensor")) == 3


async def test_unload(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
) -> None:
    entry = await setup_entry()
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
