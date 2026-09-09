"""Data models."""

from __future__ import annotations

from dataclasses import dataclass, field
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
    in_zones: list[str] = field(default_factory=list)
    movement: Movement = Movement.UNKNOWN
    distance_home: float | None = None
    stale: bool = True
    offline: bool = True
    source_count: int = 0
    rejected_samples: int = 0
    source_status: dict[str, str] = field(default_factory=dict)
