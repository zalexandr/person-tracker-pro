"""Movement classification."""

from __future__ import annotations

from .const import Movement


def classify_speed(speed_kmh: float | None) -> Movement:
    """Classify movement from speed."""
    if speed_kmh is None:
        return Movement.UNKNOWN
    if speed_kmh < 1.0:
        return Movement.STATIONARY
    if speed_kmh < 7.5:
        return Movement.WALKING
    if speed_kmh < 25.0:
        return Movement.CYCLING
    if speed_kmh <= 220.0:
        return Movement.DRIVING
    return Movement.UNKNOWN
