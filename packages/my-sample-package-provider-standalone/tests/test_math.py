"""Tests for standalone.math module."""

from standalone.math import clamp, lerp


def test_clamp_within_range():
    assert clamp(5, 0, 10) == 5


def test_clamp_below_min():
    assert clamp(-3, 0, 10) == 0


def test_clamp_above_max():
    assert clamp(15, 0, 10) == 10


def test_clamp_at_min_boundary():
    assert clamp(0, 0, 10) == 0


def test_clamp_at_max_boundary():
    assert clamp(10, 0, 10) == 10


def test_clamp_float_values():
    assert clamp(1.5, 0.0, 1.0) == 1.0


def test_lerp_midpoint():
    assert lerp(0, 10, 0.5) == 5.0


def test_lerp_at_zero():
    assert lerp(0, 10, 0.0) == 0.0


def test_lerp_at_one():
    assert lerp(0, 10, 1.0) == 10.0


def test_lerp_negative_range():
    assert lerp(-10, 10, 0.5) == 0.0
