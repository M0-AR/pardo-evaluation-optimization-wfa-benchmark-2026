"""Pardo Ch.5 + Ch.7 strategy specifications (exact, testable, no ambiguity).

Three canonical families (cover trend + counter-trend + breakout, as Pardo demands
multi-style coverage):
 1. MA crossover (Pardo Ch.7 dialogue example): long when fast crosses above slow,
    flat when fast crosses below slow. Signal computed on CLOSE, traded NEXT OPEN
    (no look-ahead; Ch.6 phantom-trade guard).
 2. RSI counter-trend: long when RSI(period) < oversold, exit when RSI > overbought.
 3. Donchian breakout (Turtle/TTS simplified, Pardo Ch.2): long when Close breaks
    above highest High of last N bars, exit when Close breaks below lowest Low of last M=N//2.
"""
from __future__ import annotations
import pandas as pd
import numpy as np


def rsi_value(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi.fillna(50.0)


def ma_signals(df: pd.DataFrame, fast: int, slow: int) -> pd.DataFrame:
    close = df["Close"]
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    cross_up = (f > s) & (f.shift(1) <= s.shift(1))
    cross_dn = (f < s) & (f.shift(1) >= s.shift(1))
    # position held AFTER signal bar; execution happens next open in backtest.py
    pos = pd.Series(0, index=df.index, dtype=int)
    cur = 0
    # loop is O(n) and exact; keeps reversal/non-reversal semantics unambiguous
    cu = cross_up.fillna(False).to_numpy()
    cd = cross_dn.fillna(False).to_numpy()
    out = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        if cu[i]:
            cur = 1
        elif cd[i]:
            cur = 0
        out[i] = cur
    pos[:] = out
    return pd.DataFrame({"position": pos, "fast": f, "slow": s})


def rsi_signals(df: pd.DataFrame, period: int = 14, oversold: float = 30.0,
                overbought: float = 70.0) -> pd.DataFrame:
    r = rsi_value(df["Close"], period)
    enter = r < oversold
    exit_ = r > overbought
    out = np.zeros(len(df), dtype=int)
    cur = 0
    en = enter.fillna(False).to_numpy()
    ex = exit_.fillna(False).to_numpy()
    for i in range(len(df)):
        if en[i]:
            cur = 1
        elif ex[i]:
            cur = 0
        out[i] = cur
    return pd.DataFrame({"position": pd.Series(out, index=df.index), "rsi": r})


def donchian_signals(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    m = n // 2 if n >= 4 else 1
    hi = df["High"].rolling(n).max().shift(1)  # yesterday's channel: no look-ahead
    lo = df["Low"].rolling(m).min().shift(1)
    close = df["Close"]
    enter = close > hi
    exit_ = close < lo
    out = np.zeros(len(df), dtype=int)
    cur = 0
    en = enter.fillna(False).to_numpy()
    ex = exit_.fillna(False).to_numpy()
    for i in range(len(df)):
        if en[i]:
            cur = 1
        elif ex[i]:
            cur = 0
        out[i] = cur
    return pd.DataFrame({"position": pd.Series(out, index=df.index),
                         "hi": hi, "lo": lo})
