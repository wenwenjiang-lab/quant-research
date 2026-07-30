import numpy as np
import pandas as pd
import pytest
from src.forecast_models import diebold_mariano_hac, evaluate_forecasts, expanding_linear_predictions, fold_loss_stability, qlike_loss


def test_qlike_is_zero_for_perfect_forecast() -> None:
    assert np.allclose(qlike_loss(np.array([1., 2.]), np.array([1., 2.])), 0)
    with pytest.raises(ValueError):
        qlike_loss(np.array([0.]), np.array([1.]))


def test_expanding_predictions_are_out_of_sample() -> None:
    n = 40
    panel = pd.DataFrame({"session_date": pd.bdate_range("2020-01-01", periods=n), "x": np.arange(n, dtype=float), "y": 2 + np.arange(n, dtype=float)})
    predictions = expanding_linear_predictions(panel, features=["x"], target="y", minimum_training_sessions=20, test_block_sessions=5)
    assert predictions.session_date.min() > panel.session_date.iloc[19]
    metrics = evaluate_forecasts(predictions, benchmark_forecast=np.full(len(predictions), panel.y.iloc[:20].mean()))
    assert metrics.observations == len(predictions)
    assert metrics.oos_r_squared > 0.9


def test_paired_loss_comparison_and_fold_stability() -> None:
    candidate_loss = np.array([1., 2., 1., 2., 1., 2.])
    baseline_loss = candidate_loss + np.array([.2, .3, .1, .4, .2, .3])
    result = diebold_mariano_hac(candidate_loss, baseline_loss, max_lags=1)
    assert result.mean_candidate_minus_baseline < 0
    candidate = pd.DataFrame({"session_date": pd.bdate_range("2023-01-02", periods=4), "actual": [2.,3.,4.,5.], "forecast": [2.,3.,4.,5.], "fold": [0,0,1,1]})
    baseline = candidate.assign(forecast=[1.,2.,3.,4.])
    folds = fold_loss_stability(candidate, baseline)
    assert (folds.improvement > 0).all()
