"""
dataset.py -- Generate KE-ratio data with the Python (default) or MATLAB simulation.

Run from anywhere:
    python src/dataset.py 1000                     # Python, seed 0 -> data/raw/python_seed0.csv
    python src/dataset.py 1000 --seed 3            # -> data/raw/python_seed3.csv
    python src/dataset.py 100 --lang matlab --seed 2 --out data/raw/batch.csv
    python src/dataset.py --designs data/raw/matlab_uniform_5000.csv   # re-run given designs (Python only)

Both languages sample valid designs the same way (uniform + rejection of
(2/9)*c2^2 >= c3), but with different random number generators: the same
--seed gives DIFFERENT designs in Python and MATLAB.

Every output CSV gets a sidecar <name>.meta.json with one entry per run (lang,
seed or designs file, n, code version, timing). Running the same lang + seed
(or designs file) into the same CSV twice is refused unless --force is given.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulation.python_simulation.generate_data import COLUMNS  # noqa: E402
from simulation.python_simulation.sampling import is_valid, sample_designs  # noqa: E402

RAW_DIR = PROJECT_ROOT / "data" / "raw"
MATLAB_DIR = "simulation/matlab_simulation"   # relative to PROJECT_ROOT
C2_COLS, C3_COLS = COLUMNS[:4], COLUMNS[4:8]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def default_out(lang, seed, designs_file=None):
    """data/raw/<lang>_seed<seed>.csv, or data/raw/<lang>_<designs stem>.csv with --designs."""
    tag = Path(designs_file).stem if designs_file else f"seed{seed}"
    return RAW_DIR / f"{lang}_{tag}.csv"


def default_workers():
    """CPUs this pod may use. On DSMLP os.cpu_count() reports the whole node
    (e.g. 256), so prefer the Kubernetes CPU limit when it is set."""
    limit = os.environ.get("KUBERNETES_LIMIT_CPU")
    if limit:
        return max(1, int(float(limit)))
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:   # macOS / Windows
        return os.cpu_count() or 1


def read_csv(path):
    """Read floats back exactly as written (pandas' default parser can be off in the last digit)."""
    return pd.read_csv(path, float_precision="round_trip")


def load_designs(path, n=None):
    """(c2, c3) arrays from a CSV with columns c2_A..c3_D; extra columns are ignored."""
    df = read_csv(path)
    missing = [c for c in C2_COLS + C3_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"{path} is missing columns: {', '.join(missing)}")
    if n is not None:
        df = df.head(n)
    c2, c3 = df[C2_COLS].to_numpy(float), df[C3_COLS].to_numpy(float)
    n_invalid = int((~is_valid(c2, c3)).any(axis=1).sum())
    if n_invalid:
        print(f"Warning: {n_invalid} of {len(df)} designs in {path} violate (2/9)*c2^2 < c3; "
              f"simulating them anyway.", file=sys.stderr)
    return c2, c3


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_commit():
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT,
                                capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"
    return (commit or "unknown") + ("+uncommitted-changes" if dirty else "")


def library_versions():
    import numba
    import scipy
    return {"python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "numba": numba.__version__, "pandas": pd.__version__}


# ---------------------------------------------------------------------------
# Sidecar (<out>.meta.json) and duplicate guard
# ---------------------------------------------------------------------------

def meta_path(out_file):
    return Path(out_file).with_suffix(".meta.json")


def read_meta(out_file):
    path = meta_path(out_file)
    if path.exists():
        return json.loads(path.read_text())
    return {"batches": []}


def write_meta(out_file, meta):
    meta_path(out_file).write_text(json.dumps(meta, indent=2) + "\n")


def find_duplicate(out_file, batch, first_design=None):
    """Describe why this batch is already in out_file, or return None.

    Uses the sidecar when there is one. For an older CSV without a sidecar, a
    Python seed run checks whether its first design is already in the file."""
    for old in read_meta(out_file)["batches"]:
        if old["lang"] != batch["lang"]:
            continue
        if batch.get("designs_sha256") and old.get("designs_sha256") == batch["designs_sha256"]:
            return f"designs file {batch['designs_file']} was already run ({old['started']})"
        if batch.get("seed") is not None and old.get("seed") == batch["seed"]:
            return f"{batch['lang']} seed {batch['seed']} was already run ({old['started']})"
    if first_design is not None and Path(out_file).exists() and not meta_path(out_file).exists():
        existing = read_csv(out_file)[C2_COLS + C3_COLS].to_numpy(float)
        if len(existing) and (existing == np.concatenate(first_design)).all(axis=1).any():
            return f"the first design of seed {batch['seed']} is already in the file"
    return None


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def _matlab_str(text):
    """Text as a MATLAB single-quoted string."""
    return "'" + str(text).replace("'", "''") + "'"


def build_matlab_command(n, out_file, seed, matlab_bin="matlab"):
    code = f"addpath({_matlab_str(MATLAB_DIR)}); generate_data({n}, {_matlab_str(out_file)}, {seed})"
    return [matlab_bin, "-batch", code]


def run_matlab(n, out_file, seed, matlab_bin="matlab"):
    if shutil.which(matlab_bin) is None:
        raise SystemExit(f"'{matlab_bin}' was not found on PATH. MATLAB is needed for --lang matlab "
                         f"(use the full path to the executable if it is installed).")
    subprocess.run(build_matlab_command(n, out_file, seed, matlab_bin), check=True, cwd=PROJECT_ROOT)
    rows = read_csv(out_file).tail(n)
    return {"n": n, "n_failed": int(rows["KE_ratio"].isna().sum()), "mean_runtime_s": None}


def run_python(c2, c3, out_file, workers):
    from simulation.python_simulation.generate_data import generate_data
    return generate_data(c2, c3, out_file, workers=workers)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Generate KE-ratio data with the DEM impact simulation.")
    p.add_argument("n_samples", type=int, nargs="?",
                   help="Number of designs to simulate (with --designs: use only the first N)")
    p.add_argument("--lang", choices=["python", "matlab"], default="python",
                   help="Which simulation to run (default: python)")
    p.add_argument("--seed", type=int, default=0,
                   help="Random seed (default: 0). Seeds are language-specific.")
    p.add_argument("--out", metavar="FILE",
                   help="CSV to write/append to (default: data/raw/<lang>_seed<seed>.csv)")
    p.add_argument("--workers", type=int, default=None,
                   help="Parallel worker processes for --lang python (default: CPUs available)")
    p.add_argument("--designs", metavar="FILE",
                   help="Simulate the designs in this CSV instead of sampling (python only)")
    p.add_argument("--force", action="store_true",
                   help="Run even if this lang + seed (or designs file) is already in the output")
    args = p.parse_args(argv)

    if args.n_samples is None and args.designs is None:
        p.error("give n_samples, or --designs FILE")
    if args.n_samples is not None and args.n_samples < 1:
        p.error("n_samples must be at least 1")
    if args.designs and args.lang == "matlab":
        p.error("--designs is only supported with --lang python")
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.workers is not None and args.lang == "matlab":
        print("Note: --workers is ignored for --lang matlab.", file=sys.stderr)
    workers = args.workers or default_workers()

    out_file = Path(args.out).resolve() if args.out else default_out(args.lang, args.seed, args.designs)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    batch = {"lang": args.lang, "started": datetime.now().isoformat(timespec="seconds"),
             "finished": None, "git_commit": git_commit()}
    first_design = None
    if args.designs:
        c2, c3 = load_designs(args.designs, args.n_samples)
        batch.update(seed=None, designs_file=str(args.designs), designs_sha256=file_sha256(args.designs))
    else:
        batch.update(seed=args.seed, designs_file=None, designs_sha256=None)
        if args.lang == "python":
            c2, c3 = sample_designs(args.n_samples, args.seed)
            first_design = (c2[0], c3[0])
    n = args.n_samples if args.lang == "matlab" else len(c2)
    batch.update(n=n, workers=workers if args.lang == "python" else 1,
                 solver="numba" if args.lang == "python" else "ode45",
                 versions=library_versions() if args.lang == "python" else {"matlab": "see MATLAB install"})

    duplicate = find_duplicate(out_file, batch, first_design)
    if duplicate and not args.force:
        raise SystemExit(f"Refusing to append to {out_file}: {duplicate}.\n"
                         f"Use a different --seed or --out, or pass --force to append anyway.")

    # Record the batch before running, so an interrupted run is still caught by the guard
    meta = read_meta(out_file)
    meta["batches"].append(batch)
    write_meta(out_file, meta)

    print(f"Simulating {n} designs with {args.lang} -> {out_file}")
    if args.lang == "matlab":
        result = run_matlab(n, out_file, args.seed)
    else:
        result = run_python(c2, c3, out_file, workers)

    batch.update(finished=datetime.now().isoformat(timespec="seconds"),
                 n_failed=result["n_failed"], mean_runtime_s=result["mean_runtime_s"])
    write_meta(out_file, meta)


if __name__ == "__main__":
    main()
