"""Exception hierarchy for the Storz & Bickel BLE API.

These exceptions wrap the lower-level ``bleak`` errors so that the coordinator can
map them onto Home Assistant's ``ConfigEntryNotReady`` / ``UpdateFailed`` flow
without leaking transport-specific details into the rest of the integration.
"""

from __future__ import annotations


class StorzBickelError(Exception):
    """Base error for all Storz & Bickel API failures."""


class StorzBickelConnectionError(StorzBickelError):
    """Raised when establishing or maintaining the BLE connection fails."""


class StorzBickelNotConnectedError(StorzBickelError):
    """Raised when an operation is attempted while not connected to the device."""


class StorzBickelCharacteristicError(StorzBickelError):
    """Raised when a required GATT characteristic is missing or unreadable."""
