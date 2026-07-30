# Data

Market data is stored locally and is not committed to this public repository.
This separation protects licensed data and keeps the research workflow
reproducible without redistributing vendor observations.

## Current local datasets

### Primary research dataset: Databento

- Instrument: Micro E-mini Nasdaq-100 futures (MNQ)
- Dataset: CME Globex MDP 3.0 (`GLBX.MDP3`)
- Requested series: `MNQ.v.0`, the front continuous contract selected by
  previous-day volume
- Frequency: one-minute OHLCV bars
- Coverage: 2019-05-05 through 2026-07-29 UTC
- Observations: 2,549,259 bars across 87 monthly files
- Price adjustment: none; observed contract prices are not back-adjusted
- Raw timestamps: UTC; research clock: `America/New_York`

The batch files live under `data/raw/databento/` and are excluded by
`.gitignore`. The public repository contains ingestion logic and synthetic
tests, but no licensed observations or API credentials.

### Development cross-check dataset: ProjectX/TopstepX

- Instrument: Micro E-mini Nasdaq-100 futures (MNQ)
- Source: historical market-data cache created through the owner's authorized
  ProjectX/TopstepX connection
- Frequency: one-minute OHLCV bars
- Timestamp format: ISO 8601 with UTC offsets; research code converts timestamps
  explicitly to `America/New_York`
- Local coverage: 42 trading days from 2026-06-01 through 2026-07-28
- Observations: 31,120 bars
- Columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`

These files live under `data/raw/mnq/` and are excluded by `.gitignore`.
Generated analytical datasets belong under `data/processed/` and are excluded
as well.

## Validation status

The Databento batch contains 87 monthly files with consistent schemas, no
duplicate or non-monotonic timestamps, no invalid OHLC rows, and no
nonpositive-volume rows. This verifies file-level structure, not exchange-calendar
completeness or economic validity.

The ProjectX/TopstepX files pass the repository's OHLC price and
duplicate-timestamp checks. Nine missing one-minute intervals occur on 2026-06-11 before 07:00 New
York time; no interval gaps occur during the 09:30-16:00 research window.
2026-06-19 and 2026-07-03 contain 210 rather than 390 regular-session bars
because of early closes and must be flagged or excluded from full-session
outcomes. These checks establish structural validity only; they do not establish
contract-continuity accuracy or research results.

## Limitations

The continuous series is selected using a volume rule and is not price-adjusted.
Roll boundaries can therefore create discontinuities that must not be interpreted
as intraday returns. Instrument identifiers, roll behavior, exchange holidays,
shortened sessions, and missing bars require explicit audits before inference.
The longer sample satisfies a size prerequisite but does not itself establish
alpha or complete the study. Chronological holdouts and external validation are
still required before drawing conclusions.
