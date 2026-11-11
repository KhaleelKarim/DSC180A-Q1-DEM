"""Uniform sampling with per-family rejection of invalid springs."""

import numpy as np
import pytest

from simulation.python_simulation.sampling import is_valid, sample_designs


def test_shapes_and_bounds():
    c2, c3 = sample_designs(500, seed=1)
    assert c2.shape == c3.shape == (500, 4)
    assert ((c2 >= -120) & (c2 <= 0)).all()
    assert ((c3 >= 0) & (c3 <= 4000)).all()


def test_every_family_is_valid():
    c2, c3 = sample_designs(5000, seed=2)
    assert ((2 / 9) * c2**2 < c3).all()


def test_is_valid_boundary():
    assert not is_valid(-90.0, 1800.0)        # (2/9) * 90^2 = 1800 exactly
    assert is_valid(-90.0, 1800.0001)


def test_seed_reproducible():
    a = sample_designs(20, seed=7)
    b = sample_designs(20, seed=7)
    c = sample_designs(20, seed=8)
    np.testing.assert_array_equal(a[0], b[0])
    np.testing.assert_array_equal(a[1], b[1])
    assert not np.array_equal(a[0], c[0])


def test_spring_category_shares():
    """Uniform over the valid region: about 83% monotonic (q < 3), 12.5%
    snap-through (3 <= q < 4) and 4.5% bistable (q >= 4), with q = c2^2 / c3."""
    c2, c3 = sample_designs(50_000, seed=3)
    q = (c2**2 / c3).ravel()
    assert np.mean(q < 3) == pytest.approx(0.83, abs=0.01)
    assert np.mean((q >= 3) & (q < 4)) == pytest.approx(0.125, abs=0.01)
    assert np.mean(q >= 4) == pytest.approx(0.045, abs=0.01)
