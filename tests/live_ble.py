"""Standalone live BLE check against real Storz & Bickel hardware.

Run via ``script/test-live`` (host only) — **not** under pytest. It scans for a
nearby device, connects over BLE, reads its identity/state, and disconnects. It
performs **no writes**: the heater and pump are never actuated.

Why this is a plain script and not a pytest test
------------------------------------------------
The ``pytest-homeassistant-custom-component`` harness (which the rest of the suite
depends on to import the integration) patches ``platform.system()`` to ``"Linux"``
so Home Assistant tests run deterministically. Under that patch, ``bleak`` selects
the Linux BlueZ/dbus backend and cannot drive the real CoreBluetooth radio on a
macOS host. Running outside pytest keeps the real platform backend, so an actual
scan works. Importing the integration still needs the full HA stack, so this runs
in the normal project environment.

Exit codes: 0 = connected and read state (or cleanly skipped — no adapter/device),
1 = a device was found but the connect/read failed.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

# Make the repo root importable when invoked as ``python tests/live_ble.py``.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bleak import BleakScanner
from bleak.exc import BleakError

from custom_components.storz_bickel.api import (
    StorzBickelConnectionError,
    create_device,
    detect_device_type,
)

# How long to scan for an advertising Storz & Bickel device before giving up.
_SCAN_TIMEOUT_SECONDS = 10.0


async def _run() -> int:
    """Scan, connect, read identity/state, and disconnect. Return an exit code."""
    try:
        discovered = await BleakScanner.discover(
            timeout=_SCAN_TIMEOUT_SECONDS, return_adv=True
        )
    except (BleakError, OSError) as err:
        print(f"SKIP: no usable Bluetooth adapter for live scan: {err}")
        return 0

    match = None
    for ble_device, adv in discovered.values():
        device_type = detect_device_type(adv.local_name, adv.service_uuids)
        if device_type is not None:
            match = (device_type, ble_device)
            break

    if match is None:
        print(
            f"SKIP: no nearby Storz & Bickel device found "
            f"(scanned {_SCAN_TIMEOUT_SECONDS:.0f}s; power one on and stay in range)"
        )
        return 0

    device_type, ble_device = match
    print(
        f"Found {device_type} at {ble_device.address} ({ble_device.name}) — connecting..."
    )
    device = create_device(device_type, ble_device)
    try:
        await device.async_connect()
        if not device.connected:
            print("FAIL: async_connect() returned but the device is not connected")
            return 1

        state = device.state
        print(
            f"Connected. serial={state.serial_number!r} "
            f"firmware={state.firmware_version!r} "
            f"current_temp={state.current_temperature!r}"
        )
        if all(
            value is None
            for value in (
                state.serial_number,
                state.firmware_version,
                state.current_temperature,
            )
        ):
            print("FAIL: connected but read no identity/state")
            return 1

        print(f"PASS: live BLE connect + read succeeded for {device_type}")
        return 0
    except (BleakError, TimeoutError, StorzBickelConnectionError) as err:
        print(f"FAIL: could not connect/read {device_type}: {err}")
        return 1
    finally:
        await device.async_disconnect()


def main() -> int:
    """Entry point: run the async check and return its exit code."""
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
