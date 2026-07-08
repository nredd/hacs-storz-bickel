"""Button platform for Storz & Bickel workflows (canned BLE action sequences)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from custom_components.storz_bickel.const import PARALLEL_UPDATES as _PARALLEL_UPDATES
from custom_components.storz_bickel.entity import StorzBickelEntity
from custom_components.storz_bickel.workflow import FILL_BALLOON_STEPS, FULL_SESSION_STEPS

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )
    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PARALLEL_UPDATES = _PARALLEL_UPDATES


@dataclass(frozen=True, kw_only=True)
class StorzBickelButtonEntityDescription(ButtonEntityDescription):
    """Describes a Storz & Bickel button entity."""

    capability: str
    press_fn: Callable[[StorzBickelDataUpdateCoordinator], Coroutine[Any, Any, None]]


async def _press_full_session(coordinator: StorzBickelDataUpdateCoordinator) -> None:
    """Start the "Full session" workflow."""
    if coordinator.workflow_runner is not None:
        coordinator.workflow_runner.async_start("full_session", FULL_SESSION_STEPS)


async def _press_fill_balloon(coordinator: StorzBickelDataUpdateCoordinator) -> None:
    """Start the "Fill balloon" workflow."""
    if coordinator.workflow_runner is not None:
        coordinator.workflow_runner.async_start("fill_balloon", FILL_BALLOON_STEPS)


async def _press_stop(coordinator: StorzBickelDataUpdateCoordinator) -> None:
    """Cancel the running workflow, if any."""
    if coordinator.workflow_runner is not None:
        coordinator.workflow_runner.async_cancel()


# All gated on the "pump" capability: both default workflows require the pump,
# so that's what actually determines whether the steps are runnable.
BUTTONS: tuple[StorzBickelButtonEntityDescription, ...] = (
    StorzBickelButtonEntityDescription(
        key="workflow_full_session",
        translation_key="workflow_full_session",
        capability="pump",
        icon="mdi:play-circle-outline",
        press_fn=_press_full_session,
    ),
    StorzBickelButtonEntityDescription(
        key="workflow_fill_balloon",
        translation_key="workflow_fill_balloon",
        capability="pump",
        icon="mdi:balloon",
        press_fn=_press_fill_balloon,
    ),
    StorzBickelButtonEntityDescription(
        key="workflow_stop",
        translation_key="workflow_stop",
        capability="pump",
        icon="mdi:stop-circle-outline",
        press_fn=_press_stop,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StorzBickelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up workflow button entities supported by the connected device."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    async_add_entities(
        StorzBickelButton(coordinator, description)
        for description in BUTTONS
        if getattr(capabilities, description.capability)
    )


class StorzBickelButton(StorzBickelEntity, ButtonEntity):
    """A capability-gated workflow trigger."""

    entity_description: StorzBickelButtonEntityDescription

    async def async_press(self) -> None:
        """Run the button's action."""
        await self.entity_description.press_fn(self.coordinator)
