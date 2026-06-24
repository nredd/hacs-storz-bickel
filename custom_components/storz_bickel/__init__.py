"""The Storz & Bickel integration.

Connects to a Storz & Bickel Bluetooth vaporizer (Volcano Hybrid, Venty, Veazy,
or Crafty), maintains a persistent BLE connection, and exposes its controls and
telemetry as Home Assistant entities. All communication is local; there is no
cloud or companion-app dependency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from custom_components.storz_bickel.api import DeviceType, create_device
from custom_components.storz_bickel.const import CONF_DEVICE_TYPE, DOMAIN, POLL_INTERVAL_SECONDS
from custom_components.storz_bickel.coordinator import StorzBickelDataUpdateCoordinator
from custom_components.storz_bickel.data import StorzBickelData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: StorzBickelConfigEntry) -> bool:
    """Set up a Storz & Bickel device from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    device_type = DeviceType(entry.data[CONF_DEVICE_TYPE])

    ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if ble_device is None:
        msg = f"Could not find Storz & Bickel device with address {address}"
        raise ConfigEntryNotReady(msg)

    device = create_device(device_type, ble_device)
    coordinator = StorzBickelDataUpdateCoordinator(hass, entry, device, POLL_INTERVAL_SECONDS)
    entry.runtime_data = StorzBickelData(
        device=device,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: StorzBickelConfigEntry) -> bool:
    """Unload a config entry and disconnect from the device."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    data = getattr(entry, "runtime_data", None)
    if unload_ok and data is not None:
        await data.coordinator.async_shutdown()
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: StorzBickelConfigEntry) -> None:
    """Reload a config entry after its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
