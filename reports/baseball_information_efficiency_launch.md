# Study 05 — The Baseball Information Efficiency Project

## A live, pre-registered forecasting experiment featuring the 2026 New York Mets

**Public launch:** 2026-08-03  
**Status:** prospective collection begins with the next eligible game day  
**Coverage:** all MLB regular-season games; the New York Mets are the public-facing case study

> Can a transparent model built only from information available before first pitch produce well-calibrated MLB win probabilities—and, later, add information beyond simple baselines?

This page launches a prospective research record. It does **not** report a profitable strategy, validated Alpha, or an ability to beat betting markets. Forecasts will be timestamped before eligible games, preserved rather than selectively deleted, and evaluated only after the preregistered sample gates are reached.

## Why this study exists

Sports forecasting has the same core problems as quantitative finance: noisy outcomes, non-stationarity, model selection risk, data revisions, and strong incentives to tell a compelling story after the fact. The research design therefore emphasizes process discipline over headline accuracy:

1. build a chronological historical panel;
2. compare transparent baselines before adding complexity;
3. reject challengers that do not improve out-of-sample performance;
4. freeze the selected model and daily forecast window;
5. collect genuinely prospective predictions;
6. score calibration and probability loss without deleting losses or retuning after outcomes are known.

## Historical data audit

The local research dataset contains **8,566 completed MLB regular-season games**:

| Period | Role | Games |
|---|---:|---:|
| 2023 | Training | 2,430 |
| 2024 | Validation | 2,427 |
| 2025 through 2026-06-30 | Development | 3,709 |
| **Total** |  | **8,566** |

The source is the public MLB schedule/game feed. Raw responses, normalized snapshots, local prediction ledgers, and operational logs remain outside GitHub. Public reports contain only non-redistributive aggregates, protocol definitions, and code.

The July 2026 data were inspected while validating the pipeline and are therefore **not** treated as a blind prospective holdout. An earlier 15-game pilot was also excluded because it used the wrong forecast window. Both exclusions were documented before the eligible prospective series begins.

## Model development result

The selected baseline is a chronological Elo model with a fixed home-field adjustment. On the Development period:

| Model | Log loss | Brier score | Decision |
|---|---:|---:|---|
| 50% probability baseline | 0.693147 | — | Reference |
| Fixed home-win baseline | 0.690881 | — | Reference |
| Chronological Elo | **0.684305** | **0.245667** | Frozen prospective model |
| Ridge challenger | 0.686551 | — | Rejected |

The challenger failed to outperform the simpler Elo specification, so it was not promoted. This is a model-governance decision, not evidence of economic value.

## Prospective protocol

- **Forecast time:** 2:10 PM America/New_York on each eligible game day.
- **Forecast window:** 2:00–2:59 PM New York time.
- **Eligibility:** a game must not have started when the forecast is created.
- **Model version:** chronological-elo-v1.0.3-k5-ha20-1400-windowlocked.
- **Primary metrics:** log loss, Brier score, calibration, and transparent baseline comparisons.
- **Minimum evidence gate:** no broad performance claim before the preregistered prospective threshold is met.
- **Model governance:** no outcome-driven retuning after the prospective series begins.
- **Audit rule:** missed, late, duplicated, or otherwise invalid rows are recorded as protocol deviations rather than silently repaired.
- **Publication:** aggregate protocol and research updates are public; raw data and the append-only local ledger remain private.

The New York Mets provide a recognizable case study, but the statistical population is the full MLB schedule. Mets-specific results will be labeled as a smaller narrative slice, not substituted for the league-wide evaluation.

## What will be published

During the season, this repository will publish:

- protocol amendments made before they affect eligible forecasts;
- model version and forecast-timing rules;
- prospective status updates and non-redistributive aggregates;
- negative, null, and failed results alongside positive results;
- a final report after the prespecified evidence gate.

It will not publish licensed or raw vendor data, private logs, credentials, or a betting recommendation.

## Interpretation boundary

A lower historical log loss does not establish profit. Probability calibration is not the same as beating a market after prices, limits, timing, and transaction costs. Market-odds comparison is a separate research question and will not be claimed unless a properly timestamped odds dataset and frozen comparison protocol are added.

## Reproducibility and integrity

The public repository contains research code, protocol documents, tests, and aggregate evidence. Local-only data are protected by version-control exclusions. The work is designed so that a reader can distinguish historical model development, inspected July pipeline validation, genuinely prospective forecasts, statistical predictive quality, and any later economic or market-efficiency analysis.

## Disclaimer

Research and educational use only. This project is not affiliated with MLB, the New York Mets, Point72, or Steve Cohen. Nothing here is investment advice, betting advice, or evidence of guaranteed performance.
