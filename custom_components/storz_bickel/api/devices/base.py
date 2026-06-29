"""Abstract base class for Storz & Bickel BLE devices.

``SBDevice`` owns the BLE connection lifecycle (via ``bleak-retry-connector``),
exposes typed read/write helpers, manages notification subscriptions, and fans
state updates out to registered callbacks (the coordinator subscribes here to get
push updates). Concrete subclasses implement the per-device GATT protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from typing import TYPE_CHECKING

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from custom_components.storz_bickel.api.exceptions import (
    StorzBickelConnectionError,
    StorzBickelNotConnectedError,
)
from custom_components.storz_bickel.api.models import DeviceCapabilities, SBDeviceState
from custom_components.storz_bickel.const import LOGGER

if TYPE_CHECKING:
    from collections.abc import Callable

    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice

    from custom_components.storz_bickel.api.models import DeviceType


class SBDevice(ABC):
    """Base class implementing the BLE transport shared by all device families."""

    device_type: DeviceType
    capabilities: DeviceCapabilities = DeviceCapabilities()
    temp_min: float
    temp_max: float
    temp_step: float = 1.0

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the device with its discovered ``BLEDevice`` handle.

        Args:
            ble_device: The connectable ``BLEDevice`` resolved by Home Assistant's
                Bluetooth stack. Refresh it via :meth:`set_ble_device` before each
                reconnect so the latest advertisement path is used.
        """
        self._ble_device = ble_device
        self._client: BleakClientWithServiceCache | None = None
        self._connect_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._state = SBDeviceState()
        self._callbacks: list[Callable[[SBDeviceState], None]] = []
        self._notify_uuids: list[str] = []

    # --- Identity ---------------------------------------------------------- #

    @property
    def address(self) -> str:
        """Return the device's Bluetooth address."""
        return self._ble_device.address

    @property
    def name(self) -> str:
        """Return a human-readable name used for connection logging."""
        return self._ble_device.name or self.address

    @property
    def state(self) -> SBDeviceState:
        """Return the most recent device state snapshot."""
        return self._state

    @property
    def connected(self) -> bool:
        """Return whether an active BLE connection is currently held."""
        return self._client is not None and self._client.is_connected

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Update the cached ``BLEDevice`` handle (called before reconnecting)."""
        self._ble_device = ble_device

    # --- Push callbacks ---------------------------------------------------- #

    def register_callback(
        self, callback: Callable[[SBDeviceState], None]
    ) -> Callable[[], None]:
        """Register a listener for state updates.

        Args:
            callback: Invoked with the latest :class:`SBDeviceState` whenever new
                data arrives (via notification or poll).

        Returns:
            A function that unregisters the callback when called.
        """
        self._callbacks.append(callback)

        def _unregister() -> None:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

        return _unregister

    def _fire_callbacks(self) -> None:
        """Notify all registered listeners of the current state."""
        for callback in list(self._callbacks):
            callback(self._state)

    # --- Connection lifecycle --------------------------------------------- #

    async def async_connect(self) -> None:
        """Establish the BLE connection, read identity, and subscribe to updates.

        Raises:
            StorzBickelConnectionError: If the connection cannot be established.
        """
        async with self._connect_lock:
            if self.connected:
                return
            LOGGER.debug("Connecting to %s (%s)", self.name, self.address)
            try:
                self._client = await establish_connection(
                    BleakClientWithServiceCache,
                    self._ble_device,
                    self.name,
                    disconnected_callback=self._handle_disconnect,
                )
                await self._read_static_info()
                await self._subscribe()
                await self.async_poll()
            except (BleakError, TimeoutError) as err:
                await self._safe_disconnect()
                msg = f"Could not connect to {self.name}: {err}"
                raise StorzBickelConnectionError(msg) from err
            LOGGER.debug("Connected to %s", self.name)
            self._fire_callbacks()

    async def async_disconnect(self) -> None:
        """Disconnect from the device and clear the client handle."""
        async with self._connect_lock:
            await self._safe_disconnect()

    async def _safe_disconnect(self) -> None:
        """Disconnect without raising, tolerating an already-closed client."""
        client = self._client
        self._client = None
        if client is not None:
            try:
                await client.disconnect()
            except BleakError as err:  # pragma: no cover - best-effort cleanup
                LOGGER.debug("Error during disconnect from %s: %s", self.name, err)

    def _handle_disconnect(self, _client: BleakClientWithServiceCache) -> None:
        """Handle an unexpected disconnect reported by bleak."""
        LOGGER.debug("Device %s disconnected", self.name)
        self._client = None
        self._fire_callbacks()

    # --- GATT helpers ------------------------------------------------------ #

    def _require_client(self) -> BleakClientWithServiceCache:
        """Return the active client or raise if not connected."""
        if self._client is None or not self._client.is_connected:
            msg = f"Not connected to {self.name}"
            raise StorzBickelNotConnectedError(msg)
        return self._client

    async def _read(self, uuid: str) -> bytes:
        """Read raw bytes from a GATT characteristic."""
        return bytes(await self._require_client().read_gatt_char(uuid))

    async def _read_uint16(self, uuid: str) -> int | None:
        """Read a little-endian uint16 characteristic, or ``None`` if too short."""
        data = await self._read(uuid)
        if len(data) < 2:
            return None
        return int.from_bytes(data[:2], byteorder="little")

    async def _read_uint8(self, uuid: str) -> int | None:
        """Read a single-byte characteristic, or ``None`` if empty."""
        data = await self._read(uuid)
        return data[0] if data else None

    async def _read_string(self, uuid: str) -> str | None:
        """Read and decode a UTF-8 string characteristic."""
        data = await self._read(uuid)
        return data.decode("utf-8", errors="replace").strip() or None

    async def _try_read_uint16(self, uuid: str) -> int | None:
        """Read a uint16 characteristic, returning ``None`` if it is unavailable."""
        try:
            return await self._read_uint16(uuid)
        except BleakError:
            return None

    async def _try_read_string(self, uuid: str) -> str | None:
        """Read a string characteristic, returning ``None`` if it is unavailable."""
        try:
            return await self._read_string(uuid)
        except BleakError:
            return None

    async def _write(
        self, uuid: str, payload: bytes = b"", *, response: bool = False
    ) -> None:
        """Write bytes to a GATT characteristic."""
        async with self._write_lock:
            await self._require_client().write_gatt_char(uuid, payload, response=response)

    async def _start_notify(
        self, uuid: str, handler: Callable[[BleakGATTCharacteristic, bytearray], None]
    ) -> None:
        """Subscribe to notifications for a characteristic and track it."""
        await self._require_client().start_notify(uuid, handler)
        self._notify_uuids.append(uuid)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        """Clamp ``value`` into the inclusive ``[low, high]`` range."""
        return max(low, min(value, high))

    # --- Per-device protocol (implemented by subclasses) ------------------- #

    @abstractmethod
    async def _read_static_info(self) -> None:
        """Read static identity (serial, firmware) into the state once connected."""

    @abstractmethod
    async def _subscribe(self) -> None:
        """Subscribe to the device's notify characteristic(s) for push updates."""

    @abstractmethod
    async def async_poll(self) -> SBDeviceState:
        """Read polled values (e.g. current temperature) and return the new state."""

    @abstractmethod
    async def async_set_target_temperature(self, celsius: float) -> None:
        """Set the heater target temperature in degrees Celsius."""

    @abstractmethod
    async def async_set_heater(self, *, on: bool) -> None:
        """Turn the heater on or off."""

    # Optional controls: overridden by devices that advertise the capability. The
    # base implementations raise, but keep the full signatures so callers (and the
    # type checker) see a consistent interface across every device family.

    async def async_set_pump(self, *, on: bool) -> None:
        """Turn the pump on or off (Volcano only)."""
        raise self._unsupported("pump")

    async def async_set_vibration(self, *, on: bool) -> None:
        """Enable or disable vibration feedback."""
        raise self._unsupported("vibration")

    async def async_set_led_brightness(self, percent: int) -> None:
        """Set the LED/LCD brightness as a percentage (0-100)."""
        raise self._unsupported("led_brightness")

    async def async_set_auto_shutoff(self, *, on: bool) -> None:
        """Enable or disable the auto-shutoff timer."""
        raise self._unsupported("auto_shutoff")

    async def async_set_auto_shutoff_minutes(self, minutes: int) -> None:
        """Set the auto-shutoff duration in minutes."""
        raise self._unsupported("auto_shutoff")

    async def async_set_boost_temperature(self, celsius: float) -> None:
        """Set the boost target temperature (portable devices)."""
        raise self._unsupported("boost_temperature")

    def _unsupported(self, feature: str) -> StorzBickelConnectionError:
        """Return an error describing an unsupported feature for this device."""
        return StorzBickelConnectionError(
            f"{self.device_type} does not support {feature}"
        )
