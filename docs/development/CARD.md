# Companion Lovelace card

The integration bundles a custom dashboard card (`custom:storz-bickel-card`). This page covers how
it is built, served, and tested. For user-facing configuration, see the README's
[Companion Lovelace card](../../README.md#companion-lovelace-card) section.

## How the card ships

HACS installs integration-category repositories by copying `custom_components/storz_bickel/`
verbatim, so the card's built bundle is **committed** to the repo at:

```text
custom_components/storz_bickel/www/storz-bickel-card.js
```

On setup, `async_setup` in `custom_components/storz_bickel/__init__.py`:

1. serves the bundle via `hass.http.async_register_static_paths` at
   `/storz_bickel/storz-bickel-card.js`, and
2. injects it into the frontend with `frontend.add_extra_js_url`, using
   `?v=<manifest version>` as a cache-buster so browsers pick up new releases without a hard
   refresh.

`async_setup` runs once per Home Assistant boot regardless of how many devices are configured, so
the resource is never registered twice. Users need no dashboard resource configuration at all.

## Toolchain

The card lives in `card/` and is TypeScript + [Lit](https://lit.dev), with a deliberately small
toolchain — the TypeScript analogue of the Python side's `uv`/`ruff`/`ty`:

| Concern        | Tool                                       |
| -------------- | ------------------------------------------ |
| Install        | `bun install` (lockfile: `bun.lock`)       |
| Bundle         | `bun build` (single minified ES module)    |
| Tests          | `bun test` (Jest-compatible) + happy-dom   |
| Lint + format  | Biome (`biome ci` / `biome check --write`) |
| Types          | strict `tsc --noEmit`                      |

Bun is pinned in `card/.bun-version` (kept in sync with the bun feature version in
`.devcontainer/devcontainer.json`, which is what CI's devcontainer-based `Smoke` job uses) so the
committed bundle is reproducible. The build sets `NODE_ENV=production` to select Lit's production
export condition.

## Development workflow

```bash
script/card             # bun install + build the bundle into www/
script/card-lint        # Biome, fix mode
script/card-lint-check  # Biome, CI mode (no writes)
script/card-type-check  # strict tsc
script/card-test        # bun test --coverage
script/card-check       # the full gate, exactly as CI runs it
```

**The bundle must be rebuilt and committed with any `card/src` change.** CI's `Smoke` job (via
`script/smoke` → `script/card-check`) rebuilds and fails on `git diff` drift in `www/`.
`script/check` runs `script/card-check` automatically when
Bun is available (and skips it otherwise, so Python-only environments still pass).

## Architecture notes

- **Device-based config.** The card takes a device registry id, not a pile of entity ids. Entity
  ids are derived in `card/src/entities.ts` from `hass.entities` by matching
  `platform === "storz_bickel"` and each entry's `translation_key` (the integration sets it equal
  to the entity description key). This survives entity renames and doubles as capability
  detection: no `pump` entity → no AIR toggle (Venty/Crafty), no `battery` sensor → no battery
  chip (Volcano).
- **Single source of truth for heat.** The HEAT toggle drives the `climate` entity
  (`set_hvac_mode`), never the parallel heater switch.
- **Optimistic steppers and dial drags.** The ± stepper and dragging the dial update a pending
  target immediately and debounce ~500 ms before calling `climate.set_temperature`.
- **Pump safety stays server-side.** The card just toggles the pump switch; failsafe/cooldown
  enforcement lives in the integration's pump guard. The pump failsafe/cooldown *duration*
  dropdowns in the device-info panel write to the config entry's options (`number.set_value` on an
  option-backed number entity), which reloads the entry — the same mechanism the options flow
  itself uses. This is a real, if infrequent, UX cost (a BLE reconnect per change) that's
  documented at the entity level (`custom_components/storz_bickel/number/__init__.py`).
- **No HA frontend imports.** The card hand-rolls the minimal `hass` typings it needs
  (`card/src/types.ts`) and uses native elements (`<details>`, `<input type="range">`, `<select>`)
  styled with HA theme variables, so it has zero runtime dependencies beyond Lit and works in
  happy-dom tests.
- **Self-registering subcomponents.** Each subcomponent module (`dial.ts`, `seven-segment.ts`,
  `history-chart.ts`, `sessions-chart.ts`) calls `customElements.define` for its own tag at the
  bottom of the file (guarded by `customElements.get`), so importing a subcomponent directly (as
  the tests do) is enough to register it — no central registry.
- **Dashboard layout is a literal port, not a redesign.** The two-column layout (readout, dial,
  stepper, HEAT/AIR on the left; session/history/sessions/device-info panels on the right) and the
  dial's rotating-knob mechanism were ported pixel-for-pixel from a design mockup rather than
  reinterpreted — see the geometry comments at the top of `card/src/dial.ts`. It reflows to a
  single column under a `@container` query for narrow dashboard slots.
- **No external fonts or charting libraries.** The seven-segment readout and both charts
  (`history-chart.ts`, `sessions-chart.ts`) are hand-built with CSS and SVG, matching the existing
  dial's approach, so the card stays a single self-contained bundle with no CDN font/script
  dependency (important for HA installs without outbound internet access).
- **Temperature history has no dedicated backend entity.** `history-chart.ts` queries HA's
  `history/period` REST API directly against the `temperature` sensor (already
  `state_class: measurement`, so it's recorder/LTS-eligible out of the box) instead of requiring a
  new integration-side sensor.
- **Sessions-per-day comes from `session_history`'s `daily_counts` attribute** (added alongside
  the existing 48h `sessions` attribute — see `custom_components/storz_bickel/session/entities.py`),
  bucketed from the tracker's full in-memory lifetime session list, not just the short live-view
  window.
