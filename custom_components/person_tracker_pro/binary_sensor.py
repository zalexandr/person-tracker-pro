"""Binary sensor platform."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .entity import PersonTrackerEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities([StaleSensor(coordinator), OfflineSensor(coordinator)])


class StaleSensor(PersonTrackerEntity, BinarySensorEntity):
    """Location stale sensor."""

    _attr_name = "Location stale"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        return self.coordinator.data.stale


class OfflineSensor(PersonTrackerEntity, BinarySensorEntity):
    """Location offline sensor."""

    _attr_name = "Location offline"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        return self.coordinator.data.offline

    @property
    def available(self):
        return True
