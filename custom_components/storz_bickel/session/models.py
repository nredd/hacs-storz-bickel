"""Data models for completed usage sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Session:
    """A completed, qualifying heater-on session.

    Timestamps are ISO 8601 UTC strings (not ``datetime``) so the record is
    directly JSON-serializable for both the persisted store and entity
    attributes exposed to the Lovelace card. Setpoint statistics are in
    degrees Celsius; convert to a display unit only at the entity layer.
    """

    start: str
    stop: str
    min_setpoint_c: float
    max_setpoint_c: float
    median_setpoint_c: float
    mode_setpoint_c: float
    average_setpoint_c: float
    pump_seconds: float

    def as_dict(self) -> dict[str, Any]:
        """Return a plain, JSON-serializable representation."""
        return asdict(self)
