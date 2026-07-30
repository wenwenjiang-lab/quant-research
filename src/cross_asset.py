"""Point-in-time utilities for synchronized cross-asset return panels.

The functions in this module enforce interval and lag semantics only. They do
not download data, estimate an empirical relationship, or represent a trading
strategy.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


REQUIRED_COLUMNS = {"timestamp", "close"}


def validate_price_bars(bars: pd.DataFrame, *, asset: str) -> pd.DataFrame:
    """Validate and normalize timestamped close-price bars for one asset.

    Timestamps must be timezone-aware and unique. Prices must be finite and
    strictly positive. The returned frame is sorted without mutating input.
    """

    missing = REQUIRED_COLUMNS.difference(bars.columns)
    if missing:
        raise ValueError(f"{asset}: missing columns: {sorted(missing)}")

    clean = bars.loc[:, ["timestamp", "close"]].copy()
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
) -> pd.DataFrame:
    """Build a complete-case, point-in-time panel from overlapping bars.

    Each close-to-close return is indexed by the interval ending at its
    timestamp. Cross-asset predictors are shifted by at least one interval;
    contemporaneous cross-asset returns are retained only as outcomes and
    diagnostics, never under a predictor name.
    """

    lag_values = tuple(int(lag) for lag in lags)
    if not lag_values or any(lag < 1 for lag in lag_values):
        raise ValueError("lags must contain positive integers")
    if len(set(lag_values)) != len(lag_values):
        raise ValueError("lags must be unique")

    futures = validate_price_bars(futures_bars, asset="futures").rename(
        columns={"close": "futures_close"}
    )
    qqq = validate_price_bars(qqq_bars, asset="qqq").rename(
        columns={"close": "qqq_close"}
    )
    panel = futures.merge(qqq, on="timestamp", how="inner", validate="one_to_one")
    panel["futures_return"] = panel["futures_close"].pct_change(fill_method=None)
    panel["qqq_return"] = panel["qqq_close"].pct_change(fill_method=None)

    for lag in lag_values:
        panel[f"futures_return_lag{lag}"] = panel["futures_return"].shift(lag)
        panel[f"qqq_return_lag{lag}"] = panel["qqq_return"].shift(lag)

    required = [
        "futures_return",
        "qqq_return",
        *[f"futures_return_lag{lag}" for lag in lag_values],
        *[f"qqq_return_lag{lag}" for lag in lag_values],
    ]
    return panel.dropna(subset=required).reset_index(drop=True)
