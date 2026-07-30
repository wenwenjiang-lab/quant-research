# Quantitative Market Research Portfolio

> **Status: Active research portfolio — work in progress.** No trading result, alpha claim, or performance conclusion should be inferred from unfinished studies.

This repository applies a scientific research workflow to systematic market behavior across liquid futures and ETFs. The current study uses Micro E-mini Nasdaq-100 futures (MNQ) as the first test case; the methods are designed to extend to NQ, ES, SPY, QQQ, and other liquid instruments.

The portfolio is aimed at early-career opportunities in quantitative research, quantitative trading, and markets analytics. It emphasizes reproducible evidence rather than discretionary trade ideas or unsupported performance claims.

## Recruiter snapshot

| Capability | Evidence in this repository |
|---|---|
| Hypothesis-driven research | Prespecified questions, null/alternative hypotheses, variables, tests, and limitations |
| Python research engineering | Validated data loading, reusable feature calculations, typed functions, and unit tests |
| Statistical reasoning | Effect estimates, confidence intervals, hypothesis tests, and multiple-testing control |
| Time-series validation | Chronological and expanding-window splits that prevent look-ahead leakage |
| Market understanding | Opening range, volatility, transaction costs, session definitions, and contract-roll risks |
| Communication | Research design, methodology, assumptions, status labels, and explicit limitations |

## Current research program

### Study 01 — Opening Range Behavior in Nasdaq-100 Futures

**Instrument:** CME Micro E-mini Nasdaq-100 futures (MNQ)  
**Theme:** Intraday futures behavior and candidate signal validation  
**Status:** 🚧 Research in progress

The study asks whether prespecified opening-range characteristics are associated with the direction or magnitude of subsequent same-session price behavior. The design is documented in [research_questions.md](research_questions.md), and the validation standards are documented in [reports/research_methodology.md](reports/research_methodology.md).

No market data, empirical result, backtest, or claim of alpha has been added yet.

## Research pipeline

```text
Question and economic rationale
        ↓
Prespecified signal and outcome
        ↓
Data validation and session construction
        ↓
Descriptive statistics and effect sizes
        ↓
Chronological / walk-forward validation
        ↓
Costs, robustness, and multiple-testing controls
        ↓
Candidate signal — only if evidence survives
```

## Research roadmap

| Stage | Study | Status |
|---|---|---|
| 1 | MNQ opening-range behavior | In progress |
| 2 | Regime and parameter robustness | Planned |
| 3 | MNQ/NQ/QQQ cross-instrument comparison | Planned |
| 4 | ES/SPY external validation | Planned |
| 5 | Multi-signal and portfolio analysis | Planned |
| 6 | Machine learning versus statistical baselines | Planned |

See [PORTFOLIO_ROADMAP.md](PORTFOLIO_ROADMAP.md) for milestones and completion criteria.

## Repository structure

```text
quant-research/
├── .github/workflows/       # Automated test checks
├── data/
│   ├── raw/                 # Original licensed data (not committed)
│   └── processed/           # Derived analytical data (not committed)
├── notebooks/               # Reproducible analyses (planned)
├── src/
│   ├── data_loader.py       # OHLC loading and validation
│   ├── opening_range.py     # Opening-range feature calculations
│   ├── statistical_tests.py # Inference and multiplicity controls
│   └── validation.py        # Leakage-resistant time-series splits
├── figures/                 # Generated figures (not committed)
├── reports/                 # Methods and research reports
├── tests/                   # Synthetic-data unit tests
├── PORTFOLIO_ROADMAP.md
├── research_questions.md
├── pyproject.toml
└── requirements.txt
```

## Local setup

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest
```

Tests use synthetic fixtures only. The repository contains no fabricated market observations.

## Research standards

- Separate exploratory analysis from confirmatory testing.
- Define timestamps, time zones, sessions, and contract rolls explicitly.
- Preserve chronological order and isolate holdout periods.
- Report effect sizes and confidence intervals alongside p-values.
- Control multiple testing across intervals, thresholds, and outcomes.
- Include fees, spread, slippage, and realistic execution assumptions before discussing economic value.
- Document negative and inconclusive results.

## Disclaimer

This repository is for research and educational purposes only. It is not investment advice and does not represent a completed or deployable trading strategy.
