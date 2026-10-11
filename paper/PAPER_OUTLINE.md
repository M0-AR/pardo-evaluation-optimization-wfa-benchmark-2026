# Paper skeleton — from benchmark to publishable (builds only on results/ in this repo)

**Working title:** *Window-Ratio Power in Walk-Forward Analysis: Why Short Out-of-Sample Windows Masquerade as Strategy Failure (A Pardo Replication on Live 2015–2026 Data)*

## RQs
- RQ1: Does Pardo WFA (rolling, purged) separate robust from overfit MA trend systems across 8 live assets? (exp 03)
- RQ2: Is median-WFE / pass-rate a monotone function of OOS/IS ratio at fixed strategy? (exp 05, H1)
- RQ3: Do PROM vs Sharpe vs GT-Score select different locked params, and does GT-Score generalize best? (ablation — harness ready)
- RQ4: Does CPCV-purge change verdicts vs unpurged WFA? (ablation — harness ready)

## H1 (pre-registered before exp 04 holdout was inspected for tuning)
Short-OOS (63d, ratio ≤0.125) WFA is underpowered (<30 concatenated-OOS trades, placebo p≈1) and yields false FAILs; 252/252 (ratio 1.0) maximizes measured robustness at fixed costs. Mechanism: estimator noise, not alpha decay.

## Identification
- Rolling WFA, purge 5d, PROM-locked, concatenated-OOS scoring only; holdout (last 126d) never tuned.
- Placebo: 200 label-permutations per series → z/p; dof-remaining; big-fish; param-jump stability.
- Threats: daily-only, long/flat-only, Yahoo-grade data, single family (MA) in matrix — all disclosed; extensions listed.

## Tables/Figures (all generatable from results/)
1. Preliminary grid (01) — theory-expectation check.
2. PROM optimization surface (02) — plateau vs spike.
3. Main WFA folds + summary (03) — SPY ROBUST vs EURUSD FAIL.
4. Window-ratio matrix (05) — the H1 figure (pass/WFE vs ratio).
5. Live holdout (04) — honesty plot: WFA-robust ≠ next-quarter profit.
6. Costs/purge ablation (future) + objective horse-race (future).

## Ethics/reproducibility
Frozen cache + seeds + docker + tests; no cherry-picked folds (all folds in CSVs); negative results (EURUSD, SPY holdout loss) reported. Not investment advice.
