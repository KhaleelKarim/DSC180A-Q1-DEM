"""
Python version of main_disorder_v2.m: spring coefficients in, KE ratio out.

    ratio = main_disorder_v2(c2, c3)

c2 and c3 hold one value per spring family (A, B, C, D). The function runs two
impact simulations, one with the nonlinear springs and one with an otherwise
identical linear chain, and returns
    max KE of the last mass (nonlinear) / max KE of the last mass (linear).

Two interchangeable solvers:
    solver="numba"  custom compiled Dormand-Prince stepper (fast, default)
    solver="scipy"  scipy.integrate.solve_ivp RK45 (trusted reference)
"""

import math

import numpy as np
from scipy.integrate import solve_ivp

from . import constants as k
from .equations_of_motion import rhs
from .integrator import max_last_ke


def _family_vector(c, name):
    """Accept shape (4,) or (4, 1), like MATLAB's 4x1 column."""
    c = np.asarray(c, dtype=float)
    if c.size != 4 or c.ndim > 2 or (c.ndim == 2 and 1 not in c.shape):
        raise ValueError(f"{name} must have 4 values (one per family), got shape {c.shape}")
    return c.reshape(4)


def output_grid(c2, c3):
    """Output times 0:dt:T, built the same way as main_disorder_v2.m.

    dt is 1/100 of the period of the stiffest spring, using the tangent
    stiffness 1 + 2*c2 + 3*c3 (CLAUDE.md known issue #1 -- kept on purpose)."""
    c2 = _family_vector(c2, "c2")
    c3 = _family_vector(c3, "c3")
    k_f = max(1.0, float(np.max(1 + 2 * c2 + 3 * c3)))
    f = 1 / (2 * math.pi) * math.sqrt(k_f / k.M0_IMPACTOR)
    dt = (1 / f) / k.OUTPUT_PER_CYCLE
    # Like MATLAB's colon operator, tolerate round-off when T/dt is a whole number
    q = k.T_END / dt
    n = round(q) if abs(q - round(q)) <= 1e-10 * q else math.floor(q)
    return np.arange(n + 1) * dt


def spring_arrays(c2, c3):
    """Expand the 4 family values into 20 per-spring arrays (MATLAB repelem)."""
    c1 = np.ones(k.N)
    C2 = np.repeat(_family_vector(c2, "c2"), k.FAMILY_SIZE)
    C3 = np.repeat(_family_vector(c3, "c3"), k.FAMILY_SIZE)
    return c1, C2, C3


def initial_state():
    y0 = np.zeros(k.N_STATE)
    y0[1] = k.V_IMPACTOR
    return y0


def _material():
    return (k.M_LAYER, k.M_IMPACTOR, k.C_IMPACT, k.ZETA)


def simulate(c1, c2, c3, t_grid):
    """Full trajectory with scipy (rows = state components, columns = times).
    Used by the scipy solver, and for plotting/debugging."""
    args = (c1, c2, c3) + _material()
    sol = solve_ivp(rhs, (t_grid[0], t_grid[-1]), initial_state(), method="RK45",
                    t_eval=t_grid, rtol=k.RTOL, atol=k.ATOL, args=args)
    if not sol.success:
        raise RuntimeError(f"solve_ivp failed: {sol.message}")
    return sol


def _max_last_ke_scipy(c1, c2, c3, t_grid):
    sol = simulate(c1, c2, c3, t_grid)
    return float(np.max(0.5 * sol.y[2 * k.N + 1] ** 2))


def _max_last_ke_numba(c1, c2, c3, t_grid):
    ke, _stats = max_last_ke(initial_state(), t_grid, c1, c2, c3, *_material(), k.RTOL, k.ATOL)
    return ke


def main_disorder_v2(c2, c3, solver="numba"):
    """KE ratio for one design. c2, c3: 4 values each (families A-D)."""
    if solver == "numba":
        max_ke = _max_last_ke_numba
    elif solver == "scipy":
        max_ke = _max_last_ke_scipy
    else:
        raise ValueError(f"solver must be 'numba' or 'scipy', got {solver!r}")

    t_grid = output_grid(c2, c3)
    c1, C2, C3 = spring_arrays(c2, c3)
    zeros = np.zeros(k.N)

    ke_lin = max_ke(c1, zeros, zeros, t_grid)
    ke_non = max_ke(c1, C2, C3, t_grid)
    return ke_non / ke_lin
