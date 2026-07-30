# Quantitative Market Research

[![Tests](https://github.com/wenwenjiang-lab/quant-research/actions/workflows/tests.yml/badge.svg)](https://github.com/wenwenjiang-lab/quant-research/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Status: active research — work in progress.** This repository does not
> claim a completed study, validated alpha, or deployable trading strategy.

This repository develops a reproducible empirical-research workflow for liquid
futures and ETFs. The first study examines opening-range behavior in Micro
E-mini Nasdaq-100 futures (MNQ). MNQ is the initial test case; the research
design is intended to extend to NQ, ES, QQQ, SPY, and related instruments.

The emphasis is on falsifiable hypotheses, reliable market-data construction,
leakage-resistant validation, statistical uncertainty, and clear reporting of
negative or inconclusive evidence.

## Study 01 — Opening Range Behavior in Nasdaq-100 Futures

**Question.** Are prespecified opening-range characteristics associated with
the direction or magnitude of the remainder of the same trading session?

**Primary unit of analysis.** One regular trading session.

**Current state.** The protocol, data contract, quality gates, feature pipeline,
statistical utilities, and chronological validation tools are implemented. A
licensed local Databento sample covering May 2019 through July 2026 is undergoing
session, calendar, and continuous-contract audits. Development-only estimates
show a positive but regime-sensitive magnitude association that attenuates after
controlling for lagged volatility. Influence diagnostics remain unresolved; the
final holdout has not been accessed and no confirmatory inference is reported.

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
[`configs/opening_range.toml`](configs/opening_range.toml).

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
Candidate signal only if statistical and economic evidence survives
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

## Repository structure

```text
quant-research/
├── .github/workflows/          # Continuous test validation
├── configs/
│   └── opening_range.toml      # Draft machine-readable study specification
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
│   └── validation.py           # Leakage-resistant time-series splits
├── reports/
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

## Roadmap

1. Complete exchange-calendar, missing-bar, and contract-roll audits.
2. Expand the sample to satisfy the protocol's minimum-session requirement.
3. Freeze the confirmatory specification and final holdout boundary.
4. Produce descriptive statistics without tuning on the holdout.
5. Run prespecified inference and robustness checks.
6. Evaluate execution costs only if a relationship survives validation.
7. Test external validity in NQ/QQQ and then ES/SPY.

## Disclaimer

Research and educational use only. Nothing in this repository is investment
advice or evidence of guaranteed performance.
