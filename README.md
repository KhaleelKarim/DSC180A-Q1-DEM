# Disorder DEM: Impact Mitigation in Nonlinear Spring Chains

DSC 180A capstone (UCSD Data Science). We simulate a 1-D chain of 20 masses connected by nonlinear springs and struck
by a small, fast impactor. This replicates the *Disorder DEM* paper (`references/`). The chain's 20 springs form
4 families, and each family has two coefficients (c₂, c₃). Those **8 coefficients** are the inputs. The output is the
**KE ratio**: how much kinetic energy reaches the far end compared to an all-linear chain. Lower means better impact
mitigation. We generate datasets of (8 coefficients → KE ratio) for data-science analysis.

## 1. Install

You need **Python 3.10 or newer** (tested with 3.11) and git.

```bash
git clone https://github.com/KhaleelKarim/DSC180A-Q1-DEM.git
cd DSC180A-Q1-DEM
```

Create a virtual environment, an isolated folder holding this project's packages, and activate it:

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux / DSMLP
source .venv/bin/activate
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

**MATLAB is optional.** The build uses the Python simulation. MATLAB is only needed if you call
`src/dataset.py --lang matlab` yourself (see [Advanced](#6-advanced-calling-the-scripts-directly)).

## 2. Build

Run everything from the repository root:

```bash
python run.py all
```

| Command | What it does | Output (automatic names) |
|---|---|---|
| `python run.py data` | Simulates the designs described in `config/data.json` | `data/raw/<lang>_seed<seed>_n<n_samples>.csv` (+ `.meta.json`) |
| `python run.py viz` | Draws figures 00–05 from the dataset in `config/viz.json` | `results/visualizations/<dataset name>/*.png` |
| `python run.py all` | `data`, then `viz` | both of the above |
| `python run.py clean` | Lists the outputs above and asks before deleting them | — |

For example, `"seed": 50` and `"n_samples": 100` produce `data/raw/python_seed50_n100.csv` and figures in
`results/visualizations/python_seed50_n100/`.

You can chain targets; they run in the order given, e.g. `python run.py clean all`.
Add `-y` to skip `clean`'s confirmation prompt.

**How long it takes.** About 0.1 s per design on a laptop: 100 designs take a few seconds and 2,000 about a minute.
360,000 designs take roughly 20+ minutes on DSMLP's 8 CPUs.

**Re-running is safe.** If the dataset already exists and matches the config, `data` skips it. Because the automatic
name includes the seed and sample count, changing either one simply builds a new file. If you give your own `out` name
and then change the config, `data` refuses to mix old and new data: run `python run.py clean` first, or pick a new name.

> Note: `clean` deletes figures in `results/visualizations/`, which are tracked by git. They'll show as deleted in
> `git status` until you rebuild.

## 3. Configuration

Each target reads a JSON file in `config/`. Paths are relative to the repository root.
**Leave a path as `null` to get the automatic name**, or type your own to override it.

**`config/data.json`**

| Key | Meaning | `null` means |
|---|---|---|
| `n_samples` | Number of designs to simulate | — (required) |
| `seed` | Random seed for sampling designs (seeds are language-specific) | — (required) |
| `lang` | Simulation engine: `"python"` or `"matlab"` | — (required) |
| `out` | CSV to write | `data/raw/<lang>_seed<seed>_n<n_samples>.csv` |
| `workers` | Parallel processes | all available CPUs |

**`config/viz.json`**

| Key | Meaning | `null` means |
|---|---|---|
| `input` | Dataset CSV to plot | the file the `data` target writes |
| `out_dir` | Folder for the figures | `results/visualizations/<input file name without .csv>` |

So with both files' paths left as `null`, you only ever edit `n_samples`/`seed`, and `viz` follows `data`
automatically. Set `input` yourself to plot some other dataset, e.g. `"data/raw/matlab_uniform_5000.csv"`.

## 4. Tests

```bash
pytest -m "not slow"   # fast tests
pytest                 # everything, including full simulations
```

## 5. Repository layout

```
run.py                     build script (targets: data, viz, all, clean)
config/                    one JSON settings file per target
src/
  dataset.py               dataset generation (called by `run.py data`)
  visualize_data.py        exploratory figures (called by `run.py viz`)
  ...                      OAT (one-at-a-time sensitivity) helper scripts
simulation/
  python_simulation/       Python port of the simulation (default engine)
  matlab_simulation/       original MATLAB simulation from the paper's authors
data/raw/                  generated datasets (not tracked by git)
data/oat/                  one-at-a-time sensitivity sweeps
results/visualizations/    figures
notebooks/                 analysis notebooks
references/                papers (PDF + markdown)
tests/                     pytest suite
```

## 6. Advanced: calling the scripts directly

`run.py` is a thin wrapper. The underlying scripts offer more options:

```bash
python src/dataset.py 1000 --seed 3                         # -> data/raw/python_seed3_n1000.csv
python src/dataset.py 100 --lang matlab --seed 2            # use the MATLAB simulation
python src/dataset.py --designs data/raw/matlab_uniform_5000.csv   # re-run specific designs
python src/visualize_data.py data/raw/python_seed3_n1000.csv # figures 00-06 (06 = OAT sweeps)
```

Run `python src/dataset.py --help` for all flags.
