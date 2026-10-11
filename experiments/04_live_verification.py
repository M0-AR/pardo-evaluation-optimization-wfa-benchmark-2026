"""Exp 04 — Strict live/holdout verification (AlgoXpert-2026 OOS lock + CPCV purge).

- holdout = last `holdout_days` bars, NEVER used in any tuning (exp 01-03 use data before it)
- params locked = median best (fast,slow) across WFA folds (stable plateau, not spike)
- reports live CAGR/sharpe/dd + permutation placebo z + big-fish flag + dof remaining
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import yaml, pandas as pd
from pardo_wfa.data import download_all
from pardo_wfa.strategies import ma_signals
from pardo_wfa.backtest import backtest_long_flat
from pardo_wfa.metrics import summary_stats
from pardo_wfa.overfit import permutation_placebo, big_fish_flag, degrees_of_freedom_remaining

cfg = yaml.safe_load(open("config/experiment.yaml"))
data = download_all(cfg["data"]["symbols"], cfg["data"]["start"], cfg["data"]["end"], cfg["data"]["cache_dir"])
os.makedirs("results", exist_ok=True)
rows = []
H = cfg["live"]["holdout_days"]
for sym, df in data.items():
    try:
        folds = pd.read_csv(f"results/03_wfa_{sym.replace('=','_').replace('-','_')}.csv")
        f_lock = int(folds["fast"].median())
        s_lock = int(folds["slow"].median())
    except Exception:  # noqa: BLE001
        f_lock, s_lock = 10, 30
    live = df.iloc[-H:]
    pre = df.iloc[:-H]
    sig = ma_signals(live, f_lock, s_lock)
    bt = backtest_long_flat(live, sig["position"], cfg["data"]["commission_per_trade"], cfg["live"]["fee_bps"])
    st = summary_stats(bt["equity"], bt["rets"], bt["trades"], live["Close"], cfg["data"]["risk_free"])
    pb = permutation_placebo(bt["rets"])
    bf = big_fish_flag(bt["trades"])
    dof = degrees_of_freedom_remaining(len(pre), max(f_lock, s_lock), 3)
    rows.append({"symbol": sym, "fast": f_lock, "slow": s_lock, **st,
                 "placebo_z": pb["z"], "placebo_p": pb["p"],
                 "big_fish": bf["flag"], "top2_share": bf["top2_share"], "dof_remain": dof})
    print(f"{sym:10s} MA({f_lock},{s_lock}) live_cagr={st['cagr']:+.2%} sharpe={st['sharpe']:+.2f} dd={st['max_dd']:.2%} z={pb['z']:+.2f} bigfish={bf['flag']} dof={dof:.1%}")
pd.DataFrame(rows).to_csv("results/04_live.csv", index=False)
print("saved results/04_live.csv")
