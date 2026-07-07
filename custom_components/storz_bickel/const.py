"""Constants for the Storz & Bickel integration."""

from __future__ import annotations

from logging import Logger, getLogger

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

# Bundled Lovelace card, served by the integration and injected into the
# frontend on setup (see async_setup in __init__.py).
CARD_FILENAME = "storz-bickel-card.js"
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"

# Entities are updated from a single coordinator; serialize platform updates.
PARALLEL_UPDATES = 0

# Active-connection poll cadence (seconds). Heat/pump state arrives via BLE
# notifications; the current temperature is read on this interval.
POLL_INTERVAL_SECONDS = 3
