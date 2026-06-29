# Architectural and Design Decisions

This document records significant architectural and design decisions made during the development of this integration.

## Format

Each decision is documented with:

- **Date:** When the decision was made
- **Context:** Why this decision was necessary
- **Decision:** What was decided
- **Rationale:** Why this approach was chosen
- **Consequences:** Expected impacts and trade-offs

---

## Decision Log

### Use DataUpdateCoordinator for All Data Fetching

**Date:** 2025-11-29 (Template initialization)

**Context:** The integration needs to fetch data from an external API and share it with multiple entities. Home Assistant provides several patterns for this.

**Decision:** Use `DataUpdateCoordinator` from `homeassistant.helpers.update_coordinator` as the central data management component.

**Rationale:**

- Provides built-in support for update intervals and error handling
- Automatic retry with exponential backoff
- Shared data access prevents duplicate API calls
- Standard pattern recommended by Home Assistant
- Entities automatically become unavailable when coordinator fails

**Consequences:**

- All entities must inherit from `CoordinatorEntity`
- Single update interval applies to all entities
- Data is fetched even if no entities are enabled
- Coordinator manages entity lifecycle and availability

---

### Separate API Client from Coordinator

**Date:** 2025-11-29 (Template initialization)

**Context:** The coordinator needs to fetch data, but business logic should be separated from data transport.

**Decision:** Implement BLE communication in a dedicated `api/` layer (per-device adapters under
`api/devices/`), with the coordinator only orchestrating updates.

**Rationale:**

- Separation of concerns: transport vs. orchestration
- Easier to test API client in isolation
- Simpler to swap API implementation if needed
- Clearer error handling boundaries

**Consequences:**

- Additional abstraction layer
- Coordinator depends on API client
- API client raises custom exceptions for error translation

---

### Platform-Specific Directories

**Date:** 2025-11-29 (Template initialization)

**Context:** Integration supports multiple platforms (sensor, binary_sensor, switch, etc.).

**Decision:** Each platform gets its own directory with individual entity files.

**Rationale:**

- Clear organization as integration grows
- Easier to find specific entity implementations
- Supports multiple entities per platform cleanly
- Follows Home Assistant Core pattern

**Consequences:**

- More files/directories than single-file approach
- Platform `__init__.py` must import and register entities
- Slightly more initial setup overhead

---

### EntityDescription for Static Metadata

**Date:** 2025-11-29 (Template initialization)

**Context:** Entities have static metadata (name, icon, device class) that doesn't change.

**Decision:** Use `EntityDescription` dataclasses to define static entity metadata.

**Rationale:**

- Declarative and easy to read
- Type-safe with dataclasses
- Recommended Home Assistant pattern
- Separates static configuration from dynamic behavior

**Consequences:**

- Each entity type needs an EntityDescription
- Dynamic entities need custom handling
- Static and dynamic properties clearly separated

---

### Capability-Gated Entities Instead of Per-Device Subclasses

**Date:** 2026-06 (Storz & Bickel integration)

**Context:** The Volcano, Venty, Veazy, and Crafty expose overlapping but different controls and
telemetry. Hard-coding device-type checks in every platform would scatter that knowledge and make
new models painful to add.

**Decision:** Each device adapter declares a `DeviceCapabilities` flag set (`api/models.py`).
Platforms iterate their `EntityDescription`s and create only the entities whose `capability` flag is
set for the connected device (e.g. `sensor/__init__.py` filters on `getattr(capabilities, ...)`).

**Rationale:**

- One source of truth for what a model supports
- Adding a model is mostly declaring its capabilities
- Platforms stay free of device-type `if`-ladders

**Consequences:**

- Entity descriptions carry a `capability` field
- Capabilities must be kept accurate per device, since they drive the entity list
- Some entities (e.g. serial number) are always created but may stay empty if a model doesn't report
  the value over BLE

---

### Push via BLE Notifications with Automatic Reconnect

**Date:** 2026-06 (Storz & Bickel integration)

**Context:** The device communicates over Bluetooth Low Energy and pushes state changes (heating,
pump) as GATT notifications. Connections can drop when the device moves out of range or the official
app grabs the single allowed connection.

**Decision:** Run as `iot_class: local_push` — subscribe to BLE notifications for live state and poll
only the current temperature on a short interval. Use `bleak-retry-connector` for resilient
connect/reconnect, and tie entity availability to the live connection.

**Rationale:**

- Real-time heating/pump state without aggressive polling
- Robust against the frequent, expected BLE disconnects
- Honest availability: entities go unavailable when the link is down

**Consequences:**

- Entities are unavailable without a live connection (single-connection constraint applies)
- Reconnect/backoff logic must be maintained in the API layer

---

### Device-Type Detection at the Config Flow

**Date:** 2026-06 (Storz & Bickel integration)

**Context:** Setup is Bluetooth-only; the correct adapter and capabilities must be chosen from the
advertisement, with no user input.

**Decision:** Detect the model from the BLE local name / service UUID during discovery and the
config flow, keying the config entry on the device's Bluetooth address.

**Rationale:**

- Zero-configuration setup (no host/port/credentials)
- Address-based unique ID is stable and avoids duplicates

**Consequences:**

- New models need matchers in `manifest.json` and a detection branch
- If a device's address changes, it must be removed and re-added

---

## Future Considerations

### State Restoration

**Status:** Not yet implemented

Consider implementing state restoration for switches and configurable settings to maintain state across Home Assistant restarts when the external device is unavailable.

### Multi-Device Support

**Status:** Not yet implemented

Current architecture assumes single device per config entry. If multi-device support is needed, coordinator data structure will need redesign to map device ID → data.

### Multi-Model Validation

**Status:** Volcano validated; Venty / Veazy / Crafty pending

Venty, Veazy, and Crafty support is reverse-engineered and pending broader hardware validation.
GATT UUIDs and capability flags for those models may need correction as real-hardware reports come
in.

---

## Decision Review

These decisions should be reviewed periodically (suggested: quarterly or when major features are added) to ensure they still serve the integration's needs.
