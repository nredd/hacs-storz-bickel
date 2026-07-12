"""Constants for the Storz & Bickel integration."""

from __future__ import annotations

from logging import Logger, getLogger

from homeassistant.const import UnitOfTemperature

LOGGER: Logger = getLogger(__package__)

DOMAIN = "storz_bickel"
MANUFACTURER = "Storz & Bickel"
ATTRIBUTION = "Data provided by the Storz & Bickel device over Bluetooth"

# Config entry data keys.
CONF_DEVICE_TYPE = "device_type"

# Config entry option keys (per-device pump protections).
CONF_PUMP_FAILSAFE_ENABLED = "pump_failsafe_enabled"
CONF_PUMP_FAILSAFE_SECONDS = "pump_failsafe_seconds"
CONF_PUMP_COOLDOWN_ENABLED = "pump_cooldown_enabled"
CONF_PUMP_COOLDOWN_SECONDS = "pump_cooldown_seconds"

DEFAULT_PUMP_FAILSAFE_ENABLED = True
DEFAULT_PUMP_FAILSAFE_SECONDS = 45
DEFAULT_PUMP_COOLDOWN_ENABLED = True
DEFAULT_PUMP_COOLDOWN_SECONDS = 5

# Config entry option key for the climate entity's display unit (independent of
# the device's own on-screen unit and of Home Assistant's system-wide setting).
CONF_TEMPERATURE_UNIT = "temperature_unit"
DEFAULT_TEMPERATURE_UNIT = UnitOfTemperature.CELSIUS

# Config entry option key for the climate entity's target-temperature step,
# independent of any fixed per-device-type default (see api/devices/base.py).
CONF_TEMP_STEP = "temp_step"
DEFAULT_TEMP_STEP = 1.0

# Bounds how long a workflow will wait for a temperature rung to be reached
# before giving up (generous enough for a cold start to 170C, still bounds a
# stalled/disconnected device).
WORKFLOW_TEMPERATURE_WAIT_TIMEOUT_SECONDS = 600

# Entities are updated from a single coordinator; serialize platform updates.
PARALLEL_UPDATES = 0

# Active-connection poll cadence (seconds). Heat/pump state arrives via BLE
# notifications; the current temperature is read on this interval.
POLL_INTERVAL_SECONDS = 3

# Session tracking: a heater-on window (optionally spanning brief off gaps) that
# qualifies as a tracked "session" once it meets the minimum duration and, for
# pump-capable devices, has run the pump continuously for the qualifying window.
SESSION_MIN_DURATION_SECONDS = 120
SESSION_PUMP_QUALIFY_SECONDS = 5
SESSION_HEATER_OFF_TIMEOUT_SECONDS = 900
SESSION_SETPOINT_ROUND_NDIGITS = 0
SESSION_HISTORY_ATTRIBUTE_WINDOW_HOURS = 48
SESSION_DAILY_BUCKET_DAYS = 14
SESSION_STORAGE_VERSION = 1
SESSION_STORAGE_KEY_PREFIX = f"{DOMAIN}_sessions"
