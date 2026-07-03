"""Pump failsafe window and cooldown enforcement for the air pump.

The Volcano's pump can be switched on from Home Assistant, the physical device,
or (indirectly) the failsafe below. All of those state changes funnel through the
coordinator's device callback, so :class:`StorzBickelPumpGuard` observes every
``pump_on`` edge regardless of origin:

- **Failsafe window**: a rising edge arms a one-shot timer that turns the pump
  back off after the configured duration, bounding accidental runs.
- **Cooldown**: a falling edge starts a cooldown during which the switch entity
  rejects turn-on requests, preventing wasteful rapid off->on toggling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util

from custom_components.storz_bickel.api import StorzBickelError
from custom_components.storz_bickel.const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import CALLBACK_TYPE, HomeAssistant

    from custom_components.storz_bickel.api import SBDevice, SBDeviceState


class StorzBickelPumpGuard:
    """Enforce a pump failsafe window and a post-off cooldown for one device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: SBDevice,
        *,
        failsafe_enabled: bool,
        failsafe_seconds: int,
        cooldown_enabled: bool,
        cooldown_seconds: int,
    ) -> None:
        """Initialize the guard with per-entry option values.

        Args:
            hass: The Home Assistant instance.
            device: The device adapter whose pump is being guarded.
            failsafe_enabled: Whether the auto-off failsafe window is active.
            failsafe_seconds: Seconds after a pump-on before it is forced off.
            cooldown_enabled: Whether the off->on cooldown is active.
            cooldown_seconds: Seconds after a pump-off during which turn-on is
                rejected.
        """
        self._hass = hass
        self._device = device
        self._failsafe_enabled = failsafe_enabled
        self._failsafe_seconds = failsafe_seconds
        self._cooldown_enabled = cooldown_enabled
        self._cooldown_seconds = cooldown_seconds
        # None = unknown (startup or after a disconnect), so the first observed
        # pump-on always counts as a rising edge.
        self._last_pump_on: bool | None = None
        self._cancel_failsafe: CALLBACK_TYPE | None = None
        self._pump_off_at: datetime | None = None

    @property
    def cooldown_remaining(self) -> float:
        """Return the seconds left in the cooldown, or ``0.0`` if none is active."""
        if not self._cooldown_enabled or self._pump_off_at is None:
            return 0.0
        elapsed = (dt_util.utcnow() - self._pump_off_at).total_seconds()
        return max(0.0, self._cooldown_seconds - elapsed)

    @callback
    def handle_state(self, state: SBDeviceState) -> None:
        """Detect pump on/off edges in a state update and react to them.

        Must be invoked for every state update the coordinator observes so
        device-originated pump activations are covered too.
        """
        if not self._device.connected:
            # We cannot act (or trust edges) while disconnected. Resetting to
            # unknown makes a post-reconnect pump-on a fresh rising edge, which
            # re-arms a full failsafe window.
            self._cancel_timer()
            self._last_pump_on = None
            return

        pump_on = state.pump_on
        if pump_on is True and self._last_pump_on is not True:
            # Rising edge, including from unknown: a pump found already running
            # (startup, reconnect) still gets a full failsafe window.
            self._arm_failsafe()
        elif pump_on is False and self._last_pump_on is True:
            # Falling edge only from a known on-state: merely observing an idle
            # pump (first update after startup/reconnect) starts no cooldown.
            self._cancel_timer()
            self._pump_off_at = dt_util.utcnow()
        self._last_pump_on = pump_on

    @callback
    def raise_if_cooldown_active(self) -> None:
        """Reject a turn-on request while the cooldown is running.

        Raises:
            ServiceValidationError: If the pump turned off less than the
                configured cooldown ago.
        """
        remaining = self.cooldown_remaining
        if remaining > 0:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="pump_cooldown_active",
                translation_placeholders={"remaining": f"{remaining:.0f}"},
            )

    @callback
    def async_shutdown(self) -> None:
        """Cancel any armed failsafe timer (entry unload/reload)."""
        self._cancel_timer()

    @callback
    def _arm_failsafe(self) -> None:
        """Arm the auto-off timer on a rising edge, if not already armed.

        The armed-timer check keeps duplicate rising edges (the optimistic write
        from ``async_set_pump`` followed by the notification echo) from extending
        the window.
        """
        if not self._failsafe_enabled or self._cancel_failsafe is not None:
            return
        self._cancel_failsafe = async_call_later(
            self._hass, self._failsafe_seconds, self._async_failsafe_expired
        )

    @callback
    def _cancel_timer(self) -> None:
        """Cancel the failsafe timer if one is armed."""
        if self._cancel_failsafe is not None:
            self._cancel_failsafe()
            self._cancel_failsafe = None

    async def _async_failsafe_expired(self, _now: datetime) -> None:
        """Turn the pump off after the failsafe window elapsed."""
        self._cancel_failsafe = None
        if self._device.state.pump_on is not True:
            return
        try:
            await self._device.async_set_pump(on=False)
        except StorzBickelError as err:
            # Typically the BLE connection dropped; handle_state's disconnect
            # reset re-arms a fresh window once the device reconnects.
            LOGGER.warning(
                "Pump failsafe could not turn off %s: %s", self._device.name, err
            )
