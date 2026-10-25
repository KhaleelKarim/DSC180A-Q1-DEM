"""Tests for src/dataset.py.

Most tests are pure Python. The orchestration tests use a tiny fake 'octave'
script (it writes made-up KE ratios), so splitting, resuming and merging can be
checked in seconds. One test marked `octave` runs the real simulation.

    pytest                # everything (the real-Octave test is skipped if octave is missing)
    pytest -m "not octave"
"""

import shutil
import stat
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import dataset as ds

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATLAB_SAMPLE = PROJECT_ROOT / "data" / "raw" / "LHS_20_samples.csv"


# ---------------------------------------------------------------------------
# Designs
# ---------------------------------------------------------------------------

def test_lhs_shape_and_bounds():
    d = ds.make_lhs_designs(50, seed=1)
    assert list(d.columns) == ds.DESIGN_COLS
    assert list(d["design_id"]) == list(range(50))
    c2, c3 = d[ds.COEF_COLS[:4]].values, d[ds.COEF_COLS[4:]].values
    assert (c2 >= -120).all() and (c2 <= 0).all()
    assert (c3 >= 0).all() and (c3 <= 4000).all()


def test_lhs_one_sample_per_stratum():
    n = 40
    d = ds.make_lhs_designs(n, seed=2)
    unit_c2 = (d[ds.COEF_COLS[:4]].values + 120) / 120
    unit_c3 = d[ds.COEF_COLS[4:]].values / 4000
    for col in np.hstack([unit_c2, unit_c3]).T:
        assert sorted(np.floor(col * n).astype(int)) == list(range(n))


def test_lhs_seed_reproducible():
    pd.testing.assert_frame_equal(ds.make_lhs_designs(10, 3), ds.make_lhs_designs(10, 3))
    assert not ds.make_lhs_designs(10, 3).equals(ds.make_lhs_designs(10, 4))


def test_load_designs_from_matlab_csv():
    d = ds.load_designs(MATLAB_SAMPLE)
    assert list(d.columns) == ds.DESIGN_COLS        # KE_ratio dropped
    assert list(d["design_id"]) == list(range(len(d)))
    raw = ds.read_csv(MATLAB_SAMPLE)
    np.testing.assert_array_equal(d[ds.COEF_COLS].values, raw[ds.COEF_COLS].values)


def test_load_designs_missing_column(tmp_path):
    f = tmp_path / "bad.csv"
    pd.DataFrame({"c2_A": [1.0]}).to_csv(f, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        ds.load_designs(f)


def test_output_name():
    assert ds.output_name("octave", 200000, 0) == ds.RAW_DIR / "octave_200000_seed0.csv"
    assert ds.output_name("matlab", 5, 7) == ds.RAW_DIR / "matlab_5_seed7.csv"
    assert (ds.output_name("octave", 20, 0, "data/raw/LHS_20_samples.csv")
            == ds.RAW_DIR / "octave_20_LHS_20_samples.csv")


@pytest.mark.parametrize("n,k", [(10, 3), (8, 8), (3, 8), (1, 4)])
def test_split_chunks_covers_every_design_once(n, k):
    d = ds.make_lhs_designs(n, 0)
    chunks = ds.split_chunks(d, k)
    assert len(chunks) == min(n, k)
    assert all(len(c) > 0 for c in chunks)
    assert sorted(pd.concat(chunks)["design_id"]) == list(range(n))


# ---------------------------------------------------------------------------
# Shards
# ---------------------------------------------------------------------------

HEADER = "design_id,c2_A,c2_B,c2_C,c2_D,c3_A,c3_B,c3_C,c3_D,KE_ratio,runtime_s,status\n"


def _row(i, status="ok"):
    return f"{i},-1,-2,-3,-4,10,20,30,40,0.5,1.0,{status}\n"


def test_read_completed_ignores_truncated_rows(tmp_path):
    (tmp_path / "out_r0_w0.csv").write_text(HEADER + _row(0) + _row(1, "error") + "2,-1,-2,-3")
    (tmp_path / "out_r0_w1.csv").write_text(HEADER + _row(3) + "4,-1,-2,-3,-4,10,20,30,40,0.5,1.0,o")
    (tmp_path / "out_r0_w2.csv").write_text("")    # header not written yet
    assert ds.read_completed(tmp_path) == {0, 1, 3}


def test_next_run_index(tmp_path):
    assert ds.next_run_index(tmp_path) == 0
    (tmp_path / "out_r0_w0.csv").write_text(HEADER)
    (tmp_path / "out_r2_w1.csv").write_text(HEADER)
    assert ds.next_run_index(tmp_path) == 3


# ---------------------------------------------------------------------------
# Commands and CLI
# ---------------------------------------------------------------------------

def test_build_matlab_command():
    cmd = ds.build_matlab_command(5, "data/raw/matlab_5_seed0.csv", 0)
    assert cmd == ["matlab", "-batch",
                   "addpath('simulation/core', 'simulation/matlab'); "
                   "generate_data(5, 'data/raw/matlab_5_seed0.csv', 0)"]


def test_build_octave_command_quotes_paths():
    cmd = ds.build_octave_command("/a/in.csv", "/b/it's.csv")
    assert cmd[:4] == ["octave", "--no-gui", "--quiet", "--eval"]
    assert "run_designs('/a/in.csv', '/b/it''s.csv')" in cmd[4]


def test_parse_args_defaults():
    a = ds.parse_args(["10"])
    assert (a.n_samples, a.program, a.seed, a.designs, a.workers) == (10, "matlab", 0, None, None)


def test_parse_args_requires_n_or_designs():
    with pytest.raises(SystemExit):
        ds.parse_args(["--program", "octave"])


def test_parse_args_designs_not_supported_for_matlab():
    with pytest.raises(SystemExit):
        ds.parse_args(["--designs", str(MATLAB_SAMPLE)])


def test_default_workers_uses_kubernetes_limit(monkeypatch):
    monkeypatch.setenv("KUBERNETES_LIMIT_CPU", "8")
    assert ds.default_workers() == 8


# ---------------------------------------------------------------------------
# Orchestration with a fake Octave
# ---------------------------------------------------------------------------

FAKE_OCTAVE = '''#!{python}
import re, sys
import pandas as pd
sys.path.insert(0, {root!r})
from src.dataset import read_csv
if "--version" in sys.argv:
    print("fake octave 0.0"); sys.exit(0)
code = sys.argv[-1]
in_file, out_file = re.search(r"run_designs\\('(.*)', '(.*)'\\)", code).groups()
d = read_csv(in_file)
d["KE_ratio"] = d["design_id"] / 1000.0
d["runtime_s"] = 0.0
d["status"] = "ok"
d.to_csv(out_file, index=False, float_format="%.17g")
'''


@pytest.fixture
def fake_octave(tmp_path):
    exe = tmp_path / "octave"
    exe.write_text(FAKE_OCTAVE.format(python=sys.executable, root=str(PROJECT_ROOT)))
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    return str(exe)


def test_run_octave_merges_all_shards(tmp_path, fake_octave):
    designs = ds.make_lhs_designs(13, seed=5)
    out = tmp_path / "octave_13_seed5.csv"
    assert ds.run_octave(designs, out, workers=4, octave_bin=fake_octave, poll_seconds=0.1)

    result = ds.read_csv(out)
    assert list(result["design_id"]) == list(range(13))
    np.testing.assert_array_equal(result[ds.COEF_COLS].values, designs[ds.COEF_COLS].values)
    assert len(list((tmp_path / "octave_13_seed5_work").glob("out_r0_w*.csv"))) == 4
    assert out.with_suffix(".meta.json").exists()


def test_run_octave_resumes_without_duplicates(tmp_path, fake_octave):
    designs = ds.make_lhs_designs(10, seed=6)
    out = tmp_path / "octave_10_seed6.csv"
    work = tmp_path / "octave_10_seed6_work"
    work.mkdir()
    designs.to_csv(work / "designs.csv", index=False, float_format=ds.FULL_PRECISION)
    # An earlier run that finished designs 0-3 and died mid-way through design 4
    (work / "out_r0_w0.csv").write_text(HEADER + "".join(_row(i) for i in range(4)) + "4,-1,-2")

    assert ds.run_octave(designs, out, workers=2, octave_bin=fake_octave, poll_seconds=0.1)
    result = ds.read_csv(out)
    assert list(result["design_id"]) == list(range(10))
    assert (work / "out_r1_w0.csv").exists()            # fresh shards for the resumed run


def test_run_octave_rejects_different_designs(tmp_path, fake_octave):
    out = tmp_path / "octave_5_seed0.csv"
    ds.run_octave(ds.make_lhs_designs(5, 0), out, 1, fake_octave, poll_seconds=0.1)
    with pytest.raises(SystemExit, match="different set of designs"):
        ds.run_octave(ds.make_lhs_designs(5, 1), out, 1, fake_octave, poll_seconds=0.1)


# ---------------------------------------------------------------------------
# Octave copies of the simulation
# ---------------------------------------------------------------------------

def test_main_disorder_v2_vec_matches_original():
    """main_disorder_v2_vec.m must be main_disorder_v2.m with only the function
    name, header comment and ODE function swapped, so a change to the original
    can't silently leave the Octave copy behind."""
    original = (PROJECT_ROOT / "simulation/core/main_disorder_v2.m").read_text()
    copy = (PROJECT_ROOT / "simulation/octave/main_disorder_v2_vec.m").read_text()
    copy_lines = copy.splitlines()
    body = [copy_lines[0]] + [ln for ln in copy_lines[1:4] if not ln.startswith("%")] + copy_lines[4:]
    restored = ("\n".join(body)
                .replace("main_disorder_v2_vec(", "main_disorder_v2(")
                .replace("impact_equation_of_motion_vec(", "impact_equation_of_motion_hetero("))
    assert restored == original.rstrip("\n")


# ---------------------------------------------------------------------------
# Real Octave (slow)
# ---------------------------------------------------------------------------

RHS_CHECK = """
addpath('simulation/core', 'simulation/octave');
rand('seed', 1); randn('seed', 1); N = 20; mat = [1 0.1 1.2e4 0.02]; worst = 0;
for trial = 1:40
  C = [ones(N,1) repelem(-120*rand(4,1),5,1) repelem(4000*rand(4,1),5,1)];
  for k = 1:50
    x = zeros(2*(N+1),1);
    x(1:2:end) = cumsum(0.02*randn(N+1,1)) * (0.1 + rand);
    x(2:2:end) = 0.3*randn(N+1,1);
    a = impact_equation_of_motion_hetero(0, x, C, mat, 0);
    b = impact_equation_of_motion_vec(0, x, C, mat, 0);
    worst = max(worst, max(abs(a - b)) / max(abs(a)));
  end
end
printf('WORST %.17g\\n', worst);
"""


@pytest.mark.octave
@pytest.mark.skipif(shutil.which("octave") is None, reason="octave not on PATH")
def test_vectorized_rhs_matches_original():
    """On 2000 random states (both tension and compression, impactor in and out of
    contact) the vectorized ODE function agrees with the original to rounding error."""
    out = subprocess.run(["octave", "--no-gui", "--quiet", "--eval", RHS_CHECK],
                         capture_output=True, text=True, cwd=PROJECT_ROOT, check=True)
    worst = float(out.stdout.split("WORST")[1])
    assert worst < 1e-14


@pytest.mark.octave
@pytest.mark.skipif(shutil.which("octave") is None, reason="octave not on PATH")
def test_real_octave_two_designs(tmp_path):
    designs = ds.load_designs(MATLAB_SAMPLE).head(2)
    out = tmp_path / "octave_2_real.csv"
    assert ds.run_octave(designs, out, workers=2, poll_seconds=5)
    result = ds.read_csv(out)
    assert (result["status"] == "ok").all()
    assert (result["KE_ratio"] > 0).all()
