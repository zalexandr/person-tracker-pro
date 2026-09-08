"""Device tracker platform."""

from __future__ import annotations

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

from .const import ATTR_ACCURACY, ATTR_CONFIDENCE, ATTR_MOVEMENT, ATTR_SOURCE, ATTR_ZONE
from .entity import PersonTrackerEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up tracker."""
    coordinator = entry.runtime_data
    async_add_entities([PersonTrackerTracker(coordinator)])


class PersonTrackerTracker(PersonTrackerEntity, TrackerEntity):
    """Fused tracker."""

    _attr_name = "Location"

    @property
    def latitude(self) -> float | None:
        sample = self.coordinator.data.sample
        return sample.latitude if sample else None

    @property
    def longitude(self) -> float | None:
        sample = self.coordinator.data.sample
        return sample.longitude if sample else None

    @property
    def location_accuracy(self) -> int:
        sample = self.coordinator.data.sample
        return round(sample.accuracy) if sample else 0

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        sample = data.sample
        return {
            ATTR_ACCURACY: sample.accuracy if sample else None,
            ATTR_CONFIDENCE: data.confidence,
            ATTR_MOVEMENT: data.movement,
            ATTR_SOURCE: sample.source if sample else None,
            ATTR_ZONE: data.zone,
            "stale": data.stale,
            "offline": data.offline,
            "rejected_samples": data.rejected_samples,
        }
