"""run.py: the data / viz / all / clean targets, using tiny temporary configs."""

import json

import pandas as pd
import pytest

import run
from src import dataset as ds


@pytest.fixture
def fake_python_run(monkeypatch):
    """Replace the real simulation with an instant one (KE ratio varies with the design)."""
    def run_python(c2, c3, out_file, workers):
        from simulation.python_simulation.generate_data import generate_data
        return generate_data(c2, c3, out_file, workers=1, simulate=_fake_ke, verbose=False)
    monkeypatch.setattr(ds, "run_python", run_python)


def _fake_ke(c2, c3):
    return 0.05 + abs(float(c2[0])) / 100


@pytest.fixture
def configs(tmp_path):
    """Write data.json and viz.json into tmp_path/config; return (config_dir, csv, fig_dir)."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    csv, fig_dir = tmp_path / "raw" / "d.csv", tmp_path / "figs"
    write_data_config(config_dir, csv, seed=1)
    (config_dir / "viz.json").write_text(json.dumps({"input": str(csv), "out_dir": str(fig_dir)}))
    return config_dir, csv, fig_dir


def write_data_config(config_dir, csv, seed, n=5):
    (config_dir / "data.json").write_text(json.dumps(
        {"n_samples": n, "seed": seed, "lang": "python", "out": str(csv), "workers": 1}))


def build(config_dir, *targets):
    run.main([*targets, "--config-dir", str(config_dir), "--yes"])


def test_data_builds_then_skips(configs, fake_python_run, capsys):
    config_dir, csv, _ = configs
    build(config_dir, "data")
    assert len(pd.read_csv(csv)) == 5

    build(config_dir, "data")
    assert "already built" in capsys.readouterr().out
    assert len(pd.read_csv(csv)) == 5          # nothing appended


def test_data_refuses_when_config_changed(configs, fake_python_run):
    config_dir, csv, _ = configs
    build(config_dir, "data")
    write_data_config(config_dir, csv, seed=2)
    with pytest.raises(SystemExit, match="doesn't match"):
        build(config_dir, "data")


def test_viz_needs_data_first(configs):
    config_dir, _, _ = configs
    with pytest.raises(SystemExit, match="run.py data"):
        build(config_dir, "viz")


def test_all_then_clean(configs, fake_python_run, tmp_path):
    config_dir, csv, fig_dir = configs
    keep = csv.parent / "keep_me.csv"           # an unrelated file next to the data

    build(config_dir, "all")
    keep.write_text("x\n")
    assert sorted(p.name for p in fig_dir.iterdir()) == run.FIGURES
    assert ds.meta_path(csv).exists()

    build(config_dir, "clean")
    assert not csv.exists() and not ds.meta_path(csv).exists()
    assert not fig_dir.exists()
    assert keep.exists()


def test_clean_cancelled_keeps_files(configs, fake_python_run, monkeypatch):
    config_dir, csv, _ = configs
    build(config_dir, "data")
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    run.main(["clean", "--config-dir", str(config_dir)])
    assert csv.exists()


def test_unknown_target_rejected():
    with pytest.raises(SystemExit):
        run.parse_args(["visualizations"])


# ---------------------------------------------------------------------------
# Automatic names when a path is null / missing in the config
# ---------------------------------------------------------------------------

AUTO_DATA = {"n_samples": 2000, "seed": 35, "lang": "python", "out": None}


def test_auto_names_follow_data_config():
    csv = run.ROOT / "data" / "raw" / "python_seed35_n2000.csv"
    assert run.data_out(AUTO_DATA) == csv
    assert run.viz_input({"input": None, "out_dir": None}, AUTO_DATA) == csv
    assert run.viz_out_dir({}, AUTO_DATA) == run.ROOT / "results" / "visualizations" / "python_seed35_n2000"


def test_auto_names_change_with_n_samples():
    assert run.data_out({**AUTO_DATA, "n_samples": 500}).name == "python_seed35_n500.csv"


def test_user_names_override_auto_names():
    data_cfg = {**AUTO_DATA, "out": "data/raw/mine.csv"}
    assert run.data_out(data_cfg) == run.ROOT / "data" / "raw" / "mine.csv"
    # viz follows the user's data name unless it has its own
    assert run.viz_out_dir({"input": None, "out_dir": None}, data_cfg).name == "mine"
    viz_cfg = {"input": "data/raw/other.csv", "out_dir": "results/figs"}
    assert run.viz_input(viz_cfg, data_cfg) == run.ROOT / "data" / "raw" / "other.csv"
    assert run.viz_out_dir(viz_cfg, data_cfg) == run.ROOT / "results" / "figs"
