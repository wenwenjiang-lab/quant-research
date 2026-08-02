# Order-Book Depth and One-Second Price Direction in MNQ Futures

> **Status: completed one-time holdout evaluation; registered replication failed.**
> The evidence does not support a claim of tradable Alpha, profitability,
> deployability, or causality.

## Research question

Does ten-level limit-order-book state contain incremental information about the
direction of the MNQ midpoint one second later, beyond transparent market-state
controls and top-of-book information?

The comparison is deliberately incremental. A positive result requires the
multi-level model to outperform a baseline that already observes spread,
recent midpoint movement, short-horizon volatility, message activity, time of
day, level-one imbalance, and microprice displacement.

## Data

- Source: licensed Databento CME Globex MDP 3.0 `mbp-10` records for `MNQ.v.0`.
- Window: 09:30â€“10:00 New York time.
- Development: 43 sessions, 2026-05-01 through 2026-06-30.
- Final holdout: 19 sessions, 2026-07-01 through 2026-07-27.
- Audited events: 196,679,054 Development and 93,992,308 holdout updates.
- Decision grid: one timestamp per second.
- Eligible observations: 77,214 Development and 34,143 holdout decisions.

Licensed raw records, vendor metadata, API credentials, and derived market-data
panels are excluded from version control.

## Data construction and quality controls

The event stream was converted to end-labeled 100-millisecond book snapshots.
The audit verified vendor hashes, schema and symbol identity, receive-time and
sequence order, ten-level completeness, positive displayed size, depth order,
tick conformity, and crossed or locked states.

The same frozen eligibility rule was applied to Development and holdout:

1. retain one decision timestamp per second;
2. require a complete one-second feature history and one-second outcome horizon;
3. reject nonfinite or nonpositive-spread states; and
4. embargo decisions whose lookback or label interval intersects a rejected
   100-millisecond state.

All 19 holdout sessions passed the structural audit. The low-activity July 3
session was retained because it satisfied the registered structural rules.

## Models

The primary outcome has three classes: midpoint down, unchanged, or up one
second later. Models use L2-regularized multinomial logistic regression.
Scaling, class frequencies, and regularization selection use past sessions only.

- **Controls:** spread, recent midpoint change, recent volatility, message
  activity, and time of day.
- **Top-of-book baseline:** controls plus level-one imbalance and microprice
  displacement.
- **Multi-level candidate:** top-of-book baseline plus five- and ten-level
  imbalance and displayed depth.

Development validation used 15 initial training sessions followed by four
consecutive seven-session validation blocks. The final models were refit on all
43 Development sessions. The deterministic parameter-selection rule had been
frozen before holdout download; the final numeric values (`C=1.0` for the
top-of-book model and `C=0.1` for the multi-level model) were materialized after
download but before parsing any holdout market-data file. This procedural timing
deviation is disclosed rather than omitted.

## Registered decision rules

The Development gate required at least 0.001 lower mean session log loss than
the strongest baseline, improvement in at least three of four validation
blocks, no material Brier-score deterioration, and successful convergence.

Before holdout outcomes were evaluated, replication required:

- candidate minus top-of-book mean session log loss at most -0.001;
- improvement on at least 10 of 19 sessions;
- candidate minus baseline Brier score at most 0.001; and
- valid probability outputs throughout.

## Results

### Development

The multi-level candidate passed the Development gate. Relative to the
top-of-book baseline, mean session log loss improved by 0.001738, all four
chronological blocks improved, and 21 of 28 validation sessions improved. A
session bootstrap interval for the difference was [-0.003685, -0.000492].

### Final holdout

The direction of the effect persisted, but its magnitude did not:

| Metric | Final holdout result |
|---|---:|
| Candidate minus baseline mean session log loss | -0.000222 |
| Candidate minus baseline mean session Brier score | -0.000064 |
| Candidate session wins | 11 / 19 |
| Session bootstrap 95% interval | [-0.000505, 0.000059] |
| One-sided exact sign-test p-value | 0.3238 |
| Registered replication | **FAIL** |

![Session-level holdout log-loss differences](../figures/market_microstructure_holdout_log_loss.svg)

The observed log-loss improvement was approximately 13% of the Development
improvement and fell short of the frozen 0.001 threshold. The uncertainty
interval crossed zero. The correct classification is therefore a failed
replication, despite a slightly favorable point estimate.

## Interpretation

The study provides evidence that deeper book state can appear incrementally
predictive during model development, but that the measured improvement was not
stable enough to satisfy an untouched future-sample criterion. This is a useful
negative result: it quantifies the degree of performance decay and prevents a
small, unstable statistical effect from being presented as Alpha.

No profit estimate is reported. The target is a future midpoint classification,
not an executable fill. A trading claim would additionally require queue
position, latency, adverse selection, commissions, exchange fees, spread
crossing, market impact, and capacity analysis.

## Limitations

- The sample covers less than three months and only one intraday window.
- `MNQ.v.0` is a continuous contract representation; roll-state effects require
  additional study.
- MBP-10 shows displayed depth, not individual queue priority or hidden liquidity.
- Session-level uncertainty is based on only 19 holdout days.
- The study tests one-second prediction, not executable profitability.

## Research disposition

The registered test is closed and will not be retuned. Any future investigation
must be labeled as a new study with new hypotheses and a new untouched sample.
Reasonable follow-up questions include whether the effect is regime-dependent,
whether it transfers to NQ or QQQ, and whether event-time sampling is more stable
than clock-time sampling. Those questions are not answered by this result.

