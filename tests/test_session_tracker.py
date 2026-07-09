"""Unit tests for the SessionTracker state machine."""

from __future__ import annotations

import statistics
from typing import TYPE_CHECKING, cast

import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.storz_bickel.api import DeviceType, capabilities_for
from custom_components.storz_bickel.api.models import SBDeviceState
from custom_components.storz_bickel.session import Session, SessionStore, SessionTracker

if TYPE_CHECKING:
    from freezegun.api import FrozenDateTimeFactory
    from homeassistant.core import HomeAssistant

    from custom_components.storz_bickel.api import SBDevice
    from custom_components.storz_bickel.api.models import DeviceCapabilities

ADDRESS = "AA:BB:CC:DD:EE:FF"


class _StubDevice:
    """Minimal device stub exposing only what SessionTracker reads."""

    def __init__(self, capabilities: DeviceCapabilities) -> None:
        self.connected = True
        self.capabilities = capabilities
        self.address = ADDRESS


def _stub_device(capabilities: DeviceCapabilities) -> SBDevice:
    """Return a device stub, cast to SBDevice for the tracker's signature."""
    return cast("SBDevice", _StubDevice(capabilities))


async def _elapse(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: float
) -> None:
    """Advance time and let any due timers fire."""
    freezer.tick(seconds)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


def _state(
    *, heater_on: bool, pump_on: bool | None = None, target: float | None = 180.0
) -> SBDeviceState:
    return SBDeviceState(heater_on=heater_on, pump_on=pump_on, target_temperature=target)


async def _make_tracker(hass: HomeAssistant, device: SBDevice) -> SessionTracker:
    tracker = SessionTracker(hass, device, SessionStore(hass, device.address))
    await tracker.async_load()
    return tracker


async def test_session_start_and_finalize(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A qualifying heater+pump window produces one session record."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 120)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1
    assert tracker.sessions[0].pump_seconds == pytest.approx(6.0, abs=0.5)


async def test_minimum_duration_rejects_short_window(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A window under the 2-minute minimum is discarded, even if pump qualifies."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert tracker.sessions == []


async def test_pump_qualifying_rejects_short_bursts(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A pump-capable device needs one continuous >=5s pump burst to qualify."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=False))
    for _ in range(3):
        tracker.handle_state(_state(heater_on=True, pump_on=True))
        await _elapse(hass, freezer, 2)
        tracker.handle_state(_state(heater_on=True, pump_on=False))
        await _elapse(hass, freezer, 5)
    await _elapse(hass, freezer, 120)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert tracker.sessions == []


async def test_pump_qualifies_via_one_long_burst(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """One >=5s burst qualifies the session; total pump time sums every burst."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=False))
    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 2)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 3)
    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 120)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1
    assert tracker.sessions[0].pump_seconds == pytest.approx(8.0, abs=0.5)


async def test_non_pump_device_qualifies_without_pump(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Non-pump devices qualify on heater-on + duration alone."""
    device = _stub_device(capabilities_for(DeviceType.VENTY))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=None))
    await _elapse(hass, freezer, 130)
    tracker.handle_state(_state(heater_on=False, pump_on=None))
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1
    assert tracker.sessions[0].pump_seconds == 0.0


async def test_heater_off_within_grace_resumes_same_session(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A brief heater-off gap pauses, not ends, the open window."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 60)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 600)  # gap well under the 15-minute grace window
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 70)  # total on-time now exceeds the 2-minute minimum
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1


async def test_two_bursts_beyond_grace_window_do_not_combine(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A gap past the 15-minute grace window finalizes and starts a fresh window."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 60)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)  # exceeds the grace window: first window finalizes

    # First window never reached the 2-minute minimum, so it was discarded.
    assert tracker.sessions == []

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 120)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1


async def test_stat_computation_matches_statistics_module(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Min/max/median/mode/average match independently computed statistics."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)
    expected: list[float] = []

    def push(*, heater_on: bool, pump_on: bool | None, target: float | None) -> None:
        tracker.handle_state(_state(heater_on=heater_on, pump_on=pump_on, target=target))
        if target is not None:
            expected.append(target)

    push(heater_on=True, pump_on=True, target=180.0)
    await _elapse(hass, freezer, 1)
    push(heater_on=True, pump_on=True, target=185.0)
    await _elapse(hass, freezer, 1)
    push(heater_on=True, pump_on=True, target=190.0)
    await _elapse(hass, freezer, 1)
    push(heater_on=True, pump_on=True, target=180.0)
    await _elapse(hass, freezer, 6)
    push(heater_on=True, pump_on=False, target=180.0)
    await _elapse(hass, freezer, 120)
    push(heater_on=False, pump_on=False, target=None)
    await _elapse(hass, freezer, 901)

    assert len(tracker.sessions) == 1
    session = tracker.sessions[0]
    assert session.min_setpoint_c == min(expected)
    assert session.max_setpoint_c == max(expected)
    assert session.median_setpoint_c == statistics.median(expected)
    assert session.average_setpoint_c == statistics.mean(expected)
    assert session.mode_setpoint_c == statistics.mode([round(v) for v in expected])


async def test_favorite_temperature_is_mode_of_session_modes(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """Favorite temperature is the mode of each session's own modal setpoint."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    def make_session(mode_c: float) -> Session:
        return Session(
            start="2024-01-01T00:00:00+00:00",
            stop="2024-01-01T00:10:00+00:00",
            min_setpoint_c=mode_c,
            max_setpoint_c=mode_c,
            median_setpoint_c=mode_c,
            mode_setpoint_c=mode_c,
            average_setpoint_c=mode_c,
            pump_seconds=10.0,
        )

    tracker.sessions = [make_session(180.0), make_session(185.0), make_session(180.0)]
    assert tracker.favorite_temperature_celsius == 180.0


async def test_persistence_round_trip(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> None:
    """A finalized session survives a shutdown/reload of the store."""
    device = _stub_device(capabilities_for(DeviceType.VOLCANO))
    tracker = await _make_tracker(hass, device)

    tracker.handle_state(_state(heater_on=True, pump_on=True))
    await _elapse(hass, freezer, 6)
    tracker.handle_state(_state(heater_on=True, pump_on=False))
    await _elapse(hass, freezer, 120)
    tracker.handle_state(_state(heater_on=False, pump_on=False))
    await _elapse(hass, freezer, 901)
    assert len(tracker.sessions) == 1

    await tracker.async_shutdown()

    fresh_tracker = SessionTracker(hass, device, SessionStore(hass, device.address))
    await fresh_tracker.async_load()
    assert fresh_tracker.sessions == tracker.sessions
