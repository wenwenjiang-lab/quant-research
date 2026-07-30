# Cross-Asset Final-Holdout Results

> **Status: registered statistical finding confirmed; study complete.** The
> final holdout was evaluated exactly once after explicit authorization. This
> confirms a narrow forecasting relationship, not executable Alpha or a
> deployable trading strategy.

## Frozen evaluation

The holdout contains 137,472 synchronized one-minute observations across all
358 eligible sessions from 2025-02-20 through 2026-07-29. The restricted model
uses QQQ return lags 1–5. The unrestricted model adds MNQ return lags 1–5. Both
models were fit once on the frozen development sample, excluding the final
development session as an embargo.

## Primary result

| Metric | Final holdout |
|---|---:|
| Incremental OOS R² | 0.1888% |
| HAC paired-loss statistic | 2.362 |
| HAC paired-loss p-value | 0.0182 |
| Session-aggregated statistic | 2.022 |
| Session-aggregated p-value | 0.0432 |
| Restricted directional accuracy | 48.64% |
| Unrestricted directional accuracy | 50.27% |

![MNQ–QQQ final holdout evidence](../figures/cross_asset_holdout_summary.svg)

The unrestricted model has lower squared forecast loss under both registered
minute-level and session-aggregated inference. The frozen confirmation rule—
positive incremental OOS R² and paired-loss p-value below 0.05—is satisfied.

## Interpretation

The final holdout supports the registered claim that lagged MNQ returns contain
incremental one-minute information for QQQ returns beyond QQQ's own lags. The
effect is smaller than in development (0.1888% versus 0.5029% incremental OOS
R²), which is consistent with realistic out-of-sample attenuation.

This result must not be described as validated Alpha. Development sensitivity
tests show that the improvement disappears when the one-minute MNQ lag is
removed. No spread, fee, latency, queue-position, fill, market-impact, or
capacity model has been evaluated. Directional accuracy is only 50.27%.

## Research decision

The statistical information-transmission question is complete and confirmed.
The holdout is permanently closed to further model selection, threshold
changes, or alternative specifications. Any economic-value or execution study
must receive a new study ID, new hypotheses, and a new untouched evaluation
sample.

## Reproducibility boundary

The registered code, aggregate statistics, and decision are public. Licensed
bars, row-level forecasts, and loss observations remain local and are excluded
from version control.
