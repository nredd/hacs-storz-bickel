"""Active-connection DataUpdateCoordinator for Storz & Bickel devices.

The coordinator keeps a persistent BLE connection to one device. Heat/pump (and,
for portables, the full status frame) arrive as notifications and are pushed to
entities via :meth:`async_set_updated_data`; the current temperature is read on a
short poll interval. The live ``BLEDevice`` is re-resolved from Home Assistant's
Bluetooth stack each cycle so reconnects use the freshest advertisement path.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.storz_bickel.api import (
    SBDeviceState,
    StorzBickelConnectionError,
    StorzBickelError,
)
from custom_components.storz_bickel.const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from custom_components.storz_bickel.api import SBDevice
    from custom_components.storz_bickel.data import StorzBickelConfigEntry


class StorzBickelDataUpdateCoordinator(DataUpdateCoordinator[SBDeviceState]):
    """Manage the BLE connection and distribute device state to entities."""

    config_entry: StorzBickelConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: StorzBickelConfigEntry,
        device: SBDevice,
        update_interval_seconds: float,
    ) -> None:
        """Initialize the coordinator for a single device.

        Args:
            hass: The Home Assistant instance.
            config_entry: The config entry for this device.
            device: The connected device adapter.
            update_interval_seconds: Polling cadence for the current temperature.
        """
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self.device = device
        self._unregister_callback = device.register_callback(self._handle_device_update)

    def _handle_device_update(self, state: SBDeviceState) -> None:
        """Push a notification-driven state update to all entities."""
        self.async_set_updated_data(state)

    async def _async_setup(self) -> None:
        """Establish the initial connection before the first data fetch."""
        try:
            await self._ensure_connected()
        except StorzBickelError as err:
            raise ConfigEntryNotReady(str(err)) from err

    async def _async_update_data(self) -> SBDeviceState:
        """Ensure the connection is alive and poll the current temperature."""
        try:
            await self._ensure_connected()
            return await self.device.async_poll()
        except StorzBickelError as err:
            raise UpdateFailed(str(err)) from err

    async def _ensure_connected(self) -> None:
        """Reconnect if needed, resolving the latest BLEDevice from HA Bluetooth."""
        if self.device.connected:
            return
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass,
            self.device.address,
            connectable=True,
        )
        if ble_device is None:
            msg = f"{self.device.name} is not currently in range"
            raise StorzBickelConnectionError(msg)
        self.device.set_ble_device(ble_device)
        await self.device.async_connect()

    async def async_shutdown(self) -> None:
        """Disconnect from the device and tear down the coordinator."""
        await super().async_shutdown()
        self._unregister_callback()
        await self.device.async_disconnect()
