"""Binary sensor platform."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import Movement
from .coordinator import PersonTrackerCoordinator
from .entity import PersonTrackerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[PersonTrackerCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            StaleSensor(coordinator, entry.entry_id),
            OfflineSensor(coordinator, entry.entry_id),
            MovingSensor(coordinator, entry.entry_id),
        ],
        True,
    )


class StaleSensor(PersonTrackerEntity, BinarySensorEntity):
    """Expose whether the latest location is stale."""

    _attr_name = "Location stale"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: PersonTrackerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, f"{entry_id}_stale")

    @property
    def is_on(self) -> bool:
        """Return whether the location is stale."""
        return self.coordinator.data.stale


class OfflineSensor(PersonTrackerEntity, BinarySensorEntity):
    """Expose whether all location data is offline."""

    _attr_name = "Location offline"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: PersonTrackerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, f"{entry_id}_offline")

    @property
    def is_on(self) -> bool:
        """Return whether the location is offline."""
        return self.coordinator.data.offline


class MovingSensor(PersonTrackerEntity, BinarySensorEntity):
    """Expose whether the person is moving."""

    _attr_name = "Moving"

    def __init__(self, coordinator: PersonTrackerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, f"{entry_id}_moving")

    @property
    def is_on(self) -> bool:
        """Return whether the person is moving."""
        return self.coordinator.data.movement not in (
            Movement.UNKNOWN,
            Movement.STATIONARY,
        )
