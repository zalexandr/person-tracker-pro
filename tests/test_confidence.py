from datetime import datetime, timezone

from custom_components.person_tracker_pro.confidence import calculate_confidence
from custom_components.person_tracker_pro.models import LocationSample


def test_no_sample_is_zero():
    assert calculate_confidence(None) == 0


def test_good_recent_sample_is_high():
    sample = LocationSample(
        50, 19, 5, datetime.now(timezone.utc), "test"
    )
    assert calculate_confidence(sample) >= 95
