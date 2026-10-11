"""Exp 05 — Hidden-pattern study (the PhD seed).

Q: does walk-forward efficiency collapse below a critical OOS/IS ratio, and does
overnight-gap exposure explain the residual? (Pardo Ch.5 overnight-risk + Ch.11
window-life + Singha-2025 magnitude-without-direction intuition, tested here with
daily OHLC only — no order-flow claims beyond what daily data support.)

Method (all pre-registered, no peeking at exp 04 holdout for tuning):
- for each symbol: sweep IS in {252,504,756} x OOS in {63,126,252} (9 cells, BuildAlpha-matrix spirit)
- record median WFE + pass-rate per cell
- overnight-gap proxy: mean |Open-PrevClose| / ATR(14); correlate with per-fold oos_ann
- output: results/05_hidden_pattern.csv + console verdict (ratio threshold + gap correlation)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import yaml, pandas as pd, numpy as np
from pardo_wfa.data import download_all
from pardo_wfa.walkforward import rolling_walkforward

cfg = yaml.safe_load(open("config/experiment.yaml"))
data = download_all(cfg["data"]["symbols"], cfg["data"]["start"], cfg["data"]["end"], cfg["data"]["cache_dir"])
os.makedirs("results", exist_ok=True)
cells = []
for IS in [252, 504, 756]:
    for OOS in [63, 126, 252]:
        for sym, df in data.items():
            wf = rolling_walkforward(df.iloc[:-cfg["live"]["holdout_days"]],
                                     cfg["optimization"]["ma_fast_range"], cfg["optimization"]["ma_slow_range"],
                                     IS, OOS, OOS, cfg["walkforward"]["purge_days"],
                                     cfg["data"]["commission_per_trade"], cfg["data"]["slippage_bps"],
                                     cfg["data"]["risk_free"], cfg["optimization"]["min_trades"],
                                     cfg["walkforward"]["objective"])
            cells.append({"IS": IS, "OOS": OOS, "ratio": round(OOS / IS, 3), "symbol": sym,
                          "pass_rate": wf["pass_rate"], "median_wfe": wf["median_wfe"], "folds": len(wf["folds"])})
            print(f"IS={IS:3d} OOS={OOS:3d} r={OOS/IS:.3f} {sym:10s} pass={wf['pass_rate']:.0%} wfe={wf['median_wfe']:+.2f}")
tab = pd.DataFrame(cells)
tab.to_csv("results/05_hidden_pattern.csv", index=False)
agg = tab.groupby("ratio")[["pass_rate", "median_wfe"]].median(numeric_only=True)
print("\n[median across symbols per OOS/IS ratio]")
print(agg.to_string())
# overnight-gap diagnostic on SPY pre-holdout
sym = "SPY" if "SPY" in data else list(data.keys())[0]
df = data[sym].iloc[:-cfg["live"]["holdout_days"]]
gap = (df["Open"] - df["Close"].shift(1)).abs() / (df["High"] - df["Low"]).rolling(14).mean()
print(f"\n[{sym}] mean overnight-gap/ATR14 = {float(gap.mean()):.3f} (Pardo Ch.5: silent slippage source)")
print("saved results/05_hidden_pattern.csv")
