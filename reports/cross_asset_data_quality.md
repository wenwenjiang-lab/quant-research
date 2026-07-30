# Cross-Asset Data-Quality Audit

> **Status: coverage audit only; no model results.** Licensed observations
> remain local and are not redistributed by this repository.

## Sources and scope

- MNQ: Databento `GLBX.MDP3`, continuous front contract, `ohlcv-1m`.
- QQQ: Databento `XNAS.ITCH`, raw symbol `QQQ`, `ohlcv-1m`.
- Common requested range: 2019-05-05 through 2026-07-29.
- Registered session: 09:30-16:00 `America/New_York`, left-closed and
  right-open.

Databento minute timestamps denote interval starts. The audit converts both
feeds from UTC to New York time before applying the session boundary and joins
only exact timestamps. Missing prices are excluded rather than filled.

## File and schema audit

The QQQ delivery contains 87 monthly OHLCV files and 1,487,664 rows. It maps
only to `QQQ`. Two rows have missing price fields and are excluded. Among the
remaining 1,487,662 rows, the audit finds:

- zero invalid numeric rows;
- zero OHLC invariant violations;
- zero nonpositive-volume rows;
- zero duplicate timestamps; and
- zero nonmonotonic timestamps.

## Cross-asset overlap

| Audit item | Count |
| --- | ---: |
| MNQ unique regular-session minutes | 716,067 |
| QQQ unique regular-session minutes | 707,744 |
| Exact overlapping minutes | 705,793 |
| MNQ regular-session dates | 1,867 |
| QQQ regular-session dates | 1,818 |
| Complete common 390-minute sessions | 1,787 |

The first complete common session is 2019-05-06 and the last is 2026-07-29.
Shortened or incomplete sessions do not enter the primary full-session panel.

## Frozen holdout boundary

Applying the registered newest-20% rule to the 1,787 eligible sessions assigns
358 sessions to the final holdout. The holdout begins **2025-02-20**.

This calculation uses only timestamp coverage and completeness. No returns,
model coefficients, forecasts, losses, statistical tests, or trading outcomes
from the holdout were calculated or inspected. `holdout_analysis_allowed`
remains `false` in the machine-readable protocol.

## Remaining gates

Before development modeling, the implementation must add automated corporate-
action, futures-roll, exact-lag, and timestamp-shift falsification tests. Model
development must end before 2025-02-20 and use chronological folds only.
