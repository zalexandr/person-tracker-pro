"""Coordinator and multi-source fusion engine."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .confidence import calculate_confidence
from .const import (
    CONF_HOME_ZONE,
    CONF_MAX_ACCURACY,
    CONF_MAX_JUMP_METERS,
    CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT,
    CONF_SOURCE_ENTITIES,
    CONF_STALE_TIMEOUT,
    DEFAULT_HOME_ZONE,
    DEFAULT_MAX_ACCURACY,
    DEFAULT_MAX_JUMP_METERS,
    DEFAULT_MAX_SPEED_KMH,
    DEFAULT_OFFLINE_TIMEOUT,
    DEFAULT_STALE_TIMEOUT,
    DOMAIN,
    PrivacyMode,
)
from .gps_filter import FilterConfig, accept_sample, haversine_meters
from .models import LocationSample, LocationState
from .movement import classify_speed

_LOGGER = logging.getLogger(__name__)


class PersonTrackerCoordinator(DataUpdateCoordinator[LocationState]):
    """Manage one Person Tracker PRO runtime."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self.config: dict[str, Any] = {
            CONF_MAX_ACCURACY: DEFAULT_MAX_ACCURACY,
            CONF_MAX_JUMP_METERS: DEFAULT_MAX_JUMP_METERS,
            CONF_MAX_SPEED_KMH: DEFAULT_MAX_SPEED_KMH,
            CONF_STALE_TIMEOUT: DEFAULT_STALE_TIMEOUT,
            CONF_OFFLINE_TIMEOUT: DEFAULT_OFFLINE_TIMEOUT,
            CONF_HOME_ZONE: DEFAULT_HOME_ZONE,
            "privacy_mode": PrivacyMode.FULL.value,
            **config,
        }
        if not self.config.get(CONF_SOURCE_ENTITIES) and self.config.get("source_entity"):
            self.config[CONF_SOURCE_ENTITIES] = [self.config["source_entity"]]
        self.previous: LocationSample | None = None
        self.rejected_samples = 0
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=None)

    @property
    def person_entity(self) -> str:
        """Return the linked person entity."""
        return self.config["person_entity"]

    @property
    def source_entities(self) -> list[str]:
        """Return configured location source entities."""
        return list(self.config.get(CONF_SOURCE_ENTITIES, []))

    @property
    def privacy_mode(self) -> PrivacyMode:
        """Return the normalized privacy mode."""
        try:
            return PrivacyMode(self.config.get("privacy_mode", PrivacyMode.FULL.value))
        except ValueError:
            _LOGGER.warning("Unknown privacy mode; falling back to full")
            return PrivacyMode.FULL

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
                status[entity_id] = "no_location"
                continue
            try:
                accuracy = float(state.attributes.get("gps_accuracy", state.attributes.get("accuracy", 9999)))
                sample = LocationSample(
                    float(lat), float(lon), accuracy, state.last_updated, entity_id,
                    _numeric(state.attributes.get("speed")),
                    _numeric(state.attributes.get("course")),
                )
            except (TypeError, ValueError):
                status[entity_id] = "invalid_location"
                continue
            samples.append(sample)
        return samples, status

    async def _async_update_data(self) -> LocationState:
        """Read, filter and fuse all configured source entities."""
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
                status[sample.source] = "rejected"

        if accepted:
            # Location freshness is the primary source-selection signal. Accuracy
            # is only a deterministic tie-breaker for identical timestamps.
            sample = max(accepted, key=lambda item: (item.timestamp, -item.accuracy))
            self.previous = sample
        elif self.previous is not None:
            sample = self.previous
        else:
            return LocationState(source_status=status, rejected_samples=self.rejected_samples)

        now = datetime.now(timezone.utc)
        age = max(0.0, (now - sample.timestamp).total_seconds())
        home = self.hass.states.get(self.config.get(CONF_HOME_ZONE, DEFAULT_HOME_ZONE))
        distance_home = None
        if home and home.attributes.get("latitude") is not None and home.attributes.get("longitude") is not None:
            distance_home = haversine_meters(
                sample.latitude, sample.longitude,
                float(home.attributes["latitude"]), float(home.attributes["longitude"]),
            )

        zone = None
        source_state = self.hass.states.get(sample.source)
        if source_state:
            zone = source_state.attributes.get("zone")
            if zone is None and source_state.state not in {"unknown", "unavailable"}:
                zone = source_state.state

        return LocationState(
            sample=sample,
            confidence=calculate_confidence(sample, now=now, corroborated=len(accepted) > 1),
            movement=classify_speed(sample.speed_kmh),
            zone=zone,
            distance_home=distance_home,
            stale=age >= float(self.config[CONF_STALE_TIMEOUT]),
            offline=age >= float(self.config[CONF_OFFLINE_TIMEOUT]),
            source_count=len(accepted),
            rejected_samples=self.rejected_samples,
            source_status=status,
        )

    async def async_request_location(self) -> None:
        """Refresh the fused state from current Home Assistant source states."""
        await self.async_refresh()

    async def async_recalculate(self) -> None:
        """Recalculate presence immediately from current source states."""
        await self.async_refresh()


def _numeric(value: Any) -> float | None:
    """Convert a source attribute to a float when possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
