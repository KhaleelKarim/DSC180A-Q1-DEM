"""
Random valid designs: the same algorithm as generate_data.m.

Each (c2, c3) pair is drawn uniformly from c2 in [-120, 0], c3 in [0, 4000].
Pairs that violate the positive-strain-energy constraint (2/9)*c2^2 < c3
(paper Methods 5.2, SI-2) are redrawn as a pair until every family is valid,
so the designs are uniform over the valid region.

The algorithm matches MATLAB, but the random numbers do not: the same seed
gives different designs in Python and MATLAB.
"""

import numpy as np

C2_RANGE = (-120.0, 0.0)
C3_RANGE = (0.0, 4000.0)
N_FAMILIES = 4


def is_valid(c2, c3):
    """True where a (c2, c3) pair satisfies the positive-strain-energy constraint."""
    return (2 / 9) * np.asarray(c2) ** 2 < np.asarray(c3)


def sample_designs(n, seed=0):
    """Return (c2, c3), each an (n, 4) array: one row per design, one column per family."""
    rng = np.random.default_rng(seed)

    def draw(size):
        return (rng.uniform(*C2_RANGE, size), rng.uniform(*C3_RANGE, size))

    c2, c3 = draw((n, N_FAMILIES))
    bad = ~is_valid(c2, c3)
    while bad.any():
        c2[bad], c3[bad] = draw(int(bad.sum()))
        bad = ~is_valid(c2, c3)
    return c2, c3
