"""src/dataset.py: arguments, default names, MATLAB command, designs file, sidecar, guard."""

import json

import numpy as np
import pandas as pd
import pytest

from simulation.python_simulation.generate_data import COLUMNS
from simulation.python_simulation.sampling import sample_designs
from src import dataset as ds


@pytest.fixture
def fake_python_run(monkeypatch):
    """Replace the real simulation with an instant one that writes rows of 1.0."""
    def run_python(c2, c3, out_file, workers):
        from simulation.python_simulation.generate_data import generate_data
        return generate_data(c2, c3, out_file, workers=1, simulate=_one, verbose=False)
    monkeypatch.setattr(ds, "run_python", run_python)


def _one(c2, c3):
    return 1.0


# ---------------------------------------------------------------------------
# Arguments and defaults
# ---------------------------------------------------------------------------

def test_defaults():
    args = ds.parse_args(["10"])
    assert args.lang == "python" and args.seed == 0 and args.out is None


def test_old_style_commands_still_parse():
    args = ds.parse_args(["100", "--out", "data/raw/batch2.csv", "--seed", "42"])
    assert (args.n_samples, args.out, args.seed) == (100, "data/raw/batch2.csv", 42)


def test_requires_n_or_designs():
    with pytest.raises(SystemExit):
        ds.parse_args([])


def test_designs_not_allowed_with_matlab():
    with pytest.raises(SystemExit):
        ds.parse_args(["--designs", "x.csv", "--lang", "matlab"])


def test_default_out_names():
    assert ds.default_out("python", 3) == ds.RAW_DIR / "python_seed3.csv"
    assert ds.default_out("matlab", 0) == ds.RAW_DIR / "matlab_seed0.csv"
    assert ds.default_out("python", 0, "data/raw/matlab_uniform_5000.csv") == \
        ds.RAW_DIR / "python_matlab_uniform_5000.csv"


def test_default_workers_prefers_kubernetes_limit(monkeypatch):
    monkeypatch.setenv("KUBERNETES_LIMIT_CPU", "8")
    assert ds.default_workers() == 8
    monkeypatch.delenv("KUBERNETES_LIMIT_CPU")
    assert ds.default_workers() >= 1


# ---------------------------------------------------------------------------
# MATLAB path
# ---------------------------------------------------------------------------

def test_matlab_command():
    cmd = ds.build_matlab_command(5, "/tmp/it's.csv", 2)
    assert cmd[:2] == ["matlab", "-batch"]
    assert cmd[2] == ("addpath('simulation/matlab_simulation'); "
                      "generate_data(5, '/tmp/it''s.csv', 2)")


def test_matlab_runs_from_project_root(monkeypatch, tmp_path):
    out = tmp_path / "m.csv"
    calls = {}

    def fake_run(cmd, cwd=None, **kwargs):
        if cmd[0] != "matlab":             # git calls made while filling in the sidecar
            return ds.subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
        calls.update(cmd=cmd, cwd=cwd)
        pd.DataFrame([[0.0] * 8 + [0.5]], columns=COLUMNS).to_csv(out, index=False)

    monkeypatch.setattr(ds.shutil, "which", lambda _: "/usr/bin/matlab")
    monkeypatch.setattr(ds.subprocess, "run", fake_run)
    ds.main(["1", "--lang", "matlab", "--out", str(out)])
    assert calls["cwd"] == ds.PROJECT_ROOT
    batch = json.loads(ds.meta_path(out).read_text())["batches"][0]
    assert batch["lang"] == "matlab" and batch["seed"] == 0 and batch["n_failed"] == 0


def test_missing_matlab_gives_clear_error(monkeypatch, tmp_path):
    monkeypatch.setattr(ds.shutil, "which", lambda _: None)
    with pytest.raises(SystemExit, match="not found"):
        ds.run_matlab(1, tmp_path / "m.csv", 0)


# ---------------------------------------------------------------------------
# Designs file
# ---------------------------------------------------------------------------

def test_load_designs_ignores_extra_columns_and_keeps_precision(tmp_path):
    c2, c3 = sample_designs(5, seed=0)
    df = pd.DataFrame(np.c_[c2, c3, np.arange(5)], columns=COLUMNS)
    df.insert(0, "note", "x")
    path = tmp_path / "d.csv"
    df.to_csv(path, index=False, float_format="%.17g")
    l2, l3 = ds.load_designs(path, n=3)
    np.testing.assert_array_equal(l2, c2[:3])
    np.testing.assert_array_equal(l3, c3[:3])


def test_load_designs_warns_on_invalid(tmp_path, capsys):
    path = tmp_path / "d.csv"
    pd.DataFrame([[-100.0] * 4 + [10.0] * 4 + [1.0]], columns=COLUMNS).to_csv(path, index=False)
    ds.load_designs(path)
    assert "violate" in capsys.readouterr().err


def test_load_designs_missing_column(tmp_path):
    path = tmp_path / "d.csv"
    pd.DataFrame({"c2_A": [1.0]}).to_csv(path, index=False)
    with pytest.raises(SystemExit, match="missing columns"):
        ds.load_designs(path)


# ---------------------------------------------------------------------------
# Sidecar and duplicate guard
# ---------------------------------------------------------------------------

def test_sidecar_created_then_appended(tmp_path, fake_python_run):
    out = tmp_path / "p.csv"
    ds.main(["3", "--seed", "1", "--out", str(out), "--workers", "1"])
    ds.main(["2", "--seed", "2", "--out", str(out), "--workers", "1"])
    batches = json.loads(ds.meta_path(out).read_text())["batches"]
    assert [b["seed"] for b in batches] == [1, 2]
    assert [b["n"] for b in batches] == [3, 2]
    assert all(b["finished"] and b["lang"] == "python" and b["solver"] == "numba" for b in batches)
    assert len(pd.read_csv(out)) == 5


def test_guard_refuses_repeat_seed(tmp_path, fake_python_run):
    out = tmp_path / "p.csv"
    ds.main(["2", "--seed", "1", "--out", str(out), "--workers", "1"])
    with pytest.raises(SystemExit, match="already run"):
        ds.main(["2", "--seed", "1", "--out", str(out), "--workers", "1"])
    ds.main(["2", "--seed", "1", "--out", str(out), "--workers", "1", "--force"])
    assert len(pd.read_csv(out)) == 4


def test_guard_refuses_repeat_designs_file(tmp_path, fake_python_run):
    designs = tmp_path / "d.csv"
    c2, c3 = sample_designs(2, seed=0)
    pd.DataFrame(np.c_[c2, c3, [1, 1]], columns=COLUMNS).to_csv(designs, index=False, float_format="%.17g")
    out = tmp_path / "p.csv"
    ds.main(["--designs", str(designs), "--out", str(out)])
    with pytest.raises(SystemExit, match="already run"):
        ds.main(["--designs", str(designs), "--out", str(out)])


def test_guard_checks_old_files_without_sidecar(tmp_path):
    out = tmp_path / "old.csv"
    c2, c3 = sample_designs(1, seed=4)
    pd.DataFrame(np.c_[c2, c3, [0.5]], columns=COLUMNS).to_csv(out, index=False, float_format="%.17g")
    batch = {"lang": "python", "seed": 4}
    assert ds.find_duplicate(out, batch, (c2[0], c3[0])) is not None
    other2, other3 = sample_designs(1, seed=5)
    assert ds.find_duplicate(out, {"lang": "python", "seed": 5}, (other2[0], other3[0])) is None
