"""Parallel runner: CSV format, row order, failures, appending."""

import time

import numpy as np
import pandas as pd
import pytest

from simulation.python_simulation.generate_data import COLUMNS, generate_data
from simulation.python_simulation.sampling import sample_designs


# Stand-in simulations (module level so worker processes can import them)
def fake_sim(c2, c3):
    """Instant 'KE ratio' that identifies the design; earlier designs sleep
    longer so they finish last unless the runner restores input order."""
    time.sleep(0.02 * (c2[0] + 120) / 120)
    return -c2[0]


def failing_sim(c2, c3):
    if c2[0] < -60:
        raise RuntimeError("boom")
    return 1.0


def read(path):
    return pd.read_csv(path, float_precision="round_trip")


def test_columns_and_full_precision(tmp_path):
    c2, c3 = sample_designs(3, seed=0)
    out = tmp_path / "x.csv"
    generate_data(c2, c3, out, workers=2, simulate=fake_sim, verbose=False)
    df = read(out)
    assert list(df.columns) == COLUMNS
    np.testing.assert_array_equal(df[COLUMNS[:4]].to_numpy(), c2)   # exact round trip
    np.testing.assert_array_equal(df[COLUMNS[4:8]].to_numpy(), c3)


def test_rows_in_design_order_with_several_workers(tmp_path):
    c2, c3 = sample_designs(12, seed=1)
    out = tmp_path / "x.csv"
    generate_data(c2, c3, out, workers=3, simulate=fake_sim, verbose=False)
    np.testing.assert_array_equal(read(out)["KE_ratio"].to_numpy(), -c2[:, 0])


def test_failed_design_recorded_as_nan(tmp_path):
    c2, c3 = sample_designs(10, seed=2)
    out = tmp_path / "x.csv"
    with pytest.warns(UserWarning, match="failed"):
        result = generate_data(c2, c3, out, workers=2, simulate=failing_sim, verbose=False)
    ratios = read(out)["KE_ratio"].to_numpy()
    expected_nan = c2[:, 0] < -60
    np.testing.assert_array_equal(np.isnan(ratios), expected_nan)
    assert result["n_failed"] == expected_nan.sum()


def test_append_keeps_single_header(tmp_path):
    out = tmp_path / "x.csv"
    for seed in (3, 4):
        c2, c3 = sample_designs(2, seed=seed)
        generate_data(c2, c3, out, workers=1, simulate=fake_sim, verbose=False)
    assert out.read_text().count("c2_A") == 1
    assert len(read(out)) == 4


@pytest.mark.slow
def test_real_simulation_two_designs(tmp_path):
    c2, c3 = sample_designs(2, seed=5)
    out = tmp_path / "x.csv"
    result = generate_data(c2, c3, out, workers=2, verbose=False)
    ratios = read(out)["KE_ratio"]
    assert result["n_failed"] == 0
    assert (np.isfinite(ratios) & (ratios > 0)).all()
