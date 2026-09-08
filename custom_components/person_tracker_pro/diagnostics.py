"""Diagnostics."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .coordinator import PersonTrackerCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry[PersonTrackerCoordinator]
) -> dict:
    """Return diagnostics without exposing exact coordinates."""
    data = entry.runtime_data.data
    sample = data.sample
    return {
        "person_entity": entry.data.get("person_entity"),
        "source_entity": entry.data.get("source_entity"),
        "confidence": data.confidence,
        "movement": data.movement,
        "stale": data.stale,
        "offline": data.offline,
        "rejected_samples": data.rejected_samples,
        "gps_accuracy": sample.accuracy if sample else None,
        "has_location": sample is not None,
    }
