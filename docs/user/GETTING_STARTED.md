# Getting Started

This guide walks you through installing the **Storz & Bickel** integration and adding your
vaporizer to Home Assistant. The integration talks to the device directly over **Bluetooth Low
Energy (BLE)** — there is no cloud account, no companion app, and nothing to configure with a
host, port, or API key.

## Requirements

- **Home Assistant 2026.6.0 or newer.**
- **A working Bluetooth adapter within range of the device.** This can be:
  - Home Assistant's built-in Bluetooth (e.g. a Raspberry Pi 5), or
  - An [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy.html) placed near the
    device.
- The device **powered on and in range**.
- [HACS](https://hacs.xyz/) installed (recommended), or the ability to copy files manually.

> **One connection at a time.** Storz & Bickel devices accept a single Bluetooth connection. While
> Home Assistant is connected, the official Storz & Bickel phone/web app cannot connect to the
> device, and vice versa. Disconnect the app before adding the device to Home Assistant.

## Supported devices

| Device | Status |
| --- | --- |
| **Volcano Hybrid** | Fully validated against hardware |
| **Venty** | Community / reverse-engineered, pending broader validation |
| **Veazy** | Community / reverse-engineered, pending broader validation |
| **Crafty / Crafty+** | Community / reverse-engineered, pending broader validation |

## Installation

### HACS (recommended)

1. In Home Assistant, open **HACS**.
2. Open the three-dot menu → **Custom repositories**.
3. Add `https://github.com/nredd/hacs-storz-bickel` with category **Integration**.
4. Search for **Storz & Bickel** and install it.
5. **Restart Home Assistant.**

### Manual

1. Copy the `custom_components/storz_bickel` directory from this repository into your Home Assistant
   `config/custom_components/` directory.
2. **Restart Home Assistant.**

## Adding your device

Because the integration uses Bluetooth, your device is discovered automatically — you do **not**
enter any connection details.

### Automatic discovery (easiest)

1. Power on the device and make sure it is in range and **not** connected to the Storz & Bickel app.
2. Home Assistant shows a **Discovered** notification under
   **Settings → Devices & Services**.
3. Click **Configure**, confirm the prompt, and the device is added.

### Manual add

If the device isn't auto-discovered:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Storz & Bickel**.
3. Pick your device from the list of nearby Bluetooth devices.

There are no further questions — no host, port, username, API key, or update interval. The device's
Bluetooth address is used as its unique identifier.

## What you get

After setup, a single device is created with entities scoped to your model's capabilities. The
headline entity is the heater, exposed as a `climate` entity:

- **Heater** (`climate`) — heat/off and target temperature, with the live chamber temperature.
- **Switches** — heater, and (model dependent) pump, vibration, and an auto-shutoff toggle.
- **Numbers** — (model dependent) display brightness, auto-shutoff timer, boost temperature.
- **Sensors** — chamber temperature plus (model dependent) battery, runtime counters, serial number,
  and firmware versions. Several metadata sensors are **diagnostic and disabled by default** — enable
  them from the device page if you want them.
- **Binary sensors** — heating, pump (Volcano), and a connectivity sensor.

For the exact per-model entity table and how to enable diagnostic entities, see
[CONFIGURATION.md](CONFIGURATION.md). For automations and dashboard cards, see
[EXAMPLES.md](EXAMPLES.md).

> Entity IDs are derived from your device's Bluetooth name, e.g. `climate.volcano`,
> `sensor.volcano_temperature`. Check **Developer Tools → States** to see the exact IDs on your
> system; the examples in these docs use a `volcano` prefix as a placeholder.

## Troubleshooting

- **Device isn't discovered.** Confirm it's powered on, in range, and not connected to the Storz &
  Bickel app. Verify Home Assistant has a working Bluetooth adapter under
  **Settings → Devices & Services → Bluetooth**, or that an ESPHome Bluetooth proxy is online and
  near the device.
- **Entities show as unavailable.** The integration requires a live BLE connection. Range, a busy
  Bluetooth adapter, or the official app holding the connection can all cause drops; the integration
  reconnects automatically once the device is reachable again.
- **Enable debug logging.** Add the following to `configuration.yaml` and restart:

  ```yaml
  logger:
    default: info
    logs:
      custom_components.storz_bickel: debug
  ```

- **Still stuck?** Open an issue at
  <https://github.com/nredd/hacs-storz-bickel/issues> with your model, Home Assistant version, and
  debug logs.
