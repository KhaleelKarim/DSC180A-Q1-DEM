"""Select real baseline rows from data/raw/python_seed35.csv.
Run from repository root: python src/select_oat_baselines.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'raw' / 'python_seed84.csv'
OUT = ROOT / 'data' / 'oat' / 'baselines'
NAMES = ['c2_A','c2_B','c2_C','c2_D','c3_A','c3_B','c3_C','c3_D']

raw = pd.read_csv(INPUT)
missing = set(NAMES + ['KE_ratio']) - set(raw.columns)
if missing:
    raise ValueError(f'Missing CSV columns: {sorted(missing)}')
valid = raw[NAMES + ['KE_ratio']].replace([np.inf, -np.inf], np.nan).dropna()
c2 = valid[NAMES[:4]].to_numpy()
c3 = valid[NAMES[4:]].to_numpy()
feasible = ((c2 >= -120) & (c2 <= 0)).all(axis=1) & ((c3 >= 0) & (c3 <= 4000)).all(axis=1) & (c3 > (2/9) * c2**2).all(axis=1) & (valid.KE_ratio.to_numpy()>0)
valid = valid.loc[feasible]
if valid.empty:
    raise ValueError('No feasible rows in the dataset.')

# Use an actual observed row, closest to the 8D coordinate-wise median.
# Scale by empirical standard deviation, so c2 and c3 magnitudes are comparable.
medians = valid[NAMES].median()
scale = valid[NAMES].std().replace(0, 1)
distance = ((valid[NAMES] - medians) / scale).pow(2).sum(axis=1)
representative_idx = distance.idxmin()
best_idx = valid['KE_ratio'].idxmin()

OUT.mkdir(parents=True, exist_ok=True)
for kind, index in [('representative', representative_idx), ('best_ke', best_idx)]:
    row = valid.loc[[index], NAMES + ['KE_ratio']]
    target = OUT / f'{kind}.csv'
    row.to_csv(target, index=False, float_format='%.17g')
    print(f'\n{kind}: input row {index+2:,} including CSV header')
    print(row.to_string(index=False))
    print(f'Saved: {target}')
print('\nBaselines are REAL dataset rows; the minimum KE row is observational, not a proven global optimum.')
