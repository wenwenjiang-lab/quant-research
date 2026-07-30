# Model Card — MNQ–QQQ Information Transmission

> **Status: research model frozen; statistical study complete.** This model
> card documents the registered comparison and its allowed interpretation. It
> is not a production deployment specification.

## Model purpose

Estimate whether lagged MNQ returns add one-minute predictive information for
QQQ returns beyond information already contained in QQQ's own recent returns.
The model is designed for a nested forecast comparison, not for order
generation, portfolio construction, or live trading.

## Model comparison

| Component | Restricted model | Unrestricted model |
|---|---|---|
| Estimator | Ordinary least squares with intercept | Ordinary least squares with intercept |
| Own-asset inputs | QQQ return lags 1–5 | QQQ return lags 1–5 |
| Cross-asset inputs | None | MNQ return lags 1–5 |
| Target | Next one-minute QQQ return | Next one-minute QQQ return |
| Primary loss | Squared forecast error | Squared forecast error |

No primary regularization, nonlinear transformation, global scaling, or
same-timestamp cross-asset feature is used. Exploratory alternatives cannot
determine confirmation.

## Information timing

- Timestamps represent the start of left-closed, right-open one-minute bars.
- A return is available only after its source interval closes.
- Same-timestamp cross-asset predictors are prohibited.
- Prices are not forward-filled and returns are not interpolated.
- Only complete overlapping regular-session intervals are eligible.
- All joins and session labels use `America/New_York` conventions.

These controls are intended to prevent look-ahead leakage and false lead–lag
relationships caused by inconsistent timestamps.

## Training and evaluation

Development evaluation uses expanding training windows by session, 21-session
test blocks, a one-session embargo, and at least 252 training sessions. Random
shuffling and ordinary K-fold validation are prohibited.

The final 358-session holdout begins 2025-02-20. It was evaluated exactly once
after the protocol, feature set, model pair, inference method, and confirmation
rule were frozen. It is permanently closed to reruns and retuning.

## Final evidence

| Metric | Final holdout |
|---|---:|
| Sessions | 358 |
| Synchronized observations | 137,472 |
| Incremental OOS R² | 0.1888% |
| HAC paired-loss p-value | 0.0182 |
| Session-aggregated p-value | 0.0432 |
| Restricted directional accuracy | 48.64% |
| Unrestricted directional accuracy | 50.27% |

The frozen statistical rule is satisfied. The effect is smaller than in
development and disappears in the registered latency sensitivity when the
one-minute MNQ lag is removed.

## Appropriate use

- study short-horizon information transmission across related instruments;
- demonstrate point-in-time feature construction and nested forecast testing;
- reproduce software behavior with deterministic synthetic data;
- support further preregistered research questions with new evaluation data.

## Prohibited use

- claiming validated Alpha, profitability, or production readiness;
- generating live orders or position sizes;
- estimating PnL without a separately registered execution model;
- retuning specifications against the completed holdout;
- redistributing licensed bars or row-level forecasts.

## Known limitations

- The effect is statistically detectable but economically small.
- Directional accuracy is near 50%.
- Spread, fees, slippage, latency, fills, queue position, impact, and capacity
  are not modeled.
- Shared news and market structure can create association without structural
  causality.
- The primary evidence is specific to MNQ and QQQ over the registered sample.
- NQ replication and other index–ETF pairs require separately licensed data
  and a new protocol.

## Governance and reproducibility

The machine-readable specification is
[`configs/cross_asset_lead_lag.toml`](../configs/cross_asset_lead_lag.toml).
The frozen design is in
[`cross_asset_protocol.md`](cross_asset_protocol.md), the final decision is in
[`cross_asset_final_results.md`](cross_asset_final_results.md), and the
single-use execution record is in
[`cross_asset_holdout_execution.md`](cross_asset_holdout_execution.md).
Licensed observations and row-level outputs remain local and excluded from
version control.
