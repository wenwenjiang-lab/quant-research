# Research Questions and Study Design

> **Status: In progress.** This document is a proposed design, not a report of completed analysis or findings.

## Main research question

For Micro E-mini Nasdaq-100 (MNQ) futures, is opening-range behavior associated with the direction or magnitude of price movement during the remainder of the same trading session?

The opening range must be defined before confirmatory analysis, including its clock interval, exchange time zone, eligible session, and treatment of shortened trading days. Candidate intervals may be compared during exploratory analysis, but a final interval should be fixed before hypothesis testing.

## Hypotheses

**Null hypothesis (H0):** After accounting for the prespecified controls, opening-range characteristics have no statistically detectable association with subsequent same-session returns or range expansion in MNQ futures.

**Alternative hypothesis (H1):** After accounting for the prespecified controls, at least one opening-range characteristic has a statistically detectable association with subsequent same-session returns or range expansion in MNQ futures.

Directional sub-hypotheses—for example, whether an upside opening-range break predicts a positive subsequent return—should be registered before confirmatory testing. Two-sided tests are the default otherwise.

## Variables

### Explanatory variables

- Opening-range high, low, midpoint, and width in points.
- Opening-range width normalized by price and, if available, a lagged volatility measure.
- Direction and timing of the first post-range break, defined without future information.
- Whether both range boundaries are crossed after the opening interval.
- Optional prespecified controls: prior-session return, overnight return, day of week, contract-roll proximity, and lagged volatility.

### Outcome variables

- Return from the end of the opening interval to the session close.
- Maximum favorable and adverse excursion after the opening interval.
- Post-opening realized range or volatility.
- Indicator for whether a prespecified range-extension threshold is reached.

### Data and grouping variables

- Timestamp with an explicit exchange time zone.
- Trading-session date.
- OHLC prices and, when licensed and available, volume.
- Contract identifier and continuous-contract adjustment metadata.
- Session type, holiday/shortened-session flag, and data-quality flags.

## Proposed statistical tests

- Descriptive statistics and confidence intervals, reported before inferential results.
- One-sample t-test for mean post-opening returns when assumptions are defensible, paired with a Wilcoxon signed-rank or bootstrap alternative.
- Welch's t-test or Mann-Whitney U test for prespecified independent group comparisons.
- Chi-square or Fisher's exact test for categorical outcomes such as break direction versus close direction.
- OLS or robust regression for continuous outcomes and logistic regression for binary outcomes, using heteroskedasticity/autocorrelation-consistent or session-aware inference where appropriate.
- Multiple-testing control, such as Holm correction or false-discovery-rate control, when testing multiple intervals, thresholds, or outcomes.
- Walk-forward or chronological out-of-sample evaluation for any predictive specification.

Effect sizes, confidence intervals, sample sizes, diagnostics, and sensitivity analyses should accompany p-values. Test selection will be finalized after inspecting distributional and dependence properties without using the holdout period to tune hypotheses.

## Possible biases and limitations

- **Look-ahead bias:** session labels, break events, and predictors must use only information available at each observation time.
- **Data snooping and multiple testing:** trying many opening intervals, thresholds, filters, or outcomes can produce spurious significance.
- **Selection and publication bias:** emphasizing only favorable specifications would misrepresent the evidence.
- **Non-independence:** intraday observations and adjacent sessions may be serially correlated or volatility-clustered.
- **Regime dependence:** relationships may vary across volatility, monetary-policy, macroeconomic, and market-structure regimes.
- **Contract construction:** rolls, back adjustments, price gaps, and liquidity changes can affect a continuous futures series.
- **Session-definition risk:** daylight-saving changes, holidays, shortened sessions, and exchange calendar changes can cause misclassification.
- **Data quality:** missing bars, duplicate timestamps, outliers, differing vendor conventions, and timestamp errors can alter computed ranges.
- **Execution gap:** statistical association does not establish a tradable edge after spread, slippage, fees, latency, and market impact.
- **External validity:** MNQ results may not generalize to NQ, other instruments, other bar frequencies, or future periods.
- **Economic versus statistical significance:** a statistically detectable effect may be too small or unstable to matter economically.
