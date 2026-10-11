"""Exp 01 — Preliminary testing (Pardo Ch.8): verify calculations + theoretical expectations."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import yaml
from pardo_wfa.data import download_all
from pardo_wfa.strategies import ma_signals, rsi_signals, donchian_signals
from pardo_wfa.backtest import backtest_long_flat
from pardo_wfa.metrics import summary_stats

cfg = yaml.safe_load(open("config/experiment.yaml"))
data = download_all(cfg["data"]["symbols"], cfg["data"]["start"], cfg["data"]["end"], cfg["data"]["cache_dir"])
os.makedirs("results", exist_ok=True)
rows = []
for sym, df in data.items():
    for name, sig in [
        ("MA(10,30)", ma_signals(df, 10, 30)),
        (f"RSI({cfg['preliminary']['rsi_period']})", rsi_signals(df, cfg["preliminary"]["rsi_period"])),
        (f"DON({cfg['preliminary']['donchian_lookback']})", donchian_signals(df, cfg["preliminary"]["donchian_lookback"])),
    ]:
        bt = backtest_long_flat(df, sig["position"], cfg["data"]["commission_per_trade"], cfg["data"]["slippage_bps"])
        st = summary_stats(bt["equity"], bt["rets"], bt["trades"], df["Close"], cfg["data"]["risk_free"])
        rows.append({"symbol": sym, "strategy": name, **st})
        print(f"{sym:10s} {name:12s} n={st['n_trades']:4d} cagr={st['cagr']:+.2%} sharpe={st['sharpe']:+.2f} dd={st['max_dd']:.2%}")
import pandas as pd
pd.DataFrame(rows).to_csv("results/01_preliminary.csv", index=False)
print("saved results/01_preliminary.csv")
