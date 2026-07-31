from datetime import timedelta

import pandas as pd
import pytest

from src.cross_asset_holdout import EXECUTION_PHRASE, sealed_holdout_predictions


def _panel():
    dates = pd.bdate_range("2024-01-02", periods=8, tz="America/New_York")
    rows = []
    for session_number, date in enumerate(dates):
        for minute in range(3):
            own = session_number + minute / 10
            cross = session_number % 2 + minute / 20
            rows.append({
                "timestamp": date + timedelta(minutes=570 + minute),
                "session_date": date.normalize(),
                "qqq_return": 0.2 + 0.5 * own + 0.3 * cross,
                "qqq_return_lag1": own,
                "futures_return_lag1": cross,
            })
    return pd.DataFrame(rows)


def _run(panel, **overrides):
    arguments = dict(
        target="qqq_return",
        own_lag_features=["qqq_return_lag1"],
        cross_lag_features=["futures_return_lag1"],
        holdout_start="2024-01-10",
        expected_holdout_sessions=2,
        embargo_sessions=1,
        execution_allowed=True,
        execution_phrase=EXECUTION_PHRASE,
    )
    arguments.update(overrides)
    return sealed_holdout_predictions(panel, **arguments)


def test_holdout_is_sealed_by_default():
    with pytest.raises(PermissionError, match="sealed"):
        _run(_panel(), execution_allowed=False)
    with pytest.raises(PermissionError, match="sealed"):
        _run(_panel(), execution_phrase="wrong")


def test_exact_holdout_session_count_is_required():
    with pytest.raises(ValueError, match="Expected 3"):
        _run(_panel(), expected_holdout_sessions=3)


def test_authorized_holdout_run_returns_paired_forecasts_once():
    result = _run(_panel())
    assert result["session_date"].nunique() == 2
    assert len(result) == 6
    assert result["timestamp"].is_unique
    assert result["unrestricted_forecast"].notna().all()
