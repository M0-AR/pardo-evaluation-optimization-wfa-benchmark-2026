"""Generate all README/preview visuals from verified results (no hand-drawn charts)."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("docs", exist_ok=True)

# 1) WFA summary bars (pass-rate + median WFE per symbol)
s = pd.read_csv("results/03_wfa_summary.csv")
fig, ax1 = plt.subplots(figsize=(10, 5))
x = range(len(s))
ax1.bar(x, s["pass_rate"], alpha=0.7, label="pass-rate")
ax1.set_xticks(list(x), s["symbol"], rotation=20)
ax1.set_ylim(0, 1)
ax1.set_ylabel("OOS pass-rate")
ax2 = ax1.twinx()
ax2.plot(list(x), s["median_wfe"], marker="o", color="red", label="median WFE")
ax2.axhline(0.5, linestyle="--", color="gray")
ax2.set_ylabel("median WFE (healthy >0.5)")
plt.title("Walk-Forward Verdicts — 756d IS / 126d OOS, purged (live 2015-2026)")
fig.tight_layout()
fig.savefig("docs/wfa_summary.png", dpi=150)
print("wrote docs/wfa_summary.png")

# 2) Window-ratio power curve (hidden pattern)
h = pd.read_csv("results/05_hidden_pattern.csv")
agg = h.groupby("ratio")[["pass_rate", "median_wfe"]].median(numeric_only=True).reset_index()
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(agg["ratio"], agg["pass_rate"], marker="o", label="median pass-rate")
ax.plot(agg["ratio"], agg["median_wfe"], marker="s", label="median WFE")
ax.set_xlabel("OOS/IS ratio")
ax.set_ylabel("score")
ax.set_title("Hidden pattern: WFA power rises with OOS/IS ratio (1y/1y sweet spot)")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("docs/window_ratio.png", dpi=150)
print("wrote docs/window_ratio.png")

# 3) Preliminary Sharpe heat-strip per symbol (MA vs RSI vs DON)
p = pd.read_csv("results/01_preliminary.csv")
piv = p.pivot(index="symbol", columns="strategy", values="sharpe")
fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(piv.values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(piv.columns)), piv.columns)
ax.set_yticks(range(len(piv.index)), piv.index)
for i in range(len(piv.index)):
    for j in range(len(piv.columns)):
        ax.text(j, i, f"{piv.values[i, j]:+.2f}", ha="center", va="center", fontsize=8)
ax.set_title("Preliminary Sharpe (full-sample, costs in) — DON robust on equity, FX negative")
fig.colorbar(im, ax=ax, label="Sharpe")
fig.tight_layout()
fig.savefig("docs/preliminary_sharpe.png", dpi=150)
print("wrote docs/preliminary_sharpe.png")

# 4) Live holdout CAGR bars
live = pd.read_csv("results/04_live.csv")
fig, ax = plt.subplots(figsize=(10, 4.5))
colors = ["green" if v > 0 else "red" for v in live["cagr"]]
ax.bar(live["symbol"], live["cagr"], color=colors, alpha=0.75)
ax.set_ylabel("locked-holdout CAGR (last 126d)")
ax.set_title("Strict live holdout (never tuned) — honest: robust in WFA != green next quarter")
plt.xticks(rotation=20)
fig.tight_layout()
fig.savefig("docs/live_holdout.png", dpi=150)
print("wrote docs/live_holdout.png")

# 5) SPY equity snapshot: buy-hold vs MA(10,30) from frozen cache
spy = pd.read_csv("data_cache/SPY_2015-01-01_2026-10-10.csv", parse_dates=["Date"], index_col="Date")
import sys
sys.path.insert(0, "src")
from pardo_wfa.strategies import ma_signals
from pardo_wfa.backtest import backtest_long_flat
sig = ma_signals(spy, 10, 30)
bt = backtest_long_flat(spy, sig["position"], 1.0, 5.0)
bh = spy["Close"] / spy["Close"].iloc[0] * 100000
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(bt["equity"].index, bt["equity"] / 100000 * 100000, label="MA(10,30) equity ($)")
ax.plot(bh.index, bh, label="buy-hold ($)", alpha=0.6)
ax.set_title("SPY 2015-2026: MA(10,30) vs buy-hold (next-open fills, costs in)")
ax.legend()
fig.tight_layout()
fig.savefig("docs/spy_equity.png", dpi=150)
print("wrote docs/spy_equity.png")
