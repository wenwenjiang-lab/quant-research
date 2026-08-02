# Study Registry

> Machine-readable source: `configs/study_registry.toml`. Statuses record
> research decisions, not trading performance.

## STUDY-01 — Opening Range Behavior in Nasdaq-100 Futures

- **Question:** Do prespecified opening-range features improve out-of-sample forecasts of same-session volatility?
- **Design:** chronological expanding-window development evaluation
- **Sample:** 1,255 eligible Development sessions through 2024-05-23; 730 out-of-sample sessions
- **Status:** `closed_negative`
- **Holdout:** `sealed_unopened`
- **Decision:** Development confirmation gate failed; stop and retain the final holdout unopened.
- **Evidence:** [`reports/phase2_development_results.md`](../reports/phase2_development_results.md)
- **Protocol:** [`reports/phase2_protocol.md`](../reports/phase2_protocol.md)

## STUDY-02 — MNQ-QQQ Information Transmission

- **Question:** Do lagged MNQ returns add one-minute predictive information for QQQ beyond QQQ's own lags?
- **Design:** frozen restricted-versus-unrestricted forecast comparison
- **Sample:** 358 eligible final-holdout sessions from 2025-02-20 through 2026-07-29
- **Status:** `closed_confirmed_statistical`
- **Holdout:** `opened_once_closed`
- **Decision:** A small statistical relationship passed the registered holdout rule; no Alpha or profitability claim.
- **Evidence:** [`reports/cross_asset_final_results.md`](../reports/cross_asset_final_results.md)
- **Protocol:** [`reports/cross_asset_protocol.md`](../reports/cross_asset_protocol.md)

## STUDY-03 — Prospective Economic Relevance

- **Question:** Can a frozen cross-asset signal survive executable delay and conservative trading costs on genuinely new data?
- **Design:** preregistered chronological development plus future single-use holdout
- **Sample:** 0 of 343 required sessions strictly after 2026-07-29
- **Status:** `preregistered_not_started`
- **Holdout:** `unavailable_not_started`
- **Decision:** No empirical result exists; development remains locked until the sample gate is met.
- **Evidence:** [`reports/economic_relevance_protocol.md`](../reports/economic_relevance_protocol.md)
- **Protocol:** [`configs/economic_relevance.toml`](../configs/economic_relevance.toml)

## STUDY-04 — Order-Book Depth and One-Second Price Direction

- **Question:** Do ten-level MNQ order-book features improve one-second forecasts beyond top-of-book features?
- **Design:** chronological Development selection followed by one frozen July replication
- **Sample:** 43 Development sessions and 19 final-holdout sessions from 2026-05-01 through 2026-07-27
- **Status:** `closed_failed_replication`
- **Holdout:** `opened_once_closed`
- **Decision:** The Development effect did not meet the registered replication threshold; the study closed without retuning.
- **Evidence:** [`reports/market_microstructure_holdout.md`](../reports/market_microstructure_holdout.md)
- **Protocol:** [`reports/market_microstructure_holdout.md`](../reports/market_microstructure_holdout.md)

## Interpretation boundary

A confirmed statistical relationship is not automatically executable Alpha.
Closed studies cannot be reopened for tuning, and prospective studies cannot
report outcomes before their registered sample and access gates are satisfied.
