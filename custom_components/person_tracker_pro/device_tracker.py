"""Device tracker platform."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity

from .const import ATTR_ACCURACY, ATTR_CONFIDENCE, ATTR_DISTANCE_HOME, ATTR_MOVEMENT, ATTR_REJECTED, ATTR_SOURCE, ATTR_SOURCE_COUNT, ATTR_STALE, ATTR_OFFLINE, ATTR_ZONE, DOMAIN, PrivacyMode
from .entity import PersonTrackerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the fused tracker."""
    async_add_entities([PersonTrackerTracker(entry.runtime_data, entry.entry_id)], True)

class PersonTrackerTracker(PersonTrackerEntity, TrackerEntity):
    """Fused GPS tracker."""
    _attr_name = "Location"
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, f"{entry_id}_location")

    @property
    def latitude(self) -> float | None:
        sample = self.coordinator.data.sample
        if not sample or self.coordinator.config.get("privacy_mode") != PrivacyMode.FULL:
            return None
        return sample.latitude

    @property
    def longitude(self) -> float | None:
        sample = self.coordinator.data.sample
        if not sample or self.coordinator.config.get("privacy_mode") != PrivacyMode.FULL:
            return None
        return sample.longitude

    @property
    def location_accuracy(self) -> float | None:
        sample = self.coordinator.data.sample
        return sample.accuracy if sample else None

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        data = self.coordinator.data
        sample = data.sample
        return {
            ATTR_ACCURACY: sample.accuracy if sample else None,
            ATTR_CONFIDENCE: data.confidence,
            ATTR_MOVEMENT: data.movement,
            ATTR_SOURCE: sample.source if sample else None,
            ATTR_ZONE: data.zone,
            ATTR_DISTANCE_HOME: data.distance_home,
            ATTR_SOURCE_COUNT: data.source_count,
            ATTR_REJECTED: data.rejected_samples,
            ATTR_STALE: data.stale,
            ATTR_OFFLINE: data.offline,
        }
