"""Sensor platform."""

from __future__ import annotations

from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed
from homeassistant.helpers.entity import EntityCategory

from .entity import PersonTrackerEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            ConfidenceSensor(coordinator),
            AccuracySensor(coordinator),
            SpeedSensor(coordinator),
            RejectedSensor(coordinator),
        ]
    )


class ConfidenceSensor(PersonTrackerEntity):
    """Presence confidence."""

    _attr_name = "Presence confidence"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:shield-check"

    @property
    def native_value(self):
        return self.coordinator.data.confidence


class AccuracySensor(PersonTrackerEntity):
    """GPS accuracy."""

    _attr_name = "GPS accuracy"
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_icon = "mdi:crosshairs-gps"

    @property
    def native_value(self):
        sample = self.coordinator.data.sample
        return round(sample.accuracy, 1) if sample else None


class SpeedSensor(PersonTrackerEntity):
    """Speed."""

    _attr_name = "Speed"
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"

    @property
    def native_value(self):
        sample = self.coordinator.data.sample
        return round(sample.speed_kmh, 1) if sample and sample.speed_kmh is not None else None


class RejectedSensor(PersonTrackerEntity):
    """Rejected GPS samples."""

    _attr_name = "Rejected GPS samples"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:map-marker-remove"

    @property
    def native_value(self):
        return self.coordinator.data.rejected_samples
