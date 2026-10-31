"""
Equations of motion for the impactor + chain (impact_equation_of_motion_hetero.m).

Given the current state of every body, return how fast that state is changing.
This is the "right-hand side" (RHS) that the ODE solver calls over and over.

State layout (same as MATLAB, but 0-based): for body b = 0..N,
    x[2b]   = position of body b
    x[2b+1] = velocity of body b
Body 0 is the impactor, bodies 1..N are the chain masses, and body N is tied
to the wall by the last spring. Spring k (k = 0..N-1) sits to the right of
body k+1; spring N-1 connects body N to the wall.

Two versions with identical physics:
    rhs_reference  a line-for-line port of the MATLAB file (slow, used in tests)
    rhs            a compact numba version (fast, used by the solvers)
"""

import numpy as np
from numba import njit

from .impact_force import impact_force


# ---------------------------------------------------------------------------
# Reference version: mirrors impact_equation_of_motion_hetero.m branch by branch
# ---------------------------------------------------------------------------

def rhs_reference(t, x, c1, c2, c3, m, m_impact, C_impact, zeta, F=0.0):
    num_mass = len(x) // 2
    dx = np.zeros(len(x))
    pos = lambda b: x[2 * b]
    vel = lambda b: x[2 * b + 1]

    # Impactor
    dx[0] = vel(0)
    dx[1] = (F - impact_force(C_impact, pos(0), pos(1))) / m_impact

    # First chain mass (MATLAB i = 2)
    b = 1
    dx[2 * b] = vel(b)
    d = pos(b + 1) - pos(b)
    if pos(b + 1) >= pos(b):
        dx[2 * b + 1] = (c1[b - 1] * d
                         + impact_force(C_impact, pos(b - 1), pos(b))
                         - 2 * zeta * (-vel(b + 1) + vel(b))) / m
    else:
        dx[2 * b + 1] = (c1[b - 1] * d - c2[b - 1] * d**2 + c3[b - 1] * d**3
                         + impact_force(C_impact, pos(b - 1), pos(b))
                         - 2 * zeta * (-vel(b + 1) + vel(b))) / m

    # Middle masses (MATLAB i = 3 .. num_mass-1)
    for b in range(2, num_mass - 1):
        dx[2 * b] = vel(b)
        d = pos(b + 1) - pos(b)
        if pos(b + 1) >= pos(b):
            force_spring1 = c1[b - 1] * d
        else:
            force_spring1 = c1[b - 1] * d - c2[b - 1] * d**2 + c3[b - 1] * d**3
        e = pos(b) - pos(b - 1)
        if pos(b) >= pos(b - 1):
            force_spring2 = -c1[b - 2] * e
        else:
            force_spring2 = -c1[b - 2] * e + c2[b - 2] * e**2 - c3[b - 2] * e**3
        dx[2 * b + 1] = (force_spring1 + force_spring2
                         - 2 * zeta * (-vel(b + 1) + 2 * vel(b) - vel(b - 1))) / m

    # Last mass, attached to the wall (MATLAB i = num_mass)
    b = num_mass - 1
    dx[2 * b] = vel(b)
    d = 0 - pos(b)
    if 0 >= pos(b):
        force_spring1 = c1[b - 1] * d
    else:
        force_spring1 = c1[b - 1] * d - c2[b - 1] * d**2 + c3[b - 1] * d**3
    e = pos(b) - pos(b - 1)
    if pos(b) >= pos(b - 1):
        force_spring2 = -c1[b - 2] * e
    else:
        force_spring2 = -c1[b - 2] * e + c2[b - 2] * e**2 - c3[b - 2] * e**3
    dx[2 * b + 1] = (force_spring1 + force_spring2
                     - 2 * zeta * (vel(b) - vel(b - 1)) - 2 * zeta * vel(b)) / m

    return dx


# ---------------------------------------------------------------------------
# Fast version
# ---------------------------------------------------------------------------

@njit(cache=True)
def spring_force(d, c1, c2, c3):
    """Force a spring pulls with when its length change is d (d < 0 = compressed).
    Cubic in compression, linear in tension."""
    if d >= 0.0:
        return c1 * d
    return c1 * d - c2 * d * d + c3 * d * d * d


@njit(cache=True)
def rhs_into(x, c1, c2, c3, m, m_impact, C_impact, zeta, out):
    """Write dx/dt into `out` (no allocation; used inside the integrator loop).

    Each spring k carries a force s_k = spring + damper. It pulls body k+1 to
    the right and body k+2 (or the wall) to the left, so the net force on body
    b is s_{b-1} - s_{b-2}."""
    n = c1.shape[0]
    contact = impact_force(C_impact, x[0], x[2])
    out[0] = x[1]
    out[1] = -contact / m_impact

    left = 0.0  # force of the spring to the left of the current body
    for b in range(1, n + 1):
        k = b - 1
        if b < n:
            d = x[2 * b + 2] - x[2 * b]
            dv = x[2 * b + 3] - x[2 * b + 1]
        else:  # wall spring: the wall sits at 0 and does not move
            d = -x[2 * b]
            dv = -x[2 * b + 1]
        right = spring_force(d, c1[k], c2[k], c3[k]) + 2.0 * zeta * dv
        out[2 * b] = x[2 * b + 1]
        out[2 * b + 1] = (right - left) / m
        left = right
    out[3] += contact / m


@njit(cache=True)
def rhs(t, x, c1, c2, c3, m, m_impact, C_impact, zeta):
    out = np.empty_like(x)
    rhs_into(x, c1, c2, c3, m, m_impact, C_impact, zeta, out)
    return out
