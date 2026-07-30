"""Unit tests for opening-range calculations using synthetic fixtures."""

from datetime import time

import pandas as pd
import pytest

from src.opening_range import OpeningRange, calculate_opening_range


@pytest.fixture
def sample_bars() -> pd.DataFrame:
    """Return minimal synthetic bars designed only to test deterministic logic."""
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-01-02 09:29:00-05:00",
                    "2025-01-02 09:30:00-05:00",
                    "2025-01-02 09:31:00-05:00",
                    "2025-01-02 09:32:00-05:00",
                ]
            ),
            "high": [99.0, 101.0, 103.0, 110.0],
            "low": [98.0, 100.0, 99.0, 90.0],
        }
    )


def test_calculates_half_open_interval(sample_bars: pd.DataFrame) -> None:
    result = calculate_opening_range(sample_bars, start=time(9, 30), end=time(9, 32))

    assert result == OpeningRange(high=103.0, low=99.0, midpoint=101.0, width=4.0, bar_count=2)


def test_rejects_naive_timestamps(sample_bars: pd.DataFrame) -> None:
    sample_bars["timestamp"] = sample_bars["timestamp"].dt.tz_localize(None)

    with pytest.raises(ValueError, match="timezone-aware"):
        calculate_opening_range(sample_bars, start=time(9, 30), end=time(9, 32))


def test_rejects_multiple_session_dates(sample_bars: pd.DataFrame) -> None:
    extra = sample_bars.iloc[[0]].copy()
    extra["timestamp"] = pd.to_datetime(["2025-01-03 09:30:00-05:00"])

    with pytest.raises(ValueError, match="exactly one session"):
        calculate_opening_range(pd.concat([sample_bars, extra]), start=time(9, 30), end=time(9, 32))


def test_rejects_empty_interval(sample_bars: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="No bars"):
        calculate_opening_range(sample_bars, start=time(8, 0), end=time(8, 30))


def test_rejects_invalid_interval(sample_bars: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="start must be earlier"):
        calculate_opening_range(sample_bars, start=time(9, 32), end=time(9, 30))
