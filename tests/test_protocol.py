"""Unit tests for the Storz & Bickel BLE protocol adapters.

These exercise the reverse-engineered encodings (temperature scaling, command
framing, status decoding) against a fake BLE client, with no Home Assistant or
real Bluetooth involved.
"""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache
import pytest

from custom_components.storz_bickel.api import (
    DeviceType,
    capabilities_for,
    const as c,
    detect_device_type,
)
from custom_components.storz_bickel.api.devices.base import SBDevice
from custom_components.storz_bickel.api.devices.crafty import CraftyDevice
from custom_components.storz_bickel.api.devices.venty_veazy import (
    VentyDevice,
    _build_frame,
)
from custom_components.storz_bickel.api.devices.volcano import VolcanoDevice
from custom_components.storz_bickel.api.models import SBDeviceState


class FakeClient:
    """A minimal stand-in for a connected bleak client."""

    def __init__(self, reads: dict[str, bytes] | None = None) -> None:
        self.is_connected = True
        self._reads = reads or {}
        self.writes: list[tuple[str, bytes]] = []
        self.notifications: dict[str, object] = {}

    async def read_gatt_char(self, uuid: str) -> bytes:
        if uuid not in self._reads:
            msg = f"unknown characteristic {uuid}"
            raise BleakError(msg)
        return self._reads[uuid]

    async def write_gatt_char(
        self, uuid: str, data: bytes, *, response: bool = False
    ) -> None:
        _ = response
        self.writes.append((uuid, bytes(data)))

    async def start_notify(self, uuid: str, handler: object) -> None:
        self.notifications[uuid] = handler


def _make[DeviceT: SBDevice](
    device_cls: type[DeviceT], client: FakeClient | None = None
) -> tuple[DeviceT, FakeClient]:
    """Build a device of the given type backed by a fake BLE client."""
    ble = MagicMock()
    ble.address = "AA:BB:CC:DD:EE:FF"
    ble.name = device_cls.device_type.value.upper()
    device = device_cls(ble)
    fake = client or FakeClient()
    device._client = cast("BleakClientWithServiceCache", fake)
    return device, fake


# --------------------------------------------------------------------------- #
# Discovery + models
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("name", "uuids", "expected"),
    [
        ("S&B VOLCANO H", [], DeviceType.VOLCANO),
        (None, [c.VOLCANO_SERVICE_DEVICE_STATE], DeviceType.VOLCANO),
        ("VENTY", [], DeviceType.VENTY),
        ("VEAZY", [], DeviceType.VEAZY),
        ("CRAFTY+", [], DeviceType.CRAFTY),
        (None, [c.CRAFTY_SERVICE_DATA], DeviceType.CRAFTY),
        (None, [c.VENTY_SERVICE_PRIMARY], DeviceType.VENTY),
        ("Some Lamp", ["1234"], None),
    ],
)
def test_detect_device_type(
    name: str | None, uuids: list[str], expected: DeviceType | None
) -> None:
    assert detect_device_type(name, uuids) == expected


def test_total_runtime_hours() -> None:
    assert (
        SBDeviceState(hours_of_operation=120, minutes_of_operation=30).total_runtime_hours
        == 120.5
    )
    assert SBDeviceState(hours_of_operation=10).total_runtime_hours == 10.0
    assert SBDeviceState().total_runtime_hours is None


def test_capabilities() -> None:
    assert capabilities_for(DeviceType.VOLCANO).pump is True
    assert capabilities_for(DeviceType.VOLCANO).boost_temperature is False
    assert capabilities_for(DeviceType.CRAFTY).pump is False
    assert capabilities_for(DeviceType.VENTY).heater_runtime is True


def test_model_names() -> None:
    assert DeviceType.VOLCANO.model_name == "Volcano Hybrid"
    assert DeviceType.CRAFTY.model_name == "Crafty"


# --------------------------------------------------------------------------- #
# Volcano
# --------------------------------------------------------------------------- #


async def test_volcano_set_target_temperature_encoding_and_clamp() -> None:
    device, client = _make(VolcanoDevice)
    await device.async_set_target_temperature(185.0)
    uuid, payload = client.writes[-1]
    assert uuid == c.VOLCANO_UUID_TARGET_TEMP
    assert payload == (1850).to_bytes(2, "little")

    await device.async_set_target_temperature(500.0)
    assert client.writes[-1][1] == (2300).to_bytes(2, "little")
    await device.async_set_target_temperature(0.0)
    assert client.writes[-1][1] == (400).to_bytes(2, "little")


async def test_volcano_heat_and_pump_triggers() -> None:
    device, client = _make(VolcanoDevice)
    await device.async_set_heater(on=True)
    assert client.writes[-1] == (c.VOLCANO_UUID_HEAT_ON, c.VOLCANO_TRIGGER_PAYLOAD)
    await device.async_set_pump(on=False)
    assert client.writes[-1] == (c.VOLCANO_UUID_PUMP_OFF, c.VOLCANO_TRIGGER_PAYLOAD)


async def test_volcano_auto_shutoff_triggers() -> None:
    device, client = _make(VolcanoDevice)
    await device.async_set_auto_shutoff(on=True)
    assert client.writes[-1] == (c.VOLCANO_UUID_AUTO_SHUTOFF_ON, c.VOLCANO_TRIGGER_PAYLOAD)
    await device.async_set_auto_shutoff(on=False)
    assert client.writes[-1] == (c.VOLCANO_UUID_AUTO_SHUTOFF_OFF, c.VOLCANO_TRIGGER_PAYLOAD)


@pytest.mark.parametrize(
    ("raw", "heater", "pump"),
    [
        (b"\x23\x00", True, False),
        (b"\x00\x00", False, False),
        (b"\x00\x30", False, True),
        (b"\x23\x30", True, True),
    ],
)
def test_volcano_status_decode(raw: bytes, heater: bool, pump: bool) -> None:
    device, _ = _make(VolcanoDevice)
    device._handle_status_notification(MagicMock(), bytearray(raw))
    assert device.state.heater_on is heater
    assert device.state.pump_on is pump


async def test_volcano_poll_temperature() -> None:
    device, _ = _make(
        VolcanoDevice, FakeClient(reads={c.VOLCANO_UUID_CURRENT_TEMP: b"\x46\x07"})
    )
    device._poll_count = 1  # skip the slow settings refresh
    state = await device.async_poll()
    assert state.current_temperature == 186.2


async def test_volcano_vibration_read_modify_write() -> None:
    reads = {c.VOLCANO_UUID_CONTROL_REGISTER: (0x0000).to_bytes(4, "little")}
    device, client = _make(VolcanoDevice, FakeClient(reads=reads))
    await device.async_set_vibration(on=True)
    uuid, payload = client.writes[-1]
    assert uuid == c.VOLCANO_UUID_CONTROL_REGISTER
    assert int.from_bytes(payload, "little") & c.VOLCANO_MASK_VIBRATION


# --------------------------------------------------------------------------- #
# Venty / Veazy
# --------------------------------------------------------------------------- #


def test_venty_build_frame() -> None:
    frame = _build_frame(
        c.VENTY_CMD_STATUS, c.VENTY_WRITE_SET_TEMPERATURE, {4: 0x3A, 5: 0x07}
    )
    assert len(frame) == 20
    assert frame[0] == c.VENTY_CMD_STATUS
    assert frame[1] == c.VENTY_WRITE_SET_TEMPERATURE
    assert frame[4] == 0x3A
    assert frame[5] == 0x07


def test_venty_parse_status() -> None:
    device, _ = _make(VentyDevice)
    data = bytearray(20)
    data[0] = c.VENTY_CMD_STATUS
    data[4], data[5] = 0x3A, 0x07  # 1850 -> 185.0 C
    data[8] = 80  # battery
    data[11] = 1  # heater mode normal -> on
    data[14] = c.VENTY_SETTING_VIBRATION
    device._handle_notification(MagicMock(), data)
    assert device.state.target_temperature == 185
    assert device.state.battery_level == 80
    assert device.state.heater_on is True
    assert device.state.vibration is True


def test_venty_parse_extended_runtime() -> None:
    device, _ = _make(VentyDevice)
    data = bytearray(20)
    data[0] = c.VENTY_CMD_EXTENDED_DATA
    data[1], data[2], data[3] = 0x10, 0x00, 0x00  # heater runtime 16 minutes
    data[4], data[5], data[6] = 0x20, 0x00, 0x00  # battery charge 32 minutes
    device._handle_notification(MagicMock(), data)
    assert device.state.heater_runtime_minutes == 16
    assert device.state.battery_charge_time_minutes == 32


async def test_venty_set_target_temperature_frame() -> None:
    device, client = _make(VentyDevice)
    await device.async_set_target_temperature(180.0)
    uuid, payload = client.writes[-1]
    assert uuid == c.VENTY_UUID_CONTROL
    assert payload[0] == c.VENTY_CMD_STATUS
    assert payload[1] == c.VENTY_WRITE_SET_TEMPERATURE
    assert int.from_bytes(payload[4:6], "little") == 1800


# --------------------------------------------------------------------------- #
# Crafty
# --------------------------------------------------------------------------- #


def test_crafty_temperature_notification() -> None:
    device, _ = _make(CraftyDevice)
    device._handle_temperature(MagicMock(), bytearray(b"\x46\x07"))  # 1862 -> 186.2
    assert device.state.current_temperature == 186.2


def test_crafty_battery_notification() -> None:
    device, _ = _make(CraftyDevice)
    device._handle_power(MagicMock(), bytearray(b"\x55\x00"))  # 85%
    assert device.state.battery_level == 85


async def test_crafty_poll_tolerates_missing_characteristics() -> None:
    # Only target temperature is readable; every other optional read is absent.
    reads = {c.CRAFTY_UUID_TARGET_TEMP: (1900).to_bytes(2, "little")}
    device, _ = _make(CraftyDevice, FakeClient(reads=reads))
    state = await device.async_poll()
    assert state.target_temperature == 190
    assert state.led_brightness is None
