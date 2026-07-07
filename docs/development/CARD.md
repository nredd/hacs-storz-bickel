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

Bun is pinned in `card/.bun-version` (used by `oven-sh/setup-bun` in CI) so the committed bundle is
reproducible. The build sets `NODE_ENV=production` to select Lit's production export condition.

## Development workflow

```bash
script/card             # bun install + build the bundle into www/
script/card-lint        # Biome, fix mode
script/card-lint-check  # Biome, CI mode (no writes)
script/card-type-check  # strict tsc
script/card-test        # bun test --coverage
script/card-check       # the full gate, exactly as CI runs it
```

**The bundle must be rebuilt and committed with any `card/src` change.** CI's `card` job rebuilds
and fails on `git diff` drift in `www/`. `script/check` runs `script/card-check` automatically when
Bun is available (and skips it otherwise, so Python-only environments still pass).

## Architecture notes

- **Device-based config.** The card takes a device registry id, not a pile of entity ids. Entity
  ids are derived in `card/src/entities.ts` from `hass.entities` by matching
  `platform === "storz_bickel"` and each entry's `translation_key` (the integration sets it equal
  to the entity description key). This survives entity renames and doubles as capability
  detection: no `pump` entity → no pump bar (Venty/Crafty), no `battery` sensor → no battery chip
  (Volcano).
- **Single source of truth for heat.** The heat pill drives the `climate` entity
  (`set_hvac_mode`), never the parallel heater switch.
- **Optimistic steppers.** The dial's −/+ taps update a pending target immediately and debounce
  ~500 ms before calling `climate.set_temperature`.
- **Pump safety stays server-side.** The card just toggles the pump switch; failsafe/cooldown
  enforcement lives in the integration's pump guard.
- **No HA frontend imports.** The card hand-rolls the minimal `hass` typings it needs
  (`card/src/types.ts`) and uses native elements (`<details>`, `<input type="range">`) styled with
  HA theme variables, so it has zero runtime dependencies beyond Lit and works in happy-dom tests.
