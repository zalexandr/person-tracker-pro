"""Diagnostics."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_SOURCE_ENTITIES
from .coordinator import PersonTrackerCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry[PersonTrackerCoordinator]
) -> dict[str, Any]:
    """Return privacy-safe diagnostics without exact coordinates."""
    data = entry.runtime_data.data
    sample = data.sample
    return {
        "version": entry.version,
        "person_entity": entry.data.get("person_entity"),
        "source_entities": list(entry.data.get(CONF_SOURCE_ENTITIES, [])),
        "confidence": data.confidence,
        "movement": data.movement,
        "zone": data.zone,
        "distance_home_m": round(data.distance_home, 1) if data.distance_home is not None else None,
        "stale": data.stale,
        "offline": data.offline,
        "source_count": data.source_count,
        "source_status": dict(data.source_status),
        "rejected_samples": data.rejected_samples,
        "gps_accuracy": round(sample.accuracy, 1) if sample else None,
        "has_location": sample is not None,
        "last_update": sample.timestamp.isoformat() if sample else None,
    }
