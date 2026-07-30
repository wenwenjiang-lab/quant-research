"""Tests for OHLC loading and validation using temporary synthetic CSVs."""

import pandas as pd
import pytest

from src.data_loader import load_ohlc_csv


def test_loads_sorts_and_localizes_valid_csv(tmp_path) -> None:
    csv_path = tmp_path / "bars.csv"
    pd.DataFrame(
        {
            "timestamp": ["2025-01-02 09:31:00", "2025-01-02 09:30:00"],
            "open": [101, 100],
            "high": [102, 101],
            "low": [100, 99],
            "close": [101.5, 100.5],
        }
    ).to_csv(csv_path, index=False)

    result = load_ohlc_csv(csv_path, timezone="America/New_York")

    assert result["timestamp"].is_monotonic_increasing
    assert str(result["timestamp"].dt.tz) == "America/New_York"


def test_rejects_naive_timestamps_without_timezone(tmp_path) -> None:
    csv_path = tmp_path / "bars.csv"
    pd.DataFrame(
        {
            "timestamp": ["2025-01-02 09:30:00"],
            "open": [100],
            "high": [101],
            "low": [99],
            "close": [100.5],
        }
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="explicit timezone"):
        load_ohlc_csv(csv_path)


def test_rejects_price_outside_bar_range(tmp_path) -> None:
    csv_path = tmp_path / "bars.csv"
    pd.DataFrame(
        {
            "timestamp": ["2025-01-02 09:30:00-05:00"],
            "open": [102],
            "high": [101],
            "low": [99],
            "close": [100],
        }
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Open prices"):
        load_ohlc_csv(csv_path)
