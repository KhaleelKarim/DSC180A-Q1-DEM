"""
dataset.py -- Drive MATLAB's generate_data from Python.

Run from the project root:
    python src/dataset.py 100
    python src/dataset.py 100 --out data/raw/batch2.csv --seed 42
"""

import subprocess
import argparse


def generate(n_samples: int, out_file: str = "data/raw/ke_ratio_data.csv", seed: int = 0) -> None:
    """Call MATLAB's generate_data function from the project root."""
    cmd = f"addpath('simulation'); generate_data({n_samples}, '{out_file}', {seed})"
    subprocess.run(["matlab", "-batch", cmd], check=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate KE-ratio data via MATLAB simulation.")
    p.add_argument("n_samples", type=int, help="Number of random designs to simulate")
    p.add_argument("--out", default="data/raw/ke_ratio_data.csv", metavar="FILE",
                   help="CSV file to write/append to (default: data/raw/ke_ratio_data.csv)")
    p.add_argument("--seed", type=int, default=0, help="Random seed (default: 0)")
    args = p.parse_args()

    generate(args.n_samples, args.out, args.seed)
