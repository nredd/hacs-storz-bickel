"""Step primitives that make up a workflow.

Each default workflow is a fixed, fully-unrolled sequence of these steps (see
``workflow/definitions.py``); there is no generic "repeat" construct because
neither shipped workflow needs one.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SetHeat:
    """Turn the heater on or off."""

    on: bool


@dataclass(frozen=True, slots=True)
class SetTemperature:
    """Set the target temperature, in degrees Celsius."""

    celsius: float


@dataclass(frozen=True, slots=True)
class WaitUntilTemperatureReached:
    """Block until the current temperature reaches the most recent ``SetTemperature``."""


@dataclass(frozen=True, slots=True)
class RunPump:
    """Run the pump for a fixed duration, in seconds."""

    seconds: float


type WorkflowStep = SetHeat | SetTemperature | WaitUntilTemperatureReached | RunPump
