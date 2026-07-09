"""Unit tests for ``SBDevice.async_connect``'s stale-GATT-cache retry behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from bleak.exc import BleakCharacteristicNotFoundError, BleakError
import pytest

from custom_components.storz_bickel.api.devices.base import SBDevice
from custom_components.storz_bickel.api.exceptions import StorzBickelConnectionError
from custom_components.storz_bickel.api.models import DeviceType, SBDeviceState

_SERIAL_UUID = "10100008-5354-4f52-5a26-4249434b454c"

ESTABLISH_CONNECTION = (
    "custom_components.storz_bickel.api.devices.base.establish_connection"
)


class _MinimalDevice(SBDevice):
    """The smallest concrete ``SBDevice`` needed to exercise ``async_connect``."""

    device_type = DeviceType.VOLCANO
    temp_min = 40.0
    temp_max = 230.0

    async def _read_static_info(self) -> None:
        self._state.serial_number = await self._read_string(_SERIAL_UUID)

    async def _subscribe(self) -> None:
        return

    async def async_poll(self) -> SBDeviceState:
        return self._state

    async def async_set_target_temperature(self, celsius: float) -> None:
        _ = celsius

    async def async_set_heater(self, *, on: bool) -> None:
        _ = on


class _FakeClient:
    """A fake bleak client whose ``read_gatt_char`` can be scripted per-call."""

    def __init__(self, *, fail_reads: int) -> None:
        self.is_connected = True
        self._fail_reads = fail_reads
        self.clear_cache = AsyncMock()
        self.disconnect = AsyncMock()

    async def read_gatt_char(self, uuid: str) -> bytes:
        if self._fail_reads > 0:
            self._fail_reads -= 1
            raise BleakCharacteristicNotFoundError(uuid)
        return b"SN123"

    async def start_notify(
        self, uuid: str, handler: object
    ) -> None:  # pragma: no cover - unused here
        _ = (uuid, handler)


def _make_device() -> _MinimalDevice:
    ble = MagicMock()
    ble.address = "AA:BB:CC:DD:EE:FF"
    ble.name = "Volcano Test"
    return _MinimalDevice(ble)


async def test_async_connect_retries_once_on_stale_cache() -> None:
    """A missing characteristic triggers a cache clear and a fresh-discovery retry."""
    device = _make_device()
    stale_client = _FakeClient(fail_reads=1)
    fresh_client = _FakeClient(fail_reads=0)
    clients = iter([stale_client, fresh_client])

    async def _fake_establish_connection(
        *_args: object, **_kwargs: object
    ) -> _FakeClient:
        return next(clients)

    with patch(
        ESTABLISH_CONNECTION, side_effect=_fake_establish_connection
    ) as mock_connect:
        await device.async_connect()

    assert device.state.serial_number == "SN123"
    stale_client.clear_cache.assert_awaited_once()
    assert mock_connect.call_count == 2
    assert mock_connect.call_args_list[0].kwargs["use_services_cache"] is True
    assert mock_connect.call_args_list[1].kwargs["use_services_cache"] is False


async def test_async_connect_gives_up_after_second_stale_cache_failure() -> None:
    """If the retry also hits a missing characteristic, surface a connection error."""
    device = _make_device()
    clients = iter([_FakeClient(fail_reads=1), _FakeClient(fail_reads=1)])

    async def _fake_establish_connection(
        *_args: object, **_kwargs: object
    ) -> _FakeClient:
        return next(clients)

    with (
        patch(
            ESTABLISH_CONNECTION, side_effect=_fake_establish_connection
        ) as mock_connect,
        pytest.raises(StorzBickelConnectionError),
    ):
        await device.async_connect()

    assert mock_connect.call_count == 2


async def test_async_connect_does_not_retry_other_bleak_errors() -> None:
    """A non-characteristic-not-found ``BleakError`` fails after a single attempt."""
    device = _make_device()

    class _BrokenClient(_FakeClient):
        async def read_gatt_char(self, uuid: str) -> bytes:
            _ = uuid
            msg = "device disconnected"
            raise BleakError(msg)

    broken_client = _BrokenClient(fail_reads=0)

    async def _fake_establish_connection(
        *_args: object, **_kwargs: object
    ) -> _FakeClient:
        return broken_client

    with (
        patch(
            ESTABLISH_CONNECTION, side_effect=_fake_establish_connection
        ) as mock_connect,
        pytest.raises(StorzBickelConnectionError),
    ):
        await device.async_connect()

    assert mock_connect.call_count == 1
