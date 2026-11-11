"""
Simulate many designs in parallel and append the results to a CSV.

Same output as generate_data.m: columns c2_A..c2_D, c3_A..c3_D, KE_ratio, full
precision, header written only when the file is new, NaN when a design fails.

Worker processes only compute. The main process writes every row, in the same
order as the input designs, as soon as it is ready, so a run that is stopped
partway still leaves every finished row on disk.
"""

import os
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from .main_disorder import main_disorder_v2

COLUMNS = ["c2_A", "c2_B", "c2_C", "c2_D", "c3_A", "c3_B", "c3_C", "c3_D", "KE_ratio"]


def _run_one(job):
    """Simulate one design in a worker. Returns (ratio, seconds, error message or None)."""
    simulate, c2, c3 = job
    start = time.perf_counter()
    try:
        ratio = float(simulate(c2, c3))
        error = None
    except Exception as exc:  # record and keep going, like MATLAB's try/catch
        ratio, error = float("nan"), f"{type(exc).__name__}: {exc}"
    return ratio, time.perf_counter() - start, error


def _limit_threads():
    """One process per core: stop numerical libraries from starting extra threads."""
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
        os.environ[var] = "1"


def generate_data(c2, c3, out_file, workers=1, simulate=main_disorder_v2, verbose=True):
    """Simulate every design (rows of the (n, 4) arrays c2, c3) and append to out_file.

    Returns a dict with n, n_failed, mean_runtime_s and total_s."""
    c2 = np.asarray(c2, float)
    c3 = np.asarray(c3, float)
    n = len(c2)
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if not out_file.exists():
        out_file.write_text(",".join(COLUMNS) + "\n")

    jobs = [(simulate, c2[i], c3[i]) for i in range(n)]
    runtimes, n_failed = [], 0
    total_start = time.perf_counter()

    _limit_threads()
    with ProcessPoolExecutor(max_workers=max(1, workers), initializer=_limit_threads) as pool:
        # map() hands results back in input order, so rows are written in design order
        for i, (ratio, seconds, error) in enumerate(pool.map(_run_one, jobs, chunksize=1)):
            if error is not None:
                n_failed += 1
                warnings.warn(f"Design {i + 1} failed: {error}")
            values = list(c2[i]) + list(c3[i]) + [ratio]
            with out_file.open("a") as fh:
                fh.write(",".join(f"{v:.17g}" for v in values) + "\n")
            runtimes.append(seconds)
            if verbose:
                print(f"[{i + 1}/{n}]  KE ratio = {ratio:.17g}   ({seconds:.2f} s)", flush=True)

    total = time.perf_counter() - total_start
    if verbose:
        print(f"Done: {n} designs in {total:.1f} s ({n_failed} failed). Saved to {out_file.resolve()}",
              file=sys.stdout, flush=True)
    return {"n": n, "n_failed": n_failed,
            "mean_runtime_s": float(np.mean(runtimes)) if runtimes else float("nan"),
            "total_s": total}
