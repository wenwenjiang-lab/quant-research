# Research Methodology

> **Status: Proposed methodology.** No empirical analysis or result is reported here.

## Research unit

The primary unit of analysis is a trading session. Intraday bars must be mapped to an explicit exchange calendar and time zone before features or outcomes are computed. Holiday and shortened sessions are flagged rather than silently pooled with regular sessions.

## Data-quality gates

An analytical session is eligible only after checks for:

- required OHLC fields and timezone-aware timestamps;
- duplicate, missing, or out-of-order bars;
- internally consistent high, low, open, and close prices;
- expected session coverage and bar frequency;
- contract identifier, roll date, and adjustment method;
- known exchange holidays and shortened sessions.

Exclusion counts and reasons will be reported. Rules will not be changed merely to improve a result.

## Exploratory and confirmatory separation

Exploratory analysis may be used to understand distributions, data quality, and plausible specifications. Confirmatory hypotheses, opening intervals, outcome horizons, filters, and statistical tests will then be frozen before the holdout sample is evaluated.

## Validation design

Random train/test splitting is inappropriate for this time-series study. The proposed design uses:

1. an initial chronological development period;
2. expanding-window or walk-forward validation for model and threshold choices;
3. one untouched final holdout period for the primary result.

All fitted transformations—including normalization, imputation, feature selection, and model tuning—must be learned using training data only.

## Statistical reporting

Each primary analysis will report:

- sample size and missing/excluded observations;
- effect estimate in interpretable units;
- confidence interval;
- prespecified hypothesis-test result;
- distributional and dependence diagnostics;
- multiplicity-adjusted results when applicable;
- sensitivity to plausible session, roll, and outlier treatments.

P-values will not be treated as measures of economic importance.

## Economic evaluation

A statistical relationship becomes a candidate signal only after chronological validation. Any later strategy evaluation must include commissions, bid-ask spread, slippage, turnover, contract liquidity, and an execution rule that uses only information available at decision time.

Performance metrics, if eventually reported, will include uncertainty and failure periods. A positive backtest will not be described as a deployable strategy without additional validation.

## Reproducibility

- Reusable logic belongs in `src/`, not only in notebooks.
- Unit tests use synthetic fixtures and deterministic expectations.
- Notebooks will call library functions rather than duplicate core logic.
- Generated data and figures remain reproducible from documented inputs.
- Negative and inconclusive findings remain part of the research record.
