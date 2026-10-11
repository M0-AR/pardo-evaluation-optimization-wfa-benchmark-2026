"""Pardo Ch.11 Walk-Forward Analysis (rolling, purged, WFE).

Protocol (synthesis of 2026 votes: Pardo gold-standard + IBKR + BuildAlpha matrix
+ Mroziewicz window-length study + AlgoXpert IS/WFA/OOS + CPCV purge):
- rolling IS window of W days, OOS window of H days, step = H
- purge P days between IS end and OOS start (no leakage from indicator lookback)
- inside each fold: grid-search on IS only, lock best params, evaluate once on OOS
- concatenate all OOS equities -> single out-of-sample equity (only this counts)
- WFE = annualized OOS return / annualized IS return (Pardo: >50-60% healthy;
  AlgoXpert 2026: majority-pass + catastrophic veto)
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from .optimization import grid_search_ma


def walkforward_efficiency(ann_oos: float, ann_is: float) -> float:
    if ann_is == 0 or np.isnan(ann_is) or np.isnan(ann_oos):
        return 0.0
    if ann_is < 0 and ann_oos < 0:
        return 0.0
    if ann_is < 0:
        return 1.0 if ann_oos > 0 else 0.0
    return float(ann_oos / ann_is)


def rolling_walkforward(df: pd.DataFrame, fast_list, slow_list,
                        is_days: int = 756, oos_days: int = 126,
                        step_days: int = 126, purge_days: int = 5,
                        commission: float = 1.0, slippage_bps: float = 5.0,
                        risk_free: float = 0.02, min_trades: int = 30,
                        objective: str = "prom") -> dict:
    from .strategies import ma_signals
    from .backtest import backtest_long_flat
    from .metrics import summary_stats

    idx = df.index
    folds = []
    start = 0
    # Pardo statistical gate scaled to window: the 30-trade rule applies to the FULL
    # concatenated OOS (Pardo Ch.6/10). Per-fold IS gate is proportional: 756d -> 10,
    # 504d -> 7, 252d -> 5, floored at 5 so slow-MA candidates are not censored.
    is_gate = max(5, int(10 * is_days / 756))
    # need at least slow_max + purge + oos bars per fold
    while True:
        is_end = start + is_days
        oos_start = is_end + purge_days
        oos_end = oos_start + oos_days
        if oos_end > len(df):
            break
        is_df = df.iloc[start:is_end]
        oos_df = df.iloc[oos_start:oos_end]
        tab = grid_search_ma(is_df, fast_list, slow_list, commission,
                             slippage_bps, risk_free, is_gate, objective)
        if tab is None or len(tab) == 0:
            start += step_days
            continue
        best = tab.iloc[0]
        sig = ma_signals(oos_df, int(best["fast"]), int(best["slow"]))
        bt = backtest_long_flat(oos_df, sig["position"], commission, slippage_bps)
        stats = summary_stats(bt["equity"], bt["rets"], bt["trades"], oos_df["Close"], risk_free)
        # IS stats of locked params for WFE denominator
        sig_is = ma_signals(is_df, int(best["fast"]), int(best["slow"]))
        bt_is = backtest_long_flat(is_df, sig_is["position"], commission, slippage_bps)
        stats_is = summary_stats(bt_is["equity"], bt_is["rets"], bt_is["trades"], is_df["Close"], risk_free)
        folds.append({
            "is_start": str(idx[start].date()), "is_end": str(idx[is_end - 1].date()),
            "oos_start": str(idx[oos_start].date()), "oos_end": str(idx[oos_end - 1].date()),
            "fast": int(best["fast"]), "slow": int(best["slow"]),
            "is_ann": stats_is["ann_ret"], "oos_ann": stats["ann_ret"],
            "oos_sharpe": stats["sharpe"], "oos_dd": stats["max_dd"],
            "oos_trades": stats["n_trades"],
            "wfe": walkforward_efficiency(stats["ann_ret"], stats_is["ann_ret"]),
            "oos_equity_tail": float(bt["equity"].iloc[-1] / bt["equity"].iloc[0] - 1.0),
        })
        start += step_days
    folds_df = pd.DataFrame(folds)
    if len(folds_df):
        pos = (folds_df["oos_ann"] > 0).mean()
        med_wfe = float(folds_df["wfe"].median())
        param_jumps = float(pd.Series(folds_df["fast"]).diff().abs().mean())
    else:
        pos, med_wfe, param_jumps = 0.0, 0.0, float("nan")
    return {"folds": folds_df, "pass_rate": float(pos) if len(folds_df) else 0.0,
            "median_wfe": med_wfe, "param_jump": param_jumps}
