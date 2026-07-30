"""Tests for leakage-aware construction of the session research panel."""

from datetime import time

import pandas as pd
import pytest

from src.study_dataset import (
    OpeningRangeStudySpec,
    build_opening_range_panel,
    build_screened_opening_range_panel,
)


def _session_bars() -> pd.DataFrame:
    timestamps = pd.date_range(
        "2025-01-02 09:30:00",
        periods=5,
        freq="1min",
        tz="America/New_York",
    )
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": [100.0, 100.5, 101.0, 102.0, 101.5],
            "high": [101.0, 102.0, 103.0, 102.5, 102.0],
            "low": [99.0, 100.0, 100.5, 101.0, 100.0],
            "close": [100.5, 101.0, 102.0, 101.5, 100.5],
        }
    )


def test_builds_one_session_feature_and_outcome_row() -> None:
    spec = OpeningRangeStudySpec(
        opening_start=time(9, 30),
        opening_end=time(9, 32),
        outcome_end=time(9, 35),
        expected_opening_bars=2,
        expected_outcome_bars=3,
    )

    panel = build_opening_range_panel(_session_bars(), spec=spec)

    assert len(panel) == 1
    assert panel.loc[0, "opening_range_high"] == 102.0
    assert panel.loc[0, "opening_range_low"] == 99.0
    assert panel.loc[0, "post_opening_return_points"] == pytest.approx(-0.5)
    assert panel.loc[0, "opening_range_width_bps"] == pytest.approx(
        3.0 / 100.5 * 10_000
    )
    assert panel.loc[0, "post_opening_abs_return_bps"] == pytest.approx(
        0.5 / 101.0 * 10_000
    )
    assert panel.loc[0, "first_break_direction"] == "up"
    assert panel.loc[0, "opening_range_bar_count"] == 2
    assert panel.loc[0, "complete_outcome_window"]


def test_rejects_incomplete_opening_range() -> None:
    spec = OpeningRangeStudySpec(
        opening_start=time(9, 30),
        opening_end=time(9, 33),
        outcome_end=time(9, 35),
        expected_opening_bars=4,
    )

    with pytest.raises(ValueError, match="expected 4"):
        build_opening_range_panel(_session_bars(), spec=spec)


def test_screened_panel_reports_incomplete_sessions() -> None:
    complete = _session_bars()
    incomplete = _session_bars().iloc[1:].copy()
    incomplete["timestamp"] = incomplete["timestamp"] + pd.Timedelta(days=1)
    bars = pd.concat([complete, incomplete], ignore_index=True)
    spec = OpeningRangeStudySpec(
        opening_start=time(9, 30),
        opening_end=time(9, 32),
        outcome_end=time(9, 35),
        expected_opening_bars=2,
        expected_outcome_bars=3,
    )

    panel, report = build_screened_opening_range_panel(bars, spec=spec)

    assert len(panel) == 1
    assert report.observed_sessions == 2
    assert report.eligible_sessions == 1
    assert report.excluded_incomplete_opening == 1
    assert report.excluded_missing_outcome == 0
    assert report.incomplete_outcome_sessions == 0
