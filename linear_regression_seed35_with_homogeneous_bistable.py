"""DSC 180A — Linear Regression (Seed 35 + Homogeneous Bistable; 70/15/15).

Run this file from the repository root:
    python linear_regression_seed35_with_homogeneous_bistable.py

Put the dataset at:
    data/raw/python_seed35.csv

Or pass a custom path:
    python linear_regression_seed35_with_homogeneous_bistable.py --data "path/to/python_seed35.csv"

The model is fit ONLY on the 70% training set; 15% is held for validation
and 15% for independent final testing.
Homogeneous Bistable uses its own DEM data and a separate 2-feature linear model.
If data/raw/homogeneous_bistable_2000.csv does not exist, generate it with the
repository Python DEM (requires simulation/python_simulation/).

per-row metric:
    Relative Error = abs(predicted_KE_ratio - actual_KE_ratio) / actual_KE_ratio
group metric:
    MAPE = sklearn.metrics.mean_absolute_percentage_error(y_true, y_pred).
    Display MAPE percentage = 100 * MAPE.
    Per-row errors are retained for inspection, with the same epsilon handling as sklearn.

Note about labels in the team's random_forest.ipynb:
  * heterogeneous_het: heterogeneous with >=1 bistable spring family
  * heterogeneous_excluding_bistability: no bistable spring families
These two labels are disjoint subsets of the entire heterogeneous dataset.
"""

from pathlib import Path
import argparse

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (mean_absolute_error, mean_absolute_percentage_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
FEATURES = [f"c2_{s}" for s in "ABCD"] + [f"c3_{s}" for s in "ABCD"]
TARGET = "KE_ratio"
LOW_KE_THRESHOLD = 0.03
SEED = 42
HOMO_FEATURES = ["c2_A", "c3_A"]


def load_dataset(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot find {path}. Save the uploaded CSV as "
            "data/raw/python_seed35.csv, or provide --data PATH."
        )

    df = pd.read_csv(path)
    required = FEATURES + [TARGET]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing CSV columns: {missing}")

    df = df[required].copy()
    if not np.isfinite(df.to_numpy(dtype=float)).all():
        raise ValueError("Dataset contains missing, infinite, or non-numeric values")
    if (df[TARGET] <= 0).any():
        raise ValueError("Actual KE ratios must be strictly positive for relative error")

    c2 = df[FEATURES[:4]].to_numpy()
    c3 = df[FEATURES[4:]].to_numpy()
    valid = (
        ((c2 >= -120) & (c2 <= 0)).all(axis=1)
        & ((c3 >= 0) & (c3 <= 4000)).all(axis=1)
        & (c3 > (2 / 9) * c2**2).all(axis=1)
    )
    if not valid.all():
        raise ValueError(f"{(~valid).sum()} rows violate the paper's coefficient constraints")

    if df.duplicated(subset=FEATURES).any():
        raise ValueError("Repeated spring designs detected. Review duplicates before splitting.")
    return df


def group_masks(data):
    c2 = data[FEATURES[:4]].to_numpy()
    c3 = data[FEATURES[4:]].to_numpy()
    no_bistability = (c2**2 <= 4 * c3).all(axis=1)
    low_ke = data[TARGET].to_numpy() <= LOW_KE_THRESHOLD
    return {
        "entire_set": np.ones(len(data), dtype=bool),
        "heterogeneous_het": ~no_bistability,
        "heterogeneous_excluding_bistability": no_bistability,
        "low_ke_region": low_ke,
    }, no_bistability, low_ke


def group_metrics(data, predictions, split):
    predictions = np.asarray(predictions)
    actual = data[TARGET].to_numpy()
    relative_error = np.abs(predictions - actual) / np.maximum(np.abs(actual), np.finfo(np.float64).eps)
    masks, no_bistability, low_ke = group_masks(data)

    records = []
    for group, mask in masks.items():
        label = f"entire_{split}_set" if group == "entire_set" else group
        n = int(mask.sum())
        if n == 0:
            records.append({"group": label, "n_samples": 0, "mean_relative_error": np.nan,
                            "mean_relative_error_percent": np.nan,
                            "MAPE": np.nan, "MAPE_percent": np.nan})
            continue
        y_true, y_hat = actual[mask], predictions[mask]
        mre = float(mean_absolute_percentage_error(y_true, y_hat))
        records.append({
            "group": label,
            "n_samples": n,
            "mean_actual_KE_ratio": float(y_true.mean()),
            "mean_predicted_KE_ratio": float(y_hat.mean()),
            "mean_relative_error": mre,
            "MAPE": mre,
            "mean_relative_error_percent": 100 * mre,
            "MAPE_percent": 100 * mre,
            "MAE": float(mean_absolute_error(y_true, y_hat)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_hat))),
            "R2": float(r2_score(y_true, y_hat)) if n >= 2 else np.nan,
            "negative_predictions": int((y_hat < 0).sum()),
        })

    detail = data.copy()
    detail["actual_KE_ratio"] = actual
    detail["predicted_KE_ratio"] = predictions
    detail["relative_error"] = relative_error
    detail["relative_error_percent"] = 100 * relative_error
    detail["design_group"] = np.where(no_bistability, "het_excl_bist", "het")
    detail["low_ke_region"] = low_ke
    return pd.DataFrame(records), detail


def save_scatter(df, path, title="Seed 35 test set (15%): Actual vs Predicted"):
    # A reproducible subset keeps a 54,000-row scatter plot legible.
    sampled = df.sample(n=min(5000, len(df)), random_state=SEED)
    actual = sampled["actual_KE_ratio"]
    predicted = sampled["predicted_KE_ratio"]
    lo = float(min(actual.min(), predicted.min()))
    hi = float(max(actual.max(), predicted.max()))
    plt.figure(figsize=(7, 6))
    plt.scatter(actual, predicted, alpha=0.2, s=6)
    plt.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="Perfect prediction")
    plt.xlabel("Actual KE Ratio (DEM)")
    plt.ylabel("Predicted KE Ratio (Linear Regression)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()



def get_homogeneous_dataset(path, n, sampling_seed, workers):
    """Load or simulate strictly homogeneous *bistable* spring-chain designs.

    The four families share one (c2,c3) pair, satisfying simultaneously:
      -120 <= c2 < 0, 0 < c3 <= 4000,
      (2/9)*c2**2 < c3 < (1/4)*c2**2.
    A distinct filename prevents accidentally reusing the earlier mixed
    homogeneous dataset or appending to it (generate_data appends).
    """
    if not path.exists():
        try:
            from simulation.python_simulation.generate_data import generate_data
        except ImportError as exc:
            raise RuntimeError(
                "Bistable CSV not found and repository DEM import failed. "
                "Place this script at repository root, with simulation/python_simulation/."
            ) from exc
        if n < 30:
            raise ValueError("Use at least 30 homogeneous bistable designs.")
        rng = np.random.default_rng(sampling_seed)
        # No near-zero c2: avoids a nearly zero-width bistable interval.
        # c2 still lies within the paper's [-120,0] design bounds.
        c2_single = rng.uniform(-120.0, -5.0, n)
        lower = (2 / 9) * c2_single**2
        upper = (1 / 4) * c2_single**2
        c3_single = lower + rng.uniform(0.05, 0.95, n) * (upper - lower)
        c2 = np.repeat(c2_single[:, None], 4, axis=1)
        c3 = np.repeat(c3_single[:, None], 4, axis=1)
        assert np.all(c3 > (2 / 9) * c2**2)
        assert np.all(c2**2 > 4 * c3)
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Generating {n:,} homogeneous BISTABLE designs -> {path}", flush=True)
        summary = generate_data(c2, c3, path, workers=workers, verbose=False)
        if summary["n_failed"]:
            # Avoid reusing partial/failed data on the next attempt.
            raise RuntimeError(
                f"{summary['n_failed']} DEM simulations failed; inspect {path} "
                "and delete the partial file before retrying."
            )
        print("Homogeneous bistable DEM simulations completed.", flush=True)
    else:
        print(f"Using existing homogeneous bistable DEM data: {path}", flush=True)

    homo = load_dataset(path)
    c2 = homo[FEATURES[:4]].to_numpy()
    c3 = homo[FEATURES[4:]].to_numpy()
    if not (np.allclose(c2, c2[:, :1], rtol=0, atol=1e-11)
            and np.allclose(c3, c3[:, :1], rtol=0, atol=1e-11)):
        raise ValueError("CSV is not homogeneous: spring families differ.")
    bistable = (c2**2 > 4 * c3).all(axis=1)
    if not bistable.all():
        raise ValueError(
            f"CSV includes {(~bistable).sum()} NON-bistable designs. "
            "Do not use the previous homogeneous_2000.csv; use "
            "data/raw/homogeneous_bistable_2000.csv instead."
        )
    if len(homo) < 30:
        raise ValueError("At least 30 homogeneous bistable designs required.")
    print(f"Validated {len(homo):,} homogeneous BISTABLE designs (100%).")
    return homo


def homogeneous_metrics(data, predictions, split):
    """Separate homogeneous MRE, including the low-KE homogeneous subset."""
    actual = data[TARGET].to_numpy()
    predictions = np.asarray(predictions)
    re = np.abs(predictions - actual) / np.maximum(np.abs(actual), np.finfo(np.float64).eps)
    masks = {
        "homogeneous_bistable": np.ones(len(data), dtype=bool),
        "homogeneous_bistable_low_ke_region": actual <= LOW_KE_THRESHOLD,
    }
    records = []
    for group, mask in masks.items():
        count = int(mask.sum())
        if count == 0:
            records.append({"group": group, "split": split, "n_samples": 0,
                            "mean_relative_error": np.nan, "mean_relative_error_percent": np.nan,
                            "MAPE": np.nan, "MAPE_percent": np.nan,
                            "MAE": np.nan, "RMSE": np.nan, "R2": np.nan,
                            "negative_predictions": 0})
        else:
            true, pred = actual[mask], predictions[mask]
            mre = float(mean_absolute_percentage_error(true, pred))
            records.append({
                "group": group, "split": split, "n_samples": count,
                "mean_actual_KE_ratio": float(true.mean()),
                "mean_predicted_KE_ratio": float(pred.mean()),
                "mean_relative_error": mre,
            "MAPE": mre, "mean_relative_error_percent": mre * 100, "MAPE_percent": mre * 100,
                "MAE": float(mean_absolute_error(true, pred)),
                "RMSE": float(np.sqrt(mean_squared_error(true, pred))),
                "R2": float(r2_score(true, pred)) if count >= 2 else np.nan,
                "negative_predictions": int((pred < 0).sum()),
            })
    details = data.copy()
    details["actual_KE_ratio"] = actual
    details["predicted_KE_ratio"] = predictions
    details["relative_error"] = re
    details["relative_error_percent"] = re * 100
    details["design_group"] = "homogeneous_bistable"
    details["low_ke_region"] = actual <= LOW_KE_THRESHOLD
    return pd.DataFrame(records), details


def run_homogeneous(data_path, out_path, n, sampling_seed, workers):
    homo = get_homogeneous_dataset(data_path, n, sampling_seed, workers)
    train, held = train_test_split(homo, test_size=0.30, random_state=SEED, shuffle=True)
    validation, test = train_test_split(held, test_size=0.50, random_state=SEED, shuffle=True)
    model = make_pipeline(StandardScaler(), LinearRegression())
    model.fit(train[HOMO_FEATURES], train[TARGET])
    out_path.mkdir(parents=True, exist_ok=True)
    summary = []
    for split_name, subset in [("validation", validation), ("test", test)]:
        preds = model.predict(subset[HOMO_FEATURES])
        metrics, details = homogeneous_metrics(subset, preds, split_name)
        metrics.to_csv(out_path / f"{split_name}_group_metrics.csv", index=False)
        details.to_csv(out_path / f"{split_name}_predictions.csv", index_label="original_homogeneous_row")
        summary.append(metrics)
        if split_name == "test":
            save_scatter(details, out_path / "actual_vs_predicted.png",
                         title="Homogeneous Bistable test set (15%): Actual vs Predicted")
    assignment = pd.DataFrame({"original_homogeneous_row": np.arange(len(homo)), "split": ""})
    assignment.loc[train.index, "split"] = "train"
    assignment.loc[validation.index, "split"] = "validation"
    assignment.loc[test.index, "split"] = "test"
    assignment.to_csv(out_path / "split_assignments.csv", index=False)
    pd.DataFrame({
        "feature": HOMO_FEATURES,
        "standardized_regression_coefficient": model.named_steps["linearregression"].coef_,
    }).to_csv(out_path / "regression_coefficients.csv", index=False)
    joblib.dump(model, out_path / "homogeneous_bistable_linear_regression_model.joblib")
    print(f"\nHomogeneous Bistable: total={len(homo):,}, training={len(train):,}, "
          f"validation={len(validation):,}, test={len(test):,}")
    print("\nHOMOGENEOUS BISTABLE TEST METRICS (scikit-learn MAPE)")
    print(summary[-1][["group", "n_samples", "mean_relative_error_percent"]]
          .to_string(index=False, float_format=lambda x: f"{x:.5f}"))
    return summary[-1]


def main():
    parser = argparse.ArgumentParser(description="Seed 35 Linear Regression: 70/15/15 + sklearn MAPE")
    parser.add_argument("--data", type=Path, default=ROOT / "data/raw/python_seed35.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results/linear_regression_seed35")
    parser.add_argument("--homogeneous-data", type=Path,
                        default=ROOT / "data/raw/homogeneous_bistable_2000.csv",
                        help="Existing strictly bistable CSV or new DEM output path")
    parser.add_argument("--homogeneous-n", type=int, default=2000,
                        help="DEM simulations to generate if homogeneous CSV is absent")
    parser.add_argument("--homogeneous-seed", type=int, default=123)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--skip-homogeneous", action="store_true",
                        help="Only run original Seed35 8-feature model")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    data = load_dataset(args.data)

    # First: 70% for training, 30% held back.
    train, held_out = train_test_split(data, test_size=0.30, random_state=SEED, shuffle=True)
    # Split the held-out 30% equally into 15% validation and 15% test.
    validation, test = train_test_split(held_out, test_size=0.50, random_state=SEED, shuffle=True)

    model = make_pipeline(StandardScaler(), LinearRegression())
    model.fit(train[FEATURES], train[TARGET])  # TRAIN only

    val_predictions = model.predict(validation[FEATURES])
    val_metrics, val_detail = group_metrics(validation, val_predictions, "validation")
    val_metrics.to_csv(args.out / "validation_group_metrics.csv", index=False)
    # Validation is used for model decisions, not as training data.

    # Test evaluation: performed only after the pipeline was chosen.
    test_predictions = model.predict(test[FEATURES])
    test_metrics, test_detail = group_metrics(test, test_predictions, "test")
    test_metrics.to_csv(args.out / "test_group_metrics.csv", index=False)
    test_detail.insert(0, "original_seed35_row", test.index)
    test_detail.to_csv(args.out / "seed35_test_predictions.csv", index=False)
    test_detail.head(100).to_csv(args.out / "predictions_first_100_rows.csv", index=False)

    # Store split IDs to allow later SVR / RF comparisons on identical examples.
    split_ids = pd.DataFrame({"original_seed35_row": np.arange(len(data)), "split": ""})
    split_ids.loc[train.index, "split"] = "train"
    split_ids.loc[validation.index, "split"] = "validation"
    split_ids.loc[test.index, "split"] = "test"
    split_ids.to_csv(args.out / "split_assignments.csv", index=False)

    pd.DataFrame({
        "feature": FEATURES,
        "standardized_regression_coefficient": model.named_steps["linearregression"].coef_,
    }).to_csv(args.out / "regression_coefficients.csv", index=False)
    joblib.dump(model, args.out / "linear_regression_model.joblib")
    save_scatter(test_detail, args.out / "actual_vs_predicted.png")

    print(f"Dataset: {args.data}")
    print(f"Total rows: {len(data):,}")
    print(f"Training (70%): {len(train):,}")
    print(f"Validation (15%): {len(validation):,}")
    print(f"Test (15%): {len(test):,}")
    print("\nTEST SET: scikit-learn MAPE by group")
    print(test_metrics[["group", "n_samples", "mean_relative_error", "mean_relative_error_percent"]]
          .to_string(index=False, float_format=lambda x: f"{x:.5f}"))
    print("\nResults saved to:", args.out.resolve())
    if not args.skip_homogeneous:
        homo_test_metrics = run_homogeneous(
            args.homogeneous_data, args.out / "homogeneous_bistable",
            args.homogeneous_n, args.homogeneous_seed, args.workers)
        combined = pd.concat([
            test_metrics.assign(model="heterogeneous_8_features"),
            homo_test_metrics.assign(model="homogeneous_bistable_2_features"),
        ], ignore_index=True)
        combined.to_csv(args.out / "all_test_group_metrics.csv", index=False)
        print("\nCombined group metrics saved to:", args.out / "all_test_group_metrics.csv")
    print("Seed 84 was not used.")


if __name__ == "__main__":
    main()
