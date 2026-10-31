"""
Hertzian contact force between the impactor and the first mass (impact_force.m).

The contact only pushes, never pulls: if the impactor (position x1) has moved
past the first mass (position x2), they overlap by x1 - x2 and the force is
C * overlap^(3/2). Otherwise they are apart and the force is zero, which lets
the impactor bounce off.
"""

from numba import njit


@njit(cache=True)
def impact_force(C, x1, x2):
    if x1 > x2:
        return C * (x1 - x2) ** 1.5
    return 0.0
