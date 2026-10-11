"""Exp 02 — Multimarket multiperiod grid optimization (Pardo Ch.10)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import yaml, pandas as pd
from pardo_wfa.data import download_all
from pardo_wfa.optimization import grid_search_ma

cfg = yaml.safe_load(open("config/experiment.yaml"))
data = download_all(cfg["data"]["symbols"], cfg["data"]["start"], cfg["data"]["end"], cfg["data"]["cache_dir"])
os.makedirs("results", exist_ok=True)
all_tabs = {}
for sym, df in data.items():
    tab = grid_search_ma(df, cfg["optimization"]["ma_fast_range"], cfg["optimization"]["ma_slow_range"],
                         cfg["data"]["commission_per_trade"], cfg["data"]["slippage_bps"],
                         cfg["data"]["risk_free"], cfg["optimization"]["min_trades"],
                         cfg["walkforward"]["objective"])
    all_tabs[sym] = tab
    tab.to_csv(f"results/02_opt_{sym.replace('=','_').replace('-','_')}.csv", index=False)
    if len(tab):
        r = tab.iloc[0]
        print(f"{sym:10s} best fast={int(r['fast']):3d} slow={int(r['slow']):3d} prom={r['prom']:+.2f} sharpe={r['sharpe']:+.2f} dd={r['max_dd']:.2%} n={int(r['n_trades'])}")
    else:
        print(f"{sym:10s} NO candidate passed min_trades gate")
print("saved results/02_opt_*.csv")
