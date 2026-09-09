"""Binary sensor platform."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import Movement
from .entity import PersonTrackerEntity

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities([
        StaleSensor(coordinator, entry.entry_id),
        OfflineSensor(coordinator, entry.entry_id),
        MovingSensor(coordinator, entry.entry_id),
    ], True)

class StaleSensor(PersonTrackerEntity, BinarySensorEntity):
    _attr_name = "Location stale"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    def __init__(self, coordinator, entry_id): super().__init__(coordinator, f"{entry_id}_stale")
    @property
    def is_on(self): return self.coordinator.data.stale

class OfflineSensor(PersonTrackerEntity, BinarySensorEntity):
    _attr_name = "Location offline"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    def __init__(self, coordinator, entry_id): super().__init__(coordinator, f"{entry_id}_offline")
    @property
    def is_on(self): return self.coordinator.data.offline

class MovingSensor(PersonTrackerEntity, BinarySensorEntity):
    _attr_name = "Moving"
    def __init__(self, coordinator, entry_id): super().__init__(coordinator, f"{entry_id}_moving")
    @property
    def is_on(self): return self.coordinator.data.movement not in (Movement.UNKNOWN, Movement.STATIONARY)
