"""Session detection: turns heater/pump state edges into qualifying sessions.

A session is a heater-on window (optionally paused across brief heater-off
gaps, see below) that lasts at least :data:`SESSION_MIN_DURATION_SECONDS` and,
for pump-capable devices, ran the pump continuously for at least
:data:`SESSION_PUMP_QUALIFY_SECONDS` at least once. Every coordinator state
update samples the current setpoint while a window is open; those samples
become the finalized session's min/max/median/mode/average.

Heater-off does not immediately end an open window: a grace timer of
:data:`SESSION_HEATER_OFF_TIMEOUT_SECONDS` starts on the falling edge, and if
the heater comes back on before it fires, accumulation resumes in the same
window (this tolerates normal PID on/off cycling instead of fragmenting one
real usage session into disqualified pieces). If the timer fires, the window
finalizes using the heater's last-observed off time as the stop time.
"""

from __future__ import annotations

import statistics
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from custom_components.storz_bickel.const import (
    SESSION_HEATER_OFF_TIMEOUT_SECONDS,
    SESSION_MIN_DURATION_SECONDS,
    SESSION_PUMP_QUALIFY_SECONDS,
    SESSION_SETPOINT_ROUND_NDIGITS,
)
from custom_components.storz_bickel.session.models import Session

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE, HomeAssistant

    from custom_components.storz_bickel.api import SBDevice, SBDeviceState
    from custom_components.storz_bickel.session.store import SessionStore


class SessionTracker:
    """Detect qualifying sessions from device state updates for one device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: SBDevice,
        store: SessionStore,
        on_finalized: Callable[[], None] | None = None,
    ) -> None:
        """Initialize the tracker; call :meth:`async_load` before first use.

        Args:
            hass: The Home Assistant instance.
            device: The device adapter whose state drives session detection.
            store: Persists the lifetime session list.
            on_finalized: Called after a window is finalized (whether or not it
                qualified as a session). Session finalization happens on the
                grace-timer's own schedule, independent of the coordinator's
                poll/push cycle, so entities that derive their state from the
                tracker need this hook to know to re-render.
        """
        self._hass = hass
        self._device = device
        self._store = store
        self._on_finalized = on_finalized
        self.sessions: list[Session] = []

        # None = unknown (startup or after a disconnect), matching the same
        # convention as StorzBickelPumpGuard so the first observed heater-on
        # always counts as a fresh rising edge.
        self._last_heater_on: bool | None = None
        self._last_pump_on: bool | None = None

        self._window_start: datetime | None = None
        self._setpoint_samples: list[float] = []
        self._pump_on_since: datetime | None = None
        self._pump_total_seconds: float = 0.0
        self._pump_qualified: bool = False
        self._heater_off_since: datetime | None = None
        self._cancel_grace_timer: CALLBACK_TYPE | None = None

    async def async_load(self) -> None:
        """Load the persisted lifetime session list."""
        self.sessions = await self._store.async_load()

    async def async_shutdown(self) -> None:
        """Cancel any armed grace timer and flush the session list to disk."""
        self._cancel_grace_timer_if_armed()
        await self._store.async_save(self.sessions)

    @property
    def total_pump_seconds(self) -> float:
        """Return cumulative pump-on time across all completed sessions."""
        return sum(session.pump_seconds for session in self.sessions)

    @property
    def last_session_stop(self) -> datetime | None:
        """Return the stop time of the most recently completed session."""
        if not self.sessions:
            return None
        return dt_util.parse_datetime(self.sessions[-1].stop)

    @property
    def favorite_temperature_celsius(self) -> float | None:
        """Return the mode of each session's own modal setpoint, in Celsius."""
        if not self.sessions:
            return None
        modal_setpoints = [round(session.mode_setpoint_c) for session in self.sessions]
        return statistics.mode(modal_setpoints)

    @callback
    def handle_state(self, state: SBDeviceState) -> None:
        """Detect heater/pump edges in a state update and react to them.

        Must be invoked for every state update the coordinator observes (both
        the poll and push paths), mirroring ``StorzBickelPumpGuard.handle_state``.
        """
        if not self._device.connected:
            # A disconnect is not a heater-off observation: leave any open
            # window untouched, only reset the edge-detection flags so the
            # next post-reconnect observation isn't spuriously treated as a
            # duplicate edge (same convention as StorzBickelPumpGuard).
            self._last_heater_on = None
            self._last_pump_on = None
            return

        heater_on = state.heater_on
        if heater_on is True and self._last_heater_on is not True:
            self._on_heater_rising_edge()
        elif heater_on is False and self._last_heater_on is True:
            self._on_heater_falling_edge()
        self._last_heater_on = heater_on

        if self._window_start is not None:
            if state.target_temperature is not None:
                self._setpoint_samples.append(state.target_temperature)
            if self._device.capabilities.pump:
                self._handle_pump_edge(state.pump_on)

    @callback
    def _on_heater_rising_edge(self) -> None:
        """Open a new window, or resume one paused by a brief heater-off gap."""
        self._cancel_grace_timer_if_armed()
        self._heater_off_since = None
        if self._window_start is None:
            self._window_start = dt_util.utcnow()
            self._setpoint_samples = []
            self._pump_total_seconds = 0.0
            self._pump_qualified = False
            self._pump_on_since = None
            self._last_pump_on = None

    @callback
    def _on_heater_falling_edge(self) -> None:
        """Arm the grace timer; the open window is not finalized yet."""
        self._heater_off_since = dt_util.utcnow()
        self._arm_grace_timer()

    @callback
    def _handle_pump_edge(self, pump_on: bool | None) -> None:
        """Track pump-on intervals within the open window.

        A still-open interval is checked against the qualifying threshold on
        every tick (not just at close time), so a session that ends mid-pump
        still counts a long-enough burst.
        """
        now = dt_util.utcnow()
        if pump_on is True and self._last_pump_on is not True:
            self._pump_on_since = now
        elif pump_on is False and self._last_pump_on is True:
            if self._pump_on_since is not None:
                duration = (now - self._pump_on_since).total_seconds()
                self._pump_total_seconds += duration
                if duration >= SESSION_PUMP_QUALIFY_SECONDS:
                    self._pump_qualified = True
                self._pump_on_since = None
        elif pump_on is True and self._pump_on_since is not None:
            elapsed = (now - self._pump_on_since).total_seconds()
            if elapsed >= SESSION_PUMP_QUALIFY_SECONDS:
                self._pump_qualified = True
        self._last_pump_on = pump_on

    @callback
    def _arm_grace_timer(self) -> None:
        if self._cancel_grace_timer is not None:
            return
        self._cancel_grace_timer = async_call_later(
            self._hass, SESSION_HEATER_OFF_TIMEOUT_SECONDS, self._async_grace_expired
        )

    @callback
    def _cancel_grace_timer_if_armed(self) -> None:
        if self._cancel_grace_timer is not None:
            self._cancel_grace_timer()
            self._cancel_grace_timer = None

    async def _async_grace_expired(self, _now: datetime) -> None:
        """Finalize the open window once the heater has been off long enough."""
        self._cancel_grace_timer = None
        if self._window_start is None or self._heater_off_since is None:
            return
        await self._async_finalize(self._heater_off_since)

    async def _async_finalize(self, stop: datetime) -> None:
        """Close the open window, recording a session if it qualifies.

        Runs on the grace timer's own schedule rather than the coordinator's
        poll/push cycle, so ``on_finalized`` is invoked unconditionally to let
        the coordinator prompt its entities to re-render.
        """
        start = self._window_start
        samples = self._setpoint_samples
        pump_seconds = self._pump_total_seconds
        if self._pump_on_since is not None:
            pump_seconds += (stop - self._pump_on_since).total_seconds()
        pump_qualified = self._pump_qualified
        duration_seconds = (stop - start).total_seconds() if start is not None else 0.0

        self._reset_window()
        try:
            if start is None or duration_seconds < SESSION_MIN_DURATION_SECONDS:
                return
            if self._device.capabilities.pump and not pump_qualified:
                return
            if not samples:
                return

            rounded_samples = [round(s, SESSION_SETPOINT_ROUND_NDIGITS) for s in samples]
            session = Session(
                start=start.isoformat(),
                stop=stop.isoformat(),
                min_setpoint_c=min(samples),
                max_setpoint_c=max(samples),
                median_setpoint_c=statistics.median(samples),
                mode_setpoint_c=statistics.mode(rounded_samples),
                average_setpoint_c=statistics.mean(samples),
                pump_seconds=pump_seconds,
            )
            self.sessions.append(session)
            await self._store.async_save(self.sessions)
        finally:
            if self._on_finalized is not None:
                self._on_finalized()

    @callback
    def _reset_window(self) -> None:
        self._window_start = None
        self._setpoint_samples = []
        self._pump_total_seconds = 0.0
        self._pump_qualified = False
        self._pump_on_since = None
        self._heater_off_since = None
