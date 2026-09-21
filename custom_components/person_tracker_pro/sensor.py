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
        DistanceHomeSensor(coordinator, entry.entry_id),
        LatitudeSensor(coordinator, entry.entry_id),
        LongitudeSensor(coordinator, entry.entry_id),
        CourseSensor(coordinator, entry.entry_id),
        ZoneSensor(coordinator, entry.entry_id),
        SourceSensor(coordinator, entry.entry_id),
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


class DistanceHomeSensor(BaseSensor):
    """Distance from the configured home zone."""

    _attr_name = "Distance home"
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:home-map-marker"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_distance_home")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.distance_home
        return round(value, 1) if value is not None else None


class LatitudeSensor(BaseSensor):
    """Current fused latitude."""

    _attr_name = "Latitude"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:latitude"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_latitude")

    @property
    def native_value(self) -> float | None:
        sample = self.coordinator.data.sample
        return round(sample.latitude, 6) if sample else None


class LongitudeSensor(BaseSensor):
    """Current fused longitude."""

    _attr_name = "Longitude"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:longitude"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_longitude")

    @property
    def native_value(self) -> float | None:
        sample = self.coordinator.data.sample
        return round(sample.longitude, 6) if sample else None


class CourseSensor(BaseSensor):
    """Current travel direction in degrees."""

    _attr_name = "Course"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:compass-outline"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_course")

    @property
    def native_value(self) -> float | None:
        sample = self.coordinator.data.sample
        return round(sample.course, 1) if sample and sample.course is not None else None


class ZoneSensor(BaseSensor):
    """Current resolved zone."""

    _attr_name = "Current zone"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:map-marker-radius"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_zone")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.zone


class SourceSensor(BaseSensor):
    """Source used for the current fused location."""

    _attr_name = "Location source"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:source-branch"

    def __init__(self, c: Any, e: str) -> None:
        super().__init__(c, f"{e}_source")

    @property
    def native_value(self) -> str | None:
        sample = self.coordinator.data.sample
        return sample.source if sample else None


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
