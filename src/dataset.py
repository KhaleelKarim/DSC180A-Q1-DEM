"""
dataset.py -- Generate KE-ratio data by running the simulation in MATLAB or Octave.

Run from anywhere (paths are resolved relative to the project root):
    python src/dataset.py 100                                  # MATLAB (default), seed 0
    python src/dataset.py 100 --seed 42 --out data/raw/x.csv   # MATLAB, custom file
    python src/dataset.py 200000 --program octave --workers 8  # Octave, 8 parallel workers
    python src/dataset.py --program octave --designs data/raw/LHS_20_samples.csv

MATLAB path: calls simulation/matlab/generate_data.m, which samples and simulates
designs itself (one process).

Octave path: Python samples the designs (or reads them from --designs), splits them
into one chunk per worker, starts one Octave process per chunk running
simulation/octave/run_designs.m, and merges the per-worker "shard" CSVs at the end.
Shards live in data/raw/<name>_work/. If the run is interrupted, rerunning the same
command skips designs that are already finished.

Note: MATLAB and Python Latin hypercube samplers differ, so the same seed gives
different designs in the two pathways.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import qmc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

COEF_COLS = ["c2_A", "c2_B", "c2_C", "c2_D", "c3_A", "c3_B", "c3_C", "c3_D"]
DESIGN_COLS = ["design_id"] + COEF_COLS
VALID_STATUS = {"ok", "error"}

# Design space from the paper's Methods section
C2_RANGE = (-120.0, 0.0)
C3_RANGE = (0.0, 4000.0)

FULL_PRECISION = "%.17g"   # enough digits to reproduce a double exactly


def read_csv(path, **kwargs) -> pd.DataFrame:
    """pd.read_csv that reads floats back exactly. pandas < 3's default parser can
    be off in the last digit; pandas >= 3 is exact by default (and deprecates the flag)."""
    if int(pd.__version__.split(".")[0]) < 3:
        kwargs.setdefault("float_precision", "round_trip")
    return pd.read_csv(path, **kwargs)


# ---------------------------------------------------------------------------
# Designs
# ---------------------------------------------------------------------------

def make_lhs_designs(n: int, seed: int = 0) -> pd.DataFrame:
    """Latin hypercube sample of n designs over the paper's design space."""
    try:
        sampler = qmc.LatinHypercube(d=8, rng=seed)    # SciPy >= 1.15
    except TypeError:
        sampler = qmc.LatinHypercube(d=8, seed=seed)   # older SciPy
    unit = sampler.random(n)                           # values in [0, 1)

    lower = np.array([C2_RANGE[0]] * 4 + [C3_RANGE[0]] * 4)
    upper = np.array([C2_RANGE[1]] * 4 + [C3_RANGE[1]] * 4)
    designs = pd.DataFrame(lower + (upper - lower) * unit, columns=COEF_COLS)
    designs.insert(0, "design_id", np.arange(n))
    return designs


def load_designs(path) -> pd.DataFrame:
    """Read designs from a CSV. Extra columns (e.g. KE_ratio) are ignored."""
    df = read_csv(path)
    missing = [c for c in COEF_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(missing)}")
    if "design_id" not in df.columns:
        df["design_id"] = np.arange(len(df))
    df = df[DESIGN_COLS].copy()
    df["design_id"] = df["design_id"].astype(int)
    if df["design_id"].duplicated().any():
        raise ValueError(f"{path} has duplicate design_id values")
    return df


def output_name(program: str, n: int, seed: int = 0, designs_path=None) -> Path:
    """Automatic output file: data/raw/<program>_<n>_seed<seed>.csv
    (or <program>_<n>_<designs-file-stem>.csv when designs come from a file)."""
    tag = Path(designs_path).stem if designs_path else f"seed{seed}"
    return RAW_DIR / f"{program}_{n}_{tag}.csv"


def split_chunks(df: pd.DataFrame, k: int) -> list:
    """Split df into at most k near-equal, non-empty chunks."""
    k = max(1, min(k, len(df)))
    return [df.iloc[idx] for idx in np.array_split(np.arange(len(df)), k)]


# ---------------------------------------------------------------------------
# Shards (per-worker outputs)
# ---------------------------------------------------------------------------

def read_shards(work_dir) -> pd.DataFrame:
    """All complete result rows from the worker shards in work_dir.

    A row cut off mid-write has a missing or partial 'status' (the last column),
    so it is dropped here and that design gets re-run on resume.
    """
    frames = []
    for shard in sorted(Path(work_dir).glob("out_*.csv")):
        try:
            df = read_csv(shard, on_bad_lines="skip")
        except pd.errors.EmptyDataError:   # worker hasn't written its header yet
            continue
        if "status" in df.columns:
            frames.append(df[df["status"].isin(VALID_STATUS)])
    if not frames:
        return pd.DataFrame(columns=DESIGN_COLS + ["KE_ratio", "runtime_s", "status"])
    results = pd.concat(frames, ignore_index=True)
    results["design_id"] = results["design_id"].astype(int)
    return results.drop_duplicates("design_id")


def read_completed(work_dir) -> set:
    """design_ids that already have a complete result row."""
    return set(read_shards(work_dir)["design_id"])


def next_run_index(work_dir) -> int:
    """Each (re)launch writes fresh shards out_r<run>_w<k>.csv, so a resumed worker
    never appends after a half-written line from an earlier run."""
    runs = [int(p.name.split("_")[1][1:]) for p in Path(work_dir).glob("out_r*_w*.csv")]
    return max(runs, default=-1) + 1


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def _quote(path) -> str:
    """Path as a MATLAB/Octave single-quoted string."""
    return "'" + str(path).replace("'", "''") + "'"


def build_matlab_command(n: int, out_file, seed: int, matlab_bin: str = "matlab") -> list:
    code = (f"addpath('simulation/core', 'simulation/matlab'); "
            f"generate_data({n}, {_quote(out_file)}, {seed})")
    return [matlab_bin, "-batch", code]


def build_octave_command(in_file, out_file, octave_bin: str = "octave") -> list:
    code = (f"addpath('simulation/core', 'simulation/octave'); "
            f"run_designs({_quote(in_file)}, {_quote(out_file)})")
    return [octave_bin, "--no-gui", "--quiet", "--eval", code]


def default_workers() -> int:
    """CPUs this pod may use. On DSMLP, os.cpu_count() reports the whole node
    (e.g. 256), so prefer the Kubernetes limit when it's set."""
    limit = os.environ.get("KUBERNETES_LIMIT_CPU")
    if limit:
        return max(1, int(float(limit)))
    return os.cpu_count() or 1


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def run_matlab(n: int, out_file: Path, seed: int) -> None:
    """Same as before: MATLAB's generate_data samples and simulates n designs."""
    try:
        out_rel = out_file.relative_to(PROJECT_ROOT)
    except ValueError:
        out_rel = out_file
    subprocess.run(build_matlab_command(n, out_rel, seed), check=True, cwd=PROJECT_ROOT)


def _prepare_work_dir(designs: pd.DataFrame, work_dir: Path) -> None:
    """Save the full design list on the first run; on a resume, make sure the
    work dir really belongs to this same set of designs."""
    work_dir.mkdir(parents=True, exist_ok=True)
    saved = work_dir / "designs.csv"
    if not saved.exists():
        designs.to_csv(saved, index=False, float_format=FULL_PRECISION)
        return
    previous = read_csv(saved)
    same = (len(previous) == len(designs)
            and (previous["design_id"].values == designs["design_id"].values).all()
            and np.array_equal(previous[COEF_COLS].values, designs[COEF_COLS].values))
    if not same:
        raise SystemExit(f"{work_dir} holds a different set of designs. "
                         f"Use a different --out/--seed, or delete that folder to start over.")


def _octave_version(octave_bin: str) -> str:
    try:
        out = subprocess.run([octave_bin, "--version"], capture_output=True, text=True)
        return out.stdout.splitlines()[0]
    except (OSError, IndexError):
        return "unknown"


def _git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=PROJECT_ROOT)
        return out.stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def run_octave(designs: pd.DataFrame, out_file: Path, workers: int,
               octave_bin: str = "octave", poll_seconds: float = 30.0,
               meta: dict = None) -> bool:
    """Simulate all designs with parallel Octave workers. Returns True when the
    merged output file was written, False if some designs are still unfinished."""
    if shutil.which(octave_bin) is None:
        raise SystemExit(f"'{octave_bin}' not found. Activate the environment first: conda activate dem")

    work_dir = out_file.parent / f"{out_file.stem}_work"
    _prepare_work_dir(designs, work_dir)

    done = read_completed(work_dir)
    pending = designs[~designs["design_id"].isin(done)]
    total = len(designs)
    print(f"{len(done)}/{total} designs already done; {len(pending)} to run.")

    if len(pending) > 0:
        run = next_run_index(work_dir)
        chunks = split_chunks(pending, workers)
        env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")

        procs, logs = [], []
        for k, chunk in enumerate(chunks):
            in_file = work_dir / f"in_r{run}_w{k}.csv"
            out_shard = work_dir / f"out_r{run}_w{k}.csv"
            chunk.to_csv(in_file, index=False, float_format=FULL_PRECISION)
            log = open(work_dir / f"log_r{run}_w{k}.txt", "w")
            logs.append(log)
            procs.append(subprocess.Popen(build_octave_command(in_file, out_shard, octave_bin),
                                          cwd=PROJECT_ROOT, env=env,
                                          stdout=log, stderr=subprocess.STDOUT))
        print(f"Started {len(procs)} Octave workers. Logs: {work_dir}/log_r{run}_w*.txt")

        start, start_done = time.time(), len(done)
        try:
            while any(p.poll() is None for p in procs):
                time.sleep(poll_seconds)
                n_done = len(read_completed(work_dir))
                rate = (n_done - start_done) / (time.time() - start)   # designs per second
                eta = (total - n_done) / rate / 3600 if rate > 0 else float("nan")
                print(f"  {n_done}/{total} done  ({rate * 3600:.0f} designs/hour, ETA {eta:.1f} h)",
                      flush=True)
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()
            for p in procs:
                p.wait()
            print("\nStopped. Finished rows are saved; rerun the same command to resume.")
            raise SystemExit(130)
        finally:
            for log in logs:
                log.close()

        failed = [k for k, p in enumerate(procs) if p.returncode != 0]
        if failed:
            print(f"Workers {failed} exited with errors; see their logs in {work_dir}.")

    results = read_shards(work_dir)
    missing = total - len(results)
    if missing > 0:
        print(f"{missing} designs still unfinished; rerun the same command to resume.")
        return False

    results = results.sort_values("design_id")
    results.to_csv(out_file, index=False, float_format=FULL_PRECISION)
    n_err = int((results["status"] == "error").sum())

    meta = dict(meta or {})
    meta.update(program="octave", octave_version=_octave_version(octave_bin),
                git_commit=_git_commit(), n_designs=total, n_errors=n_err,
                workers=workers, finished=datetime.now().isoformat(timespec="seconds"),
                mean_runtime_s=float(results["runtime_s"].mean()))
    out_file.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Done: {total} designs ({n_err} errors). Saved to {out_file}")
    return True


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Generate KE-ratio data via the DEM simulation.")
    p.add_argument("n_samples", type=int, nargs="?",
                   help="Number of designs to simulate (with --designs: use only the first N)")
    p.add_argument("--program", choices=["matlab", "octave"], default="matlab",
                   help="Which program runs the simulation (default: matlab)")
    p.add_argument("--seed", type=int, default=0, help="Random seed for sampling (default: 0)")
    p.add_argument("--designs", metavar="FILE",
                   help="CSV of designs to simulate instead of sampling (octave only for now)")
    p.add_argument("--workers", type=int, default=None,
                   help="Parallel Octave workers (default: CPUs available to this pod)")
    p.add_argument("--out", metavar="FILE",
                   help="Output CSV (default: data/raw/<program>_<n>_seed<seed>.csv)")
    p.add_argument("--octave-bin", default="octave", help="Octave executable (default: octave)")
    args = p.parse_args(argv)

    if args.n_samples is None and args.designs is None:
        p.error("give n_samples, or --designs FILE")
    if args.designs and args.program == "matlab":
        p.error("--designs is not supported with --program matlab yet")
    return args


def main(argv=None) -> None:
    args = parse_args(argv)

    if args.designs:
        designs = load_designs(args.designs)
        if args.n_samples is not None:
            designs = designs.head(args.n_samples)
    else:
        designs = None
    n = len(designs) if designs is not None else args.n_samples

    out_file = Path(args.out) if args.out else output_name(args.program, n, args.seed, args.designs)
    out_file = out_file if out_file.is_absolute() else (Path.cwd() / out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    if args.program == "matlab":
        run_matlab(n, out_file, args.seed)
        return

    if designs is None:
        designs = make_lhs_designs(n, args.seed)
    workers = args.workers or default_workers()
    meta = {"seed": None if args.designs else args.seed, "designs_file": args.designs}
    ok = run_octave(designs, out_file, workers, args.octave_bin, meta=meta)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
