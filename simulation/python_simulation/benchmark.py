"""
Time one design (the example from main_disorder.m) with both solvers.

Run from the project root:
    python -m simulation.python_simulation.benchmark
Compare against MATLAB:  tic; main_disorder_v2([-70;-100;-5;-35],[1200;2000;1500;3000]); toc
"""

import os
import statistics
import time

from . import constants as k
from .integrator import max_last_ke
from .main_disorder import initial_state, main_disorder_v2, output_grid, spring_arrays

C2 = [-70, -100, -5, -35]
C3 = [1200, 2000, 1500, 3000]
REPEATS = 3


def _timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def main():
    workers = int(float(os.environ.get("KUBERNETES_LIMIT_CPU", len(os.sched_getaffinity(0)))))
    print(f"Example design c2={C2}, c3={C3}; output grid: {len(output_grid(C2, C3))} points\n")

    _, compile_s = _timed(lambda: main_disorder_v2(C2, C3, solver="numba"))
    print(f"numba warm-up (includes one-time compilation): {compile_s:.2f} s\n")

    for solver in ("numba", "scipy"):
        times = []
        for _ in range(REPEATS):
            ratio, seconds = _timed(lambda: main_disorder_v2(C2, C3, solver=solver))
            times.append(seconds)
        per_design = statistics.median(times)
        print(f"{solver:5s}: KE ratio = {ratio:.12g}, median {per_design:.3f} s/design "
              f"-> ~{workers * 3600 / per_design:,.0f} designs/hour on {workers} workers")

    # Where the numba solver spends its effort
    c1, c2, c3 = spring_arrays(C2, C3)
    grid = output_grid(C2, C3)
    material = (k.M_LAYER, k.M_IMPACTOR, k.C_IMPACT, k.ZETA, k.RTOL, k.ATOL)
    for label, (a, b) in {"linear": (c2 * 0, c3 * 0), "nonlinear": (c2, c3)}.items():
        (_, stats), seconds = _timed(lambda: max_last_ke(initial_state(), grid, c1, a, b, *material))
        print(f"  {label:9s} solve: {seconds:.3f} s, {stats['steps']} steps, "
              f"{stats['failed']} rejected, {stats['fevals']} RHS calls")


if __name__ == "__main__":
    main()
