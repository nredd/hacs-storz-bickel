"""Sensor entities exposing session history and derived statistics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import TemperatureConverter

from custom_components.storz_bickel.const import (
    CONF_TEMPERATURE_UNIT,
    DEFAULT_TEMPERATURE_UNIT,
    SESSION_DAILY_BUCKET_DAYS,
    SESSION_HISTORY_ATTRIBUTE_WINDOW_HOURS,
)
from custom_components.storz_bickel.entity import StorzBickelEntity

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime

    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from custom_components.storz_bickel.coordinator import (
        StorzBickelDataUpdateCoordinator,
    )
    from custom_components.storz_bickel.data import StorzBickelConfigEntry
    from custom_components.storz_bickel.session.tracker import SessionTracker


@dataclass(frozen=True, kw_only=True)
class StorzBickelSessionSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor derived from the device's session tracker."""

    value_fn: Callable[[SessionTracker], float | int | datetime | None]
    capability: str | None = None


SESSION_SENSORS: tuple[StorzBickelSessionSensorEntityDescription, ...] = (
    StorzBickelSessionSensorEntityDescription(
        key="last_session",
        translation_key="last_session",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda tracker: tracker.last_session_stop,
    ),
    StorzBickelSessionSensorEntityDescription(
        key="total_sessions",
        translation_key="total_sessions",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda tracker: len(tracker.sessions),
    ),
    StorzBickelSessionSensorEntityDescription(
        key="current_session_start",
        translation_key="current_session_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:timer-play-outline",
        value_fn=lambda tracker: tracker.current_session_start,
    ),
    StorzBickelSessionSensorEntityDescription(
        key="total_pump_time",
        translation_key="total_pump_time",
        capability="pump",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        suggested_display_precision=0,
        value_fn=lambda tracker: tracker.total_pump_seconds,
    ),
)


async def async_add_session_entities(
    entry: StorzBickelConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    """Set up all session-derived sensor entities for one config entry."""
    coordinator = entry.runtime_data.coordinator
    capabilities = coordinator.device.capabilities
    entities: list[SensorEntity] = [
        StorzBickelSessionSensor(coordinator, description)
        for description in SESSION_SENSORS
        if description.capability is None or getattr(capabilities, description.capability)
    ]
    entities.append(StorzBickelFavoriteTemperatureSensor(coordinator))
    entities.append(StorzBickelSessionHistorySensor(coordinator))
    async_add_entities(entities)


class StorzBickelSessionSensor(StorzBickelEntity, SensorEntity):
    """A sensor value derived from the device's session tracker."""

    entity_description: StorzBickelSessionSensorEntityDescription

    @property
    def available(self) -> bool:
        """Session data reflects stored history, not live device state."""
        return True

    @property
    def native_value(self) -> float | int | datetime | None:
        """Return the current derived value."""
        return self.entity_description.value_fn(self.coordinator.session_tracker)


class StorzBickelFavoriteTemperatureSensor(StorzBickelEntity, SensorEntity):
    """The mode of each session's modal setpoint, in the display unit.

    Deliberately has no ``device_class`` set: Home Assistant's sensor platform
    forces any ``SensorDeviceClass.TEMPERATURE`` entity to display in the
    system-wide temperature unit, which would override the per-entry
    ``CONF_TEMPERATURE_UNIT`` conversion done in :meth:`native_value` below
    (the same option the climate entity uses, independent of the system unit).
    """

    _attr_icon = "mdi:thermometer"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: StorzBickelDataUpdateCoordinator) -> None:
        """Initialize with the entry's configured display unit."""
        super().__init__(
            coordinator,
            SensorEntityDescription(
                key="favorite_temperature", translation_key="favorite_temperature"
            ),
        )
        self._attr_native_unit_of_measurement = coordinator.config_entry.options.get(
            CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT
        )

    @property
    def available(self) -> bool:
        """Favorite temperature reflects stored history, not live device state."""
        return True

    @property
    def native_value(self) -> float | None:
        """Return the favorite temperature converted to the display unit."""
        celsius = self.coordinator.session_tracker.favorite_temperature_celsius
        if celsius is None:
            return None
        return TemperatureConverter.convert(
            celsius, UnitOfTemperature.CELSIUS, self._attr_native_unit_of_measurement
        )


class StorzBickelSessionHistorySensor(StorzBickelEntity, SensorEntity):
    """Lifetime session count, with recent sessions exposed as attributes.

    The ``sessions`` attribute is the data source for the companion Lovelace
    card's live visualization: a plain JSON list of recent session records.
    """

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:history"

    def __init__(self, coordinator: StorzBickelDataUpdateCoordinator) -> None:
        """Initialize the session history sensor."""
        super().__init__(
            coordinator,
            SensorEntityDescription(
                key="session_history", translation_key="session_history"
            ),
        )

    @property
    def available(self) -> bool:
        """Session history reflects stored history, not live device state."""
        return True

    @property
    def native_value(self) -> int:
        """Return the lifetime session count."""
        return len(self.coordinator.session_tracker.sessions)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return recent sessions and a trailing daily-count breakdown.

        ``sessions`` is capped to a short rolling window for the card's live
        view; ``daily_counts`` instead buckets the tracker's full in-memory
        lifetime list (unbounded, see :class:`SessionStore`) by local date so
        a "sessions per day" chart isn't limited by the same window.
        """
        cutoff = dt_util.utcnow() - timedelta(
            hours=SESSION_HISTORY_ATTRIBUTE_WINDOW_HOURS
        )
        sessions = self.coordinator.session_tracker.sessions
        recent = [
            session.as_dict()
            for session in sessions
            if (stop := dt_util.parse_datetime(session.stop)) is not None
            and stop >= cutoff
        ]

        day_cutoff = dt_util.utcnow() - timedelta(days=SESSION_DAILY_BUCKET_DAYS)
        daily_counts: dict[str, int] = {}
        for session in sessions:
            start = dt_util.parse_datetime(session.start)
            if start is None or start < day_cutoff:
                continue
            day = dt_util.as_local(start).date().isoformat()
            daily_counts[day] = daily_counts.get(day, 0) + 1

        return {"sessions": recent, "daily_counts": daily_counts}
