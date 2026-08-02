"""Descriptive stability diagnostics for frozen predictive studies.

The functions in this module compare development and holdout samples without
fitting or selecting a model.  They are intended for post-hoc diagnosis after
a registered holdout decision has already been made.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def standardized_mean_difference(
    development: pd.Series, holdout: pd.Series
) -> float:
    """Return the holdout-minus-development mean in development SD units."""

    dev = pd.to_numeric(development, errors="coerce").dropna().to_numpy(float)
    test = pd.to_numeric(holdout, errors="coerce").dropna().to_numpy(float)
    if len(dev) == 0 or len(test) == 0:
        raise ValueError("Both samples must contain finite numeric observations")
    scale = float(np.std(dev, ddof=0))
    if scale == 0:
        return 0.0 if float(np.mean(test)) == float(np.mean(dev)) else float("inf")
    return float((np.mean(test) - np.mean(dev)) / scale)


def population_stability_index(
    development: pd.Series,
    holdout: pd.Series,
    *,
    bins: int = 10,
    epsilon: float = 1e-6,
) -> float:
    """Calculate PSI using quantile edges estimated on development only.

    Duplicate quantiles are removed, making this suitable for discrete market
    features such as spread.  The statistic is descriptive; no universal
    hypothesis-test interpretation is implied.
    """

    if bins < 2:
        raise ValueError("bins must be at least 2")
    dev = pd.to_numeric(development, errors="coerce").dropna().to_numpy(float)
    test = pd.to_numeric(holdout, errors="coerce").dropna().to_numpy(float)
    if len(dev) == 0 or len(test) == 0:
        raise ValueError("Both samples must contain finite numeric observations")
    inner = np.unique(np.quantile(dev, np.linspace(0, 1, bins + 1)[1:-1]))
    edges = np.concatenate(([-np.inf], inner, [np.inf]))
    dev_share = np.histogram(dev, bins=edges)[0] / len(dev)
    test_share = np.histogram(test, bins=edges)[0] / len(test)
    dev_share = np.clip(dev_share, epsilon, None)
    test_share = np.clip(test_share, epsilon, None)
    return float(np.sum((test_share - dev_share) * np.log(test_share / dev_share)))


def feature_drift_table(
    development: pd.DataFrame,
    holdout: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """Return deterministic, development-anchored drift summaries."""

    missing = [
        column
        for column in features
        if column not in development.columns or column not in holdout.columns
    ]
    if missing:
        raise KeyError(f"Missing requested features: {missing}")
    rows = []
    for feature in features:
        rows.append(
            {
                "feature": feature,
                "development_mean": float(development[feature].mean()),
                "holdout_mean": float(holdout[feature].mean()),
                "standardized_mean_difference": standardized_mean_difference(
                    development[feature], holdout[feature]
                ),
                "population_stability_index": population_stability_index(
                    development[feature], holdout[feature]
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(
        "population_stability_index", ascending=False, ignore_index=True
    )


def class_distribution(frame: pd.DataFrame, target: str) -> dict[str, float]:
    """Return sorted empirical class shares with string keys."""

    if target not in frame:
        raise KeyError(target)
    shares = frame[target].value_counts(normalize=True).sort_index()
    def label(key: object) -> str:
        numeric = float(key)
        return str(int(numeric)) if numeric.is_integer() else str(numeric)

    return {label(key): float(value) for key, value in shares.items()}


def leave_one_session_out_means(session_deltas: pd.Series) -> pd.Series:
    """Return the mean effect after omitting each session once."""

    values = pd.to_numeric(session_deltas, errors="raise").astype(float)
    if len(values) < 2:
        raise ValueError("At least two sessions are required")
    total = float(values.sum())
    return values.map(lambda value: (total - value) / (len(values) - 1))
