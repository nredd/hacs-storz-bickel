"""Tests for the pump failsafe window and post-off cooldown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.storz_bickel.const import (
    CONF_PUMP_COOLDOWN_ENABLED,
    CONF_PUMP_COOLDOWN_SECONDS,
    CONF_PUMP_FAILSAFE_ENABLED,
    CONF_PUMP_FAILSAFE_SECONDS,
    DOMAIN,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice


def _pump_entity_id(hass: HomeAssistant, fake_device: FakeDevice) -> str:
    """Look up the pump switch's entity ID from the registry."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "switch", DOMAIN, f"{fake_device.address}_pump"
    )
    assert entity_id is not None
    return entity_id


async def _turn_pump(hass: HomeAssistant, entity_id: str, *, on: bool) -> None:
    """Call the switch turn_on/turn_off service for the pump."""
    await hass.services.async_call(
        "switch",
        "turn_on" if on else "turn_off",
        {"entity_id": entity_id},
        blocking=True,
    )


async def _elapse(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float
) -> None:
    """Advance time and fire any timers that became due."""
    freezer.tick(seconds)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_failsafe_turns_pump_off_after_window(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """The pump is forced off 45s (default) after an HA-commanded turn-on."""
    await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True]

    await _elapse(hass, freezer, 45)
    assert fake_device.pump_calls == [True, False]
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "off"


async def test_failsafe_covers_device_originated_activation(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A pump-on observed via BLE notification (device button) is also bounded."""
    await setup_entry()

    fake_device.push_status(pump_on=True)
    await hass.async_block_till_done()

    await _elapse(hass, freezer, 45)
    assert fake_device.pump_calls == [False]


async def test_failsafe_not_extended_by_duplicate_rising_edges(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A notification echo of pump-on must not restart the failsafe window."""
    await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    await _elapse(hass, freezer, 20)
    assert fake_device.pump_calls == [True]

    # The device echoes the already-on state mid-window.
    fake_device.push_status(pump_on=True)
    await hass.async_block_till_done()

    # 45s after the original turn-on the pump must go off (not 45s after the echo).
    await _elapse(hass, freezer, 25)
    assert fake_device.pump_calls == [True, False]


async def test_cooldown_blocks_turn_on(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Turning the pump back on within the cooldown raises; after it, succeeds."""
    await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    await _turn_pump(hass, entity_id, on=False)

    with pytest.raises(ServiceValidationError):
        await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True, False]

    await _elapse(hass, freezer, 5)
    await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True, False, True]


async def test_cooldown_started_by_failsafe_off(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A failsafe-triggered off starts the cooldown just like a manual off."""
    await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    await _elapse(hass, freezer, 45)
    assert fake_device.pump_calls == [True, False]

    with pytest.raises(ServiceValidationError):
        await _turn_pump(hass, entity_id, on=True)

    await _elapse(hass, freezer, 5)
    await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True, False, True]


async def test_disabled_protections(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Disabling the toggles turns off both protections, whatever the durations."""
    await setup_entry(
        options={
            CONF_PUMP_FAILSAFE_ENABLED: False,
            CONF_PUMP_COOLDOWN_ENABLED: False,
        }
    )
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    await _elapse(hass, freezer, 600)
    assert fake_device.pump_calls == [True]

    await _turn_pump(hass, entity_id, on=False)
    await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True, False, True]


async def test_custom_durations_respected(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Configured failsafe/cooldown durations override the defaults."""
    await setup_entry(
        options={
            CONF_PUMP_FAILSAFE_SECONDS: 10,
            CONF_PUMP_COOLDOWN_SECONDS: 2,
        }
    )
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    await _elapse(hass, freezer, 9)
    assert fake_device.pump_calls == [True]
    await _elapse(hass, freezer, 1)
    assert fake_device.pump_calls == [True, False]

    with pytest.raises(ServiceValidationError):
        await _turn_pump(hass, entity_id, on=True)

    await _elapse(hass, freezer, 2)
    await _turn_pump(hass, entity_id, on=True)
    assert fake_device.pump_calls == [True, False, True]


async def test_failsafe_cancelled_on_unload(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Unloading the entry cancels an armed failsafe timer."""
    entry = await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    await _elapse(hass, freezer, 60)
    assert fake_device.pump_calls == [True]


async def test_pump_on_at_startup_arms_failsafe(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A pump already running when the entry loads still gets a failsafe window."""
    fake_device.push_status(pump_on=True)
    await setup_entry()

    await _elapse(hass, freezer, 45)
    assert fake_device.pump_calls == [False]


async def test_failsafe_disconnect_rearm(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """A disconnect cancels the timer; a reconnect with the pump on re-arms it."""
    await setup_entry()
    entity_id = _pump_entity_id(hass, fake_device)

    await _turn_pump(hass, entity_id, on=True)
    fake_device.connected = False
    fake_device.fire()
    await hass.async_block_till_done()

    # The window elapses while disconnected: no off command can (or should) be sent.
    await _elapse(hass, freezer, 100)
    assert fake_device.pump_calls == [True]

    # Reconnect with the pump still running: a fresh full window is armed.
    fake_device.connected = True
    fake_device.push_status(pump_on=True)
    await hass.async_block_till_done()

    await _elapse(hass, freezer, 45)
    assert fake_device.pump_calls == [True, False]
