"""
run.py -- Build script for the project.

    python run.py data          # simulate the dataset described in config/data.json
    python run.py viz           # draw figures 00-05 described in config/viz.json
    python run.py all           # data, then viz
    python run.py clean         # delete the outputs named in the configs (asks first)
    python run.py clean all     # targets run in the order given

Settings live in config/<target>.json. Paths in the configs are relative to the
repository root, so this script can be run from any directory. A path left as
null is filled in automatically:
    data "out"     -> data/raw/<lang>_seed<seed>_n<n_samples>.csv
    viz  "input"   -> whatever file the data target writes
    viz  "out_dir" -> results/visualizations/<input file name without .csv>
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TARGETS = ["data", "viz", "all", "clean"]
FIGURES = [
    "00_preliminary_dataset_overview.png",
    "01_ke_distribution.png",
    "02_parameter_vs_ke_scatter.png",
    "03_correlation_heatmap.png",
    "04_design_space_bounds.png",
    "05_bounds_audit.png",
]


class BuildError(Exception):
    """A problem the user can fix (shown without a traceback)."""


def load_config(config_dir, name):
    path = Path(config_dir) / f"{name}.json"
    if not path.is_file():
        raise BuildError(f"Config file not found: {path}")
    return json.loads(path.read_text())


def repo_path(p):
    """A config path, resolved relative to the repository root."""
    p = Path(p).expanduser()
    return p if p.is_absolute() else ROOT / p


def rel(p):
    """Path for printing: relative to the repo root when possible."""
    return p.relative_to(ROOT) if p.is_relative_to(ROOT) else p


# ---------------------------------------------------------------------------
# Output / input paths (config value if given, otherwise the automatic name)
# ---------------------------------------------------------------------------

def data_out(data_cfg):
    """The CSV the data target writes."""
    if data_cfg.get("out"):
        return repo_path(data_cfg["out"])
    from src.dataset import default_out
    return default_out(data_cfg["lang"], data_cfg["seed"], n_samples=data_cfg["n_samples"])


def viz_input(viz_cfg, data_cfg):
    """The CSV the viz target plots."""
    return repo_path(viz_cfg["input"]) if viz_cfg.get("input") else data_out(data_cfg)


def viz_out_dir(viz_cfg, data_cfg):
    """The folder the viz target saves figures in."""
    if viz_cfg.get("out_dir"):
        return repo_path(viz_cfg["out_dir"])
    return ROOT / "results" / "visualizations" / viz_input(viz_cfg, data_cfg).stem


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def is_built(out, cfg):
    """True if `out` is a finished run of exactly this config (judged from its .meta.json)."""
    from src.dataset import meta_path, read_meta
    if not meta_path(out).exists():
        return False
    batches = read_meta(out)["batches"]
    return (len(batches) == 1
            and batches[0].get("finished") is not None
            and batches[0].get("lang") == cfg["lang"]
            and batches[0].get("seed") == cfg["seed"]
            and batches[0].get("n") == cfg["n_samples"]
            and batches[0].get("designs_file") is None)


def build_data(cfg):
    out = data_out(cfg)
    if out.exists():
        if is_built(out, cfg):
            print(f"[data] {rel(out)} is already built for this config, skipping.")
            return
        raise BuildError(
            f"[data] {rel(out)} exists but doesn't match config/data.json "
            f"(different n_samples/seed/lang, an interrupted run, or a file from elsewhere).\n"
            f"Run `python run.py clean` then `python run.py data`, or change \"out\" in the config.")

    from src.dataset import generate
    print(f"[data] Simulating {cfg['n_samples']:,} designs (seed {cfg['seed']}, {cfg['lang']})")
    generate(n_samples=cfg["n_samples"], seed=cfg["seed"], out=out,
             lang=cfg["lang"], workers=cfg.get("workers"))


def build_viz(cfg, data_cfg):
    csv = viz_input(cfg, data_cfg)
    if not csv.is_file():
        raise BuildError(f"[viz] Input data not found: {csv}\nRun `python run.py data` first.")
    from src.visualize_data import make_figures
    print(f"[viz] Drawing figures from {csv.name}")
    make_figures(csv, viz_out_dir(cfg, data_cfg), include_oat=False)


def clean(data_cfg, viz_cfg, assume_yes=False):
    from src.dataset import meta_path
    out = data_out(data_cfg)
    fig_dir = viz_out_dir(viz_cfg, data_cfg)
    targets = [p for p in [out, meta_path(out)] + [fig_dir / f for f in FIGURES] if p.exists()]
    if not targets:
        print("[clean] Nothing to clean.")
        return

    print("[clean] This will delete:")
    for p in targets:
        print(f"    {rel(p)}")
    if not assume_yes and input("Delete these? [y/N] ").strip().lower() not in ("y", "yes"):
        print("[clean] Cancelled; nothing deleted.")
        return
    for p in targets:
        p.unlink()
    if fig_dir.is_dir() and not any(fig_dir.iterdir()):
        fig_dir.rmdir()
    print(f"[clean] Deleted {len(targets)} file(s).")


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Build the project's data and figures.",
        epilog="Targets: data = simulate dataset, viz = draw figures 00-05, "
               "all = data then viz, clean = delete those outputs.")
    p.add_argument("targets", nargs="+", choices=TARGETS, metavar="target",
                   help="one or more of: " + ", ".join(TARGETS))
    p.add_argument("-y", "--yes", action="store_true",
                   help="don't ask for confirmation before `clean` deletes files")
    p.add_argument("--config-dir", default=ROOT / "config",
                   help="folder holding data.json and viz.json (default: config/)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    steps = []
    for t in args.targets:
        steps += ["data", "viz"] if t == "all" else [t]

    try:
        for step in steps:
            if step == "data":
                build_data(load_config(args.config_dir, "data"))
            elif step == "viz":
                build_viz(load_config(args.config_dir, "viz"), load_config(args.config_dir, "data"))
            elif step == "clean":
                clean(load_config(args.config_dir, "data"), load_config(args.config_dir, "viz"),
                      assume_yes=args.yes)
    except BuildError as err:
        raise SystemExit(str(err))


if __name__ == "__main__":
    main()
