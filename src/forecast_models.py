"""Transparent baseline models and losses for Phase II forecasting."""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy import stats

from .forecast_validation import expanding_window_folds


@dataclass(frozen=True)
class ForecastMetrics:
    observations: int
    mae: float
    rmse: float
    qlike: float
    oos_r_squared: float


@dataclass(frozen=True)
class LossComparison:
    observations: int
    mean_candidate_minus_baseline: float
    hac_standard_error: float
    test_statistic: float
    p_value: float


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


def diebold_mariano_hac(
    candidate_loss: np.ndarray, baseline_loss: np.ndarray, *, max_lags: int = 5
) -> LossComparison:
    """Test the mean paired loss difference with Newey-West uncertainty."""
    candidate = np.asarray(candidate_loss, float)
    baseline = np.asarray(baseline_loss, float)
    if candidate.shape != baseline.shape or candidate.ndim != 1 or len(candidate) < 3:
        raise ValueError("Loss arrays must be aligned one-dimensional samples")
    if not np.isfinite(candidate).all() or not np.isfinite(baseline).all():
        raise ValueError("Loss arrays must be finite")
    if not 0 <= max_lags < len(candidate):
        raise ValueError("Invalid HAC lag count")
    differential = candidate - baseline
    centered = differential - differential.mean()
    long_run_variance = float(centered @ centered) / len(centered)
    for lag in range(1, max_lags + 1):
        covariance = float(centered[lag:] @ centered[:-lag]) / len(centered)
        long_run_variance += 2 * (1 - lag / (max_lags + 1)) * covariance
    standard_error = float(np.sqrt(max(long_run_variance, 0) / len(centered)))
    if standard_error == 0:
        raise ValueError("HAC standard error is zero")
    statistic = float(differential.mean() / standard_error)
    return LossComparison(len(differential), float(differential.mean()), standard_error, statistic, float(2 * stats.norm.sf(abs(statistic))))


def fold_loss_stability(candidate: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    """Return paired QLIKE improvement by registered evaluation fold."""
    merged = candidate.merge(baseline[["session_date", "forecast"]], on="session_date", suffixes=("_candidate", "_baseline"), validate="one_to_one")
    merged["candidate_loss"] = qlike_loss(merged["actual"].to_numpy(), merged["forecast_candidate"].to_numpy())
    merged["baseline_loss"] = qlike_loss(merged["actual"].to_numpy(), merged["forecast_baseline"].to_numpy())
    return merged.groupby("fold", as_index=False).agg(observations=("actual", "size"), candidate_qlike=("candidate_loss", "mean"), baseline_qlike=("baseline_loss", "mean")).assign(improvement=lambda x: x.baseline_qlike - x.candidate_qlike)
