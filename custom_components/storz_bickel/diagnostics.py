"""Diagnostics for the Storz & Bickel integration.

Learn more: https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from custom_components.storz_bickel.data import StorzBickelConfigEntry

# The BLE address and serial number can identify a physical device/owner.
TO_REDACT = {CONF_ADDRESS, "address", "serial_number"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001 - required signature
    entry: StorzBickelConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data
    coordinator = data.coordinator
    device = data.device

    return async_redact_data(
        {
            "entry": {
                "title": entry.title,
                "data": dict(entry.data),
                "unique_id": entry.unique_id,
            },
            "device": {
                "type": device.device_type.value,
                "name": device.name,
                "address": device.address,
                "connected": device.connected,
                "capabilities": asdict(device.capabilities),
            },
            "coordinator": {
                "last_update_success": coordinator.last_update_success,
                "update_interval": str(coordinator.update_interval),
                "last_exception": (
                    repr(coordinator.last_exception)
                    if coordinator.last_exception
                    else None
                ),
            },
            "state": asdict(device.state),
        },
        TO_REDACT,
    )
