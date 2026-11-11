"""
Fixed simulation parameters, copied from main_disorder_v2.m.

Everything is nondimensional. Only the spring coefficients c2 and c3 change
from design to design; everything here stays the same.
"""

import math

N = 20                  # number of masses in the chain (impactor not counted)
FAMILY_SIZE = 5         # springs per family; 4 families (A-D) x 5 = 20 springs
M_LAYER = 1.0           # mass of each chain mass
ZETA = 0.02             # viscous damping parameter

M0_IMPACTOR = N / 2     # half the chain mass
M_IMPACTOR = 0.01 * M0_IMPACTOR
V_IMPACTOR = 0.25
C_IMPACT = 1.2e4        # Hertzian contact stiffness

RTOL = 1e-12            # ode45 RelTol
ATOL = 1e-12            # ode45 AbsTol (same for every state component)

CYCLES = 25             # simulated time = 25 periods of the slowest linear mode
OUTPUT_PER_CYCLE = 100  # output points per period of the stiffest mode

F0 = 1 / (2 * math.pi) * math.sqrt(1 / M0_IMPACTOR)
T_END = CYCLES / F0     # T in main_disorder_v2.m

N_STATE = 2 * (N + 1)   # positions and velocities of the impactor + N masses
