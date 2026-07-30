"""Tests for Databento normalization and regular-session selection."""

from datetime import time

import pandas as pd
import pytest

from src.databento_loader import load_databento_ohlcv, select_regular_trading_session


def _vendor_frame(timestamps: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ts_event": timestamps,
            "rtype": [33] * len(timestamps),
            "publisher_id": [1] * len(timestamps),
            "instrument_id": [12345] * len(timestamps),
            "open": [100.0] * len(timestamps),
            "high": [101.0] * len(timestamps),
            "low": [99.0] * len(timestamps),
            "close": [100.5] * len(timestamps),
            "volume": [10] * len(timestamps),
            "symbol": ["MNQ.v.0"] * len(timestamps),
        }
    )


def test_loads_multiple_vendor_files_and_preserves_provenance(tmp_path) -> None:
    _vendor_frame(["2025-01-02T14:31:00Z"]).to_csv(tmp_path / "b.csv", index=False)
    _vendor_frame(["2025-01-02T14:30:00Z"]).to_csv(tmp_path / "a.csv", index=False)

    result = load_databento_ohlcv(tmp_path)

    assert len(result) == 2
    assert result["timestamp"].is_monotonic_increasing
    assert str(result["timestamp"].dt.tz) == "UTC"
    assert result["instrument_id"].tolist() == [12345, 12345]
    assert result["symbol"].tolist() == ["MNQ.v.0", "MNQ.v.0"]


def test_rejects_duplicate_vendor_timestamps(tmp_path) -> None:
    frame = _vendor_frame(["2025-01-02T14:30:00Z"])
    frame.to_csv(tmp_path / "a.csv", index=False)
    frame.to_csv(tmp_path / "b.csv", index=False)

    with pytest.raises(ValueError, match="duplicate timestamps"):
        load_databento_ohlcv(tmp_path)


def test_selects_new_york_regular_session_and_excludes_weekend() -> None:
    bars = _vendor_frame(
        [
            "2025-01-02T14:29:00Z",
            "2025-01-02T14:30:00Z",
            "2025-01-02T20:59:00Z",
            "2025-01-02T21:00:00Z",
            "2025-01-04T15:00:00Z",
        ]
    ).rename(columns={"ts_event": "timestamp"})
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)

    result = select_regular_trading_session(
        bars, start=time(9, 30), end=time(16, 0)
    )

    assert result["timestamp"].dt.strftime("%H:%M").tolist() == ["09:30", "15:59"]
    assert str(result["timestamp"].dt.tz) == "America/New_York"
