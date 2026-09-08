"""Constants for Person Tracker PRO."""

from __future__ import annotations

from enum import StrEnum

DOMAIN = "person_tracker_pro"
PLATFORMS = ["device_tracker", "sensor", "binary_sensor"]

CONF_PERSON_ENTITY = "person_entity"
CONF_SOURCE_ENTITY = "source_entity"
CONF_BATTERY_ENTITY = "battery_entity"
CONF_MAX_ACCURACY = "max_accuracy"
CONF_MAX_JUMP_METERS = "max_jump_meters"
CONF_MAX_SPEED_KMH = "max_speed_kmh"
CONF_ENTER_CONFIRMATION = "enter_confirmation"
CONF_EXIT_CONFIRMATION = "exit_confirmation"
CONF_STALE_TIMEOUT = "stale_timeout"
CONF_OFFLINE_TIMEOUT = "offline_timeout"
CONF_DWELL_TIME = "dwell_time"
CONF_PRIVACY_MODE = "privacy_mode"

DEFAULT_MAX_ACCURACY = 150.0
DEFAULT_MAX_JUMP_METERS = 1000.0
DEFAULT_MAX_SPEED_KMH = 220.0
DEFAULT_ENTER_CONFIRMATION = 10
DEFAULT_EXIT_CONFIRMATION = 30
DEFAULT_STALE_TIMEOUT = 600
DEFAULT_OFFLINE_TIMEOUT = 1800
DEFAULT_DWELL_TIME = 300

ATTR_CONFIDENCE = "confidence"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_ACCURACY = "gps_accuracy"
ATTR_LAST_UPDATE = "last_update"
ATTR_MOVEMENT = "movement"
ATTR_SOURCE = "source"
ATTR_ZONE = "zone"
ATTR_DISTANCE_HOME = "distance_home"
ATTR_SPEED = "speed"
ATTR_COURSE = "course"

EVENT_ENTERED_ZONE = "person_tracker_entered_zone"
EVENT_LEFT_ZONE = "person_tracker_left_zone"
EVENT_STARTED_MOVING = "person_tracker_started_moving"
EVENT_STOPPED_MOVING = "person_tracker_stopped_moving"
EVENT_LOCATION_STALE = "person_tracker_location_stale"
EVENT_LOCATION_RECOVERED = "person_tracker_location_recovered"

SERVICE_REQUEST_LOCATION = "request_location"
SERVICE_RECALCULATE = "recalculate_presence"
SERVICE_SET_PRIVACY = "set_privacy_mode"


class PrivacyMode(StrEnum):
    """Privacy modes."""

    FULL = "full"
    ZONE_ONLY = "zone_only"
    PRIVATE = "private"


class Movement(StrEnum):
    """Movement classification."""

    UNKNOWN = "unknown"
    STATIONARY = "stationary"
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    DRIVING = "driving"
