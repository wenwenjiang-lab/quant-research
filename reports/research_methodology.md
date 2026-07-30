# Research Methodology

> **Status: proposed methodology.** No empirical finding is reported here.

## Research unit and estimand

The primary observational unit is a trading session. The primary estimand is
the mean post-opening return associated with the prespecified opening-range
definition. Intraday bars are mapped to an explicit market clock before any
feature or outcome is calculated.

## Data-quality gates

A session is eligible only after checks for:

- required OHLC fields and timezone-aware timestamps;
- duplicate, missing, or out-of-order bars;
- internally consistent and positive prices;
- expected bar frequency and complete opening-range coverage;
- contract identifier, expiry, roll date, and adjustment method;
- exchange holidays and shortened sessions.

Missing trade-derived minute aggregates are not automatically classified as
vendor errors. They may represent zero-trade minutes, exchange halts, shortened
sessions, or missing coverage. The audit records the interval and requires an
explicit classification rule; it does not silently forward-fill prices.

Exclusion counts and reasons must be reported. Exclusion rules may not be
changed merely to improve a result.

## Exploratory and confirmatory separation

Exploratory work may characterize distributions, data quality, and plausible
model specifications. Before the final holdout is accessed, the following are
frozen in the machine-readable study configuration:

- opening interval and eligible session;
- primary feature and outcome;
- inclusion and exclusion rules;
- model, test statistic, and significance level;
- hypothesis family and multiplicity correction;
- development and holdout boundaries.

Exploratory findings are labelled as such and are not presented as confirmatory
evidence.

## Validation design

Random train/test splitting is inappropriate. The proposed design uses:

1. a chronological development sample;
2. expanding-window validation for model and threshold choices;
3. one untouched final holdout for the primary result.

The provisional 70/30 session-count boundary is 2024-05-23/2024-05-24. It was
computed from eligible session dates without evaluating outcome values. The
holdout remains unavailable for inference until the protocol is frozen.

All fitted transformations—including normalization, imputation, feature
selection, and model tuning—are learned from training data only. Overlapping
labels or horizons require purging or embargo where applicable.

## Statistical reporting

Every primary analysis reports:

- eligible and excluded session counts;
- effect estimate in interpretable units;
- uncertainty interval and prespecified test result;
- distributional and serial-dependence diagnostics;
- multiplicity-adjusted inference when applicable;
- sensitivity to plausible session, roll, and outlier treatments.

P-values are not treated as measures of economic importance. Model residuals
and session-level dependence determine whether conventional, robust, clustered,
or bootstrap inference is appropriate.

## Economic evaluation

A statistical relationship becomes a candidate signal only after chronological
validation. Any later strategy evaluation must specify decision timing and
include commissions, bid-ask spread, slippage, turnover, contract liquidity,
and conservative fill assumptions.

Performance reporting, if eventually warranted, includes uncertainty, drawdown,
tail behavior, turnover, capacity limitations, and failure periods. A positive
backtest is not described as a deployable strategy.

## Reproducibility

- Core logic resides in tested modules rather than only in notebooks.
- Unit tests use deterministic synthetic fixtures.
- Raw licensed data remains outside version control.
- Processed datasets are generated from documented inputs and frozen settings.
- Random procedures use explicit seeds.
- Negative and inconclusive findings remain in the research record.
