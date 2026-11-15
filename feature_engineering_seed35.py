"""DSC 180A: Seed35 feature-engineering comparison (no re-running DEM).

Run from repository root:
  python feature_engineering_seed35.py

Requires:
  data/raw/python_seed35.csv
  results/linear_regression_seed35/split_assignments.csv

Uses the EXACT previous train/validation/test assignment by original row order.
Selects the feature set using validation MAPE (not test) and evaluates the
selected model on test. Existing previously viewed test results make this
an exploratory evaluation; confirm conclusions on independent future DEM data.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error, mean_squared_error, r2_score

FEATURES = [f'c2_{s}' for s in 'ABCD'] + [f'c3_{s}' for s in 'ABCD']
TARGET = 'KE_ratio'
LOW_KE = 0.03
ROOT = Path(__file__).resolve().parent


def physics_features(x):
    """Only input-coefficient-derived features; never use KE_ratio as a feature."""
    out = x.copy()
    c2 = x[FEATURES[:4]].to_numpy(dtype=float)
    c3 = x[FEATURES[4:]].to_numpy(dtype=float)
    bistability_margin = c2**2 - 4.0*c3
    energy_margin = c3 - (2.0 / 9.0)*c2**2
    for i, name in enumerate('ABCD'):
        out[f'c2_squared_{name}'] = c2[:, i]**2
        out[f'c2_c3_interaction_{name}'] = c2[:, i] * c3[:, i]
        out[f'bistability_margin_{name}'] = bistability_margin[:, i]
        out[f'positive_energy_margin_{name}'] = energy_margin[:, i]
        out[f'bistable_indicator_{name}'] = (bistability_margin[:, i] > 0).astype(int)
    for family, values in [('c2', c2), ('c3', c3)]:
        out[f'{family}_mean'] = values.mean(axis=1)
        out[f'{family}_std'] = values.std(axis=1)
        out[f'{family}_range'] = values.max(axis=1) - values.min(axis=1)
    out['n_bistable_families'] = (bistability_margin > 0).sum(axis=1)
    return out


def evaluate(y, pred, group):
    y = np.asarray(y)
    pred = np.asarray(pred)
    c2 = group[FEATURES[:4]].to_numpy()
    c3 = group[FEATURES[4:]].to_numpy()
    no_bistability = (c2**2 <= 4*c3).all(axis=1)
    masks = {
        'entire_set': np.ones(len(y), dtype=bool),
        'heterogeneous_het': ~no_bistability,
        'heterogeneous_excluding_bistability': no_bistability,
        'low_ke_region': y <= LOW_KE,
    }
    rows = []
    for label, mask in masks.items():
        yt, yp = y[mask], pred[mask]
        rows.append({
            'group':label, 'n_samples':len(yt),
            'MAPE_percent':100*mean_absolute_percentage_error(yt, yp) if len(yt) else np.nan,
            'MAE':mean_absolute_error(yt, yp) if len(yt) else np.nan,
            'RMSE':np.sqrt(mean_squared_error(yt, yp)) if len(yt) else np.nan,
            'R2':r2_score(yt, yp) if len(yt)>1 else np.nan,
            'negative_predictions':int((yp<0).sum()),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,default=ROOT/'data/raw/python_seed35.csv')
    parser.add_argument('--splits',type=Path,default=ROOT/'results/linear_regression_seed35/split_assignments.csv')
    parser.add_argument('--out',type=Path,default=ROOT/'results/feature_engineering_seed35')
    args = parser.parse_args()
    df = pd.read_csv(args.data)
    missing = [col for col in FEATURES+[TARGET] if col not in df.columns]
    if missing: raise ValueError(f'Missing columns: {missing}')
    assignments = pd.read_csv(args.splits)
    if len(df)!=len(assignments): raise ValueError('Dataset and split file have different row counts')
    if not np.array_equal(assignments['original_seed35_row'].to_numpy(), np.arange(len(df))):
        raise ValueError('Split assignments do not match original dataset row order')
    if set(assignments['split']) != {'train','validation','test'}:
        raise ValueError('Unexpected split names')
    if not np.isfinite(df[FEATURES+[TARGET]].to_numpy()).all() or (df[TARGET]<=0).any():
        raise ValueError('Missing/nonfinite features or nonpositive KE_ratio')
    mask = {s:assignments['split'].eq(s).to_numpy() for s in ['train','validation','test']}
    X = df[FEATURES]
    y = df[TARGET]
    feature_sets = {
        'Original Linear Regression': (X, make_pipeline(StandardScaler(), LinearRegression())),
        'Polynomial Degree 2 + Ridge': (X, make_pipeline(PolynomialFeatures(degree=2,include_bias=False),StandardScaler(),Ridge(alpha=1.0))),
        'Physics Features + Ridge': (physics_features(X), make_pipeline(StandardScaler(),Ridge(alpha=1.0))),
    }
    args.out.mkdir(parents=True,exist_ok=True)
    comparisons=[]
    fit_models={}
    for label,(features,model) in feature_sets.items():
        print(f'Fitting {label} ...', flush=True)
        model.fit(features.loc[mask['train']],y.loc[mask['train']])
        pred = model.predict(features.loc[mask['validation']])
        results = evaluate(y.loc[mask['validation']], pred, df.loc[mask['validation']])
        results.insert(0,'model',label)
        comparisons.append(results)
        fit_models[label]=model
    validation = pd.concat(comparisons,ignore_index=True)
    validation.to_csv(args.out/'validation_group_comparison.csv',index=False)
    print('\nValidation group comparison:')
    print(validation[['model','group','n_samples','MAPE_percent']].to_string(index=False,float_format=lambda x:f'{x:.3f}'))
    # Pick model using ONLY overall validation MAPE; low-KE MAPE is diagnostic.
    overall=validation[validation.group=='entire_set']
    best_label=overall.loc[overall.MAPE_percent.idxmin(),'model']
    best_features,best_model=feature_sets[best_label]
    test_pred=best_model.predict(best_features.loc[mask['test']])
    test_metrics=evaluate(y.loc[mask['test']],test_pred,df.loc[mask['test']])
    test_metrics.insert(0,'model',best_label)
    test_metrics.to_csv(args.out/'selected_model_test_metrics.csv',index=False)
    test_detail=df.loc[mask['test'],FEATURES+[TARGET]].copy()
    test_detail.insert(0,'original_seed35_row',test_detail.index)
    test_detail['predicted_KE_ratio']=test_pred
    test_detail['relative_error_percent'] = 100*np.abs(test_pred-test_detail[TARGET].to_numpy())/np.maximum(test_detail[TARGET].to_numpy(),np.finfo(float).eps)
    test_detail.to_csv(args.out/'selected_model_test_predictions.csv',index=False)
    joblib.dump(best_model,args.out/'selected_model.joblib')
    print(f'\nSelected by OVERALL validation MAPE: {best_label}')
    print('\nSelected-model test results:')
    print(test_metrics[['group','n_samples','MAPE_percent','MAE','RMSE','R2']].to_string(index=False,float_format=lambda x:f'{x:.4f}'))
    print(f'\nSaved to {args.out.resolve()}')
    print('CAUTION: This is exploratory if you have already inspected the Seed35 test set. Confirm on a new independent DEM test set.')


if __name__=='__main__':
    main()
