"""Runtime data attached to each Storz & Bickel config entry.

Access pattern: ``entry.runtime_data.device`` / ``entry.runtime_data.coordinator``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from custom_components.storz_bickel.api import SBDevice
    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )


type StorzBickelConfigEntry = ConfigEntry[StorzBickelData]


@dataclass
class StorzBickelData:
    """Runtime data for a Storz & Bickel config entry.

    Stored as ``entry.runtime_data`` after a successful setup and provides typed
    access to the connected device and its coordinator.
    """

    device: SBDevice
    coordinator: StorzBickelDataUpdateCoordinator
    integration: Integration
