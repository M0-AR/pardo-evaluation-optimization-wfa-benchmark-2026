"""Pardo Ch.13 overfitting diagnostics (from scratch).

- degrees_of_freedom_remaining(): 1 - used/total (Pardo >=90% rule)
- permutation_placebo(): label-permutation null (Singha 2025 z-test spirit) —
  shuffle returns B times, recompute Sharpe, report z of realized vs null
- big_fish_flag(): top-2 trades share of total profit > 50% on <50 trades
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def degrees_of_freedom_remaining(n_bars: int, longest_lookback: int, n_rules: int) -> float:
    used = longest_lookback + n_rules
    return max(0.0, 1.0 - used / max(n_bars, 1))


def permutation_placebo(rets: pd.Series, n_perm: int = 200, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    r = rets.to_numpy()
    def sharpe(x):
        sd = x.std()
        return 0.0 if sd == 0 else float(x.mean() / sd * np.sqrt(252))
    real = sharpe(r)
    nulls = np.array([sharpe(rng.permutation(r)) for _ in range(n_perm)])
    mu, sd = float(nulls.mean()), float(nulls.std() + 1e-12)
    z = (real - mu) / sd
    p = float((nulls >= real).mean())
    return {"realized_sharpe": real, "null_mean": mu, "null_sd": sd, "z": float(z), "p": float(p)}


def big_fish_flag(trades: pd.DataFrame) -> dict:
    if trades is None or len(trades) < 5:
        return {"flag": False, "top2_share": 0.0}
    # approximate $ P/L via ret (capital-comparable); use sorted rets
    s = trades["ret"].sort_values(ascending=False).to_numpy()
    tot = s.sum()
    top2 = s[:2].sum()
    share = float(top2 / tot) if tot > 0 else 0.0
    return {"flag": bool(share > 0.5 and len(trades) < 50), "top2_share": share}
