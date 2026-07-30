# Cross-Asset Development Results

> **Status: development gate passed; final holdout sealed.** These results use
> only observations before 2025-02-20. They are evidence of short-horizon
> information transmission, not a trading strategy or validated Alpha.

## Registered question

Does adding lagged MNQ returns improve one-minute QQQ forecasts beyond QQQ's
own lagged returns? The restricted and unrestricted linear models use identical
expanding training windows, one-session embargoes, and test timestamps.

## Development evidence

The evaluation contains 451,584 one-minute forecasts across 1,176 test sessions
and 56 non-overlapping test folds from 2020-06-01 through 2025-02-19.

| Direction | Incremental OOS R² | Positive folds | HAC paired-loss p-value | Decision |
|---|---:|---:|---:|---|
| MNQ → QQQ | 0.5029% | 56 / 56 | < 0.0001 | Development gate passed |
| QQQ → MNQ | -0.0145% | 23 / 56 | 0.0694 | No improvement |

For the primary direction, inference remains strong after first averaging the
paired loss differential within each trading session and then applying a
five-session Newey–West correction (test statistic 12.14; p < 0.0001).

## Latency sensitivity

| MNQ information set | Incremental OOS R² | Positive folds | Session-level p-value |
|---|---:|---:|---:|
| Registered lags 1–5 minutes | 0.5029% | 100.0% | < 0.0001 |
| Lags 2–5 minutes only | -0.0153% | 42.9% | 0.0019 against improvement |
| Lag 5 minutes only | -0.0054% | 46.4% | 0.0605 |

The incremental information is concentrated in the first minute. Removing the
one-minute MNQ lag eliminates the improvement. This is consistent with rapid
price discovery, but it materially weakens any economic or implementation
interpretation. No transaction-cost, fill, or execution analysis has been
performed.

## Research decision

The prespecified numerical development criteria are satisfied in the primary
direction, the reverse direction is reported, and latency sensitivity is
documented. The final holdout remains sealed until this code and report are
reviewed and frozen. If opened, it must be evaluated exactly once using the
registered specification; no post-holdout tuning is permitted.

## Limitations

- Development evidence can still reflect sample-specific structure.
- The one-minute result may be too short-lived to survive realistic latency,
  spread, fees, queue position, or market impact.
- MNQ and QQQ differ in venue, trading mechanics, and price formation.
- The linear model tests incremental predictability, not causal transmission.
- Statistical significance does not imply economically tradable returns.
