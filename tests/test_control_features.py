"""Tests that volatility controls use prior sessions only."""

import pandas as pd

from src.control_features import add_lagged_volatility_controls


def test_lagged_controls_do_not_use_current_session() -> None:
    panel = pd.DataFrame(
        {
            "session_date": pd.date_range("2025-01-01", periods=6, freq="D").date,
            "session_range_bps": [10, 20, 30, 40, 50, 600],
        }
    )

    result = add_lagged_volatility_controls(panel)

    assert pd.isna(result.loc[0, "lag1_session_range_bps"])
    assert result.loc[5, "lag1_session_range_bps"] == 50
    assert result.loc[5, "lag5_mean_session_range_bps"] == 30
