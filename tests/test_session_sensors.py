"""End-to-end tests for session-derived sensor entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.storz_bickel.const import CONF_TEMPERATURE_UNIT, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from tests.conftest import FakeDevice


def _entity_id(hass: HomeAssistant, fake_device: FakeDevice, key: str) -> str:
    """Look up a session sensor's entity ID from the registry by unique ID."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{fake_device.address}_{key}"
    )
    assert entity_id is not None
    return entity_id


async def _elapse(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float
) -> None:
    """Advance time and let any due timers/coordinator refreshes fire."""
    freezer.tick(seconds)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def _run_qualifying_session(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, fake_device: FakeDevice
) -> None:
    """Drive the fake device through one qualifying heater+pump session."""
    await fake_device.async_set_heater(on=True)
    await hass.async_block_till_done()
    await fake_device.async_set_pump(on=True)
    await _elapse(hass, freezer, 6)
    await fake_device.async_set_pump(on=False)
    await _elapse(hass, freezer, 120)
    await fake_device.async_set_heater(on=False)
    await hass.async_block_till_done()
    await _elapse(hass, freezer, 901)


async def test_session_sensors_populate_after_qualifying_session(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """After one qualifying session, the session sensors reflect it."""
    await setup_entry()
    await _run_qualifying_session(hass, freezer, fake_device)

    total_sessions = hass.states.get(_entity_id(hass, fake_device, "total_sessions"))
    assert total_sessions is not None
    assert total_sessions.state == "1"

    last_session = hass.states.get(_entity_id(hass, fake_device, "last_session"))
    assert last_session is not None
    assert last_session.state not in ("unknown", "unavailable")

    total_pump_time = hass.states.get(_entity_id(hass, fake_device, "total_pump_time"))
    assert total_pump_time is not None
    assert float(total_pump_time.state) == pytest.approx(6.0, abs=0.5)

    history = hass.states.get(_entity_id(hass, fake_device, "session_history"))
    assert history is not None
    assert history.state == "1"
    assert len(history.attributes["sessions"]) == 1
    assert sum(history.attributes["daily_counts"].values()) == 1


async def test_current_session_start_reflects_open_window(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """current_session_start is set while a window is open, then clears."""
    await setup_entry()

    current_session = hass.states.get(
        _entity_id(hass, fake_device, "current_session_start")
    )
    assert current_session is not None
    assert current_session.state in ("unknown", "unavailable", "none")

    await fake_device.async_set_heater(on=True)
    await hass.async_block_till_done()

    current_session = hass.states.get(
        _entity_id(hass, fake_device, "current_session_start")
    )
    assert current_session is not None
    assert current_session.state not in ("unknown", "unavailable", "none")

    await _run_qualifying_session(hass, freezer, fake_device)

    current_session = hass.states.get(
        _entity_id(hass, fake_device, "current_session_start")
    )
    assert current_session is not None
    assert current_session.state in ("unknown", "unavailable", "none")


async def test_current_session_duration_survives_grace_toggle(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Duration tracks the open window and does not reset on a heat toggle."""
    await setup_entry()

    duration = hass.states.get(_entity_id(hass, fake_device, "current_session_duration"))
    assert duration is not None
    assert duration.state in ("unknown", "unavailable", "none")

    await fake_device.async_set_heater(on=True)
    await hass.async_block_till_done()
    await _elapse(hass, freezer, 60)
    fake_device.fire()
    await hass.async_block_till_done()

    duration = hass.states.get(_entity_id(hass, fake_device, "current_session_duration"))
    assert duration is not None
    assert float(duration.state) == pytest.approx(60.0, abs=1.0)

    # Heater off then back on within the 15-minute grace window: the same
    # window resumes, so the duration keeps counting from the original start.
    await fake_device.async_set_heater(on=False)
    await hass.async_block_till_done()
    await _elapse(hass, freezer, 60)
    await fake_device.async_set_heater(on=True)
    await hass.async_block_till_done()

    duration = hass.states.get(_entity_id(hass, fake_device, "current_session_duration"))
    assert duration is not None
    assert float(duration.state) == pytest.approx(120.0, abs=1.0)

    # Once the grace window expires the window closes and duration clears.
    await fake_device.async_set_heater(on=False)
    await hass.async_block_till_done()
    await _elapse(hass, freezer, 901)

    duration = hass.states.get(_entity_id(hass, fake_device, "current_session_duration"))
    assert duration is not None
    assert duration.state in ("unknown", "unavailable", "none")


async def test_favorite_temperature_unit_conversion(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """favorite_temperature converts to the configured display unit."""
    await setup_entry(options={CONF_TEMPERATURE_UNIT: UnitOfTemperature.FAHRENHEIT})
    await _run_qualifying_session(hass, freezer, fake_device)

    favorite = hass.states.get(_entity_id(hass, fake_device, "favorite_temperature"))
    assert favorite is not None
    # fake_device's target_temperature is 180.0 C -> 356.0 F.
    assert float(favorite.state) == pytest.approx(356.0, abs=0.5)


async def test_session_sensors_available_while_disconnected(
    hass: HomeAssistant,
    setup_entry: Callable[..., Awaitable[MockConfigEntry]],
    fake_device: FakeDevice,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Session data stays visible even when the BLE connection drops."""
    await setup_entry()
    await _run_qualifying_session(hass, freezer, fake_device)

    fake_device.connected = False
    fake_device.fire()
    await hass.async_block_till_done()

    total_sessions = hass.states.get(_entity_id(hass, fake_device, "total_sessions"))
    assert total_sessions is not None
    assert total_sessions.state == "1"
