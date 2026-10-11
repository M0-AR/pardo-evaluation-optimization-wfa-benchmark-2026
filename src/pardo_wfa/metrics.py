"""Pardo Ch.12 performance evaluation + 2026 robust objectives.

- max_drawdown, Sharpe (annualized), PROM (Bo Thunman / Pardo Ch.9: pessimistic
  return on margin — penalizes small samples via sqrt rule)
- gt_score: Sheppert (2026) GT-Score spirit — composite of Sharpe, consistency
  (win-rate distance from 0.5 scaled), and downside (Sterling-like ret/dd).
  Implemented from scratch to avoid paper-code reuse.
- model_efficiency: net profit / perfect profit (Pardo Ch.12). Perfect profit =
  sum |swing| buying every valley selling every peak on CLOSE (unachievable ideal).
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> tuple[float, float]:
    peak = equity.cummax()
    dd = (equity - peak) / peak.replace(0.0, np.nan)
    dd = dd.fillna(0.0)
    return float(dd.min()), float(((equity - peak).min()))


def sharpe_annualized(rets: pd.Series, risk_free: float = 0.02, periods: int = 252) -> float:
    ex = rets - risk_free / periods
    sd = ex.std()
    if sd == 0 or np.isnan(sd):
        return 0.0
    return float(ex.mean() / sd * np.sqrt(periods))


def prom(trades: pd.DataFrame, margin: float = 10000.0) -> float:
    """Pessimistic Return on Margin: shrink wins down / losses up by sqrt(n)."""
    if trades is None or len(trades) == 0:
        return -1.0
    wins = trades[trades["ret"] > 0]
    loss = trades[trades["ret"] <= 0]
    nw, nl = len(wins), len(loss)
    aw = wins["ret"].mean() if nw else 0.0
    al = -loss["ret"].mean() if nl else 0.0
    adj_w = max(nw - np.sqrt(nw), 0.0) * aw if nw else 0.0
    adj_l = (nl + np.sqrt(nl)) * al if nl else 0.0
    return float((adj_w - adj_l) * 100000.0 / margin / 100.0)


def gt_score(equity: pd.Series, rets: pd.Series, trades: pd.DataFrame) -> float:
    """Composite robust objective (GT-Score spirit): Sharpe + consistency - downside."""
    sh = sharpe_annualized(rets)
    n = len(trades) if trades is not None else 0
    if n == 0:
        return -10.0
    win_rate = float((trades["ret"] > 0).mean())
    consistency = 1.0 - abs(win_rate - 0.55) * 2.0  # reward ~55% systematic sweet spot
    dd_rel, _ = max_drawdown(equity)
    total_ret = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    downside = total_ret / abs(dd_rel) if dd_rel < 0 else total_ret * 2.0
    sample_bonus = min(np.log1p(n) / np.log1p(100), 1.0)  # 0..1, saturates ~100 trades
    return float(0.5 * np.tanh(sh / 2.0) + 0.3 * consistency + 0.2 * np.tanh(downside) + 0.2 * sample_bonus)


def perfect_profit(close: pd.Series) -> float:
    d = close.diff().abs().sum()
    return float(d) if not np.isnan(d) else 0.0


def model_efficiency(net_profit: float, close: pd.Series) -> float:
    pp = perfect_profit(close)
    if pp <= 0:
        return 0.0
    return float(net_profit / pp)


def summary_stats(equity: pd.Series, rets: pd.Series, trades: pd.DataFrame,
                  close: pd.Series, risk_free: float = 0.02) -> dict:
    total_ret = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    yrs = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    cagr = float((1.0 + total_ret) ** (1.0 / yrs) - 1.0) if total_ret > -1 else -1.0
    dd_rel, dd_abs = max_drawdown(equity)
    n = len(trades)
    win_rate = float((trades["ret"] > 0).mean()) if n else 0.0
    years = yrs
    ann_ret = total_ret / years if years else 0.0
    return {
        "total_ret": total_ret, "cagr": cagr, "ann_ret": ann_ret,
        "sharpe": sharpe_annualized(rets, risk_free),
        "max_dd": dd_rel, "max_dd_abs": dd_abs,
        "n_trades": n, "win_rate": win_rate,
        "prom": prom(trades), "gt": gt_score(equity, rets, trades),
        "model_eff": model_efficiency(float(equity.iloc[-1] - equity.iloc[0]), close),
        "years": years,
    }
