"""Pipeline smoke tests — every file change must pass these before commit (no hand-edit without verify)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pandas as pd, numpy as np

def _synth(n=500, seed=0):
    rng = np.random.default_rng(seed)
    px = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    df = pd.DataFrame({"Open": px, "High": px * 1.005, "Low": px * 0.995, "Close": px,
                       "Volume": 1_000_000}, index=pd.date_range("2020-01-01", periods=n))
    return df

def test_signals_no_lookahead():
    from pardo_wfa.strategies import ma_signals, donchian_signals
    df = _synth()
    s = ma_signals(df, 5, 20)
    assert s["position"].isin([0, 1]).all()
    d = donchian_signals(df, 20)
    assert d["position"].iloc[:21].sum() == 0  # channel needs warmup, no peeking

def test_backtest_costs_reduce_equity():
    from pardo_wfa.strategies import ma_signals
    from pardo_wfa.backtest import backtest_long_flat
    df = _synth()
    sig = ma_signals(df, 5, 20)
    free = backtest_long_flat(df, sig["position"], 0.0, 0.0)
    costly = backtest_long_flat(df, sig["position"], 10.0, 50.0)
    assert costly["equity"].iloc[-1] <= free["equity"].iloc[-1] + 1e-6

def test_wfe_math():
    from pardo_wfa.walkforward import walkforward_efficiency
    assert walkforward_efficiency(0.10, 0.20) == 0.5
    assert walkforward_efficiency(-0.05, 0.20) < 0.1

def test_placebo_runs():
    from pardo_wfa.overfit import permutation_placebo
    r = pd.Series(np.random.default_rng(1).normal(0, 1, 300))
    out = permutation_placebo(r, n_perm=20)
    assert "z" in out and np.isfinite(out["z"])
