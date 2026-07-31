from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from src.cross_asset_models import expanding_nested_predictions, nested_forecast_loss_panel


def _panel(sessions=10, rows_per_session=3):
    dates = pd.bdate_range("2024-01-02", periods=sessions, tz="America/New_York")
    rows = []
    for session_number, date in enumerate(dates):
        for minute in range(rows_per_session):
            own = session_number + minute / 10
            cross = (session_number % 3) - minute / 20
            rows.append({
                "timestamp": date + timedelta(minutes=570 + minute),
                "session_date": date.normalize(),
                "qqq_return": 0.2 + 0.5 * own + 0.3 * cross,
                "qqq_return_lag1": own,
                "futures_return_lag1": cross,
            })
    return pd.DataFrame(rows)


def test_nested_predictions_use_session_level_embargo_and_paired_rows():
    panel = _panel()
    predictions = expanding_nested_predictions(
        panel, target="qqq_return", own_lag_features=["qqq_return_lag1"],
        cross_lag_features=["futures_return_lag1"], holdout_start="2025-01-01",
        minimum_training_sessions=4, test_block_sessions=2, embargo_sessions=1,
    )
    sessions = panel["session_date"].drop_duplicates().reset_index(drop=True)
    assert predictions["session_date"].min() == sessions.iloc[5]
    assert len(predictions) == 5 * 3
    assert predictions["timestamp"].is_unique
    assert np.allclose(predictions["unrestricted_forecast"], predictions["actual"])


def test_holdout_rows_are_rejected_before_model_fitting():
    panel = _panel()
    with pytest.raises(ValueError, match="Final holdout access is prohibited"):
        expanding_nested_predictions(
            panel, target="qqq_return", own_lag_features=["qqq_return_lag1"],
            cross_lag_features=["futures_return_lag1"],
            holdout_start=panel["session_date"].iloc[-1], minimum_training_sessions=4,
        )


def test_feature_sets_must_be_disjoint():
    with pytest.raises(ValueError, match="disjoint"):
        expanding_nested_predictions(
            _panel(), target="qqq_return", own_lag_features=["qqq_return_lag1"],
            cross_lag_features=["qqq_return_lag1"], holdout_start="2025-01-01",
        )


def test_squared_loss_panel_is_observation_aligned():
    predictions = pd.DataFrame({
        "actual": [1.0, 2.0], "restricted_forecast": [0.0, 1.5],
        "unrestricted_forecast": [0.5, 2.0],
    })
    losses = nested_forecast_loss_panel(predictions)
    assert losses["restricted_loss"].tolist() == [1.0, 0.25]
    assert losses["unrestricted_loss"].tolist() == [0.25, 0.0]
    assert losses["loss_improvement"].tolist() == [0.75, 0.25]


def test_mixed_daylight_saving_offsets_from_csv_are_normalized():
    panel = _panel(sessions=8)
    panel["timestamp"] = panel["timestamp"].astype(str)
    panel["session_date"] = panel["session_date"].astype(str)
    panel.loc[panel.index[-3:], "timestamp"] = panel.loc[
        panel.index[-3:], "timestamp"
    ].str.replace("-05:00", "-04:00", regex=False)
    predictions = expanding_nested_predictions(
        panel, target="qqq_return", own_lag_features=["qqq_return_lag1"],
        cross_lag_features=["futures_return_lag1"], holdout_start="2025-01-01",
        minimum_training_sessions=4, test_block_sessions=2, embargo_sessions=1,
    )
    assert predictions["session_date"].nunique() == 3
    assert isinstance(predictions["session_date"].dtype, pd.DatetimeTZDtype)
