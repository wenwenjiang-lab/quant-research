# Cross-Asset Final-Holdout Execution Plan

> **Status: frozen but not authorized.** This document defines the only
> permitted final-holdout evaluation. No observation beginning 2025-02-20 or
> later has been inspected by the model or summarized in a result.

## Preconditions

1. PR containing the development result and evaluation code is merged.
2. All automated tests pass on the exact frozen code revision.
3. The development gate and latency sensitivity are reported publicly.
4. A separate explicit decision authorizes the irreversible single evaluation.
5. `holdout_analysis_allowed` remains `false` until that decision.

## Frozen execution

- Primary direction: lagged MNQ returns forecasting one-minute QQQ returns.
- Restricted model: QQQ return lags 1–5 with an intercept.
- Unrestricted model: the restricted features plus MNQ return lags 1–5.
- Estimator: ordinary least squares without tuning or regularization.
- Training sample: eligible development sessions before 2025-02-20, excluding
  the final development session as a one-session embargo.
- Evaluation sample: exactly 358 eligible sessions beginning 2025-02-20.
- Primary loss: squared error.
- Primary statistics: incremental OOS R² and five-lag HAC paired-loss test.
- Sensitivity: session-mean loss differential with five-session HAC correction.

The implementation requires both a configuration authorization and the exact
single-use execution phrase. It rejects a changed holdout session count,
overlapping feature sets, invalid timestamps, or accidental default execution.

## Decision rule

The final result confirms the development finding only if incremental OOS R²
is positive and the registered paired-loss p-value is below 0.05. Regardless
of outcome, no model or threshold may be changed after opening the holdout.

## Interpretation boundary

Confirmation would support statistical one-minute information transmission,
not executable Alpha. The development latency analysis already shows that the
incremental improvement disappears when the one-minute MNQ lag is removed.
