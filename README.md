# Quantitative Market Research

[![Tests](https://github.com/wenwenjiang-lab/quant-research/actions/workflows/tests.yml/badge.svg)](https://github.com/wenwenjiang-lab/quant-research/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Status: active research portfolio.** Registered studies may be complete,
> but this repository does not claim validated alpha or a deployable strategy.

Start with the concise [`research portfolio summary`](reports/executive_summary.md).
Study 01 produced a registered negative forecasting result and kept its final
holdout sealed. Study 02 confirmed a small MNQ–QQQ information-transmission
effect in a single-use holdout. Neither result is presented as validated Alpha
or a deployable strategy.

This repository develops a reproducible empirical-research workflow for liquid
futures and ETFs. The first study examines opening-range behavior in Micro
E-mini Nasdaq-100 futures (MNQ). MNQ is the initial test case; the research
design is intended to extend to NQ, ES, QQQ, SPY, and related instruments.

The emphasis is on falsifiable hypotheses, reliable market-data construction,
leakage-resistant validation, statistical uncertainty, and clear reporting of
negative or inconclusive evidence.

## Run without market data

Exercise the full forecasting path with deterministic synthetic data. This
validates software behavior only and does not reproduce or imply market results:

```bash
python -m src.synthetic_demo
```

## Study 01 — Opening Range Behavior in Nasdaq-100 Futures

**Question.** Are prespecified opening-range characteristics associated with
the direction or magnitude of the remainder of the same trading session?

**Primary unit of analysis.** One regular trading session.

**Research decision.** Phase I finds a positive but regime-sensitive descriptive
association that attenuates after controlling for lagged volatility. Phase II
then asks whether Opening Range features improve a pre-open volatility forecast.
They do not: the candidate has relative out-of-sample R² of -0.0401, worse QLIKE,
and improves only 3 of 12 walk-forward folds. The registered confirmation gate
is not passed, so the final holdout remains sealed. This is a completed negative
decision for the registered question, not validated alpha or a trading strategy.

The full hypotheses and limitations are in
[`research_questions.md`](research_questions.md). The methodology is in
[`reports/research_methodology.md`](reports/research_methodology.md), and the
current construction audit is in
[`reports/data_quality_report.md`](reports/data_quality_report.md). The
development-only model report is in
[`reports/development_analysis.md`](reports/development_analysis.md). The
Phase II forecasting protocol is in
[`reports/phase2_protocol.md`](reports/phase2_protocol.md). The
development-only feature audit is in
[`reports/phase2_data_quality.md`](reports/phase2_data_quality.md). The
development-period forecasting decision is documented in
[`reports/phase2_development_results.md`](reports/phase2_development_results.md). The
machine-readable draft specification is in
[`configs/opening_range.toml`](configs/opening_range.toml), and the Phase II
specification is in
[`configs/phase2_forecasting.toml`](configs/phase2_forecasting.toml).

## Research architecture

```text
Licensed raw bars (local only)
        |
        v
Schema, timestamp, OHLCV and interval audits
        |
        v
Session construction and prespecified opening-range features
        |
        v
Session-level analytical panel
        |
        v
Development sample -> expanding-window validation -> untouched holdout
        |
        v
Effect sizes, uncertainty, multiplicity control and development-only robustness
checks—including robust slopes, influence removal, nonlinear form, trailing
volatility regimes, and contract-roll sensitivity
        |
        v
Registered gate fails -> stop research question and keep holdout sealed
```

## Implemented research controls

| Research risk | Control implemented in this repository |
|---|---|
| Ambiguous timestamps | Timezone-aware parsing and explicit New York conversion |
| Invalid observations | OHLC invariants, volume checks, duplicate and interval audits |
| Look-ahead leakage | Opening features and post-opening outcomes use disjoint intervals |
| Random time-series splitting | Chronological and expanding-window validation utilities |
| Multiple comparisons | Holm family-wise p-value adjustment |
| Overstated conclusions | Minimum-sample gate and explicit in-progress status |
| Restricted vendor data | Raw and processed observations excluded from version control |
| Post-hoc model search | Frozen confirmation gate and formal stop decision |
| Irreproducible licensed sample | Deterministic synthetic end-to-end demonstration |

## Repository structure

```text
quant-research/
├── .github/workflows/          # Continuous test validation
├── configs/
│   ├── opening_range.toml       # Phase I machine-readable specification
│   ├── phase2_forecasting.toml  # Forecasting protocol and confirmation gate
│   └── cross_asset_lead_lag.toml # Frozen MNQ–QQQ specification
├── data/
│   ├── README.md               # Provenance, schema and limitations
│   ├── raw/                    # Licensed source data; never committed
│   └── processed/              # Reproducible derived data; never committed
├── notebooks/                  # Thin exploratory/reporting notebooks
├── src/
│   ├── data_loader.py          # Typed OHLC ingestion and validation
│   ├── databento_loader.py      # Vendor normalization and RTH selection
│   ├── data_quality.py         # Structural market-data audit
│   ├── opening_range.py        # Opening-range calculation
│   ├── study_dataset.py        # Session-level feature/outcome panel
│   ├── statistical_tests.py    # Inference and multiplicity controls
│   ├── robustness_analysis.py  # Guarded development-only sensitivities
│   ├── forecast_features.py    # Point-in-time features and leakage audit
│   ├── forecast_validation.py  # Expanding-window folds and holdout guard
│   ├── forecast_models.py      # Baselines, losses and paired inference
│   ├── synthetic_demo.py       # Data-free end-to-end software demonstration
│   ├── cross_asset.py          # Point-in-time MNQ–QQQ panel construction
│   ├── cross_asset_models.py   # Restricted and unrestricted baselines
│   ├── cross_asset_evaluation.py # Walk-forward comparison and inference
│   ├── cross_asset_holdout.py  # Single-use holdout enforcement
│   └── validation.py           # Leakage-resistant time-series splits
├── reports/
│   ├── executive_summary.md    # Recruiter-facing two-study summary
│   ├── cross_asset_protocol.md # Registered information-transmission design
│   ├── cross_asset_development_results.md # Development-only evidence
│   ├── cross_asset_final_results.md # Single-use holdout decision
│   └── research_methodology.md # Prespecified research standards
├── tests/                      # Deterministic synthetic-data tests
├── PORTFOLIO_ROADMAP.md
├── research_questions.md
├── pyproject.toml
└── requirements.txt
```

## Reproduce the test suite

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

Tests use synthetic fixtures only. No fabricated market observation is used as
an empirical result.

## Research principles

- Freeze primary definitions before inspecting the final holdout.
- Treat data construction as part of the statistical model.
- Report sample size, effect size, confidence interval, and failure periods.
- Prefer transparent baselines before complex machine-learning models.
- Distinguish statistical association from economic value after costs.
- Preserve negative and inconclusive findings.
- Do not describe a backtest as a production strategy.

## Study 02 — MNQ–QQQ Information Transmission

This independent study examines cross-asset information transmission between
Nasdaq futures and QQQ with synchronized timestamps, lead-lag controls, and a
separately protected evaluation sample.

The draft protocol is now versioned in
[`reports/cross_asset_protocol.md`](reports/cross_asset_protocol.md), with its
machine-readable specification in
[`configs/cross_asset_lead_lag.toml`](configs/cross_asset_lead_lag.toml).
The non-redistributive coverage audit is in
[`reports/cross_asset_data_quality.md`](reports/cross_asset_data_quality.md).
The leakage-safe development-panel audit is in
[`reports/cross_asset_development_panel.md`](reports/cross_asset_development_panel.md).
Development results are reported in
[`reports/cross_asset_development_results.md`](reports/cross_asset_development_results.md).
Lagged MNQ returns improve one-minute QQQ forecasts in the development sample,
but the improvement disappears when the one-minute lag is removed. This is
evidence of rapid information transmission, not validated Alpha or a trading
strategy. Licensed observations remain local. The final holdout was evaluated
exactly once and confirmed a smaller positive effect: 0.1888% incremental OOS
R² with paired-loss p = 0.0182 and session-level p = 0.0432.
The single-use holdout procedure is frozen in
[`reports/cross_asset_holdout_execution.md`](reports/cross_asset_holdout_execution.md),
and the final decision is reported in
[`reports/cross_asset_final_results.md`](reports/cross_asset_final_results.md).
The holdout is now permanently closed to retuning or repeat evaluation.

![MNQ–QQQ final holdout evidence](figures/cross_asset_holdout_summary.svg)

## Disclaimer

Research and educational use only. Nothing in this repository is investment
advice or evidence of guaranteed performance.
