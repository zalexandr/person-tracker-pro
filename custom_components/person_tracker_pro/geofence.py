"""Geofence hysteresis helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(slots=True)
class PendingTransition:
    """Pending zone transition."""

    zone: str | None
    started_at: datetime


def transition_confirmed(
    pending: PendingTransition | None,
    *,
    now: datetime,
    required_seconds: int,
) -> bool:
    """Return True when a pending transition lasted long enough."""
    if pending is None:
        return False
    return now - pending.started_at >= timedelta(seconds=required_seconds)
