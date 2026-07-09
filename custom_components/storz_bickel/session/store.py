"""Persistence for a device's lifetime session history."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.storage import Store

from custom_components.storz_bickel.const import (
    SESSION_STORAGE_KEY_PREFIX,
    SESSION_STORAGE_VERSION,
)
from custom_components.storz_bickel.session.models import Session

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class SessionStore:
    """Load/save a device's lifetime session list as JSON.

    Keyed by BLE address (not config entry ID) so the history survives a
    remove-and-re-add of the config entry, matching how entity unique IDs are
    keyed elsewhere in the integration.
    """

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the store for one device address."""
        self._store: Store[dict[str, Any]] = Store(
            hass, SESSION_STORAGE_VERSION, f"{SESSION_STORAGE_KEY_PREFIX}_{address}"
        )

    async def async_load(self) -> list[Session]:
        """Load the persisted session list, or an empty list if none exists."""
        data = await self._store.async_load()
        if data is None:
            return []
        return [Session(**record) for record in data.get("sessions", [])]

    async def async_save(self, sessions: list[Session]) -> None:
        """Persist the full session list."""
        await self._store.async_save({"sessions": [s.as_dict() for s in sessions]})
