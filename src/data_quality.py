"""Deterministic data-quality checks for intraday OHLCV research data."""

from dataclasses import dataclass
from datetime import timedelta

import pandas as pd
from pandas.tseries.frequencies import to_offset


@dataclass(frozen=True)
class DataQualityReport:
    """Machine-readable summary of structural market-data checks."""

    row_count: int
    session_count: int
    duplicate_timestamps: int
    invalid_ohlc_rows: int
    nonpositive_price_rows: int
    negative_volume_rows: int
    unexpected_intraday_intervals: int
    passed: bool


def audit_intraday_bars(
    bars: pd.DataFrame,
    *,
    timestamp_column: str = "timestamp",
    timezone: str = "America/New_York",
    expected_frequency: str = "1min",
) -> DataQualityReport:
    """Audit schema, price invariants, duplicates, and within-day bar spacing.

    The function reports problems instead of repairing or dropping observations.
    Calendar completeness and contract-roll validity require separate metadata and
    are deliberately outside this structural audit.
    """
    required = {timestamp_column, "open", "high", "low", "close"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if bars.empty:
        raise ValueError("At least one bar is required")

    timestamps = pd.to_datetime(bars[timestamp_column], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("Timestamps must be valid")
    if timestamps.dt.tz is None:
        raise ValueError("Timestamps must be timezone-aware")

    prices = bars[["open", "high", "low", "close"]].apply(
        pd.to_numeric, errors="coerce"
    )
    invalid_numeric = prices.isna().any(axis=1)
    invalid_ohlc = (
        invalid_numeric
        | (prices["high"] < prices["low"])
        | (prices["open"] > prices["high"])
        | (prices["open"] < prices["low"])
        | (prices["close"] > prices["high"])
        | (prices["close"] < prices["low"])
    )
    nonpositive = (prices <= 0).any(axis=1) | invalid_numeric

    negative_volume = pd.Series(False, index=bars.index)
    if "volume" in bars.columns:
        volume = pd.to_numeric(bars["volume"], errors="coerce")
        negative_volume = volume.isna() | (volume < 0)

    local_timestamps = timestamps.dt.tz_convert(timezone)
    ordered = pd.DataFrame({"timestamp": local_timestamps}).sort_values("timestamp")
    ordered["session_date"] = ordered["timestamp"].dt.date
    offset = to_offset(expected_frequency)
    if offset.nanos % 1_000:
        raise ValueError("Expected frequency must resolve to whole microseconds")
    expected_delta = timedelta(microseconds=offset.nanos // 1_000)
    deltas = ordered.groupby("session_date")["timestamp"].diff()
    unexpected_intervals = int(((deltas.notna()) & (deltas != expected_delta)).sum())

    duplicates = int(timestamps.duplicated().sum())
    invalid_count = int(invalid_ohlc.sum())
    nonpositive_count = int(nonpositive.sum())
    negative_volume_count = int(negative_volume.sum())
    passed = not any(
        (
            duplicates,
            invalid_count,
            nonpositive_count,
            negative_volume_count,
            unexpected_intervals,
        )
    )
    return DataQualityReport(
        row_count=len(bars),
        session_count=int(local_timestamps.dt.date.nunique()),
        duplicate_timestamps=duplicates,
        invalid_ohlc_rows=invalid_count,
        nonpositive_price_rows=nonpositive_count,
        negative_volume_rows=negative_volume_count,
        unexpected_intraday_intervals=unexpected_intervals,
        passed=passed,
    )
