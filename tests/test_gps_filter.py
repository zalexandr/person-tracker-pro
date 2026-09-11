from datetime import datetime, timedelta, timezone

from custom_components.person_tracker_pro.gps_filter import (
    FilterConfig,
    accept_sample,
    haversine_meters,
)
from custom_components.person_tracker_pro.models import LocationSample


def sample(
    lat: float, lon: float, timestamp: datetime, accuracy: float = 5
) -> LocationSample:
    """Create a test location sample."""
    return LocationSample(lat, lon, accuracy, timestamp, "test")


def test_haversine_zero() -> None:
    """Identical coordinates have zero distance."""
    assert haversine_meters(50, 19, 50, 19) == 0


def test_accept_first_sample() -> None:
    """The first valid sample is accepted."""
    timestamp = datetime.now(timezone.utc)
    assert accept_sample(sample(50, 19, timestamp), None, FilterConfig())


def test_reject_bad_accuracy() -> None:
    """Samples outside the configured accuracy limit are rejected."""
    timestamp = datetime.now(timezone.utc)
    assert not accept_sample(sample(50, 19, timestamp, 500), None, FilterConfig())


def test_reject_impossible_jump() -> None:
    """An impossible movement jump is rejected."""
    timestamp = datetime.now(timezone.utc)
    previous = sample(50, 19, timestamp)
    current = sample(51, 20, timestamp + timedelta(seconds=2))
    assert not accept_sample(current, previous, FilterConfig())
