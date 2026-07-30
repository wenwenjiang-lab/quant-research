"""Transparent baseline models and losses for Phase II forecasting."""

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .forecast_validation import expanding_window_folds


@dataclass(frozen=True)
class ForecastMetrics:
    observations: int
    mae: float
    rmse: float
    qlike: float
    oos_r_squared: float


def qlike_loss(actual: np.ndarray, forecast: np.ndarray) -> np.ndarray:
    """Return QLIKE losses for strictly positive variance-like quantities."""
    actual = np.asarray(actual, float)
    forecast = np.asarray(forecast, float)
    if actual.shape != forecast.shape or (actual <= 0).any() or (forecast <= 0).any():
        raise ValueError("QLIKE inputs must share shape and be strictly positive")
    ratio = actual / forecast
    return ratio - np.log(ratio) - 1.0


def expanding_linear_predictions(
    panel: pd.DataFrame,
    *,
    features: list[str],
    target: str,
    minimum_training_sessions: int = 504,
    test_block_sessions: int = 63,
    embargo_sessions: int = 1,
) -> pd.DataFrame:
    """Fit unregularized linear baselines using training data only in each fold."""
    required = {"session_date", target, *features}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    clean = panel[["session_date", target, *features]].dropna().reset_index(drop=True)
    folds = expanding_window_folds(clean["session_date"], minimum_training_sessions=minimum_training_sessions, test_block_sessions=test_block_sessions, embargo_sessions=embargo_sessions)
    outputs = []
    for number, fold in enumerate(folds):
        train, test = clean.iloc[fold.train_indices], clean.iloc[fold.test_indices]
        x_train = np.column_stack((np.ones(len(train)), train[features].to_numpy(float)))
        beta = np.linalg.lstsq(x_train, train[target].to_numpy(float), rcond=None)[0]
        x_test = np.column_stack((np.ones(len(test)), test[features].to_numpy(float)))
        forecast = np.maximum(x_test @ beta, np.finfo(float).eps)
        outputs.append(pd.DataFrame({"session_date": test["session_date"], "actual": test[target], "forecast": forecast, "fold": number}))
    return pd.concat(outputs, ignore_index=True)


def evaluate_forecasts(predictions: pd.DataFrame, *, benchmark_forecast: np.ndarray) -> ForecastMetrics:
    """Evaluate forecasts against an aligned registered benchmark."""
    actual = predictions["actual"].to_numpy(float)
    forecast = predictions["forecast"].to_numpy(float)
    benchmark = np.asarray(benchmark_forecast, float)
    if benchmark.shape != actual.shape:
        raise ValueError("Benchmark must align with predictions")
    errors = actual - forecast
    denominator = np.sum((actual - benchmark) ** 2)
    return ForecastMetrics(len(actual), float(np.mean(np.abs(errors))), float(np.sqrt(np.mean(errors**2))), float(np.mean(qlike_loss(actual, forecast))), float(1 - np.sum(errors**2) / denominator))
