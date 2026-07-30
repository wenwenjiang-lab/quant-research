# Cross-Asset Development Panel Audit

> **Status: development data frozen; no model results.** This report documents
> data construction only. It contains no licensed observations, forecasts,
> performance statistics, holdout results, or Alpha claim.

## Purpose

This audit verifies that the development panel for study
`nq-qqq-lead-lag-001` follows the frozen point-in-time protocol before any
forecast model is fitted. The panel synchronizes one-minute MNQ and QQQ returns
on exact timestamps during the 09:30--16:00 America/New_York session.

## Frozen sample boundary

| Field | Value |
|---|---:|
| Development sessions | 1,429 |
| Development rows | 548,736 |
| First session | 2019-05-06 |
| Last development session | 2025-02-19 |
| Final holdout start | 2025-02-20 |
| Rows at or after holdout start | 0 |
| Maximum registered lag | 5 minutes |

Only common sessions with all 390 regular-session one-minute bars for both
instruments are eligible. The protected final holdout is excluded before
returns or lagged predictors are calculated.

## Point-in-time controls

- Returns require observations exactly one minute apart within the same
  trading session.
- Futures returns cannot cross an instrument/contract change.
- Missing minutes are not bridged, forward-filled, or interpolated.
- Cross-asset predictors use only registered lags of 1 through 5 minutes.
- Same-timestamp cross-asset predictors are forbidden.
- Duplicate synchronized timestamps: 0.
- Missing values in the final development panel: 0.

These controls are enforced in `src/cross_asset.py` and covered by synthetic
unit tests, including missing-minute, overnight-boundary, contract-change, and
timezone-aware holdout-boundary cases.

## Interpretation

This artifact establishes a reproducible and leakage-resistant development
sample. It does **not** establish predictability, economic value, a trading
strategy, or validated Alpha. Model specification and expanding-window
evaluation remain subsequent development-only stages. The final holdout stays
sealed until all confirmation code and decision rules are frozen.
