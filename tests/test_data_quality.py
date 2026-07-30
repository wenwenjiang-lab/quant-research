"""Tests for deterministic intraday data-quality reporting."""

import pandas as pd

from src.data_quality import audit_intraday_bars


def _bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-01-02 09:30:00-05:00",
                    "2025-01-02 09:31:00-05:00",
                    "2025-01-02 09:32:00-05:00",
                ]
            ),
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [10, 20, 30],
        }
    )


def test_clean_bars_pass_audit() -> None:
    report = audit_intraday_bars(_bars())

    assert report.passed
    assert report.row_count == 3
    assert report.session_count == 1
    assert report.unexpected_intraday_intervals == 0


def test_audit_reports_duplicates_bad_prices_and_gaps() -> None:
    bars = _bars()
    bars.loc[1, "timestamp"] = bars.loc[0, "timestamp"]
    bars.loc[2, "high"] = 98.0
    bars.loc[2, "volume"] = -1

    report = audit_intraday_bars(bars)

    assert not report.passed
    assert report.duplicate_timestamps == 1
    assert report.invalid_ohlc_rows == 1
    assert report.negative_volume_rows == 1
    assert report.unexpected_intraday_intervals == 2
