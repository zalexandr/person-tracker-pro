from datetime import datetime, timedelta, timezone

from custom_components.person_tracker_pro.gps_filter import FilterConfig, accept_sample, haversine_meters
from custom_components.person_tracker_pro.models import LocationSample


def sample(lat, lon, t, accuracy=5):
    return LocationSample(lat, lon, accuracy, t, "test")


def test_haversine_zero():
    assert haversine_meters(50, 19, 50, 19) == 0


def test_accept_first_sample():
    t = datetime.now(timezone.utc)
    assert accept_sample(sample(50, 19, t), None, FilterConfig())


def test_reject_bad_accuracy():
    t = datetime.now(timezone.utc)
    assert not accept_sample(sample(50, 19, t, 500), None, FilterConfig())


def test_reject_impossible_jump():
    t = datetime.now(timezone.utc)
    previous = sample(50, 19, t)
    current = sample(51, 20, t + timedelta(seconds=2))
    assert not accept_sample(current, previous, FilterConfig())
