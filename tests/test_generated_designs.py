"""
Check CSVs produced by simulation/generate_data.m contain only valid designs.

Every file matching data/raw/valid_*.csv is checked. Run from the project root:
    pytest tests/test_generated_designs.py -s
(-s shows the spring-category breakdown printed for each file.)
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((PROJECT_ROOT / "data" / "raw").glob("valid_*.csv"))

C2_COLS = ["c2_A", "c2_B", "c2_C", "c2_D"]
C3_COLS = ["c3_A", "c3_B", "c3_C", "c3_D"]
COLUMNS = C2_COLS + C3_COLS + ["KE_ratio"]

pytestmark = pytest.mark.skipif(not FILES, reason="no data/raw/valid_*.csv files yet")


def load(path):
    return pd.read_csv(path, float_precision="round_trip")


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_columns(path):
    assert list(load(path).columns) == COLUMNS


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_within_bounds(path):
    d = load(path)
    assert ((d[C2_COLS] >= -120) & (d[C2_COLS] <= 0)).all().all()
    assert ((d[C3_COLS] >= 0) & (d[C3_COLS] <= 4000)).all().all()


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_positive_strain_energy(path):
    """Every family must satisfy (2/9)*c2^2 < c3 (paper Methods 5.2, SI-2)."""
    d = load(path)
    c2, c3 = d[C2_COLS].to_numpy(), d[C3_COLS].to_numpy()
    bad_rows = np.flatnonzero(((2 / 9) * c2**2 >= c3).any(axis=1))
    assert bad_rows.size == 0, f"rows violating the constraint: {bad_rows.tolist()}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_category_breakdown(path):
    """Informational: share of springs per SI-3 category (q = c2^2 / c3).
    For large files, expect roughly 83% monotonic, 12.5% snap-through, 4.5% bistable."""
    d = load(path)
    q = (d[C2_COLS].to_numpy() ** 2 / d[C3_COLS].to_numpy()).ravel()
    shares = {
        "monotonic (q<3)": np.mean(q < 3),
        "snap-through (3<=q<4)": np.mean((q >= 3) & (q < 4)),
        "bistable (4<=q<4.5)": np.mean(q >= 4),
    }
    print(f"\n{path.name}: {len(d)} designs, {q.size} springs")
    for name, share in shares.items():
        print(f"  {name:24s} {share:6.1%}")
    print(f"  KE ratio range: {d['KE_ratio'].min():.4g} to {d['KE_ratio'].max():.4g}")
