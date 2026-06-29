# Configuration Reference

The Storz & Bickel integration is configured **entirely through the UI over Bluetooth**. There is
**no YAML configuration, no options to set, and no credentials** — once a device is added (see
[GETTING_STARTED.md](GETTING_STARTED.md)), the right entities are created automatically based on the
model. This page documents what those entities are and how to tailor them.

## How configuration works

- **Setup is Bluetooth-only.** The device is auto-discovered or picked from a list of nearby
  devices; there is nothing to type in. The device's BLE address is its unique ID.
- **No reconfigure / options flow.** There are no host, port, API key, scan-interval, or SSL
  settings to change. If a device's address changes, remove and re-add it.
- **Live state is push-based.** Heating and pump state arrive via Bluetooth notifications. The
  current chamber temperature is polled roughly every 3 seconds while connected.
- **Availability follows the connection.** Entities are available only while Home Assistant holds a
  live BLE connection. Remember that **only one connection is allowed at a time** — the official app
  must be disconnected.

## Entities by model

Which entities are created depends on what your model exposes. ✓ = created, — = not applicable to
that model.

| Entity (suffix) | Volcano | Venty | Veazy | Crafty |
| --- | :---: | :---: | :---: | :---: |
| `climate` — Heater (heat/off + target temp) | ✓ | ✓ | ✓ | ✓ |
| `switch` — Heater | ✓ | ✓ | ✓ | ✓ |
| `switch` — Pump | ✓ | — | — | — |
| `switch` — Vibration | ✓ | ✓ | ✓ | — |
| `switch` — Auto shutoff (on/off toggle) | ✓ | — | — | — |
| `number` — Display brightness (0–100 %) | ✓ | — | — | ✓ |
| `number` — Auto shutoff timer (0–720 min) | ✓ | ✓ | ✓ | ✓ |
| `number` — Boost temperature (0–30 °C) | — | ✓ | ✓ | ✓ |
| `binary_sensor` — Heating | ✓ | ✓ | ✓ | ✓ |
| `binary_sensor` — Pump | ✓ | — | — | — |
| `binary_sensor` — Connection (diagnostic) | ✓ | ✓ | ✓ | ✓ |
| `sensor` — Temperature | ✓ | ✓ | ✓ | ✓ |
| `sensor` — Battery | — | ✓ | ✓ | ✓ |
| `sensor` — Total runtime | ✓ | — | — | ✓ |
| `sensor` — Hours of operation † | ✓ | — | — | ✓ |
| `sensor` — Minutes of operation † | ✓ | — | — | ✓ |
| `sensor` — Heater runtime | — | ✓ | ✓ | — |
| `sensor` — Battery charge time † | — | ✓ | ✓ | — |
| `sensor` — Serial number † | ✓ | ✓ | ✓ | ‡ |
| `sensor` — Firmware version † | ✓ | ✓ | ✓ | ✓ |
| `sensor` — Bluetooth firmware version † | ✓ | ✓ | ✓ | ✓ |

† **Diagnostic, disabled by default.** Enable from the device page if you want it (see below).
‡ The serial-number sensor exists on the Crafty but stays empty — the Crafty does not expose a
serial over BLE.

### Heater temperature range

| Model | Min | Max | Step |
| --- | --- | --- | --- |
| Volcano Hybrid | 40 °C | 230 °C | 1 °C |
| Venty / Veazy / Crafty | 40 °C | 210 °C | 1 °C |

## Customizing entities

### Enable diagnostic sensors

Serial number, firmware versions, and the hours/minutes/charge-time counters are created as
**diagnostic** entities and are **disabled by default** to keep your entity list tidy. To turn one
on:

1. Open **Settings → Devices & Services → Storz & Bickel** and click your device.
2. Find the entity (disabled entities are listed under the device), open it, and toggle
   **Enabled**.

### Rename, hide, or assign areas

Use the entity settings dialog (gear icon on any entity) to override the friendly name, hide it from
the dashboard, or assign it to an area. These are standard Home Assistant entity customizations and
do not affect the integration.

## Notes & limitations

- **No services.** This integration does not register custom services; control everything through
  the standard `climate`, `switch`, and `number` entities (and the actions Home Assistant provides
  for them, e.g. `climate.set_temperature`).
- **One device per physical unit.** Each vaporizer is a single config entry keyed on its Bluetooth
  address; there is nothing to configure for "multiple instances" beyond adding each device.
- **Reverse-engineered models.** Venty, Veazy, and Crafty support is community-contributed and
  pending broader hardware validation; some values may be missing or imprecise on those models.

See [EXAMPLES.md](EXAMPLES.md) for automations and dashboard cards built on these entities.
