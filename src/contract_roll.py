"""Auditable contract-identity checks for continuous futures research."""

from __future__ import annotations

import pandas as pd


def build_contract_roll_audit(
    bars: pd.DataFrame,
    *,
    timezone: str = "America/New_York",
) -> pd.DataFrame:
    """Summarize contract identity and transitions by local session date.

    The function does not infer expiry symbols or repair roll discontinuities.
    It records the dominant vendor instrument identifier, flags sessions with
    multiple identifiers, and marks changes from the preceding observed session.
    """
    required = {"timestamp", "instrument_id"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if bars.empty:
        raise ValueError("At least one bar is required")

    timestamps = pd.to_datetime(bars["timestamp"], errors="coerce")
    identifiers = pd.to_numeric(bars["instrument_id"], errors="coerce")
    if timestamps.isna().any() or timestamps.dt.tz is None:
        raise ValueError("Timestamps must be valid and timezone-aware")
    if identifiers.isna().any():
        raise ValueError("Instrument identifiers must be numeric")

    working = pd.DataFrame(
        {
            "session_date": timestamps.dt.tz_convert(timezone).dt.date,
            "instrument_id": identifiers.astype("int64"),
        }
    )
    counts = (
        working.groupby(["session_date", "instrument_id"], sort=True)
        .size()
        .rename("bar_count")
        .reset_index()
    )
    primary = (
        counts.sort_values(
            ["session_date", "bar_count", "instrument_id"],
            ascending=[True, False, True],
        )
        .drop_duplicates("session_date")
        .rename(
            columns={
                "instrument_id": "primary_instrument_id",
                "bar_count": "primary_instrument_bar_count",
            }
        )
    )
    distinct = counts.groupby("session_date")["instrument_id"].nunique().rename(
        "distinct_instrument_ids"
    )
    result = primary.merge(distinct, on="session_date", validate="one_to_one")
    result["mixed_contract_session"] = result["distinct_instrument_ids"] > 1
    result["contract_switch"] = result["primary_instrument_id"].ne(
        result["primary_instrument_id"].shift()
    )
    result.loc[result.index[0], "contract_switch"] = False
    return result.reset_index(drop=True)
