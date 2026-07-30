"""Point-in-time feature construction for Phase II volatility forecasting."""

from __future__ import annotations

from datetime import time
import pandas as pd

FEATURE_AVAILABILITY = {
    "previous_session_range_bps": "previous_close",
    "lag5_mean_session_range_bps": "previous_close",
    "lag20_mean_session_range_bps": "previous_close",
    "overnight_return_bps": "09:30",
    "overnight_range_bps": "09:30",
    "opening_gap_bps": "09:30",
    "opening_range_width_bps": "10:00",
    "opening_range_return_bps": "10:00",
    "opening_range_realized_range_bps": "10:00",
}


def build_phase2_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Add strictly lagged historical features to a chronological session panel."""
    required = {"session_date", "session_range_bps"}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    result = panel.copy()
    result["session_date"] = pd.to_datetime(result["session_date"], errors="coerce")
    if result["session_date"].isna().any() or not result["session_date"].is_monotonic_increasing:
        raise ValueError("Session dates must be valid and chronologically ordered")
    if result["session_date"].duplicated().any():
        raise ValueError("Session dates must be unique")
    ranges = pd.to_numeric(result["session_range_bps"], errors="coerce")
    result["previous_session_range_bps"] = ranges.shift(1)
    result["lag5_mean_session_range_bps"] = ranges.shift(1).rolling(5).mean()
    result["lag20_mean_session_range_bps"] = ranges.shift(1).rolling(20).mean()
    return result


def audit_feature_cutoff(feature_availability: dict[str, str], *, cutoff: str = "10:00") -> None:
    """Reject any model feature whose declared availability is after cutoff."""
    cutoff_time = time.fromisoformat(cutoff)
    for feature, available_at in feature_availability.items():
        if available_at == "previous_close":
            continue
        if time.fromisoformat(available_at) > cutoff_time:
            raise ValueError(f"Feature {feature} is unavailable by {cutoff}")


def assert_no_target_in_features(feature_columns: list[str], target: str) -> None:
    """Reject direct target inclusion and target-derived feature names."""
    forbidden = [name for name in feature_columns if name == target or name.startswith("post_1000_")]
    if forbidden:
        raise ValueError(f"Target leakage detected: {', '.join(forbidden)}")


def build_intraday_forecast_rows(
    bars: pd.DataFrame, *, timezone: str = "America/New_York", holdout_start: str = "2024-05-24"
) -> pd.DataFrame:
    """Construct auditable pre-open, opening-range, and post-10:00 fields."""
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    work = bars.copy()
    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
    if work["timestamp"].isna().any() or work["timestamp"].dt.tz is None:
        raise ValueError("Timestamps must be valid and timezone-aware")
    work["timestamp"] = work["timestamp"].dt.tz_convert(timezone)
    work = work.sort_values("timestamp")
    work["session_date"] = work["timestamp"].dt.date
    rows = []
    for date, day in work.groupby("session_date", sort=True):
        date_ts = pd.Timestamp(date)
        if date_ts >= pd.Timestamp(holdout_start):
            continue
        clock = day["timestamp"].dt.time
        opening = day[(clock >= time(9, 30)) & (clock < time(10, 0))]
        target = day[(clock >= time(10, 0)) & (clock < time(16, 0))]
        preopen = day[clock < time(9, 30)]
        if len(opening) != 30 or len(target) != 360 or preopen.empty:
            continue
        prior = work[work["session_date"] < date]
        if prior.empty:
            continue
        prior_close = float(prior.iloc[-1]["close"])
        open_price = float(opening.iloc[0]["open"])
        or_end = float(opening.iloc[-1]["close"])
        rows.append({
            "session_date": date_ts,
            "overnight_return_bps": (float(preopen.iloc[-1]["close"]) / prior_close - 1) * 10_000,
            "overnight_range_bps": (float(preopen["high"].max()) - float(preopen["low"].min())) / prior_close * 10_000,
            "opening_gap_bps": (open_price / prior_close - 1) * 10_000,
            "opening_range_width_bps": (float(opening["high"].max()) - float(opening["low"].min())) / open_price * 10_000,
            "opening_range_return_bps": (or_end / open_price - 1) * 10_000,
            "opening_range_realized_range_bps": (float(opening["high"].max()) - float(opening["low"].min())) / open_price * 10_000,
            "post_1000_realized_range_bps": (float(target["high"].max()) - float(target["low"].min())) / float(target.iloc[0]["open"]) * 10_000,
            "feature_max_timestamp": opening["timestamp"].max(),
            "target_min_timestamp": target["timestamp"].min(),
        })
    result = pd.DataFrame(rows)
    if not result.empty and (result["feature_max_timestamp"].dt.time >= time(10, 0)).any():
        raise ValueError("Feature timestamp exceeds the 10:00 cutoff")
    return result
