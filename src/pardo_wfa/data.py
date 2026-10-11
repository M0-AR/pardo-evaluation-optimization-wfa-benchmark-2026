"""Live + cached OHLC downloader (Yahoo Finance, no key).

Best practice 2026 (votes: vectorbt YFData docs, IBKR WFA guide, RebellionResearch 2026):
- single source of truth on disk (csv cache) so every experiment is reproducible
- explicit cache key = symbol+start+end; refresh only on demand
- no look-ahead: download-then-freeze; purge gap applied later in walkforward.py
"""
from __future__ import annotations
import os
import pandas as pd
import yfinance as yf


def _flat(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.rename(columns={c: str(c).replace(" ", "_") for c in df.columns})
    rename = {}
    for c in list(df.columns):
        lc = c.lower()
        if "open" in lc and "adj" not in lc:
            rename[c] = "Open"
        elif "high" in lc:
            rename[c] = "High"
        elif "low" in lc:
            rename[c] = "Low"
        elif lc == "close" or lc.startswith("close"):
            rename[c] = "Close"
        elif "volume" in lc:
            rename[c] = "Volume"
    df = df.rename(columns=rename)
    return df


def download_symbol(symbol: str, start: str, end: str, cache_dir: str = "data_cache") -> pd.DataFrame:
    os.makedirs(cache_dir, exist_ok=True)
    safe = symbol.replace("=", "_").replace("-", "_").replace("/", "_")
    path = os.path.join(cache_dir, f"{safe}_{start}_{end}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
        return df
    df = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=False)
    if df is None or len(df) == 0:
        raise RuntimeError(f"empty download for {symbol}")
    df = _flat(df)
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    df = df[keep].dropna()
    df.to_csv(path)
    return df


def download_all(symbols, start, end, cache_dir="data_cache"):
    out = {}
    for s in symbols:
        try:
            out[s] = download_symbol(s, start, end, cache_dir)
        except Exception as e:  # noqa: BLE001
            print(f"[data] FAIL {s}: {type(e).__name__}: {str(e)[:200]}")
    return out
