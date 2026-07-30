# Development-Sample Analysis

> **Status: exploratory development evidence only.** The final holdout begins
> on 2024-05-24 and was not accessed for this analysis. This document does not
> report a confirmatory result, a trading strategy, or validated alpha.

## Prespecified model

The development model asks whether normalized opening-range width is associated
with the magnitude of the remainder-of-session price move:

```text
post_opening_abs_return_bps
    = intercept + beta * opening_range_width_bps + error
```

The predictor is the 09:30–10:00 New York opening-range width divided by its
midpoint and expressed in basis points. The outcome is the absolute return from
the first 10:00 bar open to the final eligible regular-session close, also in
basis points. The model uses 1,256 development sessions through 2024-05-23.

## Development result

| Quantity | Estimate |
|---|---:|
| Slope (`beta`) | 0.7975 |
| Newey-West HAC standard error, 5 lags | 0.1031 |
| HAC 95% confidence interval | [0.5954, 0.9996] |
| Two-sided asymptotic p-value | 1.05 × 10^-14 |
| R² | 0.1779 |
| Moving-block-bootstrap standard error | 0.1013 |
| Bootstrap 95% percentile interval | [0.5995, 0.9894] |

Within the development period, a one-basis-point wider opening range is
associated with approximately 0.80 basis points more absolute price displacement
from 10:00 to the session close. The five-session moving-block bootstrap gives a
similar uncertainty interval to the HAC calculation.

## Lagged-volatility robustness model

To test whether the baseline relationship merely reflects persistent market
volatility, a robustness model adds the mean full-session range from the five
strictly preceding observed sessions. The control cannot contain current-session
information.

| Quantity | Estimate |
|---|---:|
| Complete-case sessions | 1,251 |
| Opening-range slope after control | 0.4817 |
| HAC standard error | 0.1406 |
| HAC 95% confidence interval | [0.2061, 0.7573] |
| Two-sided asymptotic p-value | 0.000614 |
| Lagged-volatility slope | 0.2355 |
| R² | 0.2117 |

The focal slope remains positive but is approximately 40% smaller than the
baseline estimate. This attenuation indicates that volatility persistence
explains a material part of the original association. The remaining coefficient
is development evidence of incremental association, not proof of causality or
out-of-sample predictive value.

## Residual and influence diagnostics

| Diagnostic | Observed value |
|---|---:|
| Durbin-Watson | 2.1113 |
| Lag-1 residual autocorrelation | -0.0557 |
| Cook's-distance threshold (`4/n`) | 0.00318 |
| Sessions above threshold | 77 |
| Maximum Cook's distance | 0.7043 |

The first-order residual-dependence diagnostics are modest, but the influence
diagnostic is a serious limitation. A small number of sessions may materially
affect the linear slope, so robust-estimator and influence sensitivity checks are
required before the protocol can be frozen.

## Descriptive yearly stability

The following estimates are descriptive diagnostics, not a family of separate
confirmatory tests.

| Year | Sessions | Slope | HAC 95% interval |
|---:|---:|---:|---:|
| 2019 | 162 | 0.2535 | [-0.0620, 0.5689] |
| 2020 | 245 | 0.9938 | [0.6049, 1.3827] |
| 2021 | 251 | 0.6162 | [0.3338, 0.8985] |
| 2022 | 250 | 0.2719 | [-0.1575, 0.7012] |
| 2023 | 248 | 0.4005 | [0.1296, 0.6714] |
| 2024 development period | 100 | -0.0664 | [-0.4552, 0.3224] |

The magnitude and uncertainty vary substantially by year, and the partial 2024
development estimate is negative. This weakens any claim that one stable linear
relationship characterizes all regimes. The final holdout remains sealed.

## What this does not show

- The outcome is magnitude, not direction; the model does not say whether price
  will rise or fall.
- Association does not establish causality or an executable decision rule.
- The relationship may largely reflect persistent intraday volatility rather
  than a distinct source of economic edge.
- R² is not strategy performance, and the analysis includes no return series,
  Sharpe ratio, turnover, costs, spread, slippage, or market impact.
- The model form, regime stability, influential observations, and roll/calendar
  sensitivities remain material limitations despite the diagnostics above.
- The final holdout has not been evaluated, so this is not confirmatory evidence.

## Next validation gates

1. Run robust-estimator, influence-removal, and nonlinear-form sensitivities on
   the development period, reporting all prespecified variants.
2. Run registered calendar, roll-boundary, and volatility-regime sensitivities.
3. Decide whether the model is sufficiently stable to justify confirmation; a
   negative decision is an acceptable research result.
4. Freeze the protocol and code version before permitting holdout access.
5. Evaluate the primary model exactly once on the final holdout only if the
   development diagnostics justify doing so.
6. Treat any later directional or economic strategy analysis as a separate,
   explicitly timed research question.
