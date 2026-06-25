"""Opt-in live BLE test against real Storz & Bickel hardware.

Unlike the rest of the suite (which drives a fake client and never touches a real
radio), this test actually scans for a nearby device, connects over BLE, reads its
identity/state, and disconnects. It performs **no writes** — the heater and pump are
never actuated.

It is double-guarded so the default suite and CI stay hermetic:

* Static opt-in: skipped unless ``SB_LIVE_BLE`` is set in the environment.
* Runtime skips: if no Bluetooth adapter is usable, or no Storz & Bickel device is
  advertising in range, the test *skips* (it does not fail).

This must run on the **host** (e.g. macOS, where bleak uses CoreBluetooth), not inside
the devcontainer — a Linux Docker container on macOS has no path to the Mac's Bluetooth
radio. Use ``script/test-live`` to run it with the slim ``live`` dependency group.
"""

from __future__ import annotations

import os

from bleak import BleakScanner
from bleak.exc import BleakError
import pytest

from custom_components.storz_bickel.api import create_device, detect_device_type

# Apply the `live` marker (for `-m live` selection) and the opt-in guard to everything
# in this module. Without SB_LIVE_BLE set, the test never runs — keeping `uv run pytest`
# and CI fully hermetic.
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("SB_LIVE_BLE"),
        reason="live BLE test is opt-in; set SB_LIVE_BLE=1 and run on the host",
    ),
]

# How long to scan for an advertising Storz & Bickel device before giving up.
_SCAN_TIMEOUT_SECONDS = 10.0


async def test_live_scan_connect_and_read() -> None:
    """Scan, detect, connect to a real S&B device, and read its identity/state."""
    try:
        discovered = await BleakScanner.discover(
            timeout=_SCAN_TIMEOUT_SECONDS, return_adv=True
        )
    except (BleakError, OSError) as err:
        pytest.skip(f"no usable Bluetooth adapter for live scan: {err}")

    # Pick the first advertisement that classifies as a Storz & Bickel device.
    match = None
    for ble_device, adv in discovered.values():
        device_type = detect_device_type(adv.local_name, adv.service_uuids)
        if device_type is not None:
            match = (device_type, ble_device)
            break

    if match is None:
        pytest.skip(
            "no nearby Storz & Bickel device found "
            f"(scanned {_SCAN_TIMEOUT_SECONDS:.0f}s; power one on and stay in range)"
        )

    device_type, ble_device = match
    device = create_device(device_type, ble_device)

    try:
        await device.async_connect()
        assert device.connected, "async_connect() returned but device is not connected"

        # At least one real value must have come back from the device, proving the
        # GATT read path works end-to-end (static info read on connect + initial poll).
        state = device.state
        assert any(
            value is not None
            for value in (
                state.serial_number,
                state.firmware_version,
                state.current_temperature,
            )
        ), f"connected to {device_type} but read no identity/state: {state}"
    finally:
        await device.async_disconnect()
