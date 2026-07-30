"""Development-only robustness diagnostics for the opening-range study.

These functions describe model sensitivity. They neither search the final
holdout nor convert a statistical association into a trading rule.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .primary_analysis import fit_primary_hac_regression


@dataclass(frozen=True)
class SensitivityEstimate:
    """One labeled slope estimate from a prespecified sensitivity."""

    label: str
    sample_size: int
    slope: float
    confidence_low: float
    confidence_high: float
    p_value: float


@dataclass(frozen=True)
class NonlinearFormResult:
    """HAC quadratic-model coefficients and a joint form diagnostic."""

    sample_size: int
    linear_coefficient: float
    quadratic_coefficient: float
    quadratic_p_value: float
    r_squared: float
    hac_max_lags: int


def _development_numeric(
    panel: pd.DataFrame, columns: list[str], *, minimum_rows: int = 8
) -> pd.DataFrame:
    required = {"sample", *columns}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if set(panel["sample"].dropna().astype(str)) != {"development"}:
        raise ValueError("Analysis input must contain development sessions only")
    numeric = panel[columns].apply(pd.to_numeric, errors="coerce").dropna()
    if len(numeric) < minimum_rows or not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("Insufficient finite complete observations")
    return numeric


def _hac_fit(
    design: np.ndarray, y: np.ndarray, *, max_lags: int
) -> tuple[np.ndarray, np.ndarray, float]:
    if not 0 <= max_lags < len(y):
        raise ValueError("max_lags must be nonnegative and smaller than sample size")
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
    total = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - float(np.sum(residuals**2)) / total
    return beta, covariance, r_squared


def influence_trimmed_sensitivity(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
) -> SensitivityEstimate:
    """Refit after removing observations with Cook's distance above ``4/n``."""
    numeric = _development_numeric(panel, [predictor, outcome])
    x = numeric[predictor].to_numpy(float)
    y = numeric[outcome].to_numpy(float)
    design = np.column_stack((np.ones(len(x)), x))
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y - design @ beta
    mse = float(residuals @ residuals) / (len(y) - design.shape[1])
    hat = np.sum((design @ np.linalg.inv(design.T @ design)) * design, axis=1)
    cooks = (residuals**2 / (design.shape[1] * mse)) * (
        hat / np.maximum((1.0 - hat) ** 2, np.finfo(float).eps)
    )
    kept = cooks <= 4.0 / len(y)
    trimmed = panel.loc[numeric.index[kept]].copy()
    result = fit_primary_hac_regression(
        trimmed, predictor=predictor, outcome=outcome, max_lags=max_lags
    )
    return SensitivityEstimate(
        label="Cook's distance <= 4/n",
        sample_size=result.sample_size,
        slope=result.slope,
        confidence_low=result.confidence_low,
        confidence_high=result.confidence_high,
        p_value=result.p_value,
    )


def theil_sen_sensitivity(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    confidence: float = 0.95,
) -> SensitivityEstimate:
    """Estimate a median pairwise slope, robust to extreme observations."""
    numeric = _development_numeric(panel, [predictor, outcome])
    estimate = stats.theilslopes(
        numeric[outcome].to_numpy(float),
        numeric[predictor].to_numpy(float),
        alpha=confidence,
    )
    return SensitivityEstimate(
        label="Theil-Sen",
        sample_size=len(numeric),
        slope=float(estimate.slope),
        confidence_low=float(estimate.low_slope),
        confidence_high=float(estimate.high_slope),
        p_value=float("nan"),
    )


def quadratic_form_sensitivity(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
) -> NonlinearFormResult:
    """Fit a centered quadratic form with HAC uncertainty."""
    numeric = _development_numeric(panel, [predictor, outcome])
    x = numeric[predictor].to_numpy(float)
    centered = x - x.mean()
    y = numeric[outcome].to_numpy(float)
    design = np.column_stack((np.ones(len(x)), centered, centered**2))
    beta, covariance, r_squared = _hac_fit(design, y, max_lags=max_lags)
    quadratic_se = float(np.sqrt(max(covariance[2, 2], 0.0)))
    statistic = float(beta[2] / quadratic_se)
    return NonlinearFormResult(
        sample_size=len(x),
        linear_coefficient=float(beta[1]),
        quadratic_coefficient=float(beta[2]),
        quadratic_p_value=float(2.0 * stats.norm.sf(abs(statistic))),
        r_squared=r_squared,
        hac_max_lags=max_lags,
    )


def volatility_regime_sensitivities(
    panel: pd.DataFrame,
    *,
    regime_variable: str = "lag5_mean_session_range_bps",
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
) -> list[SensitivityEstimate]:
    """Estimate slopes within low, middle, and high trailing-volatility thirds."""
    numeric = _development_numeric(panel, [regime_variable, predictor, outcome])
    regimes = pd.qcut(
        numeric[regime_variable],
        q=3,
        labels=["low", "middle", "high"],
        duplicates="raise",
    )
    estimates: list[SensitivityEstimate] = []
    for label in ["low", "middle", "high"]:
        subset = panel.loc[numeric.index[regimes == label]].copy()
        result = fit_primary_hac_regression(
            subset, predictor=predictor, outcome=outcome, max_lags=max_lags
        )
        estimates.append(
            SensitivityEstimate(
                label=f"{label} trailing volatility",
                sample_size=result.sample_size,
                slope=result.slope,
                confidence_low=result.confidence_low,
                confidence_high=result.confidence_high,
                p_value=result.p_value,
            )
        )
    return estimates


def exclude_roll_sessions_sensitivity(
    panel: pd.DataFrame,
    *,
    predictor: str = "opening_range_width_bps",
    outcome: str = "post_opening_abs_return_bps",
    max_lags: int = 5,
) -> SensitivityEstimate:
    """Refit after excluding contract-switch and mixed-contract sessions."""
    required = {"contract_switch", "mixed_contract_session"}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    flags = panel[list(required)].fillna(False).astype(bool).any(axis=1)
    subset = panel.loc[~flags].copy()
    result = fit_primary_hac_regression(
        subset, predictor=predictor, outcome=outcome, max_lags=max_lags
    )
    return SensitivityEstimate(
        label="exclude roll and mixed-contract sessions",
        sample_size=result.sample_size,
        slope=result.slope,
        confidence_low=result.confidence_low,
        confidence_high=result.confidence_high,
        p_value=result.p_value,
    )
