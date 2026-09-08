"""Entity helpers."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PersonTrackerCoordinator


class PersonTrackerEntity(CoordinatorEntity[PersonTrackerCoordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PersonTrackerCoordinator, unique_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = unique_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.person_entity)},
            "name": f"Person Tracker PRO — {coordinator.person_entity}",
            "manufacturer": "Person Tracker PRO",
            "model": "Presence Intelligence Engine",
        }
