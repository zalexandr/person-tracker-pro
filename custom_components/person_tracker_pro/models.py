"""Data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .const import Movement


@dataclass(slots=True, frozen=True)
class LocationSample:
    """A single location sample."""

    latitude: float
    longitude: float
    accuracy: float
    timestamp: datetime
    source: str
    speed_kmh: float | None = None
    course: float | None = None


@dataclass(slots=True)
class LocationState:
    """Current fused location state."""

    sample: LocationSample | None = None
    confidence: int = 0
    zone: str | None = None
    movement: Movement = Movement.UNKNOWN
    distance_home: float | None = None
    stale: bool = False
    offline: bool = False
    rejected_samples: int = 0
