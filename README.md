# Storz & Bickel for Home Assistant

A fully native Home Assistant integration for **Storz & Bickel Bluetooth vaporizers** —
control and monitor your device directly from Home Assistant over Bluetooth Low Energy.
No cloud, no companion app: 100% local.

Supported devices:

- **Volcano Hybrid** — fully validated against hardware
- **Venty**, **Veazy**, **Crafty / Crafty+** — community/reverse-engineered support, pending
  broader hardware validation

## Features

- **Heater** as a `climate` entity (heat/off + target temperature, live current temperature)
- **Pump** control (Volcano only)
- **Settings** (which appear depends on the model):
  - Display brightness (Volcano, Crafty)
  - Auto-shutoff timer (all), plus an on/off toggle (Volcano)
  - Boost temperature (Venty, Veazy, Crafty)
  - Vibration (Volcano, Venty, Veazy)
- **Telemetry & metadata** (device dependent): chamber temperature, battery level and charge time,
  total/heater runtime, hours/minutes of operation, serial number, firmware and Bluetooth firmware
  versions
- **Live state** via Bluetooth notifications (heating / pump), with automatic reconnect
- Local push — works great on a Raspberry Pi 5's built-in Bluetooth or via an ESPHome Bluetooth proxy

See [`docs/user/`](docs/user/GETTING_STARTED.md) for setup, the full per-model entity table, and
automation/dashboard examples.

## Requirements

- Home Assistant with a working Bluetooth adapter (e.g. Raspberry Pi 5 built-in Bluetooth) or an
  ESPHome Bluetooth proxy within range of the device.
- The device powered on and in range.

> **One connection at a time.** Storz & Bickel devices accept a single Bluetooth connection. While
> Home Assistant is connected, the Storz & Bickel phone/web app cannot connect to the device, and
> vice versa.

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS (category: _Integration_).
2. Install **Storz & Bickel**.
3. Restart Home Assistant.

### Manual

Copy `custom_components/storz_bickel` into your Home Assistant `config/custom_components/` directory
and restart.

## Setup

Your device is auto-discovered when it is powered on and in range — Home Assistant shows a
_Discovered_ notification you can configure in one click. You can also add it manually via
**Settings → Devices & Services → Add Integration → Storz & Bickel** and pick it from the list of
nearby devices.

## Development

This project uses the [Astral](https://astral.sh) toolchain (`uv`, `ruff`, `ty`); `pyproject.toml`
is the single source of truth for dependencies and tooling.

```bash
uv sync --locked             # set up the environment
uv run ruff format --check . # formatting
uv run ruff check .          # lint
uv run ty check              # type-check
uv run pytest                # tests
```

`script/smoke` runs the full check + test suite, exactly as CI does. CI runs `script/smoke`
**inside the project's devcontainer image** (via [`devcontainers/ci`](https://github.com/devcontainers/ci)),
so local development and CI share one environment. Open the repo in the devcontainer (VS Code /
Codespaces) to get the same toolchain.

### Live BLE check (host-only)

`tests/live_ble.py` is a real-hardware check: it scans for a nearby Storz & Bickel device, connects
over BLE, reads its identity/state, and disconnects (it never actuates the heater or pump). Run it
from your **host** machine (not the devcontainer — a Linux container on macOS has no path to the
host's Bluetooth radio):

```bash
script/test-live
```

It is a plain script, **not** part of the pytest suite, on purpose: the
`pytest-homeassistant-custom-component` harness patches the platform to Linux, which forces `bleak`
onto the BlueZ backend and breaks real CoreBluetooth scanning on macOS. Running standalone keeps the
real platform backend. `uv` auto-syncs the normal project env. With no device in range it exits 0
(clean skip); it exits non-zero only if a device is found but the connect/read fails. On macOS, grant
your terminal/IDE the Bluetooth permission on first run.

## Attribution

This integration was generated from the
[`jpawlowski/hacs.integration_blueprint`](https://github.com/jpawlowski/hacs.integration_blueprint)
template — a modernized Home Assistant integration blueprint, itself based on
[`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint).

The Volcano Hybrid BLE implementation is adapted from the MIT-licensed
[`Chuffnugget/volcano_integration`](https://github.com/Chuffnugget/volcano_integration), and the
multi-device GATT protocol details were referenced from
[`firsttris/reactive-volcano-app`](https://github.com/firsttris/reactive-volcano-app). See
[`NOTICE`](NOTICE) for details.

This project is not affiliated with or endorsed by Storz & Bickel GmbH.
