# Quantitative Research Portfolio

> **Status: In progress.** This repository contains active research. No results or conclusions should be inferred from the current materials.

This repository documents my independent quantitative research into intraday behavior of Nasdaq-100 futures (MNQ). Its objective is to investigate whether statistically significant market behaviors exist through hypothesis-driven research rather than discretionary trading.

The repository is intended as a long-term public research portfolio spanning systematic trading, market microstructure, and statistical analysis. The emphasis is on clearly stated hypotheses, transparent methods, tested analytical code, and careful discussion of limitations—not trading signals or performance claims.

## Current research project

### Statistical Analysis of Opening Range Behavior in Nasdaq-100 Futures (MNQ)

This project investigates whether features of the MNQ opening range are associated with subsequent intraday price behavior. The research design is documented in [research_questions.md](research_questions.md). Data acquisition, exploratory analysis, statistical testing, and robustness checks remain in progress.

## Research topics

Current research focuses on opening ranges, VWAP interaction, momentum continuation, volatility expansion, session statistics, and market microstructure. Potential future work includes alpha research, feature engineering, machine learning, portfolio construction, and market-regime detection.

## Research workflow

Each project follows a scientific workflow: define a hypothesis, collect appropriately licensed historical data, clean and validate it, perform statistical analysis, evaluate statistical and economic significance, document findings, and draw appropriately limited conclusions.

## Technology stack

Python, pandas, NumPy, SciPy, pytest, and Jupyter notebooks form the initial research stack. Visualization and reporting tools will be added as the analysis develops.

## Repository structure

```text
quant-research/
├── data/
│   ├── raw/                 # Original source data (not committed)
│   └── processed/           # Cleaned analytical datasets (not committed)
├── notebooks/               # Exploratory and reproducible analyses
├── src/
│   ├── data_loader.py       # Market-data loading and validation
│   └── opening_range.py     # Opening-range calculations
├── figures/                 # Generated charts and visualizations
├── reports/                 # Research write-ups
├── tests/
│   └── test_opening_range.py
├── research_questions.md    # Questions, hypotheses, and study design
├── requirements.txt
└── README.md
```

Empty directories include placeholder files so that the structure remains visible in version control. Market data should not be committed unless its license explicitly permits redistribution.

## Setup and tests

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest
```

## Research principles

- Separate exploratory work from confirmatory testing.
- Document time zones, session definitions, contract rolls, and preprocessing.
- Use out-of-sample validation where appropriate.
- Report uncertainty, robustness checks, and negative results.
- Avoid look-ahead bias, survivorship bias, and overstated conclusions.

## Disclaimer

This repository is for research and educational purposes only. It is not investment advice, and it does not represent a completed trading strategy.
