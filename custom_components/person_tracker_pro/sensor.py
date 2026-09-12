"""Sensor platform."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed
from homeassistant.helpers.entity import EntityCategory

from .const import CONF_BATTERY_ENTITY
from .entity import PersonTrackerEntity


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Any) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        ConfidenceSensor(coordinator, entry.entry_id),
        AccuracySensor(coordinator, entry.entry_id),
        SpeedSensor(coordinator, entry.entry_id),
        SourceCountSensor(coordinator, entry.entry_id),
        RejectedSensor(coordinator, entry.entry_id),
    ]
    battery_entity = entry.data.get(CONF_BATTERY_ENTITY)
    if battery_entity:
        entities.append(BatterySensor(coordinator, entry.entry_id, battery_entity))
    async_add_entities(entities, True)


class BaseSensor(PersonTrackerEntity, SensorEntity):
    """Base sensor for the integration."""

    def __init__(self, coordinator: Any, unique_id: str) -> None:
        super().__init__(coordinator, unique_id)


class ConfidenceSensor(BaseSensor):
    """Presence confidence."""

    _attr_name = "Presence confidence"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:shield-check"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_confidence")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.confidence


class AccuracySensor(BaseSensor):
    """GPS accuracy."""

    _attr_name = "GPS accuracy"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_icon = "mdi:crosshairs-gps"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_accuracy")

    @property
    def native_value(self) -> float | None:
        sample = self.coordinator.data.sample
        return round(sample.accuracy, 1) if sample else None


class SpeedSensor(BaseSensor):
    """Current speed."""

    _attr_name = "Speed"
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_icon = "mdi:speedometer"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_speed")

    @property
    def native_value(self) -> float | None:
        sample = self.coordinator.data.sample
        return round(sample.speed_kmh, 1) if sample and sample.speed_kmh is not None else None


class SourceCountSensor(BaseSensor):
    """Number of accepted active sources."""

    _attr_name = "Active sources"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_sources")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.source_count


class RejectedSensor(BaseSensor):
    """Number of rejected GPS samples."""

    _attr_name = "Rejected GPS samples"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:map-marker-remove"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_rejected")

    @property
    def native_value(self) -> int:
        return self.coordinator.data.rejected_samples


class BatterySensor(BaseSensor):
    """Expose the configured source battery sensor as a stable entity."""

    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:battery"

    def __init__(self, c: Any, entry_id: str, battery_entity: str) -> None:
        super().__init__(c, f"{entry_id}_battery")
        self._battery_entity = battery_entity

    @property
    def native_value(self) -> float | None:
        state = self.coordinator.hass.states.get(self._battery_entity)
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            return max(0.0, min(100.0, round(float(state.state), 1)))
        except (TypeError, ValueError):
            return None
