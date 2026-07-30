"""Prespecified development-sample analysis with holdout guards."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class HACRegressionResult:
    """Simple OLS slope with Newey-West heteroskedasticity/autocorrelation SE."""

    sample_size: int
    intercept: float
    slope: float
    slope_standard_error: float
    test_statistic: float
    p_value: float
    confidence_low: float
    confidence_high: float
    r_squared: float
    hac_max_lags: int


@dataclass(frozen=True)
class BlockBootstrapResult:
    """Moving-block-bootstrap summary for the primary slope."""

    resamples: int
    block_length: int
    seed: int
    slope_standard_error: float
    confidence_low: float
    confidence_high: float


@dataclass(frozen=True)
class ControlledHACResult:
    """Primary slope after controlling for trailing historical volatility."""

    sample_size: int
    excluded_incomplete_rows: int
    focal_slope: float
    focal_standard_error: float
    p_value: float
    confidence_low: float
    confidence_high: float
    lagged_volatility_slope: float
    r_squared: float
    hac_max_lags: int


@dataclass(frozen=True)
class PrimaryModelDiagnostics:
    """Development-only residual and influence diagnostics."""

    sample_size: int
    durbin_watson: float
    residual_lag1_autocorrelation: float
    influential_threshold: float
    influential_session_count: int
    maximum_cooks_distance: float


def _development_arrays(
    panel: pd.DataFrame,
    *,
    predictor: str,
    outcome: str,
) -> tuple[np.ndarray, np.ndarray]:
    required = {"sample", predictor, outcome}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    labels = set(panel["sample"].dropna().astype(str))
    if labels != {"development"}:
        raise ValueError("Analysis input must contain development sessions only")
    values = panel[[predictor, outcome]].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Predictor and outcome must be finite with no imputation")
    if len(values) < 3 or values[predictor].nunique() < 2:
        raise ValueError("At least three observations and predictor variation are required")
    return values[predictor].to_numpy(float), values[outcome].to_numpy(float)


def _ols_coefficients(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    design = np.column_stack((np.ones(len(x)), x))
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    return beta, design


def fit_primary_hac_regression(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
    confidence: float = 0.95,
) -> HACRegressionResult:
    """Fit the registered simple model and calculate Newey-West uncertainty."""
    x, y = _development_arrays(panel, predictor=predictor, outcome=outcome)
    if not 0 <= max_lags < len(x):
        raise ValueError("max_lags must be nonnegative and smaller than sample size")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")

    beta, design = _ols_coefficients(x, y)
    residuals = y - design @ beta
    bread = np.linalg.inv(design.T @ design)
    weighted = design * residuals[:, None]
    meat = weighted.T @ weighted
    for lag in range(1, max_lags + 1):
        weight = 1.0 - lag / (max_lags + 1.0)
        gamma = weighted[lag:].T @ weighted[:-lag]
        meat += weight * (gamma + gamma.T)
    covariance = bread @ meat @ bread
    covariance *= len(x) / (len(x) - design.shape[1])
    slope_se = float(np.sqrt(max(covariance[1, 1], 0.0)))
    if slope_se == 0:
        raise ValueError("HAC slope standard error is zero")
    statistic = float(beta[1] / slope_se)
    p_value = float(2.0 * stats.norm.sf(abs(statistic)))
    critical = float(stats.norm.ppf((1.0 + confidence) / 2.0))
    fitted = design @ beta
    total_sum_squares = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - float(np.sum((y - fitted) ** 2)) / total_sum_squares
    return HACRegressionResult(
        sample_size=len(x),
        intercept=float(beta[0]),
        slope=float(beta[1]),
        slope_standard_error=slope_se,
        test_statistic=statistic,
        p_value=p_value,
        confidence_low=float(beta[1] - critical * slope_se),
        confidence_high=float(beta[1] + critical * slope_se),
        r_squared=r_squared,
        hac_max_lags=max_lags,
    )


def moving_block_bootstrap_slope(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    block_length: int = 5,
    resamples: int = 5000,
    seed: int = 20260730,
    confidence: float = 0.95,
) -> BlockBootstrapResult:
    """Return a deterministic moving-block-bootstrap percentile interval."""
    x, y = _development_arrays(panel, predictor=predictor, outcome=outcome)
    if not 1 <= block_length <= len(x):
        raise ValueError("block_length must be between one and sample size")
    if resamples < 100:
        raise ValueError("At least 100 bootstrap resamples are required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")

    rng = np.random.default_rng(seed)
    possible_starts = len(x) - block_length + 1
    blocks_needed = int(np.ceil(len(x) / block_length))
    slopes = np.empty(resamples)
    for iteration in range(resamples):
        starts = rng.integers(0, possible_starts, size=blocks_needed)
        indices = np.concatenate(
            [np.arange(start, start + block_length) for start in starts]
        )[: len(x)]
        slopes[iteration] = _ols_coefficients(x[indices], y[indices])[0][1]
    tail = (1.0 - confidence) / 2.0
    return BlockBootstrapResult(
        resamples=resamples,
        block_length=block_length,
        seed=seed,
        slope_standard_error=float(slopes.std(ddof=1)),
        confidence_low=float(np.quantile(slopes, tail)),
        confidence_high=float(np.quantile(slopes, 1.0 - tail)),
    )


def fit_controlled_hac_regression(
    panel: pd.DataFrame,
    *,
    focal_predictor: str = "opening_range_width_bps",
    volatility_control: str = "lag5_mean_session_range_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
    confidence: float = 0.95,
) -> ControlledHACResult:
    """Fit the prespecified incremental-information robustness model."""
    required = {"sample", focal_predictor, volatility_control, outcome}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if set(panel["sample"].dropna().astype(str)) != {"development"}:
        raise ValueError("Analysis input must contain development sessions only")

    numeric = panel[[focal_predictor, volatility_control, outcome]].apply(
        pd.to_numeric, errors="coerce"
    )
    complete = numeric.dropna()
    if not np.isfinite(complete.to_numpy()).all():
        raise ValueError("Model values must be finite")
    if len(complete) < 4 or not 0 <= max_lags < len(complete):
        raise ValueError("Insufficient complete observations for requested HAC lags")

    y = complete[outcome].to_numpy(float)
    design = np.column_stack(
        (
            np.ones(len(complete)),
            complete[focal_predictor].to_numpy(float),
            complete[volatility_control].to_numpy(float),
        )
    )
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y - design @ beta
    bread = np.linalg.inv(design.T @ design)
    weighted = design * residuals[:, None]
    meat = weighted.T @ weighted
    for lag in range(1, max_lags + 1):
        weight = 1.0 - lag / (max_lags + 1.0)
        gamma = weighted[lag:].T @ weighted[:-lag]
        meat += weight * (gamma + gamma.T)
    covariance = bread @ meat @ bread
    covariance *= len(y) / (len(y) - design.shape[1])
    focal_se = float(np.sqrt(max(covariance[1, 1], 0.0)))
    if focal_se == 0:
        raise ValueError("HAC focal standard error is zero")
    statistic = float(beta[1] / focal_se)
    critical = float(stats.norm.ppf((1.0 + confidence) / 2.0))
    total_sum_squares = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - float(np.sum(residuals**2)) / total_sum_squares
    return ControlledHACResult(
        sample_size=len(complete),
        excluded_incomplete_rows=len(numeric) - len(complete),
        focal_slope=float(beta[1]),
        focal_standard_error=focal_se,
        p_value=float(2.0 * stats.norm.sf(abs(statistic))),
        confidence_low=float(beta[1] - critical * focal_se),
        confidence_high=float(beta[1] + critical * focal_se),
        lagged_volatility_slope=float(beta[2]),
        r_squared=r_squared,
        hac_max_lags=max_lags,
    )


def diagnose_primary_model(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
) -> PrimaryModelDiagnostics:
    """Calculate residual dependence and Cook's-distance influence diagnostics."""
    x, y = _development_arrays(panel, predictor=predictor, outcome=outcome)
    beta, design = _ols_coefficients(x, y)
    residuals = y - design @ beta
    residual_sum_squares = float(residuals @ residuals)
    degrees_freedom = len(y) - design.shape[1]
    mse = residual_sum_squares / degrees_freedom
    hat = np.sum((design @ np.linalg.inv(design.T @ design)) * design, axis=1)
    cooks = (residuals**2 / (design.shape[1] * mse)) * (
        hat / np.maximum((1.0 - hat) ** 2, np.finfo(float).eps)
    )
    threshold = 4.0 / len(y)
    lag1 = float(np.corrcoef(residuals[1:], residuals[:-1])[0, 1])
    durbin_watson = float(np.sum(np.diff(residuals) ** 2) / residual_sum_squares)
    return PrimaryModelDiagnostics(
        sample_size=len(y),
        durbin_watson=durbin_watson,
        residual_lag1_autocorrelation=lag1,
        influential_threshold=threshold,
        influential_session_count=int((cooks > threshold).sum()),
        maximum_cooks_distance=float(cooks.max()),
    )
