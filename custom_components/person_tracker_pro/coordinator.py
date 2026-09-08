"""Coordinator and runtime engine."""

from __future__ import annotations

from datetime import datetime, timezone
from math import inf
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_ENTER_CONFIRMATION,
    CONF_MAX_ACCURACY,
    CONF_MAX_JUMP_METERS,
    CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT,
    CONF_PERSON_ENTITY,
    CONF_SOURCE_ENTITY,
    CONF_STALE_TIMEOUT,
    DOMAIN,
)
from .confidence import calculate_confidence
from .gps_filter import FilterConfig, accept_sample, haversine_meters
from .models import LocationSample, LocationState
from .movement import classify_speed


class PersonTrackerCoordinator(DataUpdateCoordinator[LocationState]):
    """Manage one Person Tracker PRO runtime."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self.previous: LocationSample | None = None
        self.state = LocationState()
        self.rejected_samples = 0

        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=None,
        )

    @property
    def source_entity(self) -> str:
        return self.config[CONF_SOURCE_ENTITY]

    @property
    def person_entity(self) -> str:
        return self.config[CONF_PERSON_ENTITY]

    async def async_update(self) -> None:
        """Refresh runtime state from the configured tracker."""
        entity = self.hass.states.get(self.source_entity)
        if entity is None:
            raise UpdateFailed(f"Source entity {self.source_entity} does not exist")

        lat = entity.attributes.get("latitude")
        lon = entity.attributes.get("longitude")
        accuracy = entity.attributes.get("gps_accuracy", entity.attributes.get("accuracy"))

        if lat is None or lon is None:
            raise UpdateFailed("Source tracker has no coordinates")

        timestamp = entity.last_updated
        sample = LocationSample(
            latitude=float(lat),
            longitude=float(lon),
            accuracy=float(accuracy or 9999),
            timestamp=timestamp,
            source=self.source_entity,
            speed_kmh=_numeric(entity.attributes.get("speed")),
            course=_numeric(entity.attributes.get("course")),
        )

        filter_config = FilterConfig(
            max_accuracy=float(self.config[CONF_MAX_ACCURACY]),
            max_jump_meters=float(self.config[CONF_MAX_JUMP_METERS]),
            max_speed_kmh=float(self.config[CONF_MAX_SPEED_KMH]),
        )

        if not accept_sample(sample, self.previous, filter_config):
            self.rejected_samples += 1
            self.state.rejected_samples = self.rejected_samples
            return

        self.previous = sample
        now = datetime.now(timezone.utc)
        age = max(0.0, (now - sample.timestamp).total_seconds())

        self.state.sample = sample
        self.state.confidence = calculate_confidence(sample, now=now)
        self.state.movement = classify_speed(sample.speed_kmh)
        self.state.stale = age >= float(self.config[CONF_STALE_TIMEOUT])
        self.state.offline = age >= float(self.config[CONF_OFFLINE_TIMEOUT])
        self.state.rejected_samples = self.rejected_samples

        self.async_set_updated_data(self.state)

    async def async_request_location(self) -> None:
        """Request a source refresh when supported."""
        # Source integrations differ. We intentionally do not assume a
        # non-standard service exists. A normal coordinator refresh is safe.
        await self.async_update()


def _numeric(value: Any) -> float | None:
    """Convert a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
