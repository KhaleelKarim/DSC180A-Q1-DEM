"""Exploratory DEM figures for DSC180A: 8 spring coefficients -> KE ratio.

Run from repository root:
    python src/visualize_data.py
    python src/visualize_data.py data/raw/another_dataset.csv

These figures show LHS observational associations, NOT one-at-a-time
controlled sensitivity. For controlled sweeps, hold 7 coefficients fixed
and run the MATLAB DEM repeatedly while varying the eighth.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "raw" / "LHS_1000_samples_complete.csv"
INPUT_COLUMNS = [f"c2_{f}" for f in "ABCD"] + [f"c3_{f}" for f in "ABCD"]
REQUIRED_COLUMNS = INPUT_COLUMNS + ["KE_ratio"]

csv_path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_CSV
if not csv_path.is_absolute():
    csv_path = ROOT / csv_path
if not csv_path.is_file():
    raise FileNotFoundError(f"CSV not found: {csv_path}")

df = pd.read_csv(csv_path)
missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

for col in REQUIRED_COLUMNS:
    df[col] = pd.to_numeric(df[col], errors="coerce")
valid = np.isfinite(df[REQUIRED_COLUMNS].to_numpy()).all(axis=1) & (df["KE_ratio"] > 0).to_numpy()
clean = df.loc[valid].copy()
if clean.empty:
    raise ValueError("No rows with finite coefficients and positive finite KE ratios.")

out_dir = ROOT / "results" / "visualizations" / csv_path.stem
out_dir.mkdir(parents=True, exist_ok=True)
n = len(clean)
logke = np.log10(clean["KE_ratio"].to_numpy())

# Bounds are per family, not just global min/max.
in_range = np.ones(n, dtype=bool)
positive_energy = np.ones(n, dtype=bool)
for family in "ABCD":
    c2 = clean[f"c2_{family}"].to_numpy()
    c3 = clean[f"c3_{family}"].to_numpy()
    in_range &= (c2 >= -120) & (c2 <= 0) & (c3 >= 0) & (c3 <= 4000)
    positive_energy &= c3 > (2.0 / 9.0) * c2**2
admissible = in_range & positive_energy

print(f"CSV: {csv_path}")
print(f"Rows: {len(df):,} | finite, positive-KE rows: {n:,} | excluded: {len(df)-n:,}")
print(f"All 4 families within paper's box bounds: {in_range.sum():,} / {n:,}")
print(f"All 4 families satisfy c3 > (2/9)c2^2: {positive_energy.sum():,} / {n:,}")
print(f"Both constraints satisfied: {admissible.sum():,} / {n:,}")
print(f"KE ratio < 0.1: {(clean['KE_ratio'] < 0.1).sum():,}")
print(clean["KE_ratio"].describe(percentiles=[0.05, 0.5, 0.95]).to_string())

# Distribution. Log10 on horizontal axis retains extreme KE values.
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(logke, bins=45, edgecolor="black", linewidth=0.35)
ax.axvline(0, linestyle="--", linewidth=1.4, label="KE ratio = 1 (linear baseline)")
ax.set(xlabel="log10(KE ratio)", ylabel="Number of designs",
       title=f"DEM KE ratio distribution (n={n:,})")
ax.legend()
fig.tight_layout()
fig.savefig(out_dir / "01_ke_distribution.png", dpi=250)
plt.close(fig)

# Parameter vs. KE Ratio scatter plots
# Observational only: other 7 coefficients are also varying.
fig, axes = plt.subplots(2, 4, figsize=(17, 8), sharey=True)

for ax, col in zip(axes.flat, INPUT_COLUMNS):
    ax.scatter(clean[col], clean["KE_ratio"], s=9, alpha=0.35, rasterized=True)
    ax.set_yscale("log")
    ax.axhline(1, linewidth=0.8, linestyle="--")
    ax.set_xlabel(col)
    ax.set_title(f"{col} vs KE Ratio")

for ax in axes[:, 0]:
    ax.set_ylabel("KE Ratio (log scale)")

fig.suptitle(
    f"Parameter vs. KE Ratio scatter plots (n={n:,})\n"
    "Observational: other seven coefficients also vary",
    y=1.02
)
fig.tight_layout()
fig.savefig(out_dir / "02_parameter_vs_ke_scatter.png", dpi=250, bbox_inches="tight")
plt.close(fig)

# Correlation matrix heatmap
corr_df = clean[INPUT_COLUMNS].copy()
corr_df["log10_KE_ratio"] = np.log10(clean["KE_ratio"])

corr = corr_df.corr()

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)

labels = corr.columns.tolist()
ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_yticklabels(labels)

for i in range(len(labels)):
    for j in range(len(labels)):
        ax.text(
            j, i, f"{corr.iloc[i, j]:.2f}",
            ha="center", va="center", fontsize=8, color="black"
        )

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Correlation")

ax.set_title("Correlation matrix heatmap")
fig.tight_layout()
fig.savefig(out_dir / "03_correlation_heatmap.png", dpi=250, bbox_inches="tight")
plt.close(fig)

# Per-family design-space plots with the paper's energy constraint boundary.
fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 9),
    sharex=True,
    sharey=True
)
fig.subplots_adjust(
    left=0.09,
    right=0.78,
    bottom=0.09,
    top=0.90,
    wspace=0.28,
    hspace=0.30
)
x = np.linspace(-120, 0, 400)
for ax, family in zip(axes.flat, "ABCD"):

    sc = ax.scatter(
        clean[f"c2_{family}"],
        clean[f"c3_{family}"],
        c=logke,
        cmap="viridis",
        s=12,
        alpha=0.65,
        rasterized=True
    )

    ax.plot(
        x,
        (2 / 9) * x**2,
        linestyle="--",
        color="crimson",
        label=r"Energy boundary: $c_3=2c_2^2/9$"
    )

    ax.set(
        xlim=(-120, 0),
        ylim=(0, 4000),
        xlabel=f"c2_{family}",
        ylabel=f"c3_{family}",
        title=f"Spring family {family}"
    )
axes.flat[0].legend(loc="upper right", fontsize=8)
cbar_ax = fig.add_axes([0.84, 0.23, 0.025, 0.52])
cbar = fig.colorbar(sc, cax=cbar_ax)
cbar.set_label("log10(KE ratio)")
fig.suptitle(
    "Sampled coefficient space vs positive-strain-energy boundary",
    fontsize=15,
    y=0.97
)
fig.savefig(out_dir / "04_design_space_bounds.png", dpi=250, bbox_inches="tight")
plt.close(fig)

# Quantify how many observed designs are within the physics constraints.
fig, ax = plt.subplots(figsize=(8, 5))
labels = ["Within box bounds", "Positive-energy constraint", "Satisfy both"]
counts = [int(in_range.sum()), int(positive_energy.sum()), int(admissible.sum())]
bars = ax.bar(labels, counts)
ax.bar_label(bars, padding=4)
ax.set_ylim(0, n * 1.12)
ax.set_ylabel("Number of designs")
ax.set_title(f"Coefficient bounds audit (n={n:,})")
fig.tight_layout()
fig.savefig(out_dir / "05_bounds_audit.png", dpi=250)
plt.close(fig)

# Preliminary dataset overview: 8 coefficient histograms + KE distribution
fig, axes = plt.subplots(3, 3, figsize=(14, 10))
axes = axes.ravel()

for i, col in enumerate(INPUT_COLUMNS):
    axes[i].hist(clean[col], bins=30, edgecolor="black", linewidth=0.35)
    axes[i].set_title(col)
    axes[i].set_xlabel(col)
    axes[i].set_ylabel("Count")

axes[8].hist(logke, bins=35, edgecolor="black", linewidth=0.35)
axes[8].set_title("log10(KE_ratio)")
axes[8].set_xlabel("log10(KE_ratio)")
axes[8].set_ylabel("Count")

fig.suptitle(f"Preliminary dataset visualization (n={n:,})", y=0.98)
fig.tight_layout()
fig.savefig(out_dir / "00_preliminary_dataset_overview.png", dpi=250, bbox_inches="tight")
plt.close(fig)


# One-at-a-Time (OAT) Sensitivity Analysis
# Requires separate controlled DEM simulations.
# Each OAT CSV must vary only one coefficient while holding the other 7 fixed.

oat_dir = ROOT / "data" / "oat"
oat_plots = 0

if oat_dir.exists():

    fig, axes = plt.subplots(4, 2, figsize=(12, 16))
    axes = axes.ravel()

    for ax, col in zip(axes, INPUT_COLUMNS):

        oat_file = oat_dir / f"oat_{col}.csv"

        if not oat_file.is_file():
            ax.text(0.5, 0.5, f"Missing: {oat_file.name}",
                    ha="center", va="center")
            ax.set_axis_off()
            continue

        oat = pd.read_csv(oat_file)

        if "parameter_value" in oat.columns:
            xvals = pd.to_numeric(oat["parameter_value"], errors="coerce")
        elif col in oat.columns:
            xvals = pd.to_numeric(oat[col], errors="coerce")
        else:
            ax.set_axis_off()
            continue

        if "KE_ratio" not in oat.columns:
            ax.set_axis_off()
            continue

        yvals = pd.to_numeric(oat["KE_ratio"], errors="coerce")
        mask = np.isfinite(xvals) & np.isfinite(yvals) & (yvals > 0)

        if not mask.any():
            ax.set_axis_off()
            continue

        xvals = xvals[mask].to_numpy()
        yvals = yvals[mask].to_numpy()

        order = np.argsort(xvals)

        ax.plot(xvals[order], yvals[order], marker="o", linewidth=2)
        ax.set_yscale("log")
        ax.set_xlabel(col)
        ax.set_ylabel("KE Ratio (log scale)")
        ax.set_title(f"{col} vs KE Ratio")
        oat_plots += 1

    if oat_plots > 0:
        fig.suptitle("One-at-a-Time (OAT) Sensitivity Analysis", y=0.995)
        fig.tight_layout(rect=[0, 0, 1, 0.98])
        fig.savefig(out_dir / "06_oat_sensitivity.png",
                    dpi=250, bbox_inches="tight")
        print(f"Saved OAT figure with {oat_plots} parameter sweeps.")
    else:
        print("No valid OAT datasets found. Skipping OAT figure.")

    plt.close(fig)

else:
    print("OAT datasets not available yet. Skipping OAT sensitivity analysis.")

print(f"Saved 6 exploratory figures in: {out_dir}")
print("OAT requires controlled DEM simulations with seven fixed coefficients.")