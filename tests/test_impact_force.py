"""Hertzian contact force between the impactor and the first mass."""

import pytest

from simulation.python_simulation.impact_force import impact_force

C = 1.2e4


def test_zero_when_apart():
    assert impact_force(C, -0.3, 0.0) == 0.0


def test_zero_when_exactly_touching():
    assert impact_force(C, 0.5, 0.5) == 0.0


def test_hertz_law_in_compression():
    overlap = 0.004
    assert impact_force(C, 0.1 + overlap, 0.1) == pytest.approx(C * overlap**1.5, rel=1e-14)


def test_continuous_at_contact():
    assert impact_force(C, 1e-12, 0.0) < 1e-12
