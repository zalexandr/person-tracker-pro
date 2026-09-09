"""Coordinator and multi-source fusion engine."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .confidence import calculate_confidence
from .const import (
    CONF_HOME_ZONE, CONF_MAX_ACCURACY, CONF_MAX_JUMP_METERS, CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT, CONF_SOURCE_ENTITIES, CONF_STALE_TIMEOUT, DEFAULT_HOME_ZONE,
    DEFAULT_MAX_ACCURACY, DEFAULT_MAX_JUMP_METERS, DEFAULT_MAX_SPEED_KMH,
    DEFAULT_OFFLINE_TIMEOUT, DEFAULT_STALE_TIMEOUT, DOMAIN, PrivacyMode,
)
from .gps_filter import FilterConfig, accept_sample, haversine_meters
from .models import LocationSample, LocationState
from .movement import classify_speed

_LOGGER = logging.getLogger(__name__)

class PersonTrackerCoordinator(DataUpdateCoordinator[LocationState]):
    """Manage one Person Tracker PRO runtime."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config = {
            "max_accuracy": DEFAULT_MAX_ACCURACY,
            "max_jump_meters": DEFAULT_MAX_JUMP_METERS,
            "max_speed_kmh": DEFAULT_MAX_SPEED_KMH,
            "stale_timeout": DEFAULT_STALE_TIMEOUT,
            "offline_timeout": DEFAULT_OFFLINE_TIMEOUT,
            "home_zone": DEFAULT_HOME_ZONE,
            "privacy_mode": PrivacyMode.FULL,
            **config,
        }
        self.previous: LocationSample | None = None
        self.rejected_samples = 0
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=None)

    @property
    def person_entity(self) -> str:
        return self.config["person_entity"]

    @property
    def source_entities(self) -> list[str]:
        return list(self.config.get(CONF_SOURCE_ENTITIES, []))

    def _read_samples(self) -> tuple[list[LocationSample], dict[str, str]]:
        samples: list[LocationSample] = []
        status: dict[str, str] = {}
        for entity_id in self.source_entities:
            state = self.hass.states.get(entity_id)
            if state is None:
                status[entity_id] = "missing"
                continue
            status[entity_id] = state.state
            lat = state.attributes.get("latitude")
            lon = state.attributes.get("longitude")
            if lat is None or lon is None:
                continue
            try:
                accuracy = float(state.attributes.get("gps_accuracy", state.attributes.get("accuracy", 9999)))
                sample = LocationSample(
                    float(lat), float(lon), accuracy, state.last_updated, entity_id,
                    _numeric(state.attributes.get("speed")), _numeric(state.attributes.get("course")),
                )
            except (TypeError, ValueError):
                continue
            samples.append(sample)
        return samples, status

    async def _async_update_data(self) -> LocationState:
        samples, status = self._read_samples()
        cfg = FilterConfig(
            float(self.config[CONF_MAX_ACCURACY]),
            float(self.config[CONF_MAX_JUMP_METERS]),
            float(self.config[CONF_MAX_SPEED_KMH]),
        )
        accepted: list[LocationSample] = []
        for sample in samples:
            if accept_sample(sample, self.previous, cfg):
                accepted.append(sample)
            else:
                self.rejected_samples += 1
        if not accepted:
            if self.previous is None:
                return LocationState(source_status=status, rejected_samples=self.rejected_samples)
            sample = self.previous
        else:
            # Prefer fresh data; use accuracy only as the tie-breaker for samples
            # received within the same minute.
            newest = max(accepted, key=lambda item: item.timestamp)
            candidates = [s for s in accepted if abs((newest.timestamp - s.timestamp).total_seconds()) <= 60]
            sample = min(candidates, key=lambda item: item.accuracy)
            self.previous = sample

        now = datetime.now(timezone.utc)
        age = max(0.0, (now - sample.timestamp).total_seconds())
        home = self.hass.states.get(self.config.get(CONF_HOME_ZONE, DEFAULT_HOME_ZONE))
        distance_home = None
        if home and home.attributes.get("latitude") is not None:
            distance_home = haversine_meters(
                sample.latitude, sample.longitude,
                float(home.attributes["latitude"]), float(home.attributes["longitude"]),
            )
        return LocationState(
            sample=sample,
            confidence=calculate_confidence(sample, now=now, corroborated=len(accepted) > 1),
            movement=classify_speed(sample.speed_kmh),
            distance_home=distance_home,
            stale=age >= float(self.config[CONF_STALE_TIMEOUT]),
            offline=age >= float(self.config[CONF_OFFLINE_TIMEOUT]),
            source_count=len(accepted),
            rejected_samples=self.rejected_samples,
            source_status=status,
        )

    async def async_request_location(self) -> None:
        """Refresh the fused state without assuming a source-specific service."""
        await self.async_refresh()

    async def async_recalculate(self) -> None:
        """Recalculate presence immediately."""
        await self.async_refresh()

def _numeric(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    # Home Assistant companion apps usually expose m/s; callers that expose km/h
    # can be normalized later by a source adapter. Keep raw source semantics here.
    return result
