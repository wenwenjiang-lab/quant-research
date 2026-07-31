# Quantitative Research Roadmap

> **Portfolio status: active.** Two registered empirical studies are complete.
> Future milestones describe intended evidence, not trading performance.

## Completed research controls

- **Research protocols:** falsifiable questions, estimands, exclusions, sample
  boundaries, and decision rules are versioned before confirmatory evaluation.
- **Market-data pipeline:** schema, timestamps, OHLCV invariants, duplicates,
  bar intervals, contract rolls, and synchronized cross-venue observations are
  audited without redistributing licensed data.
- **Point-in-time datasets:** opening-range and cross-asset features are formed
  strictly before their outcomes, with explicit boundary and completeness
  checks.
- **Statistical inference:** effect sizes, HAC-aware paired tests,
  session-aggregated inference, and multiplicity controls are implemented.
- **Time-series validation:** chronological development samples,
  expanding-window evaluation, embargoes, frozen gates, and protected holdouts
  are enforced in code.
- **External validity:** the portfolio progresses from MNQ session behavior to
  synchronized MNQ–QQQ information transmission.

## Completed studies

### Study 01 — Opening Range Behavior

The registered development gate failed. The result is reported as negative,
and the final holdout remains sealed rather than being used for model search.

### Study 02 — MNQ–QQQ Information Transmission

The single-use final holdout confirmed a small one-minute statistical
relationship. The holdout is permanently closed. No trading or Alpha claim is
made because execution costs and market microstructure are outside the study.

## Next study — Economic relevance protocol

The prospective design is now frozen in
[`reports/economic_relevance_protocol.md`](reports/economic_relevance_protocol.md)
and [`configs/economic_relevance.toml`](configs/economic_relevance.toml). The
study has not started and no result is available. It requires 343 genuinely
new sessions after the completed parent sample: 274 for chronological
development and 69 for a final holdout that remains inaccessible during model
development. Current readiness is 0/343.

Any economic evaluation will be a new registered study, not a reinterpretation
or rerun of the completed holdout. Before analysis it must specify:

- an executable signal timestamp and conservative fill convention;
- spread, fees, slippage, and turnover assumptions;
- a no-trade benchmark and minimum economic-effect threshold;
- position, exposure, and loss constraints;
- chronological development and a newly protected evaluation sample;
- capacity and market-impact limitations;
- a stop rule that permits a negative economic conclusion.

## Later extensions

1. Replicate the information-transmission design on ES–SPY using harmonized
   definitions and a separately registered sample.
2. Compare regularized linear and nonlinear models only after transparent
   baselines, with calibration and stability diagnostics.
3. Add event-time and liquidity-regime analysis when suitable licensed quote or
   trade data are available.

Each extension requires its own study identifier, frozen protocol, and data
boundary. Completed holdouts are never reopened for tuning.
