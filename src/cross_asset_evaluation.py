"""Statistical evaluation for paired cross-asset development forecasts."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _normal_two_sided_p_value(statistic: float) -> float:
    """Return a two-sided standard-normal p-value without scipy dependency."""
    return math.erfc(abs(statistic) / math.sqrt(2.0))


def hac_mean_test(values: pd.Series, *, max_lag: int) -> dict[str, float]:
    """Test whether a dependent series has zero mean using Newey-West HAC.

    The Bartlett-kernel variance estimator is applied to the sample mean.
    This is suitable for the registered paired loss-differential test; it is
    not a license to select the lag after inspecting the final holdout.
    """
    sample = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if sample.size < 3:
        raise ValueError("At least three finite observations are required")
    if max_lag < 0 or max_lag >= sample.size:
        raise ValueError("max_lag must be between zero and n - 1")

    centered = sample - sample.mean()
    long_run_variance = float(centered @ centered / sample.size)
    for lag in range(1, max_lag + 1):
        covariance = float(centered[lag:] @ centered[:-lag] / sample.size)
        weight = 1.0 - lag / (max_lag + 1.0)
        long_run_variance += 2.0 * weight * covariance

    variance_of_mean = max(long_run_variance, 0.0) / sample.size
    standard_error = math.sqrt(variance_of_mean)
    statistic = float(sample.mean() / standard_error) if standard_error > 0 else math.nan
    p_value = _normal_two_sided_p_value(statistic) if math.isfinite(statistic) else math.nan
    return {
        "mean": float(sample.mean()),
        "standard_error": standard_error,
        "statistic": statistic,
        "p_value": p_value,
        "n": float(sample.size),
    }


def summarize_nested_forecasts(
    loss_panel: pd.DataFrame, *, hac_max_lag: int = 5
) -> dict[str, float]:
    """Summarize prespecified development metrics for nested forecasts."""
    required = {"fold", "restricted_loss", "unrestricted_loss", "loss_improvement"}
    missing = sorted(required.difference(loss_panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    clean = loss_panel.loc[:, sorted(required)].replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        raise ValueError("No finite paired losses are available")

    restricted = float(clean["restricted_loss"].sum())
    unrestricted = float(clean["unrestricted_loss"].sum())
    if restricted <= 0:
        raise ValueError("Restricted squared loss must be positive")
    fold_improvement = clean.groupby("fold", sort=True)["loss_improvement"].mean()
    test = hac_mean_test(clean["loss_improvement"], max_lag=hac_max_lag)
    return {
        "incremental_oos_r_squared": 1.0 - unrestricted / restricted,
        "positive_improvement_fraction": float((fold_improvement > 0).mean()),
        "mean_loss_improvement": test["mean"],
        "paired_loss_statistic": test["statistic"],
        "paired_loss_p_value": test["p_value"],
        "observations": float(len(clean)),
        "folds": float(fold_improvement.size),
    }


def confirmation_gate(
    summary: dict[str, float],
    *,
    minimum_oos_r_squared: float = 0.0,
    maximum_p_value: float = 0.05,
    minimum_positive_fraction: float = 0.60,
) -> dict[str, bool]:
    """Apply the frozen development gate without accessing a holdout."""
    decisions = {
        "positive_oos_r_squared": summary["incremental_oos_r_squared"] > minimum_oos_r_squared,
        "significant_paired_loss": summary["paired_loss_p_value"] < maximum_p_value,
        "stable_across_folds": summary["positive_improvement_fraction"] > minimum_positive_fraction,
    }
    decisions["gate_passed"] = all(decisions.values())
    return decisions
