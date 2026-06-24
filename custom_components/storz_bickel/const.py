"""Constants for the Storz & Bickel integration."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "storz_bickel"
MANUFACTURER = "Storz & Bickel"
ATTRIBUTION = "Data provided by the Storz & Bickel device over Bluetooth"

# Config entry data keys.
CONF_DEVICE_TYPE = "device_type"

# Entities are updated from a single coordinator; serialize platform updates.
PARALLEL_UPDATES = 0

# Active-connection poll cadence (seconds). Heat/pump state arrives via BLE
# notifications; the current temperature is read on this interval.
POLL_INTERVAL_SECONDS = 3
