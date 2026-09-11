"""Coordinator and multi-source fusion engine."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .confidence import calculate_confidence
from .const import (
    CONF_DWELL_TIME,
    CONF_ENTER_CONFIRMATION,
    CONF_EXIT_CONFIRMATION,
    CONF_HOME_ZONE,
    CONF_MAX_ACCURACY,
    CONF_MAX_JUMP_METERS,
    CONF_MAX_SPEED_KMH,
    CONF_OFFLINE_TIMEOUT,
    CONF_SOURCE_ENTITIES,
    CONF_STALE_TIMEOUT,
    DEFAULT_DWELL_TIME,
    DEFAULT_ENTER_CONFIRMATION,
    DEFAULT_EXIT_CONFIRMATION,
    DEFAULT_HOME_ZONE,
    DEFAULT_MAX_ACCURACY,
    DEFAULT_MAX_JUMP_METERS,
    DEFAULT_MAX_SPEED_KMH,
    DEFAULT_OFFLINE_TIMEOUT,
    DEFAULT_STALE_TIMEOUT,
    DOMAIN,
    EVENT_ENTERED_ZONE,
    EVENT_LEFT_ZONE,
    EVENT_LOCATION_RECOVERED,
    EVENT_LOCATION_STALE,
    EVENT_STARTED_MOVING,
    EVENT_STOPPED_MOVING,
    Movement,
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
            CONF_ENTER_CONFIRMATION: DEFAULT_ENTER_CONFIRMATION,
            CONF_EXIT_CONFIRMATION: DEFAULT_EXIT_CONFIRMATION,
            CONF_DWELL_TIME: DEFAULT_DWELL_TIME,
            CONF_HOME_ZONE: DEFAULT_HOME_ZONE,
            "privacy_mode": PrivacyMode.FULL.value,
            **config,
        }
        if not self.config.get(CONF_SOURCE_ENTITIES) and self.config.get("source_entity"):
            self.config[CONF_SOURCE_ENTITIES] = [self.config["source_entity"]]
        self.previous: LocationSample | None = None
        self.rejected_samples = 0
        self._confirmed_zone: str | None = None
        self._pending_zone: str | None = None
        self._pending_zone_since: datetime | None = None
        self._previous_movement = Movement.UNKNOWN
        self._previous_stale = True
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
                accuracy = float(
                    state.attributes.get(
                        "gps_accuracy", state.attributes.get("accuracy", 9999)
                    )
                )
                sample = LocationSample(
                    float(lat),
                    float(lon),
                    accuracy,
                    state.last_updated,
                    entity_id,
                    _numeric(state.attributes.get("speed")),
                    _numeric(state.attributes.get("course")),
                )
            except (TypeError, ValueError):
                status[entity_id] = "invalid_location"
                continue
            samples.append(sample)
        return samples, status

    def _confirm_zone(self, candidate: str | None, now: datetime) -> str | None:
        """Apply enter/exit confirmation and dwell time to a zone candidate."""
        if candidate == self._confirmed_zone:
            self._pending_zone = None
            self._pending_zone_since = None
            return self._confirmed_zone
        if candidate != self._pending_zone:
            self._pending_zone = candidate
            self._pending_zone_since = now
            return self._confirmed_zone
        if self._pending_zone_since is None:
            self._pending_zone_since = now
            return self._confirmed_zone

        elapsed = (now - self._pending_zone_since).total_seconds()
        timeout = (
            float(self.config.get(CONF_EXIT_CONFIRMATION, DEFAULT_EXIT_CONFIRMATION))
            if self._confirmed_zone is not None
            else float(
                self.config.get(CONF_ENTER_CONFIRMATION, DEFAULT_ENTER_CONFIRMATION)
            )
        )
        timeout = max(timeout, float(self.config.get(CONF_DWELL_TIME, DEFAULT_DWELL_TIME)))
        if elapsed < timeout:
            return self._confirmed_zone

        old_zone = self._confirmed_zone
        self._confirmed_zone = candidate
        self._pending_zone = None
        self._pending_zone_since = None
        if old_zone is not None and old_zone != candidate:
            self.hass.bus.async_fire(
                EVENT_LEFT_ZONE,
                {"person": self.person_entity, "zone": old_zone},
            )
        if candidate is not None and candidate != old_zone:
            self.hass.bus.async_fire(
                EVENT_ENTERED_ZONE,
                {"person": self.person_entity, "zone": candidate},
            )
        return self._confirmed_zone

    def _fire_state_events(
        self, movement: Movement, stale: bool, now: datetime
    ) -> None:
        """Fire movement and stale/recovered transition events."""
        was_moving = self._previous_movement not in {
            Movement.UNKNOWN,
            Movement.STATIONARY,
        }
        is_moving = movement not in {Movement.UNKNOWN, Movement.STATIONARY}
        if is_moving != was_moving:
            self.hass.bus.async_fire(
                EVENT_STARTED_MOVING if is_moving else EVENT_STOPPED_MOVING,
                {"person": self.person_entity, "movement": movement.value},
            )
        if stale != self._previous_stale:
            self.hass.bus.async_fire(
                EVENT_LOCATION_STALE if stale else EVENT_LOCATION_RECOVERED,
                {"person": self.person_entity, "timestamp": now.isoformat()},
            )
        self._previous_movement = movement
        self._previous_stale = stale

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
            sample = select_freshest_sample(accepted)
            self.previous = sample
        elif self.previous is not None:
            sample = self.previous
        else:
            return LocationState(
                source_status=status, rejected_samples=self.rejected_samples
            )

        now = datetime.now(timezone.utc)
        age = max(0.0, (now - sample.timestamp).total_seconds())
        home = self.hass.states.get(self.config.get(CONF_HOME_ZONE, DEFAULT_HOME_ZONE))
        distance_home = None
        if (
            home
            and home.attributes.get("latitude") is not None
            and home.attributes.get("longitude") is not None
        ):
            distance_home = haversine_meters(
                sample.latitude,
                sample.longitude,
                float(home.attributes["latitude"]),
                float(home.attributes["longitude"]),
            )

        candidate_zone = None
        source_state = self.hass.states.get(sample.source)
        if source_state:
            candidate_zone = source_state.attributes.get("zone")
            if candidate_zone is None and source_state.state not in {"unknown", "unavailable"}:
                candidate_zone = source_state.state
        zone = self._confirm_zone(candidate_zone, now)

        movement = classify_speed(sample.speed_kmh)
        stale = age >= float(self.config[CONF_STALE_TIMEOUT])
        offline = age >= float(self.config[CONF_OFFLINE_TIMEOUT])
        self._fire_state_events(movement, stale, now)

        return LocationState(
            sample=sample,
            confidence=calculate_confidence(
                sample, now=now, corroborated=len(accepted) > 1
            ),
            movement=movement,
            zone=zone,
            distance_home=distance_home,
            stale=stale,
            offline=offline,
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


def select_freshest_sample(samples: list[LocationSample]) -> LocationSample:
    """Select the newest fix; use accuracy only when timestamps are identical."""
    if not samples:
        raise ValueError("At least one location sample is required")
    return max(samples, key=lambda item: (item.timestamp, -item.accuracy))


def _numeric(value: Any) -> float | None:
    """Convert a source attribute to a float when possible."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
