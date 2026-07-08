"""Runs built-in workflows in the background, without blocking the poll loop.

Styled like :mod:`coordinator.pump_guard`: a small helper owned by the
coordinator. A workflow is a fixed sequence of :mod:`workflow.steps`; this
runner executes one step at a time as a config-entry background task, so it is
automatically cancelled on unload and never blocks
:class:`~custom_components.storz_bickel.coordinator.base.StorzBickelDataUpdateCoordinator`.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import async_call_later

from custom_components.storz_bickel.api import StorzBickelError
from custom_components.storz_bickel.const import (
    DOMAIN,
    LOGGER,
    WORKFLOW_TEMPERATURE_WAIT_TIMEOUT_SECONDS,
)
from custom_components.storz_bickel.workflow.steps import (
    RunPump,
    SetHeat,
    SetTemperature,
    WaitUntilTemperatureReached,
    WorkflowStep,
)

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant

    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )
    from custom_components.storz_bickel.data import StorzBickelConfigEntry


class _WorkflowTimeoutError(Exception):
    """Raised internally when a temperature wait exceeds its timeout."""


class StorzBickelWorkflowRunner:
    """Run one workflow at a time in the background for a single device."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: StorzBickelConfigEntry,
        coordinator: StorzBickelDataUpdateCoordinator,
    ) -> None:
        """Initialize the runner for one coordinator's device.

        Args:
            hass: The Home Assistant instance.
            entry: The config entry, used to create an auto-cancelled task.
            coordinator: The coordinator whose device the workflow drives, and
                whose polled data feeds ``WaitUntilTemperatureReached``.
        """
        self._hass = hass
        self._entry = entry
        self._coordinator = coordinator
        self._task: asyncio.Task[None] | None = None

    @property
    def running(self) -> bool:
        """Return whether a workflow is currently running."""
        return self._task is not None

    @callback
    def async_start(self, key: str, steps: tuple[WorkflowStep, ...]) -> None:
        """Start a workflow in the background.

        Raises:
            ServiceValidationError: If a workflow is already running.
        """
        if self._task is not None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="workflow_already_running",
            )
        self._task = self._entry.async_create_background_task(
            self._hass, self._async_run(steps), name=f"storz_bickel_workflow_{key}"
        )
        self._task.add_done_callback(self._async_on_done)

    @callback
    def _async_on_done(self, _task: asyncio.Task[None]) -> None:
        """Clear the running task once it finishes, is cancelled, or errors."""
        self._task = None

    @callback
    def async_cancel(self) -> None:
        """Cancel the running workflow, if any."""
        if self._task is not None:
            self._task.cancel()

    @callback
    def async_shutdown(self) -> None:
        """Cancel any running workflow (entry unload/reload)."""
        self.async_cancel()

    async def _async_run(self, steps: tuple[WorkflowStep, ...]) -> None:
        """Execute each step in order, stopping on a BLE error or wait timeout."""
        device = self._coordinator.device
        target_celsius: float | None = None
        try:
            for step in steps:
                match step:
                    case SetHeat(on=on):
                        await device.async_set_heater(on=on)
                    case SetTemperature(celsius=celsius):
                        target_celsius = celsius
                        await device.async_set_target_temperature(celsius)
                    case WaitUntilTemperatureReached():
                        await self._async_wait_until_reached(target_celsius)
                    case RunPump(seconds=seconds):
                        await self._async_run_pump(seconds)
        except (StorzBickelError, _WorkflowTimeoutError) as err:
            LOGGER.warning("Workflow stopped for %s: %s", device.name, err)

    async def _async_wait_until_reached(self, target_celsius: float | None) -> None:
        """Block until the current temperature reaches ``target_celsius``.

        Raises:
            _WorkflowTimeoutError: If the target is not reached within
                :data:`WORKFLOW_TEMPERATURE_WAIT_TIMEOUT_SECONDS`.
        """
        if target_celsius is None:
            return
        reached = asyncio.Event()
        timed_out = False

        @callback
        def _check() -> None:
            current = self._coordinator.data.current_temperature
            if current is not None and current >= target_celsius:
                reached.set()

        @callback
        def _on_timeout(_now: datetime) -> None:
            nonlocal timed_out
            timed_out = True
            reached.set()

        remove_listener = self._coordinator.async_add_listener(_check)
        cancel_timeout = async_call_later(
            self._hass, WORKFLOW_TEMPERATURE_WAIT_TIMEOUT_SECONDS, _on_timeout
        )
        try:
            _check()
            await reached.wait()
        finally:
            remove_listener()
            cancel_timeout()
        if timed_out:
            msg = f"timed out waiting to reach {target_celsius}°C"
            raise _WorkflowTimeoutError(msg)

    async def _async_run_pump(self, seconds: float) -> None:
        """Run the pump for ``seconds``, guaranteeing it is turned off after."""
        device = self._coordinator.device
        await device.async_set_pump(on=True)
        try:
            done = asyncio.Event()

            @callback
            def _on_done(_now: datetime) -> None:
                done.set()

            cancel_timer = async_call_later(self._hass, seconds, _on_done)
            try:
                await done.wait()
            finally:
                cancel_timer()
        finally:
            await device.async_set_pump(on=False)
