"""Pardo Ch.6 historical simulation with realistic assumptions.

- trade NEXT OPEN after signal bar (kills phantom-trade / best-guess bias)
- costs: commission (fixed $/trade) + slippage (bps of price) applied on every fill
- long/flat only (avoids short-borrow modelling disputes; short leg studied via
  inverted series in hidden-pattern experiment)
- equity curve, trade list, per-trade returns are all returned for audit
"""
from __future__ import annotations
import pandas as pd
import numpy as np


def apply_costs(price: float, commission: float, slippage_bps: float) -> float:
    return commission + price * slippage_bps / 10000.0


def backtest_long_flat(df: pd.DataFrame, position: pd.Series,
                       commission: float = 1.0, slippage_bps: float = 5.0,
                       init_cash: float = 100000.0) -> dict:
    px_open = df["Open"].to_numpy()
    pos = position.reindex(df.index).fillna(0).to_numpy().astype(int)
    # desired position known at close of bar t -> fill at open of bar t+1
    target = np.zeros_like(pos)
    target[1:] = pos[:-1]
    cash = init_cash
    shares = 0.0
    equity = np.zeros(len(df))
    trades: list[dict] = []
    entry_px = None
    entry_i = None
    for i in range(len(df)):
        px = float(px_open[i])
        want = int(target[i])
        have = 1 if shares > 0 else 0
        if want == 1 and have == 0:
            cost = apply_costs(px, commission, slippage_bps)
            # all-in (fractional) so results are capital-comparable across assets
            shares = max((cash - cost) / px, 0.0)
            cash = 0.0
            entry_px, entry_i = px, i
        elif want == 0 and have == 1:
            cost = apply_costs(px, commission, slippage_bps)
            cash = shares * px - cost
            ret = (px - entry_px) / entry_px if entry_px else 0.0
            trades.append({"entry_idx": entry_i, "exit_idx": i,
                           "entry_px": entry_px, "exit_px": px, "ret": ret})
            shares = 0.0
            entry_px, entry_i = None, None
        equity[i] = cash + shares * px
    if shares > 0:  # mark open position at last close (Pardo open-position P/L)
        equity[-1] = shares * float(df["Close"].iloc[-1])
    equity_s = pd.Series(equity, index=df.index)
    rets = equity_s.pct_change().fillna(0.0)
    return {"equity": equity_s, "rets": rets, "trades": pd.DataFrame(trades),
            "n_trades": len(trades)}
