# Cross-Asset Information-Transmission Protocol

> **Status: protocol draft; no empirical result.** This study has a new study
> ID and does not reopen or retune the completed MNQ Opening Range question.

## Research question

Does lagged MNQ information improve one-minute QQQ return forecasts beyond
QQQ's own lagged returns? The reverse direction is analyzed symmetrically so
that a preferred causal story is not selected after observing results.

The primary estimand is the difference in chronological out-of-sample squared
forecast loss between a restricted own-lag model and an unrestricted model
that adds prespecified cross-asset lags. Five- and fifteen-minute horizons are
secondary and cannot replace a failed primary result.

## Economic motivation

MNQ/NQ and QQQ reference closely related Nasdaq-100 exposure but trade through
different instruments and market structures. Price discovery may therefore be
distributed across venues. A measurable lead-lag relationship is plausible,
but shared news, timestamp conventions, stale quotes, bid-ask bounce, and
non-synchronous trading can create the same appearance without predictive
information.

## Point-in-time controls

- All timestamps must be converted to `America/New_York` and interpreted as
  interval starts before joining assets.
- A return for interval *t* is available only after that interval closes.
- Same-timestamp cross-asset predictors are forbidden in the primary model.
- Missing prices are never forward-filled and missing returns are never
  interpolated.
- Only complete overlapping regular-session intervals enter the primary panel.
- QQQ corporate actions and the futures roll rule must be documented before
  the feature panel is frozen.

## Validation

Models use expanding training windows, 21-session test blocks, and a
one-session embargo. The newest 20% of eligible sessions is reserved as a
single sealed holdout. Scaling, imputation, and any exploratory tuning must be
fit inside each training window.

The primary comparison reports incremental out-of-sample R-squared and a
HAC-aware paired loss test. The result must also be stable across more than 60%
of test blocks. Holm adjustment applies to the registered directional and
horizon family.

## Falsification and sensitivity analysis

- Reverse the forecasting direction (QQQ to MNQ).
- Shift one feed by plus or minus one minute to expose timestamp artifacts.
- Exclude the first and last five minutes of the regular session.
- Evaluate session-clustered uncertainty and high-volatility subperiods.
- Replicate the futures side with NQ if licensed data are available.

## Interpretation boundary

A lead-lag estimate is not automatically market causality, executable alpha,
or a trading strategy. Transaction costs, spread crossing, realistic latency,
fill uncertainty, and capacity require a separate preregistered study. Failure
of the confirmation gate is a complete and reportable research outcome.
