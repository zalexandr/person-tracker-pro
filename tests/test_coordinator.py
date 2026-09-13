from datetime import datetime, timedelta, timezone

import pytest

from custom_components.person_tracker_pro.coordinator import select_freshest_sample
from custom_components.person_tracker_pro.models import LocationSample


def sample(name: str, seconds: int, accuracy: float) -> LocationSample:
    return LocationSample(
        50.0, 19.0, accuracy,
        datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds),
        name,
    )


def test_selects_newest_even_when_older_fix_is_more_accurate() -> None:
    result = select_freshest_sample([
        sample("phone", 100, 5),
        sample("watch", 101, 50),
    ])
    assert result.source == "watch"


def test_accuracy_breaks_exact_timestamp_tie() -> None:
    result = select_freshest_sample([
        sample("phone", 100, 25),
        sample("watch", 100, 5),
    ])
    assert result.source == "watch"


def test_empty_samples_raise() -> None:
    with pytest.raises(ValueError, match="At least one"):
        select_freshest_sample([])
