"""Point-in-time utilities for synchronized cross-asset return panels.

The functions in this module enforce interval and lag semantics only. They do
not download data, estimate an empirical relationship, or represent a trading
strategy.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import time, timedelta

import pandas as pd


REQUIRED_COLUMNS = {"timestamp", "close"}
NEW_YORK = "America/New_York"
ONE_MINUTE = timedelta(minutes=1)


def validate_price_bars(bars: pd.DataFrame, *, asset: str) -> pd.DataFrame:
    """Validate and normalize timestamped close-price bars for one asset.

    Timestamps must be timezone-aware and unique. Prices must be finite and
    strictly positive. The returned frame is sorted without mutating input.
    """

    missing = REQUIRED_COLUMNS.difference(bars.columns)
    if missing:
        raise ValueError(f"{asset}: missing columns: {sorted(missing)}")

    optional = [column for column in ("instrument_id",) if column in bars.columns]
    clean = bars.loc[:, ["timestamp", "close", *optional]].copy()
    clean["timestamp"] = pd.to_datetime(clean["timestamp"], errors="raise")
    if clean["timestamp"].dt.tz is None:
        raise ValueError(f"{asset}: timestamps must be timezone-aware")
    if clean["timestamp"].duplicated().any():
        raise ValueError(f"{asset}: duplicate timestamps are not allowed")

    clean["close"] = pd.to_numeric(clean["close"], errors="coerce")
    if clean["close"].isna().any() or (clean["close"] <= 0).any():
        raise ValueError(f"{asset}: close prices must be finite and positive")
    return clean.sort_values("timestamp").reset_index(drop=True)


def build_synchronized_return_panel(
    futures_bars: pd.DataFrame,
    qqq_bars: pd.DataFrame,
    *,
    lags: Sequence[int] = (1, 2, 3, 4, 5),
    session_start: time = time(9, 30),
    session_end: time = time(16, 0),
    holdout_start: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Build a complete-case, point-in-time panel from overlapping bars.

    Each close-to-close return is indexed by the interval ending at its
    timestamp and exists only when the preceding timestamp is exactly one
    minute earlier in the same New York session and futures instrument.
    Cross-asset predictors are shifted by at least one exact minute;
    contemporaneous cross-asset returns are retained only as outcomes and
    diagnostics, never under a predictor name. If ``holdout_start`` is given,
    that date and every later date are excluded before any return is computed.
    """

    lag_values = tuple(int(lag) for lag in lags)
    if not lag_values or any(lag < 1 for lag in lag_values):
        raise ValueError("lags must contain positive integers")
    if len(set(lag_values)) != len(lag_values):
        raise ValueError("lags must be unique")

    futures = validate_price_bars(futures_bars, asset="futures").rename(
        columns={"close": "futures_close", "instrument_id": "futures_instrument_id"}
    )
    qqq = validate_price_bars(qqq_bars, asset="qqq").rename(
        columns={"close": "qqq_close", "instrument_id": "qqq_instrument_id"}
    )
    panel = futures.merge(qqq, on="timestamp", how="inner", validate="one_to_one")
    panel["timestamp"] = panel["timestamp"].dt.tz_convert(NEW_YORK)
    panel["session_date"] = panel["timestamp"].dt.normalize()
    local_time = panel["timestamp"].dt.time
    panel = panel.loc[(local_time >= session_start) & (local_time < session_end)].copy()

    if holdout_start is not None:
        boundary = pd.Timestamp(holdout_start)
        if boundary.tzinfo is None:
            boundary = boundary.tz_localize(NEW_YORK)
        else:
            boundary = boundary.tz_convert(NEW_YORK)
        boundary = boundary.normalize()
        panel = panel.loc[panel["session_date"] < boundary].copy()

    previous_timestamp = panel["timestamp"].shift(1)
    previous_session = panel["session_date"].shift(1)
    exact_previous_minute = (
        panel["timestamp"].sub(previous_timestamp).eq(ONE_MINUTE)
        & panel["session_date"].eq(previous_session)
    )
    same_futures_contract = pd.Series(True, index=panel.index)
    if "futures_instrument_id" in panel.columns:
        same_futures_contract = panel["futures_instrument_id"].eq(
            panel["futures_instrument_id"].shift(1)
        )

    panel["futures_return"] = panel["futures_close"].pct_change(fill_method=None).where(
        exact_previous_minute & same_futures_contract
    )
    panel["qqq_return"] = panel["qqq_close"].pct_change(fill_method=None).where(
        exact_previous_minute
    )

    for lag in lag_values:
        exact_lag = (
            panel["timestamp"].sub(panel["timestamp"].shift(lag)).eq(ONE_MINUTE * lag)
            & panel["session_date"].eq(panel["session_date"].shift(lag))
        )
        panel[f"futures_return_lag{lag}"] = panel["futures_return"].shift(lag).where(
            exact_lag
        )
        panel[f"qqq_return_lag{lag}"] = panel["qqq_return"].shift(lag).where(exact_lag)

    required = [
        "futures_return",
        "qqq_return",
        *[f"futures_return_lag{lag}" for lag in lag_values],
        *[f"qqq_return_lag{lag}" for lag in lag_values],
    ]
    return panel.dropna(subset=required).reset_index(drop=True)
