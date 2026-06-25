"""Venty and Veazy protocol adapter.

Both devices speak the same framed protocol over a single control characteristic:
a 20-byte frame ``[cmd, mask, ...payload]`` is written, and the device answers
with a notification whose first byte echoes the command. Status, extended data
(lifetime counters), and device identity are each separate commands.

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
    from bleak.backends.device import BLEDevice

_FRAME_LEN = 20
# Re-request the lifetime counters / identity every Nth poll (they change slowly).
_EXTENDED_REFRESH_EVERY = 30


def _build_frame(
    cmd: int, mask: int = 0, byte_values: dict[int, int] | None = None
) -> bytes:
    """Build a 20-byte control frame with an optional per-byte payload map."""
    frame = bytearray(_FRAME_LEN)
    frame[0] = cmd
    frame[1] = mask
    for index, value in (byte_values or {}).items():
        frame[index] = value & 0xFF
    return bytes(frame)


class VentyVeazyDevice(SBDevice):
    """Shared adapter for the Venty and Veazy portable vaporizers."""

    capabilities = DeviceCapabilities(
        vibration=True,
        auto_shutoff=True,
        boost_temperature=True,
        battery=True,
        heater_runtime=True,
    )
    temp_min = c.PORTABLE_TEMP_MIN
    temp_max = c.PORTABLE_TEMP_MAX

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the portable adapter."""
        super().__init__(ble_device)
        self._poll_count = 0

    async def _read_static_info(self) -> None:
        """Identity arrives asynchronously via the device-data command notification."""
        await self._request(c.VENTY_CMD_DEVICE_DATA)

    async def _subscribe(self) -> None:
        """Subscribe to the single control characteristic for all responses."""
        await self._start_notify(c.VENTY_UUID_CONTROL, self._handle_notification)

    async def _request(self, cmd: int) -> None:
        """Write a bare request frame for the given command."""
        await self._write(c.VENTY_UUID_CONTROL, _build_frame(cmd), response=False)

    def _handle_notification(
        self, _char: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        """Dispatch a notification frame by its echoed command byte."""
        if not data:
            return
        command = data[0]
        if command == c.VENTY_CMD_STATUS:
            self._parse_status(data)
        elif command == c.VENTY_CMD_EXTENDED_DATA:
            self._parse_extended(data)
        elif command == c.VENTY_CMD_DEVICE_DATA:
            self._parse_device_data(data)
        else:
            return
        self._fire_callbacks()

    def _parse_status(self, data: bytearray) -> None:
        """Parse the main status frame (target temp, battery, heater mode, flags)."""
        if len(data) < c.VENTY_STATUS_MIN_LEN:
            return
        target_raw = int.from_bytes(
            data[c.VENTY_STATUS_TARGET_TEMP_LO : c.VENTY_STATUS_TARGET_TEMP_LO + 2],
            byteorder="little",
        )
        self._state.target_temperature = round(target_raw / c.TEMP_SCALE)
        self._state.boost_temperature = data[c.VENTY_STATUS_BOOST_TEMP]
        self._state.battery_level = data[c.VENTY_STATUS_BATTERY]
        auto_off_seconds = int.from_bytes(
            data[c.VENTY_STATUS_AUTO_OFF_LO : c.VENTY_STATUS_AUTO_OFF_LO + 2],
            byteorder="little",
        )
        self._state.auto_shutoff_minutes = auto_off_seconds // 60
        self._state.heater_on = data[c.VENTY_STATUS_HEATER_MODE] > c.VENTY_HEATER_MODE_OFF
        settings = data[c.VENTY_STATUS_SETTINGS]
        self._state.fahrenheit = bool(settings & c.VENTY_SETTING_UNIT_FAHRENHEIT)
        self._state.vibration = bool(settings & c.VENTY_SETTING_VIBRATION)
        self._state.auto_shutoff_enabled = auto_off_seconds > 0

    def _parse_extended(self, data: bytearray) -> None:
        """Parse the extended-data frame (lifetime heater runtime + charge time)."""
        if len(data) < c.VENTY_EXT_BATTERY_CHARGE_OFF + 3:
            return
        self._state.heater_runtime_minutes = int.from_bytes(
            data[c.VENTY_EXT_HEATER_RUNTIME_OFF : c.VENTY_EXT_HEATER_RUNTIME_OFF + 3],
            byteorder="little",
        )
        self._state.battery_charge_time_minutes = int.from_bytes(
            data[c.VENTY_EXT_BATTERY_CHARGE_OFF : c.VENTY_EXT_BATTERY_CHARGE_OFF + 3],
            byteorder="little",
        )

    def _parse_device_data(self, data: bytearray) -> None:
        """Parse the device-data frame (serial number = prefix bytes 15-16 + name 9-14)."""
        if len(data) < 17:
            return
        prefix = bytes(data[15:17]).decode("utf-8", errors="replace")
        name = bytes(data[9:15]).decode("utf-8", errors="replace")
        serial = (prefix + name).strip()
        self._state.serial_number = serial or None

    async def async_poll(self) -> SBDeviceState:
        """Request the status frame and, periodically, the lifetime counters."""
        await self._request(c.VENTY_CMD_STATUS)
        if self._poll_count % _EXTENDED_REFRESH_EVERY == 0:
            await self._request(c.VENTY_CMD_EXTENDED_DATA)
        self._poll_count += 1
        return self._state

    # --- Commands ---------------------------------------------------------- #

    async def async_set_target_temperature(self, celsius: float) -> None:
        """Write the target temperature (uint16 LE tenths across bytes 4-5)."""
        safe = round(self._clamp(celsius, self.temp_min, self.temp_max))
        raw = safe * c.TEMP_SCALE
        await self._write(
            c.VENTY_UUID_CONTROL,
            _build_frame(
                c.VENTY_CMD_STATUS,
                c.VENTY_WRITE_SET_TEMPERATURE,
                {4: raw & 0xFF, 5: raw >> 8},
            ),
        )
        self._state.target_temperature = safe
        self._fire_callbacks()

    async def async_set_heater(self, *, on: bool) -> None:
        """Set the heater mode (normal when on, off otherwise)."""
        mode = c.VENTY_HEATER_MODE_NORMAL if on else c.VENTY_HEATER_MODE_OFF
        await self._write(
            c.VENTY_UUID_CONTROL,
            _build_frame(
                c.VENTY_CMD_STATUS,
                c.VENTY_WRITE_HEATER,
                {c.VENTY_STATUS_HEATER_MODE: mode},
            ),
        )
        self._state.heater_on = on
        self._fire_callbacks()

    async def async_set_boost_temperature(self, celsius: float) -> None:
        """Write the boost-offset temperature (single byte)."""
        value = int(self._clamp(celsius, 0, 30))
        await self._write(
            c.VENTY_UUID_CONTROL,
            _build_frame(
                c.VENTY_CMD_STATUS,
                c.VENTY_WRITE_SET_BOOST,
                {c.VENTY_STATUS_BOOST_TEMP: value},
            ),
        )
        self._state.boost_temperature = value
        self._fire_callbacks()

    async def async_set_auto_shutoff_minutes(self, minutes: int) -> None:
        """Write the auto-shutoff timer (uint16 LE seconds across bytes 9-10)."""
        seconds = max(0, minutes) * 60
        await self._write(
            c.VENTY_UUID_CONTROL,
            _build_frame(
                c.VENTY_CMD_STATUS,
                c.VENTY_WRITE_AUTO_SHUTOFF,
                {
                    c.VENTY_STATUS_AUTO_OFF_LO: seconds & 0xFF,
                    c.VENTY_STATUS_AUTO_OFF_LO + 1: seconds >> 8,
                },
            ),
        )
        self._state.auto_shutoff_minutes = minutes
        self._fire_callbacks()

    async def async_set_vibration(self, *, on: bool) -> None:
        """Toggle the vibration settings bit (best-effort)."""
        bit = c.VENTY_SETTING_VIBRATION if on else 0
        await self._write(
            c.VENTY_UUID_CONTROL,
            _build_frame(
                c.VENTY_CMD_STATUS,
                c.VENTY_WRITE_SETTINGS,
                {c.VENTY_STATUS_SETTINGS: bit, 15: c.VENTY_SETTING_VIBRATION},
            ),
        )
        self._state.vibration = on
        self._fire_callbacks()


class VentyDevice(VentyVeazyDevice):
    """Adapter for the Storz & Bickel Venty."""

    device_type = DeviceType.VENTY


class VeazyDevice(VentyVeazyDevice):
    """Adapter for the Storz & Bickel Veazy."""

    device_type = DeviceType.VEAZY
