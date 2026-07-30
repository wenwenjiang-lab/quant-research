# Phase II Forecasting Protocol

> **Status: preregistered development work only.** The final holdout beginning
> 2024-05-24 remains sealed. No result may be described as validated alpha.

## Research question

Does the 09:30–10:00 New York opening range improve out-of-sample forecasts of
10:00–16:00 intraday volatility beyond pre-open and historical information?

## Primary comparison

The baseline contains lagged volatility and information available before 09:30.
The candidate adds prespecified opening-range features available by 10:00. Both
use identical sessions, expanding-window folds, losses, and training-only preprocessing.

## Validation and leakage controls

- Minimum training window: 504 sessions; test blocks: 63 sessions.
- One-session embargo; no shuffle, ordinary K-fold, or future preprocessing.
- Primary loss: QLIKE; secondary losses: MAE and RMSE.
- Report out-of-sample R² and a HAC-aware Diebold–Mariano comparison.
- Machine-learning models are exploratory and cannot determine confirmation.

## Confirmation gate

Holdout access requires frozen code and protocol, positive development-period
out-of-sample R², lower QLIKE than the baseline, paired-loss p-value below 0.05,
improvement in more than 60% of blocks, and no unexplained regime reversal.
Failure of any gate is a valid negative research conclusion.

## Interpretation boundary

This phase forecasts volatility magnitude, not direction. Any position sizing,
execution, costs, slippage, or return analysis must be registered separately.
