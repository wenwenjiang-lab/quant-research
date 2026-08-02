# MNQ Data-Construction and Quality Report

> **Status: frozen construction-audit snapshot.** This report documents the
> data gates as they stood before the registered forecasting decision. It
> contains no hypothesis result or Alpha claim. Later development-only feature
> checks are in [`phase2_data_quality.md`](phase2_data_quality.md), and the
> completed decision is in
> [`phase2_development_results.md`](phase2_development_results.md).

## Source snapshot

The local research snapshot contains licensed Databento `GLBX.MDP3`
one-minute OHLCV observations for the `MNQ.v.0` continuous series from
2019-05-05 through 2026-07-29 UTC. Raw files and derived observations are
excluded from version control.

| Check | Observed value |
|---|---:|
| Monthly source files | 87 |
| Source rows | 2,549,259 |
| Duplicate timestamps | 0 |
| Non-monotonic timestamps | 0 |
| Invalid OHLC rows | 0 |
| Nonpositive-volume rows | 0 |

These checks establish file integrity and internal price consistency. They do
not establish calendar completeness, contract continuity, or economic validity.

## Regular-session construction

Timestamps are parsed in UTC and converted to `America/New_York`. The candidate
research window is the weekday half-open interval `[09:30, 16:00)`. No missing
bar is silently filled.

| Screening stage | Sessions |
|---|---:|
| Calendar dates with at least one candidate bar | 1,867 |
| Complete 30-bar opening window | 1,863 |
| Incomplete opening window excluded | 4 |
| Complete 360-bar post-opening window among opening-eligible sessions | 1,795 |
| Incomplete post-opening window flagged | 68 |

The four incomplete opening windows occur on 2019-07-04, 2020-03-09,
2020-03-12, and 2020-03-16. The March 2020 intervals overlap known periods of
extraordinary market disruption; gap classification remains a separate audit
task and is not inferred solely from absent aggregate bars.

## Interpretation of missing minute aggregates

The audit finds 56 within-session intervals longer than one minute. An absent
trade-derived OHLCV aggregate can reflect a legitimate trading halt, a minute
with no qualifying trade, a non-standard holiday session, or missing vendor
coverage. These mechanisms are not equivalent. The pipeline therefore reports
the intervals and applies conservative completeness gates instead of imputing
prices or automatically labelling every interval as corrupt.

A separate date-only lineage audit maps the 56 exceptions to 8 distinct
sessions and compares those dates with the exact 1,256-session Phase I
Development panel. The intersection is empty: no session containing a recorded
intraday gap enters that analysis. The reusable check is implemented in
`src/lineage_audit.py`; it fails closed if any overlap exists or if the declared
exception count disagrees with the event list. This resolves analytical
contamination for the historical Phase I panel but does not identify the market
or vendor mechanism behind every absent aggregate.

## Contract identity audit

The regular-session sample contains 30 distinct primary Databento instrument
identifiers and 29 changes between consecutive observed sessions. No session
contains bars from more than one instrument identifier. This is consistent with
a quarterly rolling series at the structural level, but raw expiry symbols and
vendor-selected roll dates still require an independent mapping audit.

## Provisional chronological split

After applying complete opening and outcome-window gates, 1,795 sessions remain.
Without inspecting outcome values, the configured 70/30 chronological rule
assigns 1,256 sessions through 2024-05-23 to development and 539 sessions from
2024-05-24 onward to the final holdout. This boundary is recorded as provisional
until the complete protocol is frozen. Holdout analysis is not yet permitted.

## Continuous-contract limitation

`MNQ.v.0` selects the front contract using previous-day volume. Prices are not
back-adjusted. A roll can introduce a level discontinuity, so no cross-roll
return may be treated as an ordinary price move without a separate roll audit.
The primary opening-range outcomes are intraday, but contract identifiers and
roll dates still require verification before confirmatory analysis.

## Gates recorded at this audit stage

- verify candidate shortened sessions against the exchange calendar;
- resolve continuous-series instrument identifiers to raw contracts and audit
  roll dates;
- freeze chronological development and holdout boundaries;
- publish exclusion counts for every analysis specification;
- keep the final holdout untouched until the confirmatory specification is
  frozen.

This list is preserved as historical research provenance, not as the current
repository status. The later registered study stopped after its development
gate failed, and the final holdout remains sealed with zero rows accessed.
