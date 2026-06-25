"""Device-type detection from Bluetooth advertisement data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.storz_bickel.api import const as c
from custom_components.storz_bickel.api.models import DeviceType

if TYPE_CHECKING:
    from collections.abc import Iterable


def detect_device_type(
    name: str | None, service_uuids: Iterable[str]
) -> DeviceType | None:
    """Identify the Storz & Bickel device family from advertisement data.

    Detection prefers the advertised name (the only way to tell a Venty from a
    Veazy, which share a primary service UUID) and falls back to service UUIDs.

    Args:
        name: The advertised local name (e.g. ``"S&B VOLCANO H"``), if any.
        service_uuids: Advertised GATT service UUIDs.

    Returns:
        The matching :class:`DeviceType`, or ``None`` if it is not a recognized
        Storz & Bickel device.
    """
    uuids = {uuid.lower() for uuid in service_uuids}
    upper = (name or "").upper()

    if "VOLCANO" in upper or c.VOLCANO_SERVICE_DEVICE_STATE in uuids:
        return DeviceType.VOLCANO
    if "VEAZY" in upper:
        return DeviceType.VEAZY
    if "VENTY" in upper:
        return DeviceType.VENTY
    if "CRAFTY" in upper or c.CRAFTY_SERVICE_DATA in uuids:
        return DeviceType.CRAFTY
    if c.VENTY_SERVICE_PRIMARY in uuids:
        # Shared Venty/Veazy service with no distinguishing name: default to Venty.
        return DeviceType.VENTY
    return None
