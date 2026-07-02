"""Volcano Hybrid protocol adapter.

This map is validated against real hardware. The connection/read/write/notify
approach is adapted from the MIT-licensed ``Chuffnugget/volcano_integration``
Home Assistant component (Copyright (c) 2025 Chuffnugget), reworked to use Home
Assistant's ``bleak-retry-connector`` connection management and this package's
device abstraction. See the repository ``NOTICE`` file for attribution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.storz_bickel.api import const as c
from custom_components.storz_bickel.api.devices.base import SBDevice
from custom_components.storz_bickel.api.models import (
    DeviceCapabilities,
    DeviceType,
    SBDeviceState,
)

if TYPE_CHECKING:
    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice

# Refresh slow-changing settings (brightness, auto-off, vibration, runtime) every
# Nth poll so lifetime telemetry stays fresh without hammering the BLE link.
_SETTINGS_REFRESH_EVERY = 20


class VolcanoDevice(SBDevice):
    """Adapter for the Storz & Bickel Volcano Hybrid."""

    device_type = DeviceType.VOLCANO
    capabilities = DeviceCapabilities(
        pump=True,
        vibration=True,
        auto_shutoff=True,
        auto_shutoff_toggle=True,
        led_brightness=True,
        hours_of_operation=True,
    )
    temp_min = c.VOLCANO_TEMP_MIN
    temp_max = c.VOLCANO_TEMP_MAX

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the Volcano adapter."""
        super().__init__(ble_device)
        self._poll_count = 0

    async def _read_static_info(self) -> None:
        """Read serial number and firmware versions once after connecting."""
        self._state.serial_number = await self._read_string(c.VOLCANO_UUID_SERIAL_NUMBER)
        self._state.firmware_version = await self._read_string(
            c.VOLCANO_UUID_FIRMWARE_VERSION
        )
        self._state.ble_firmware_version = await self._read_string(
            c.VOLCANO_UUID_BLE_FIRMWARE_VERSION
        )

    async def _subscribe(self) -> None:
        """Subscribe to the heat/pump status register notifications."""
        await self._start_notify(
            c.VOLCANO_UUID_STATUS_REGISTER, self._handle_status_notification
        )

    def _handle_status_notification(
        self, _char: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Decode the uint16 status bitmask (heater/pump/auto-shutoff) and push it."""
        if len(data) < 2:
            return
        value = int.from_bytes(data[:2], byteorder="little")
        self._state.heater_on = bool(value & c.VOLCANO_STATUS_MASK_HEATER)
        self._state.pump_on = bool(value & c.VOLCANO_STATUS_MASK_PUMP)
        self._state.auto_shutoff_enabled = bool(
            value & c.VOLCANO_STATUS_MASK_AUTO_SHUTOFF
        )
        self._fire_callbacks()

    async def async_poll(self) -> SBDeviceState:
        """Poll the current temperature and, periodically, the slower settings."""
        temp_raw = await self._read_uint16(c.VOLCANO_UUID_CURRENT_TEMP)
        if temp_raw is not None:
            self._state.current_temperature = temp_raw / c.TEMP_SCALE

        if self._poll_count % _SETTINGS_REFRESH_EVERY == 0:
            await self._read_settings()
        self._poll_count += 1

        self._fire_callbacks()
        return self._state

    async def _read_settings(self) -> None:
        """Read brightness, auto-shutoff, runtime counters, and the control register."""
        target_raw = await self._read_uint16(c.VOLCANO_UUID_TARGET_TEMP)
        if target_raw is not None:
            self._state.target_temperature = target_raw / c.TEMP_SCALE

        self._state.led_brightness = await self._read_uint8(c.VOLCANO_UUID_LED_BRIGHTNESS)

        auto_off = await self._read_uint8(c.VOLCANO_UUID_AUTO_OFF_ENABLE)
        if auto_off is not None:
            self._state.auto_shutoff_enabled = bool(auto_off)
        auto_off_seconds = await self._read_uint16(c.VOLCANO_UUID_AUTO_OFF_SETTING)
        if auto_off_seconds is not None:
            self._state.auto_shutoff_minutes = auto_off_seconds // 60

        self._state.hours_of_operation = await self._read_uint16(
            c.VOLCANO_UUID_HOURS_OF_OPERATION
        )
        self._state.minutes_of_operation = await self._read_uint16(
            c.VOLCANO_UUID_MINUTES_OF_OPERATION
        )

        control = await self._read_uint32_control()
        if control is not None:
            self._state.vibration = bool(control & c.VOLCANO_MASK_VIBRATION)
            self._state.fahrenheit = bool(control & c.VOLCANO_MASK_FAHRENHEIT)

    async def _read_uint32_control(self) -> int | None:
        """Read the 4-byte little-endian control register, or ``None`` if short."""
        data = await self._read(c.VOLCANO_UUID_CONTROL_REGISTER)
        if len(data) < 4:
            return None
        return int.from_bytes(data[:4], byteorder="little")

    # --- Commands ---------------------------------------------------------- #

    async def async_set_target_temperature(self, celsius: float) -> None:
        """Write the heater setpoint (uint16 LE tenths of a degree)."""
        safe = self._clamp(celsius, self.temp_min, self.temp_max)
        payload = round(safe * c.TEMP_SCALE).to_bytes(2, byteorder="little")
        await self._write(c.VOLCANO_UUID_TARGET_TEMP, payload)
        self._state.target_temperature = safe
        self._fire_callbacks()

    async def async_set_heater(self, *, on: bool) -> None:
        """Trigger the heater on/off characteristic."""
        uuid = c.VOLCANO_UUID_HEAT_ON if on else c.VOLCANO_UUID_HEAT_OFF
        await self._write(uuid, c.VOLCANO_TRIGGER_PAYLOAD)
        self._state.heater_on = on
        self._fire_callbacks()

    async def async_set_pump(self, *, on: bool) -> None:
        """Trigger the pump on/off characteristic."""
        uuid = c.VOLCANO_UUID_PUMP_ON if on else c.VOLCANO_UUID_PUMP_OFF
        await self._write(uuid, c.VOLCANO_TRIGGER_PAYLOAD)
        self._state.pump_on = on
        self._fire_callbacks()

    async def async_set_vibration(self, *, on: bool) -> None:
        """Toggle the vibration bit in the control register (read-modify-write)."""
        control = await self._read_uint32_control()
        if control is None:
            return
        control = (
            control | c.VOLCANO_MASK_VIBRATION
            if on
            else control & ~c.VOLCANO_MASK_VIBRATION
        )
        await self._write(
            c.VOLCANO_UUID_CONTROL_REGISTER, control.to_bytes(4, byteorder="little")
        )
        self._state.vibration = on
        self._fire_callbacks()

    async def async_set_led_brightness(self, percent: int) -> None:
        """Write the LED brightness (single byte 0-100)."""
        clamped = int(self._clamp(percent, 0, 100))
        await self._write(
            c.VOLCANO_UUID_LED_BRIGHTNESS, clamped.to_bytes(1, byteorder="little")
        )
        self._state.led_brightness = clamped
        self._fire_callbacks()

    async def async_set_auto_shutoff(self, *, on: bool) -> None:
        """Enable or disable auto-shutoff via the ON/OFF trigger characteristics."""
        uuid = c.VOLCANO_UUID_AUTO_SHUTOFF_ON if on else c.VOLCANO_UUID_AUTO_SHUTOFF_OFF
        await self._write(uuid, c.VOLCANO_TRIGGER_PAYLOAD)
        self._state.auto_shutoff_enabled = on
        self._fire_callbacks()

    async def async_set_auto_shutoff_minutes(self, minutes: int) -> None:
        """Set the auto-shutoff duration (uint16 LE seconds)."""
        seconds = max(0, minutes) * 60
        await self._write(
            c.VOLCANO_UUID_AUTO_OFF_SETTING, seconds.to_bytes(2, byteorder="little")
        )
        self._state.auto_shutoff_minutes = minutes
        self._fire_callbacks()
