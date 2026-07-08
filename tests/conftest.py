"""Shared pytest fixtures for the Storz & Bickel integration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

from homeassistant.const import CONF_ADDRESS
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.storz_bickel.api import DeviceType, capabilities_for
from custom_components.storz_bickel.api.models import SBDeviceState
from custom_components.storz_bickel.const import CONF_DEVICE_TYPE, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.core import HomeAssistant

ADDRESS = "AA:BB:CC:DD:EE:FF"
BLE_LOOKUP = "homeassistant.components.bluetooth.async_ble_device_from_address"
CREATE_DEVICE = "custom_components.storz_bickel.create_device"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of the custom integration in every test."""
    return


@pytest.fixture
def expected_lingering_timers() -> bool:
    """Tolerate the bluetooth manager's periodic availability-check timer.

    Setting up the ``bluetooth`` dependency schedules a recurring timer that the
    bundled test mocks do not fully tear down; Home Assistant core's own
    bluetooth tests tolerate it the same way.
    """
    return True


@pytest.fixture(autouse=True)
def _mock_linux_bt_history():
    """Stub the Linux adapter history (the bundled bluetooth mock leaves it un-stubbed).

    Without this, setting up the ``bluetooth`` dependency in tests hits the real
    BlueZ/DBus code path and fails on CI and dev machines.
    """
    with patch("bluetooth_adapters.systems.linux.LinuxAdapters.history", {}):
        yield


class FakeDevice:
    """A fake SBDevice that returns canned state without touching Bluetooth.

    Mirrors the real device's push behavior: ``async_set_pump`` performs an
    optimistic state write and fires callbacks, and ``push_status`` simulates a
    device-originated BLE status notification.
    """

    device_type = DeviceType.VOLCANO
    capabilities = capabilities_for(DeviceType.VOLCANO)
    temp_min = 40.0
    temp_max = 230.0
    temp_step = 1.0

    def __init__(self) -> None:
        self.address = ADDRESS
        self.name = "Volcano Test"
        self.connected = False
        self.pump_calls: list[bool] = []
        self.heater_calls: list[bool] = []
        self.target_temperature_calls: list[float] = []
        self.fahrenheit_calls: list[bool] = []
        self._callbacks: list[Callable[[SBDeviceState], None]] = []
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

    def register_callback(
        self, callback: Callable[[SBDeviceState], None]
    ) -> Callable[[], None]:
        self._callbacks.append(callback)

        def _unregister() -> None:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        return _unregister

    def fire(self) -> None:
        """Invoke all registered callbacks with the current state."""
        for callback in list(self._callbacks):
            callback(self._state)

    def push_status(self, *, pump_on: bool) -> None:
        """Simulate a device-originated status notification."""
        self._state.pump_on = pump_on
        self.fire()

    def set_ble_device(self, _ble_device: object) -> None:
        pass

    async def async_connect(self) -> None:
        self.connected = True

    async def async_disconnect(self) -> None:
        self.connected = False

    async def async_poll(self) -> SBDeviceState:
        return self._state

    async def async_set_pump(self, *, on: bool) -> None:
        """Record the pump command and mirror the real optimistic write."""
        self.pump_calls.append(on)
        self.push_status(pump_on=on)

    async def async_set_heater(self, *, on: bool) -> None:
        """Record the heater command and mirror the real optimistic write."""
        self.heater_calls.append(on)
        self._state.heater_on = on
        self.fire()

    async def async_set_target_temperature(self, celsius: float) -> None:
        """Record the target-temperature command and mirror the optimistic write."""
        self.target_temperature_calls.append(celsius)
        self._state.target_temperature = celsius
        self.fire()

    async def async_set_fahrenheit(self, *, on: bool) -> None:
        """Record the Fahrenheit-display command and mirror the optimistic write."""
        self.fahrenheit_calls.append(on)
        self._state.fahrenheit = on
        self.fire()


@pytest.fixture
def fake_device() -> FakeDevice:
    """Return a fresh fake Volcano device."""
    return FakeDevice()


@pytest.fixture
def setup_entry(
    hass: HomeAssistant, enable_bluetooth: None, fake_device: FakeDevice
) -> Callable[..., Awaitable[MockConfigEntry]]:
    """Return a factory that sets up a Volcano config entry backed by fake_device."""

    async def _setup(options: dict[str, Any] | None = None) -> MockConfigEntry:
        entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id=ADDRESS,
            data={CONF_ADDRESS: ADDRESS, CONF_DEVICE_TYPE: DeviceType.VOLCANO.value},
            options=options or {},
        )
        entry.add_to_hass(hass)
        with (
            patch(BLE_LOOKUP, return_value=MagicMock()),
            patch(CREATE_DEVICE, return_value=fake_device),
        ):
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
        return entry

    return _setup
