from custom_components.person_tracker_pro.const import Movement
from custom_components.person_tracker_pro.movement import classify_speed


def test_stationary():
    assert classify_speed(0.5) == Movement.STATIONARY


def test_walking():
    assert classify_speed(4) == Movement.WALKING


def test_cycling():
    assert classify_speed(18) == Movement.CYCLING


def test_driving():
    assert classify_speed(80) == Movement.DRIVING
