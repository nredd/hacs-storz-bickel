"""Data models shared across the Storz & Bickel API layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class DeviceType(StrEnum):
    """Supported Storz & Bickel device families."""

    VOLCANO = "volcano"
    VENTY = "venty"
    VEAZY = "veazy"
    CRAFTY = "crafty"

    @property
    def model_name(self) -> str:
        """Return the human-readable model name for device info."""
        return {
            DeviceType.VOLCANO: "Volcano Hybrid",
            DeviceType.VENTY: "Venty",
            DeviceType.VEAZY: "Veazy",
            DeviceType.CRAFTY: "Crafty",
        }[self]


@dataclass(slots=True)
class DeviceCapabilities:
    """Feature flags that drive which entities are created for a device.

    Each device family advertises a different subset of controls and telemetry;
    platforms consult these flags instead of hard-coding device-type checks.
    """

    heater: bool = True
    pump: bool = False
    vibration: bool = False
    auto_shutoff: bool = False
    auto_shutoff_toggle: bool = False
    led_brightness: bool = False
    boost_temperature: bool = False
    battery: bool = False
    hours_of_operation: bool = False
    heater_runtime: bool = False
    temperature_unit_display: bool = False


@dataclass(slots=True)
class SBDeviceState:
    """Snapshot of a device's readable state.

    All fields are optional: a given device family populates only the subset it
    exposes, and values stay ``None`` until first read. Temperatures are in
    degrees Celsius; runtime counters are in their native units.
    """

    # Live / control state
    current_temperature: float | None = None
    target_temperature: float | None = None
    boost_temperature: float | None = None
    heater_on: bool | None = None
    pump_on: bool | None = None
    vibration: bool | None = None
    led_brightness: int | None = None
    auto_shutoff_enabled: bool | None = None
    auto_shutoff_minutes: int | None = None
    fahrenheit: bool | None = None

    # Telemetry
    battery_level: int | None = None
    hours_of_operation: int | None = None
    minutes_of_operation: int | None = None
    heater_runtime_minutes: int | None = None
    battery_charge_time_minutes: int | None = None

    # Static identity
    serial_number: str | None = None
    firmware_version: str | None = None
    ble_firmware_version: str | None = None

    @property
    def total_runtime_hours(self) -> float | None:
        """Return lifetime heating runtime in hours, combining hours and minutes."""
        if self.hours_of_operation is None:
            return None
        minutes = self.minutes_of_operation or 0
        return round(self.hours_of_operation + minutes / 60, 2)


@dataclass(slots=True)
class DeviceInfo:
    """Static device identity gathered once after connecting."""

    serial_number: str | None = None
    firmware_version: str | None = None
    ble_firmware_version: str | None = None
    extras: dict[str, str] = field(default_factory=dict)
