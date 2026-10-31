"""main_disorder_v2: output grid, input handling, physics sanity checks, and solver agreement."""

import math

import numpy as np
import pandas as pd
import pytest
from scipy.integrate import solve_ivp

from simulation.python_simulation import constants as k
from simulation.python_simulation.equations_of_motion import rhs
from simulation.python_simulation.main_disorder import (initial_state, main_disorder_v2,
                                                       output_grid)

EXAMPLE_C2 = [-70, -100, -5, -35]      # hard-coded design in main_disorder.m
EXAMPLE_C3 = [1200, 2000, 1500, 3000]
MATLAB_5000 = "data/raw/matlab_uniform_5000.csv"


# ---------------------------------------------------------------------------
# Output grid (MATLAB's 0:dt:T)
# ---------------------------------------------------------------------------

def test_grid_matches_matlab_formula():
    grid = output_grid(EXAMPLE_C2, EXAMPLE_C3)
    k_f = 1 + 2 * -35 + 3 * 3000                # stiffest family (D)
    dt = 1 / (1 / (2 * math.pi) * math.sqrt(k_f / k.M0_IMPACTOR)) / 100
    assert grid[0] == 0.0
    assert grid[1] == pytest.approx(dt, rel=1e-14)
    assert len(grid) == 236260                  # MATLAB: numel(0:dt:T)
    assert grid[-1] <= k.T_END * (1 + 1e-12)
    assert k.T_END - grid[-1] < dt


def test_grid_for_linear_design_includes_endpoint():
    """T/dt is exactly 2500 for k_f = 1; round-off must not drop the last point."""
    grid = output_grid([0] * 4, [0] * 4)
    assert len(grid) == 2501
    assert grid[-1] == pytest.approx(k.T_END, rel=1e-12)


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def test_accepts_row_and_column_vectors():
    col = output_grid(np.array(EXAMPLE_C2).reshape(4, 1), np.array(EXAMPLE_C3).reshape(4, 1))
    np.testing.assert_array_equal(col, output_grid(EXAMPLE_C2, EXAMPLE_C3))


@pytest.mark.parametrize("bad", [[1, 2, 3], [1, 2, 3, 4, 5], np.zeros((2, 2))])
def test_rejects_wrong_number_of_families(bad):
    with pytest.raises(ValueError):
        main_disorder_v2(bad, EXAMPLE_C3)


def test_rejects_unknown_solver():
    with pytest.raises(ValueError):
        main_disorder_v2(EXAMPLE_C2, EXAMPLE_C3, solver="ode45")


# ---------------------------------------------------------------------------
# Physics sanity checks (no MATLAB needed)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("solver", ["numba", "scipy"])
def test_linear_design_gives_ratio_exactly_one(solver):
    """With c2 = c3 = 0 the 'nonlinear' chain is the linear chain."""
    assert main_disorder_v2([0] * 4, [0] * 4, solver=solver) == 1.0


def total_energy(y, c3):
    """Kinetic + spring + contact energy for a chain with c1 = 1, c2 = 0."""
    pos, vel = y[0::2], y[1::2]
    masses = np.r_[k.M_IMPACTOR, np.full(k.N, k.M_LAYER)]
    kinetic = 0.5 * np.sum(masses[:, None] * vel**2, axis=0)
    d = np.vstack([pos[2:] - pos[1:-1], -pos[-1:]])          # spring length changes
    compressed = d < 0
    spring = 0.5 * d**2 + np.where(compressed, c3[:, None] * d**4 / 4, 0.0)
    overlap = np.clip(pos[0] - pos[1], 0, None)
    contact = 0.4 * k.C_IMPACT * overlap**2.5
    return kinetic + spring.sum(axis=0) + contact


def test_energy_conserved_without_damping():
    """No damping (zeta = 0): kinetic + stored energy stays constant. Uses a
    cubic-stiffening chain so the compression branch of the RHS is exercised."""
    c1, c2, c3 = np.ones(k.N), np.zeros(k.N), np.full(k.N, 2000.0)
    sol = solve_ivp(rhs, (0, 200), initial_state(), method="DOP853", rtol=1e-12, atol=1e-14,
                    t_eval=np.linspace(0, 200, 401),
                    args=(c1, c2, c3, k.M_LAYER, k.M_IMPACTOR, k.C_IMPACT, 0.0))
    energy = total_energy(sol.y, c3)
    assert np.ptp(energy) / energy[0] < 1e-8


# ---------------------------------------------------------------------------
# Full simulations
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_example_design_is_finite_positive_and_deterministic():
    first = main_disorder_v2(EXAMPLE_C2, EXAMPLE_C3)
    assert np.isfinite(first) and first > 0
    assert main_disorder_v2(EXAMPLE_C2, EXAMPLE_C3) == first


@pytest.mark.slow
def test_numba_solver_matches_scipy_reference():
    """The custom stepper agrees with scipy's RK45 on the example design and
    10 designs from the MATLAB 5000-row file."""
    df = pd.read_csv(MATLAB_5000, float_precision="round_trip").head(10)
    designs = [(EXAMPLE_C2, EXAMPLE_C3)] + [
        (row[["c2_A", "c2_B", "c2_C", "c2_D"]].to_numpy(), row[["c3_A", "c3_B", "c3_C", "c3_D"]].to_numpy())
        for _, row in df.iterrows()]
    for c2, c3 in designs:
        fast = main_disorder_v2(c2, c3, solver="numba")
        ref = main_disorder_v2(c2, c3, solver="scipy")
        assert fast == pytest.approx(ref, rel=1e-6), (c2, c3)
