"""
The fast numba RHS must compute the same velocities/accelerations as the
line-for-line port of impact_equation_of_motion_hetero.m.
"""

import numpy as np
import pytest

from simulation.python_simulation import constants as k
from simulation.python_simulation.equations_of_motion import rhs, rhs_reference

MATERIAL = (k.M_LAYER, k.M_IMPACTOR, k.C_IMPACT, k.ZETA)


def random_springs(rng):
    return np.ones(k.N), rng.uniform(-120, 0, k.N), rng.uniform(0, 4000, k.N)


def test_fast_rhs_matches_reference_on_random_states():
    """2000 random snapshots. Positions spread enough that springs are both
    stretched and compressed, and the impactor is sometimes in contact."""
    rng = np.random.default_rng(0)
    contact_seen = no_contact_seen = 0
    for _ in range(2000):
        c1, c2, c3 = random_springs(rng)
        x = rng.normal(0.0, 0.05, k.N_STATE)
        if x[0] > x[2]:
            contact_seen += 1
        else:
            no_contact_seen += 1
        fast = rhs(0.0, x, c1, c2, c3, *MATERIAL)
        ref = rhs_reference(0.0, x, c1, c2, c3, *MATERIAL)
        np.testing.assert_allclose(fast, ref, rtol=1e-12, atol=1e-12 * np.abs(ref).max())
    assert contact_seen > 100 and no_contact_seen > 100


def test_initial_state_only_impactor_moves():
    rng = np.random.default_rng(1)
    x = np.zeros(k.N_STATE)
    x[1] = k.V_IMPACTOR
    dx = rhs(0.0, x, *random_springs(rng), *MATERIAL)
    expected = np.zeros(k.N_STATE)
    expected[0] = k.V_IMPACTOR
    np.testing.assert_array_equal(dx, expected)


def _single_spring_state(d, spring):
    """State where only spring `spring` (between bodies spring+1 and spring+2)
    has length change d; everything else at rest."""
    x = np.zeros(k.N_STATE)
    x[0] = -1.0                      # impactor well away
    for b in range(spring + 2, k.N + 1):
        x[2 * b] = d
    return x


@pytest.mark.parametrize("d", [0.01, -0.01])
def test_compression_is_cubic_tension_is_linear(d):
    c1 = np.ones(k.N)
    c2 = np.full(k.N, -50.0)
    c3 = np.full(k.N, 900.0)
    spring = 7
    x = _single_spring_state(d, spring)
    dx = rhs(0.0, x, c1, c2, c3, *MATERIAL)
    expected = d if d >= 0 else d - (-50.0) * d**2 + 900.0 * d**3
    # Spring pulls the body on its left toward the right by `expected`...
    assert dx[2 * (spring + 1) + 1] == pytest.approx(expected / k.M_LAYER, rel=1e-13)
    # ...and the body on its right back by the same amount
    assert dx[2 * (spring + 2) + 1] == pytest.approx(-expected / k.M_LAYER, rel=1e-13)


def test_wall_spring():
    """The last mass pushed toward the wall (positive position) compresses the wall spring."""
    c1, c2, c3 = np.ones(k.N), np.full(k.N, -50.0), np.full(k.N, 900.0)
    x = np.zeros(k.N_STATE)
    x[0] = -1.0
    x[2 * k.N] = 0.01                # last mass moved 0.01 toward the wall
    dx = rhs(0.0, x, c1, c2, c3, *MATERIAL)
    d_wall = -0.01                   # wall spring compressed
    d_left = 0.01                    # spring to its left stretched
    expected = (d_wall + 50.0 * d_wall**2 + 900.0 * d_wall**3) - d_left
    assert dx[2 * k.N + 1] == pytest.approx(expected / k.M_LAYER, rel=1e-13)
