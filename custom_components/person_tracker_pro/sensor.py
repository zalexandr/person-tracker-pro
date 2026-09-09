"""Sensor platform."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed
from homeassistant.helpers.entity import EntityCategory

from .entity import PersonTrackerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    async_add_entities([
        ConfidenceSensor(coordinator, entry.entry_id),
        AccuracySensor(coordinator, entry.entry_id),
        SpeedSensor(coordinator, entry.entry_id),
        SourceCountSensor(coordinator, entry.entry_id),
        RejectedSensor(coordinator, entry.entry_id),
    ], True)

class BaseSensor(PersonTrackerEntity, SensorEntity):
    def __init__(self, coordinator, unique_id: str): super().__init__(coordinator, unique_id)

class ConfidenceSensor(BaseSensor):
    _attr_name = "Presence confidence"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:shield-check"
    def __init__(self, c, e): super().__init__(c, f"{e}_confidence")
    @property
    def native_value(self): return self.coordinator.data.confidence

class AccuracySensor(BaseSensor):
    _attr_name = "GPS accuracy"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_icon = "mdi:crosshairs-gps"
    def __init__(self, c, e): super().__init__(c, f"{e}_accuracy")
    @property
    def native_value(self):
        sample = self.coordinator.data.sample
        return round(sample.accuracy, 1) if sample else None

class SpeedSensor(BaseSensor):
    _attr_name = "Speed"
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"
    def __init__(self, c, e): super().__init__(c, f"{e}_speed")
    @property
    def native_value(self):
        sample = self.coordinator.data.sample
        return round(sample.speed_kmh, 1) if sample and sample.speed_kmh is not None else None

class SourceCountSensor(BaseSensor):
    _attr_name = "Active sources"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    def __init__(self, c, e): super().__init__(c, f"{e}_sources")
    @property
    def native_value(self): return self.coordinator.data.source_count

class RejectedSensor(BaseSensor):
    _attr_name = "Rejected GPS samples"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:map-marker-remove"
    def __init__(self, c, e): super().__init__(c, f"{e}_rejected")
    @property
    def native_value(self): return self.coordinator.data.rejected_samples
