"""Opening-range calculations for intraday OHLC bars."""

from dataclasses import dataclass
from datetime import time

import pandas as pd


@dataclass(frozen=True)
class OpeningRange:
    """Summary of the high-low range over a specified opening interval."""

    high: float
    low: float
    midpoint: float
    width: float
    bar_count: int


def calculate_opening_range(
    bars: pd.DataFrame,
    *,
    start: time,
    end: time,
    timestamp_column: str = "timestamp",
) -> OpeningRange:
    """Calculate an opening range using the half-open interval ``[start, end)``.

    The function operates on one trading session at a time. Timestamps must be
    timezone-aware so the caller cannot silently apply an ambiguous market clock.

    Args:
        bars: Intraday data containing timestamp, high, and low columns.
        start: Inclusive start time in the timestamps' time zone.
        end: Exclusive end time in the timestamps' time zone.
        timestamp_column: Name of the timestamp column.

    Raises:
        ValueError: If inputs are invalid or the interval contains no bars.
    """
    required = {timestamp_column, "high", "low"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if start >= end:
        raise ValueError("start must be earlier than end within the same day")

    timestamps = pd.to_datetime(bars[timestamp_column], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("Timestamps must be valid")
    if timestamps.dt.tz is None:
        raise ValueError("Timestamps must be timezone-aware")
    if timestamps.dt.date.nunique() != 1:
        raise ValueError("Opening range must be calculated for exactly one session date")

    clock_times = timestamps.dt.time
    selected = bars.loc[(clock_times >= start) & (clock_times < end), ["high", "low"]].copy()
    selected["high"] = pd.to_numeric(selected["high"], errors="coerce")
    selected["low"] = pd.to_numeric(selected["low"], errors="coerce")
    if selected.empty:
        raise ValueError("No bars fall inside the requested opening interval")
    if selected.isna().any().any():
        raise ValueError("Opening-range high and low values must be numeric")
    if (selected["high"] < selected["low"]).any():
        raise ValueError("High prices cannot be below low prices")

    range_high = float(selected["high"].max())
    range_low = float(selected["low"].min())
    return OpeningRange(
        high=range_high,
        low=range_low,
        midpoint=(range_high + range_low) / 2.0,
        width=range_high - range_low,
        bar_count=len(selected),
    )
