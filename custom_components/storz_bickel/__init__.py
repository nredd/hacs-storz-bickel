"""The Storz & Bickel integration.

Connects to a Storz & Bickel Bluetooth vaporizer (Volcano Hybrid, Venty, Veazy,
or Crafty), maintains a persistent BLE connection, and exposes its controls and
telemetry as Home Assistant entities. All communication is local; there is no
cloud or companion-app dependency.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_integration, async_get_loaded_integration

from custom_components.storz_bickel.api import DeviceType, create_device
from custom_components.storz_bickel.const import (
    CARD_FILENAME,
    CARD_URL,
    CONF_DEVICE_TYPE,
    DOMAIN,
    POLL_INTERVAL_SECONDS,
)
from custom_components.storz_bickel.coordinator import StorzBickelDataUpdateCoordinator
from custom_components.storz_bickel.data import StorzBickelData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

    from custom_components.storz_bickel.data import StorzBickelConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Register the bundled Lovelace card with the HTTP server and frontend.

    Home Assistant calls this exactly once per run, when the component first
    loads, so the card resource is registered a single time regardless of how
    many devices are configured or how often entries reload.
    """
    integration = await async_get_integration(hass, DOMAIN)
    card_path = Path(__file__).parent / "www" / CARD_FILENAME
    # cache_headers=True is safe: the ?v= query below busts caches per release.
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(card_path), cache_headers=True)]
    )
    add_extra_js_url(hass, f"{CARD_URL}?v={integration.version or '0'}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: StorzBickelConfigEntry) -> bool:
    """Set up a Storz & Bickel device from a config entry."""
    address: str = entry.data[CONF_ADDRESS]
    device_type = DeviceType(entry.data[CONF_DEVICE_TYPE])

    ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if ble_device is None:
        msg = f"Could not find Storz & Bickel device with address {address}"
        raise ConfigEntryNotReady(msg)

    device = create_device(device_type, ble_device)
    coordinator = StorzBickelDataUpdateCoordinator(
        hass, entry, device, POLL_INTERVAL_SECONDS
    )
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
