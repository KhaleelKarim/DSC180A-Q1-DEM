"""Plot new baseline-centered OAT experiments. Run from repo root:
python src/plot_oat_new_baselines.py
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data'/'oat'
OUT = ROOT/'results'/'visualizations'/'python_seed35'
NAMES = ['c2_A','c2_B','c2_C','c2_D','c3_A','c3_B','c3_C','c3_D']
PLOTS = [('representative','07_oat_representative_design.png','Representative design'),
         ('best_ke','08_oat_best_ke_design.png','Lowest-KE sampled design')]
OUT.mkdir(parents=True, exist_ok=True)
for kind,filename,title in PLOTS:
    bpath = BASE/'baselines'/f'{kind}.csv'
    if not bpath.is_file():
        raise FileNotFoundError(f'Missing baseline {bpath}; run selector first.')
    baseline = pd.read_csv(bpath).iloc[0]
    fig,axs = plt.subplots(4,2,figsize=(13,15))
    for j,name in enumerate(NAMES):
        path=BASE/kind/f'oat_{name}.csv'
        if not path.is_file():
            raise FileNotFoundError(f'Missing {path}; complete MATLAB sweep first.')
        df=pd.read_csv(path)
        df=df[np.isfinite(df['parameter_value']) & np.isfinite(df['KE_ratio']) & (df['KE_ratio']>0)].sort_values('parameter_value')
        if df.empty: raise ValueError(f'No valid points in {path}')
        ax=axs.flat[j]
        ax.plot(df['parameter_value'],df['KE_ratio'],'o-',markersize=3,linewidth=1.4)
        ax.axvline(baseline[name],color='gray',linestyle='--',linewidth=1,label='Baseline')
        ax.scatter([baseline[name]],[baseline['KE_ratio']],color='red',marker='x',s=40,zorder=3,label='CSV baseline KE')
        ax.set_yscale('log')
        ax.set_xlabel(name)
        ax.set_ylabel('KE ratio (log scale)')
        ax.set_title(f'{name} vs. KE ratio')
        ax.grid(alpha=.25)
        if j==0: ax.legend(fontsize=8)
    fig.suptitle(f'OAT Sensitivity — {title}\nOther seven coefficients fixed at baseline; dashed line = baseline value',fontsize=13,y=.997)
    fig.tight_layout(rect=[0,0,1,.97])
    dest=OUT/filename
    fig.savefig(dest,dpi=220,bbox_inches='tight')
    plt.close(fig)
    print('Saved:',dest)
print('\nOriginal Figure 06 was not modified.')
