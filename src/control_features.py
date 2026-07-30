"""Lagged controls constructed without using current-session outcomes."""

from __future__ import annotations

import pandas as pd


def add_lagged_volatility_controls(panel: pd.DataFrame) -> pd.DataFrame:
    """Add prior-session and trailing-five-session range controls.

    ``session_range_bps`` is shifted before rolling, so every control for date
    *t* uses only sessions dated before *t*. Missing initial values are retained
    for transparent complete-case handling rather than imputed.
    """
    required = {"session_date", "session_range_bps"}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    result = panel.copy()
    dates = pd.to_datetime(result["session_date"], errors="coerce")
    ranges = pd.to_numeric(result["session_range_bps"], errors="coerce")
    if dates.isna().any() or dates.duplicated().any():
        raise ValueError("Session dates must be valid and unique")
    if ranges.isna().any() or (ranges <= 0).any():
        raise ValueError("Session ranges must be finite and positive")

    result = result.assign(_date=dates, session_range_bps=ranges).sort_values("_date")
    prior = result["session_range_bps"].shift(1)
    result["lag1_session_range_bps"] = prior
    result["lag5_mean_session_range_bps"] = prior.rolling(
        window=5, min_periods=5
    ).mean()
    return result.drop(columns="_date").reset_index(drop=True)
