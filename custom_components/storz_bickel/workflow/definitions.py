"""Built-in workflow definitions, mirroring the Storz & Bickel app's "Workflows".

V1 ships exactly two workflows; there is no user-defined workflow editor.
"""

from __future__ import annotations

from custom_components.storz_bickel.workflow.steps import (
    RunPump,
    SetHeat,
    SetTemperature,
    WaitUntilTemperatureReached,
    WorkflowStep,
)

# --- Full session: heat on, ramp in rungs, run the pump briefly at each. ---- #
_FULL_SESSION_MIN_C = 170
_FULL_SESSION_MAX_C = 200
_FULL_SESSION_STEP_C = 5
_FULL_SESSION_PUMP_SECONDS = 5


def _build_full_session_steps() -> tuple[WorkflowStep, ...]:
    """Generate the full-session ladder: heat on, then ramp+pump at each rung."""
    steps: list[WorkflowStep] = [SetHeat(on=True)]
    celsius = _FULL_SESSION_MIN_C
    while celsius <= _FULL_SESSION_MAX_C:
        steps.append(SetTemperature(celsius=float(celsius)))
        steps.append(WaitUntilTemperatureReached())
        steps.append(RunPump(seconds=_FULL_SESSION_PUMP_SECONDS))
        celsius += _FULL_SESSION_STEP_C
    return tuple(steps)


FULL_SESSION_STEPS: tuple[WorkflowStep, ...] = _build_full_session_steps()

# --- Fill balloon: heat on, set a single temperature, run the pump longer. - #
FILL_BALLOON_TEMPERATURE_C = 185
FILL_BALLOON_PUMP_SECONDS = 30

FILL_BALLOON_STEPS: tuple[WorkflowStep, ...] = (
    SetHeat(on=True),
    SetTemperature(celsius=float(FILL_BALLOON_TEMPERATURE_C)),
    WaitUntilTemperatureReached(),
    RunPump(seconds=FILL_BALLOON_PUMP_SECONDS),
)
