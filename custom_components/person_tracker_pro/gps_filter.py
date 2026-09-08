"""GPS quality and plausibility filtering."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt

from .models import LocationSample


@dataclass(slots=True, frozen=True)
class FilterConfig:
    """GPS filter configuration."""

    max_accuracy: float = 150.0
    max_jump_meters: float = 1000.0
    max_speed_kmh: float = 220.0


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in meters."""
    earth_radius = 6_371_000.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)

    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * earth_radius * atan2(sqrt(a), sqrt(1 - a))


def accept_sample(
    sample: LocationSample,
    previous: LocationSample | None,
    config: FilterConfig,
) -> bool:
    """Return whether a location sample is plausible."""
    if sample.accuracy < 0 or sample.accuracy > config.max_accuracy:
        return False

    if previous is None:
        return True

    seconds = (sample.timestamp - previous.timestamp).total_seconds()
    if seconds <= 0:
        return False

    distance = haversine_meters(
        previous.latitude,
        previous.longitude,
        sample.latitude,
        sample.longitude,
    )
    if distance > config.max_jump_meters:
        return False

    implied_speed = distance / seconds * 3.6
    return implied_speed <= config.max_speed_kmh
