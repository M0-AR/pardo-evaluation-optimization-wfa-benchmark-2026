"""Pardo Ch.10 grid optimization with anti-overscan guards.

- step sizes kept proportional (Pardo overscanning warning): caller passes explicit
  discrete candidate lists (no 1-step scan of slow MA 20..200).
- min_trades gate enforces statistical validity (Pardo >=30 rule).
- objective selectable: prom | sharpe | gt_score (default prom; 2026 vote: GT-Score
  generalizes +98% vs net-profit-only, Sheppert 2026).
"""
from __future__ import annotations
import pandas as pd
from .strategies import ma_signals, rsi_signals, donchian_signals
from .backtest import backtest_long_flat
from .metrics import summary_stats, prom, sharpe_annualized, gt_score


def _score(obj: str, res: dict) -> float:
    if obj == "sharpe":
        return res["stats"]["sharpe"]
    if obj == "gt_score":
        return res["stats"]["gt"]
    return res["stats"]["prom"]


def _run(df, sig, commission, slippage_bps, risk_free):
    bt = backtest_long_flat(df, sig["position"], commission, slippage_bps)
    stats = summary_stats(bt["equity"], bt["rets"], bt["trades"], df["Close"], risk_free)
    return {"stats": stats, "bt": bt}


def grid_search_ma(df, fast_list, slow_list, commission=1.0, slippage_bps=5.0,
                   risk_free=0.02, min_trades=30, objective="prom"):
    rows = []
    for f in fast_list:
        for s in slow_list:
            if f >= s:
                continue
            sig = ma_signals(df, f, s)
            r = _run(df, sig, commission, slippage_bps, risk_free)
            if r["stats"]["n_trades"] < min_trades:
                continue
            rows.append({"fast": f, "slow": s, "score": _score(objective, r), **r["stats"]})
    if not rows:
        return pd.DataFrame()
    tab = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    return tab


def grid_search_rsi(df, period_list, commission=1.0, slippage_bps=5.0,
                    risk_free=0.02, min_trades=30, objective="prom"):
    rows = []
    for p in period_list:
        sig = rsi_signals(df, p)
        r = _run(df, sig, commission, slippage_bps, risk_free)
        if r["stats"]["n_trades"] < min_trades:
            continue
        rows.append({"period": p, "score": _score(objective, r), **r["stats"]})
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def grid_search_donchian(df, n_list, commission=1.0, slippage_bps=5.0,
                         risk_free=0.02, min_trades=30, objective="prom"):
    rows = []
    for n in n_list:
        sig = donchian_signals(df, n)
        r = _run(df, sig, commission, slippage_bps, risk_free)
        if r["stats"]["n_trades"] < min_trades:
            continue
        rows.append({"n": n, "score": _score(objective, r), **r["stats"]})
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
