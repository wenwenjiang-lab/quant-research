import numpy as np
import pandas as pd
import pytest

from src.cross_asset_evaluation import (
    confirmation_gate,
    hac_mean_test,
    session_clustered_loss_test,
    summarize_nested_forecasts,
)


def test_hac_mean_test_detects_positive_constant_improvement_with_noise():
    values = pd.Series(np.tile([0.8, 1.0, 1.2, 1.1, 0.9], 20))
    result = hac_mean_test(values, max_lag=2)
    assert result["mean"] == pytest.approx(1.0)
    assert result["statistic"] > 5
    assert result["p_value"] < 0.05


def test_hac_mean_test_rejects_invalid_lag():
    with pytest.raises(ValueError, match="max_lag"):
        hac_mean_test(pd.Series([1.0, 2.0, 3.0]), max_lag=3)


def test_summary_uses_paired_rows_and_fold_stability():
    panel = pd.DataFrame({
        "fold": [0, 0, 1, 1],
        "restricted_loss": [4.0, 4.0, 4.0, 4.0],
        "unrestricted_loss": [3.0, 3.0, 5.0, 3.0],
        "loss_improvement": [1.0, 1.0, -1.0, 1.0],
    })
    result = summarize_nested_forecasts(panel, hac_max_lag=0)
    assert result["incremental_oos_r_squared"] == pytest.approx(0.125)
    assert result["positive_improvement_fraction"] == pytest.approx(0.5)
    assert result["folds"] == 2


def test_confirmation_gate_requires_every_registered_condition():
    summary = {
        "incremental_oos_r_squared": 0.01,
        "paired_loss_p_value": 0.01,
        "positive_improvement_fraction": 0.75,
    }
    complete = dict(
        reverse_direction_reported=True,
        latency_sensitivity_reported=True,
        protocol_and_code_frozen=True,
    )
    assert confirmation_gate(summary, **complete)["gate_passed"] is True
    summary["paired_loss_p_value"] = 0.20
    assert confirmation_gate(summary, **complete)["gate_passed"] is False


def test_confirmation_gate_stays_closed_until_required_reports_exist():
    summary = {
        "incremental_oos_r_squared": 0.01,
        "paired_loss_p_value": 0.01,
        "positive_improvement_fraction": 0.75,
    }
    result = confirmation_gate(summary)
    assert result["gate_passed"] is False
    assert result["latency_sensitivity_reported"] is False


def test_session_clustered_test_aggregates_minutes_before_inference():
    panel = pd.DataFrame({
        "session_date": np.repeat(pd.date_range("2024-01-01", periods=8), 3),
        "loss_improvement": np.tile([0.5, 1.0, 1.5], 8),
    })
    result = session_clustered_loss_test(panel, session_hac_max_lag=1)
    assert result["mean"] == pytest.approx(1.0)
    assert result["sessions"] == 8


def test_summary_rejects_nonpositive_restricted_loss():
    panel = pd.DataFrame({
        "fold": [0, 0, 0],
        "restricted_loss": [0.0, 0.0, 0.0],
        "unrestricted_loss": [0.0, 0.0, 0.0],
        "loss_improvement": [0.0, 0.0, 0.0],
    })
    with pytest.raises(ValueError, match="positive"):
        summarize_nested_forecasts(panel, hac_max_lag=0)
