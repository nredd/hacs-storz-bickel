"""Tests for the workflow buttons and the background step runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.storz_bickel.api import DeviceType, capabilities_for
from custom_components.storz_bickel.const import DOMAIN

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice

_FULL_SESSION_TEMPS = [170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0]
_FULL_SESSION_PUMP_SECONDS = 5
_FILL_BALLOON_TEMP = 185.0
_FILL_BALLOON_PUMP_SECONDS = 30


def _button_entity_id(hass: HomeAssistant, fake_device: FakeDevice, key: str) -> str:
    """Look up a workflow button's entity ID from the registry."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "button", DOMAIN, f"{fake_device.address}_{key}"
    )
    assert entity_id is not None
    return entity_id


async def _press(hass: HomeAssistant, entity_id: str) -> None:
    """Call the button.press service for the given entity."""
    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id}, blocking=True
    )


async def _elapse(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float
) -> None:
    """Advance time and fire any timers that became due."""
    freezer.tick(seconds)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_full_session_step_ordering(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """The full-session workflow ramps every rung in order, pumping at each."""
    await setup_entry()
    # Already above every rung, so each WaitUntilTemperatureReached resolves
    # instantly and only the pump-run timers gate progress.
    fake_device.state.current_temperature = 300.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_full_session"))
    for _ in _FULL_SESSION_TEMPS:
        await _elapse(hass, freezer, _FULL_SESSION_PUMP_SECONDS)

    assert fake_device.heater_calls == [True]
    assert fake_device.target_temperature_calls == _FULL_SESSION_TEMPS
    assert fake_device.pump_calls == [True, False] * len(_FULL_SESSION_TEMPS)


async def test_fill_balloon_uses_configured_constants(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """The fill-balloon workflow sets 185C and runs the pump for 30s."""
    await setup_entry()
    fake_device.state.current_temperature = 300.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_fill_balloon"))
    await _elapse(hass, freezer, _FILL_BALLOON_PUMP_SECONDS)

    assert fake_device.heater_calls == [True]
    assert fake_device.target_temperature_calls == [_FILL_BALLOON_TEMP]
    assert fake_device.pump_calls == [True, False]


async def test_wait_until_reached_blocks_until_data_updates(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """The pump does not run until the coordinator observes the target temperature."""
    await setup_entry()
    fake_device.state.current_temperature = 40.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_fill_balloon"))
    await hass.async_block_till_done()
    assert fake_device.pump_calls == []

    fake_device.state.current_temperature = _FILL_BALLOON_TEMP
    fake_device.fire()
    await hass.async_block_till_done()
    await _elapse(hass, freezer, _FILL_BALLOON_PUMP_SECONDS)

    assert fake_device.pump_calls == [True, False]


async def test_wait_timeout_stops_workflow(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A stalled temperature wait times out and stops the workflow (no pump run)."""
    await setup_entry()
    fake_device.state.current_temperature = 40.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_fill_balloon"))
    await hass.async_block_till_done()

    await _elapse(hass, freezer, 600)
    assert fake_device.pump_calls == []
    assert fake_device.heater_calls == [True]
    assert fake_device.target_temperature_calls == [_FILL_BALLOON_TEMP]


async def test_single_flight_rejects_concurrent_start(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Starting a second workflow while one is running raises."""
    await setup_entry()
    fake_device.state.current_temperature = 40.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_full_session"))
    with pytest.raises(ServiceValidationError):
        await _press(hass, _button_entity_id(hass, fake_device, "workflow_fill_balloon"))


async def test_stop_button_cancels_without_forcing_off(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Stopping mid-wait halts further steps without forcing heater/pump off."""
    await setup_entry()
    fake_device.state.current_temperature = 40.0

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_full_session"))
    await hass.async_block_till_done()
    assert fake_device.heater_calls == [True]

    await _press(hass, _button_entity_id(hass, fake_device, "workflow_stop"))
    await hass.async_block_till_done()

    assert fake_device.pump_calls == []
    await _elapse(hass, freezer, 1000)
    assert fake_device.pump_calls == []
    assert fake_device.target_temperature_calls == [170.0]


async def test_no_pump_device_gets_no_workflow_buttons(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
) -> None:
    """A pump-less device (e.g. Crafty) gets no workflow buttons at all."""
    fake_device.capabilities = capabilities_for(DeviceType.CRAFTY)
    entry = await setup_entry()

    registry = er.async_get(hass)
    for key in ("workflow_full_session", "workflow_fill_balloon", "workflow_stop"):
        assert (
            registry.async_get_entity_id("button", DOMAIN, f"{fake_device.address}_{key}")
            is None
        )
    assert entry.runtime_data.coordinator.workflow_runner is None
