"""Exp 03 — Rolling purged Walk-Forward Analysis (Pardo Ch.11, 2026 protocol)."""
import os, sys, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import yaml, pandas as pd
from pardo_wfa.data import download_all
from pardo_wfa.walkforward import rolling_walkforward

ap = argparse.ArgumentParser()
ap.add_argument("--config", default="config/experiment.yaml")
a = ap.parse_args()
cfg = yaml.safe_load(open(a.config))
data = download_all(cfg["data"]["symbols"], cfg["data"]["start"], cfg["data"]["end"], cfg["data"]["cache_dir"])
os.makedirs("results", exist_ok=True)
summ = []
for sym, df in data.items():
    wf = rolling_walkforward(df, cfg["optimization"]["ma_fast_range"], cfg["optimization"]["ma_slow_range"],
                             cfg["walkforward"]["in_sample_days"], cfg["walkforward"]["out_of_sample_days"],
                             cfg["walkforward"]["step_days"], cfg["walkforward"]["purge_days"],
                             cfg["data"]["commission_per_trade"], cfg["data"]["slippage_bps"],
                             cfg["data"]["risk_free"], cfg["optimization"]["min_trades"],
                             cfg["walkforward"]["objective"])
    wf["folds"].to_csv(f"results/03_wfa_{sym.replace('=','_').replace('-','_')}.csv", index=False)
    verdict = "ROBUST" if (wf["pass_rate"] >= 0.5 and wf["median_wfe"] >= 0.5) else ("MARGINAL" if wf["pass_rate"] >= 0.4 else "FAIL")
    print(f"{sym:10s} folds={len(wf['folds']):2d} pass={wf['pass_rate']:.0%} medWFE={wf['median_wfe']:+.2f} jump={wf['param_jump']:.1f} -> {verdict}")
    summ.append({"symbol": sym, "folds": len(wf["folds"]), "pass_rate": wf["pass_rate"],
                 "median_wfe": wf["median_wfe"], "param_jump": wf["param_jump"], "verdict": verdict})
pd.DataFrame(summ).to_csv("results/03_wfa_summary.csv", index=False)
print("saved results/03_wfa_*.csv")
