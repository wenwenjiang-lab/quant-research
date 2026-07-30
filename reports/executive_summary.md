# Executive Summary

## Question

Does the 09:30–10:00 New York opening range provide incremental out-of-sample
information for forecasting MNQ price variation from 10:00 to 16:00 beyond
lagged volatility and pre-open information?

## Design and evidence

The study validates 2,549,259 licensed one-minute observations and constructs
1,255 development sessions from 2019-05-07 through 2024-05-23. Predictors are
timestamp-audited at 10:00. Evaluation uses expanding windows, 63-session test
blocks, a one-session embargo, QLIKE, and HAC-aware paired inference.

| Metric | Baseline | Baseline + Opening Range |
|---|---:|---:|
| RMSE | 65.0295 | 66.3212 |
| QLIKE | 0.07563 | 0.07927 |
| Relative OOS R² | — | -0.0401 |

Only 3 of 12 folds improve. Candidate-minus-baseline QLIKE is 0.00364
(Newey-West SE 0.00212; two-sided p = 0.086), where positive favors baseline.

## Decision

The confirmation gate is not passed. The final holdout beginning 2024-05-24
remains sealed, and no alpha or trading-strategy claim is made. The contribution
is the auditable workflow: data governance, point-in-time features, leakage
guards, dependence-robust inference, walk-forward comparison, and acceptance
of a negative result.

![Out-of-sample model comparison](../figures/model_comparison.svg)

![Walk-forward QLIKE improvement](../figures/walk_forward_qlike.svg)

Any nonlinear model, alternative target, or opening window is a new Phase III
question requiring a new study identifier and validation plan.
