"""Presence confidence calculation."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import LocationSample


def calculate_confidence(
    sample: LocationSample | None,
    *,
    now: datetime | None = None,
    zone_match: bool = False,
    corroborated: bool = False,
) -> int:
    """Calculate a conservative 0..100 confidence score."""
    if sample is None:
        return 0

    now = now or datetime.now(timezone.utc)
    age = max(0.0, (now - sample.timestamp).total_seconds())

    score = 100.0

    if sample.accuracy > 20:
        score -= min(30.0, (sample.accuracy - 20) / 3)

    if age > 30:
        score -= min(35.0, (age - 30) / 20)

    if zone_match:
        score += 5

    if corroborated:
        score += 5

    return max(0, min(100, round(score)))
