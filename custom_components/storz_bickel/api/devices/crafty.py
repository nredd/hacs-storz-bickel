"""Crafty / Crafty+ protocol adapter.

The Crafty exposes individual GATT characteristics (like the Volcano). Newer
"Crafty+" units (firmware >= 2.51) add remote heater control, usage minutes, and
auto-off characteristics that older units lack, so optional reads/writes tolerate
missing characteristics.

This map is reverse-engineered from the ``firsttris/reactive-volcano-app`` web
app and is pending hardware validation in this repository.
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

_BOOST_MIN = 0
_BOOST_MAX = 30


class CraftyDevice(SBDevice):
    """Adapter for the Storz & Bickel Crafty and Crafty+."""

    device_type = DeviceType.CRAFTY
    capabilities = DeviceCapabilities(
        led_brightness=True,
        boost_temperature=True,
        battery=True,
        auto_shutoff=True,
        hours_of_operation=True,
    )
    temp_min = c.PORTABLE_TEMP_MIN
    temp_max = c.PORTABLE_TEMP_MAX

    async def _read_static_info(self) -> None:
        """Read firmware versions (serial is not exposed over BLE on the Crafty)."""
        self._state.firmware_version = await self._try_read_string(
            c.CRAFTY_UUID_FIRMWARE_VERSION
        )
        self._state.ble_firmware_version = await self._try_read_string(
            c.CRAFTY_UUID_BLE_FIRMWARE_VERSION
        )

    async def _subscribe(self) -> None:
        """Subscribe to current-temperature and battery (power) notifications."""
        await self._start_notify(c.CRAFTY_UUID_CURRENT_TEMP, self._handle_temperature)
        await self._start_notify(c.CRAFTY_UUID_POWER, self._handle_power)

    def _handle_temperature(
        self, _char: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Decode the current chamber temperature (uint16 LE tenths)."""
        if len(data) < 2:
            return
        self._state.current_temperature = (
            int.from_bytes(data[:2], byteorder="little") / c.TEMP_SCALE
        )
        self._fire_callbacks()

    def _handle_power(self, _char: BleakGATTCharacteristic, data: bytearray) -> None:
        """Decode the battery percentage from the power characteristic."""
        if len(data) < 2:
            return
        self._state.battery_level = int.from_bytes(data[:2], byteorder="little")
        self._fire_callbacks()

    async def async_poll(self) -> SBDeviceState:
        """Read target/boost temperature, brightness, and lifetime usage counters."""
        target = await self._try_read_uint16(c.CRAFTY_UUID_TARGET_TEMP)
        if target is not None:
            self._state.target_temperature = round(target / c.TEMP_SCALE)
        boost = await self._try_read_uint16(c.CRAFTY_UUID_BOOST_TEMP)
        if boost is not None:
            self._state.boost_temperature = round(boost / c.TEMP_SCALE)
        self._state.led_brightness = await self._try_read_uint16(
            c.CRAFTY_UUID_LED_BRIGHTNESS
        )
        self._state.hours_of_operation = await self._try_read_uint16(
            c.CRAFTY_UUID_USE_HOURS
        )
        self._state.minutes_of_operation = await self._try_read_uint16(
            c.CRAFTY_UUID_USE_MINUTES
        )
        auto_off = await self._try_read_uint16(c.CRAFTY_UUID_AUTO_OFF_COUNTDOWN)
        if auto_off is not None:
            self._state.auto_shutoff_minutes = auto_off // 60
        self._fire_callbacks()
        return self._state

    # --- Commands ---------------------------------------------------------- #

    async def async_set_target_temperature(self, celsius: float) -> None:
        """Write the target temperature (uint16 LE tenths)."""
        safe = round(self._clamp(celsius, self.temp_min, self.temp_max))
        await self._write(
            c.CRAFTY_UUID_TARGET_TEMP,
            (safe * c.TEMP_SCALE).to_bytes(2, byteorder="little"),
        )
        self._state.target_temperature = safe
        self._fire_callbacks()

    async def async_set_heater(self, *, on: bool) -> None:
        """Turn the heater on/off (Crafty+ only; single byte 0x01)."""
        await self._write(
            c.CRAFTY_UUID_HEAT_ON if on else c.CRAFTY_UUID_HEAT_OFF, b"\x01"
        )
        self._state.heater_on = on
        self._fire_callbacks()

    async def async_set_boost_temperature(self, celsius: float) -> None:
        """Write the boost-offset temperature (uint16 LE tenths)."""
        value = round(self._clamp(celsius, _BOOST_MIN, _BOOST_MAX))
        await self._write(
            c.CRAFTY_UUID_BOOST_TEMP,
            (value * c.TEMP_SCALE).to_bytes(2, byteorder="little"),
        )
        self._state.boost_temperature = value
        self._fire_callbacks()

    async def async_set_led_brightness(self, percent: int) -> None:
        """Write the LED brightness (uint16 LE)."""
        clamped = int(self._clamp(percent, 0, 100))
        await self._write(
            c.CRAFTY_UUID_LED_BRIGHTNESS, clamped.to_bytes(2, byteorder="little")
        )
        self._state.led_brightness = clamped
        self._fire_callbacks()

    async def async_set_auto_shutoff_minutes(self, minutes: int) -> None:
        """Write the auto-off countdown (uint16 LE seconds; Crafty+ only)."""
        seconds = max(0, minutes) * 60
        await self._write(
            c.CRAFTY_UUID_AUTO_OFF_COUNTDOWN, seconds.to_bytes(2, byteorder="little")
        )
        self._state.auto_shutoff_minutes = minutes
        self._fire_callbacks()
