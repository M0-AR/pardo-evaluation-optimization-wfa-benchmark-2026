"""pardo_wfa — from-scratch Pardo (2008) A-Z replication."""
from .strategies import ma_signals, rsi_signals, donchian_signals, rsi_value
from .backtest import backtest_long_flat, apply_costs
from .metrics import summary_stats, sharpe_annualized, prom, gt_score, max_drawdown, model_efficiency
from .optimization import grid_search_ma, grid_search_rsi, grid_search_donchian
from .walkforward import rolling_walkforward, walkforward_efficiency

__all__ = [
    "ma_signals", "rsi_signals", "donchian_signals", "rsi_value",
    "backtest_long_flat", "apply_costs",
    "summary_stats", "sharpe_annualized", "prom", "gt_score",
    "max_drawdown", "model_efficiency",
    "grid_search_ma", "grid_search_rsi", "grid_search_donchian",
    "rolling_walkforward", "walkforward_efficiency",
]
