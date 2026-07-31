# Research Questions and Study Design

> **Design status: archived preregistration. Study status: complete.** This
> document preserves the questions and hypotheses defined before analysis.
> Phase I reported a descriptive association; the registered Phase II
> forecasting gate later failed in development, so its final holdout remains
> sealed. See the [`research decision`](reports/research_decision.md) and
> [`portfolio summary`](reports/executive_summary.md).

## Main research question

For Micro E-mini Nasdaq-100 futures (MNQ), are prespecified opening-range
characteristics associated with the direction or magnitude of price movement
during the remainder of the same regular trading session?

The clock interval, market time zone, eligible sessions, contract construction,
outcome horizon, and exclusion rules must be frozen before confirmatory testing.

## Hypotheses

**Null hypothesis (H0).** After applying the prespecified sampling and control
rules, opening-range characteristics have no statistically detectable
association with subsequent same-session returns or range expansion.

**Alternative hypothesis (H1).** After applying the prespecified sampling and
control rules, at least one registered opening-range characteristic has a
statistically detectable association with subsequent same-session returns or
range expansion.

### Prespecified primary estimand

The primary predictor is opening-range width divided by the opening-range
midpoint and expressed in basis points. The primary outcome is the absolute
return from the first 10:00 bar open to the final eligible regular-session close,
also expressed in basis points. The primary estimand is the slope on normalized
opening-range width in a linear model with an intercept.

**Primary H0:** the population slope is zero. **Primary H1:** the population
slope is nonzero. The test is two-sided at 5%, with Newey-West HAC uncertainty
using five session lags and a moving-block-bootstrap sensitivity analysis. This
tests a market-behavior association; it is not itself a trading rule.

Directional boundary-break hypotheses are secondary and must preserve the
timestamp at which the break becomes observable. They may not replace the
primary test after results are inspected.

## Variables

### Explanatory variables

- Opening-range high, low, midpoint, and width in index points.
- Opening-range width normalized by price and lagged volatility.
- Direction and timestamp of the first post-range boundary break.
- Indicator that both boundaries are crossed after the opening interval.
- Prespecified controls: prior-session return, overnight return, day of week,
  lagged volatility, and contract-roll proximity when reliable metadata exists.

### Outcome variables

- Return from the first post-opening bar to the regular-session close.
- Maximum post-opening upward and downward excursion.
- Post-opening realized range or volatility.
- Indicator that a prespecified range-extension threshold is reached.

### Data and grouping variables

- Timezone-aware timestamp and trading-session date.
- OHLCV observations.
- Contract identifier, expiry, roll date, and adjustment metadata.
- Holiday, shortened-session, and data-quality flags.

## Proposed statistical tests

- Descriptive distributions and confidence intervals before inference.
- One-sample mean test paired with a dependence-aware or bootstrap sensitivity
  analysis when conventional assumptions are doubtful.
- Welch's t-test or Mann-Whitney U test for registered independent comparisons.
- Fisher's exact or chi-square test for categorical outcomes.
- Linear or logistic regression with robust/session-aware uncertainty estimates.
- Holm family-wise-error correction for the registered hypothesis family.
- Expanding-window validation and one untouched chronological holdout for any
  predictive specification.

Every result must include the sample size, effect size, confidence interval,
diagnostics, and sensitivity analysis. Statistical significance alone is not
evidence of an economically tradable effect.

## Biases and limitations

- **Look-ahead bias:** predictors and break events must use only information
  available at their stated decision time.
- **Data snooping:** repeated intervals, thresholds, filters, and outcomes can
  create false discoveries.
- **Selection and publication bias:** favorable specifications may not be
  reported without the corresponding failures.
- **Serial dependence:** adjacent sessions and intraday observations may be
  autocorrelated and volatility-clustered.
- **Regime dependence:** effects may change with macroeconomic, volatility, and
  market-structure regimes.
- **Futures construction:** rolls, back adjustments, gaps, and liquidity shifts
  can alter a continuous series.
- **Session-definition risk:** daylight saving, holidays, and shortened sessions
  can cause classification errors.
- **Vendor-data risk:** missing bars, timestamp conventions, outliers, and data
  revisions can affect results.
- **Execution gap:** association does not establish value after fees, spread,
  slippage, latency, and market impact.
- **External validity:** MNQ findings may not generalize to NQ, QQQ, ES, SPY,
  other frequencies, or future periods.
- **Effective-sample risk:** exclusions, serial dependence, regime concentration,
  and the untouched holdout reduce the effective information below the raw
  session count.
