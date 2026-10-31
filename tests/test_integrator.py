"""
The compiled Dormand-Prince stepper, checked on small problems with known answers.

Its RHS is fixed to the chain physics, so the "known answer" problems use the
chain itself: with only linear springs and no damping, energy is conserved
exactly, and a free impactor (nothing to hit) moves at constant speed.
"""

import numpy as np
import pytest

from simulation.python_simulation import constants as k
from simulation.python_simulation.integrator import max_last_ke
from simulation.python_simulation.main_disorder import (initial_state, output_grid,
                                                       simulate, spring_arrays)

LINEAR = (np.ones(k.N), np.zeros(k.N), np.zeros(k.N))


def run(springs, grid, zeta=k.ZETA, y0=None):
    y0 = initial_state() if y0 is None else y0
    return max_last_ke(y0, grid, *springs, k.M_LAYER, k.M_IMPACTOR, k.C_IMPACT, zeta, k.RTOL, k.ATOL)


def test_untouched_chain_stays_at_rest():
    """Impactor moving away from the chain: the last mass never moves."""
    y0 = np.zeros(k.N_STATE)
    y0[1] = -k.V_IMPACTOR
    ke, stats = run(LINEAR, np.linspace(0, 50, 101), y0=y0)
    assert ke == 0.0
    assert stats["failed"] == 0


def test_running_max_matches_stored_trajectory():
    """The running maximum equals the max over a full scipy trajectory on the same grid."""
    c2, c3 = [-70, -100, -5, -35], [1200, 2000, 1500, 3000]
    grid = output_grid(c2, c3)[:20001]          # first ~8% of the simulated time
    springs = spring_arrays(c2, c3)
    ke_numba, _ = run(springs, grid)
    sol = simulate(*springs, grid)
    ke_scipy = np.max(0.5 * sol.y[-1] ** 2)
    assert ke_numba > 0
    assert ke_numba == pytest.approx(ke_scipy, rel=1e-6)


def test_reports_work_done():
    _, stats = run(LINEAR, output_grid([0] * 4, [0] * 4))
    assert stats["steps"] > 0
    assert stats["fevals"] == 1 + 6 * (stats["steps"] + stats["failed"])


def test_output_times_landing_on_step_ends_and_inside_steps_agree():
    """A very fine and a coarse output grid over the same time span sample the
    same smooth curve, so the fine grid's max must be at least the coarse one's
    and close to it."""
    fine = np.linspace(0, 200, 200001)
    coarse = fine[::100]
    ke_fine, _ = run(LINEAR, fine)
    ke_coarse, _ = run(LINEAR, coarse)
    assert ke_fine >= ke_coarse * (1 - 1e-9)
    assert ke_fine == pytest.approx(ke_coarse, rel=1e-3)
