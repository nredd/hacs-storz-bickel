"""End-to-end setup tests for the Storz & Bickel integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_ADDRESS
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.storz_bickel.api import DeviceType, capabilities_for
from custom_components.storz_bickel.api.models import SBDeviceState
from custom_components.storz_bickel.const import CONF_DEVICE_TYPE, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant

ADDRESS = "AA:BB:CC:DD:EE:FF"
_BLE_LOOKUP = "homeassistant.components.bluetooth.async_ble_device_from_address"
_CREATE_DEVICE = "custom_components.storz_bickel.create_device"


class FakeDevice:
    """A fake SBDevice that returns canned state without touching Bluetooth."""

    device_type = DeviceType.VOLCANO
    capabilities = capabilities_for(DeviceType.VOLCANO)
    temp_min = 40.0
    temp_max = 230.0
    temp_step = 1.0

    def __init__(self) -> None:
        self.address = ADDRESS
        self.name = "Volcano Test"
        self.connected = False
        self._state = SBDeviceState(
            current_temperature=40.0,
            target_temperature=180.0,
            heater_on=False,
            pump_on=False,
            led_brightness=70,
            serial_number="SN123",
            firmware_version="1.0",
            hours_of_operation=100,
            minutes_of_operation=30,
        )

    @property
    def state(self) -> SBDeviceState:
        return self._state

    def register_callback(self, _callback: Callable[[SBDeviceState], None]) -> Callable[[], None]:
        return lambda: None

    def set_ble_device(self, _ble_device: object) -> None:
        pass

    async def async_connect(self) -> None:
        self.connected = True

    async def async_disconnect(self) -> None:
        self.connected = False

    async def async_poll(self) -> SBDeviceState:
        return self._state


async def _setup(hass: HomeAssistant, enable_bluetooth: None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=ADDRESS,
        data={CONF_ADDRESS: ADDRESS, CONF_DEVICE_TYPE: DeviceType.VOLCANO.value},
    )
    entry.add_to_hass(hass)
    with (
        patch(_BLE_LOOKUP, return_value=MagicMock()),
        patch(_CREATE_DEVICE, return_value=FakeDevice()),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_setup_creates_entities(hass: HomeAssistant, enable_bluetooth: None) -> None:
    entry = await _setup(hass, enable_bluetooth)
    assert entry.state is ConfigEntryState.LOADED

    # Climate reflects the device's current/target temperature.
    climate_states = hass.states.async_all("climate")
    assert len(climate_states) == 1
    assert climate_states[0].attributes["temperature"] == 180.0
    assert climate_states[0].attributes["current_temperature"] == 40.0

    # The Volcano exposes pump, vibration, and auto-shutoff switches.
    assert len(hass.states.async_all("switch")) == 3
    # Heater + pump + connectivity binary sensors.
    assert len(hass.states.async_all("binary_sensor")) == 3


async def test_unload(hass: HomeAssistant, enable_bluetooth: None) -> None:
    entry = await _setup(hass, enable_bluetooth)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
