"""Tests for outcome-blind chronological sample assignment."""

import pandas as pd

from src.sample_design import assign_chronological_samples


def test_assigns_only_complete_sessions_to_chronological_samples() -> None:
    panel = pd.DataFrame(
        {
            "session_date": pd.date_range("2025-01-01", periods=5, freq="D").date,
            "complete_outcome_window": [True, False, True, True, True],
            "post_opening_return_points": [999, 999, -999, 999, -999],
        }
    )

    result, report = assign_chronological_samples(
        panel, development_fraction=0.50
    )

    assert result["sample"].tolist() == [
        "development",
        "excluded",
        "development",
        "final_holdout",
        "final_holdout",
    ]
    assert report.eligible_sessions == 4
    assert report.development_sessions == 2
    assert report.holdout_sessions == 2
    assert report.development_end == "2025-01-03"
    assert report.holdout_start == "2025-01-04"
