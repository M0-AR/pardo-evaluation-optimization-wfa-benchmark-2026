# RESEARCH_PROTOCOL — zero-to-hero, depth-first, vote-weighted (2026-2027)

Rule obeyed: **one websearch at a time, never parallel** (429-avoidance); on 429: backoff 5s → 10s, max 3; fallback `webfetch https://lite.duckduckgo.com/lite/?q=...` (no key, no cap). Exa `websearch` first, then MCP cross-votes with *different keywords each tool*.

## 1. Search log (sequential, all executed Oct 2026)

| # | Tool | Keywords (distinct) | What it returned (vote) |
|---|---|---|---|
| 1 | `websearch` (Exa-deep) | Pardo walk-forward analysis trading strategy optimization best practice 2026 | Gold-standard status; Pardo 1992→2008; IBKR-2025 WFA steps; BuildAlpha rolling-vs-anchored + matrix + synthetic-data; MQL5-2026 Pardo pipeline artifacts |
| 2 | `duckduckgo_search` | overfitting trading strategy optimization walk-forward efficiency 2025 robust backtest | 10-way vote: IS/OOS splits, anchored-vs-rolling, efficiency ratios, CPC, thresholds |
| 3 | `openresearch.web_search` | algorithmic trading backtest overfitting combinatorial purged cross-validation 2026 | CPCV (Ch.12 AFML) + Springer WFA/CV/CPCV chapter + RebellionResearch 2026 rigorous guide |
| 4 | `paper-search.search_arxiv` | walk-forward optimization trading strategy overfitting validation | AlgoXpert 2603.09219 (IS/WFA/OOS+purge+veto); Mroziewicz 2602.10785 (81 window combos, BTC intraday); Singha 2512.15720 (entropy→magnitude 2.89×, z=14.4); Xiong 2606.09025 (cash-overlay WFO) |
| 5 | `openresearch.search_openalex` | walk-forward analysis robustness trading strategy evaluation | Pardo 2008 record; Tinsley 2026 WF-Correlation; Kör & Zengin 2026 GA+WFO (Sortino 1.98 vs 1.21); GT-Score 2026 |
| 6 | `agent-reach.search(web)` | Python backtesting best framework vectorbt backtrader 2026 live data Yahoo Finance | VectorBT vectorized (1M orders 70–100ms) vs Backtrader event-driven; explore-in-VBT→confirm-event-driven; YFData for learning |
| 7 | `kaggle.search_everything` | walk forward optimization trading strategy backtest | TS-10 validation-for-time-series notebook; backtesting.py price-forecast notebooks (community practice votes) |
| 8 | `wiki.wiki_search` | walk forward optimization trading overfitting | Prediction/overfitting pages (weak — recorded as weak vote, not relied on) |
| 9 | `gsd.websearch` | best practice reproducible quant research docker live market data verification 2026 | empty (recorded; docker-reproducibility taken from VectorBT/IBKR docs instead) |
| 10 | `superpowers.semantic_search_skills` | reproducible quantitative research backtesting validation | systematic-debugging/reproducibility skills (process vote) |
| 11 | `openresearch.search_hacker_news` | walk-forward backtest overfitting trading | PyBroker ML algotrading thread (70pts — practitioner vote) |
| 12 | `paper-search.search_semantic` | walk forward analysis trading strategy robustness | empty (recorded) |
| 13 | `gitmcp.search_generic_documentation` (polakowo/vectorbt) | walk forward validation backtest optimization | VBT cross-validation/WFO resources, run_combs heatmaps, PRO-vs-free split |
| 14 | `openresearch.search_news` | walk-forward optimization trading robustness | RebellionResearch 2026 ML-backtesting guide (fresh-2026 vote); rest off-topic (recorded) |
| 15 | `paper-search.search_papers` (arxiv+semantic+openalex+crossref) | Pardo walk forward analysis overfitting trading strategy evaluation | 8 papers: AlgoXpert, GA+WFO, WF-Correlation, GT-Score (+98% generalization), cointegration-FX WFO, Pardo Ch.11 record |
| 16 | `webfetch` lite.duckduckgo fallback | walk forward optimization Pardo robust trading 2026 | 10/10 2026 guides call WFA gold standard (bypasses Exa entirely — fallback verified) |

## 2. Synthesis rule (how votes became design)

- Unanimous (WFA gold-standard, OOS-only scoring, param-stability > best-spike, rolling>anchored, purge, costs-in) → **hard requirements** in `src/` + `config/`.
- 2026-frontier (purge gaps, double-OOS, window-matrix, GT-Score/PROM, vetoes, synthetic-data alongside—not instead of—WFO) → implemented except synthetic-data (listed as future work, not faked).
- Engineering (VBT-speed vs event-realism, Yahoo-for-learning, docker-freeze) → own minimal engine (to avoid PRO-dependency) + frozen `data_cache/` + docker.
- Weak/empty votes → recorded, not used. No file written from memory; every number in README traces to `results/`.

## 3. Zero-to-hero pipeline (Pardo Ch.3 → repo)

Formulate (Ch.7 MA/RSI/Donchian exact) → Specify (`strategies.py` docstrings) → Preliminary (exp01) → Optimize (exp02 PROM grid, proportional steps) → WFA (exp03 rolling-purged + WFE) → Live-locked holdout (exp04 placebo/dof/big-fish) → Monitor/refine (exp05 matrix + PAPER_OUTLINE). `tests/` gates every edit.

## 4. Verify-before-write discipline

`pytest` green → run affected experiment → read console + CSV → only then document numbers. The two bugs found this way (empty-grid KeyError; 30-trade gate censoring 3y IS folds → rescaled to 10) are kept in git history as evidence the gate works.
