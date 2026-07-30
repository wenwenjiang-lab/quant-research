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
