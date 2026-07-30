"""Leakage-resistant linear baselines for cross-asset forecasting."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def _linear_forecast(train, test, *, features: Sequence[str], target: str) -> np.ndarray:
    """Fit ordinary least squares with an intercept on one training window."""
    x_train = np.column_stack(
        (np.ones(len(train)), train.loc[:, features].to_numpy(dtype=float))
    )
    x_test = np.column_stack(
        (np.ones(len(test)), test.loc[:, features].to_numpy(dtype=float))
    )
    beta = np.linalg.lstsq(x_train, train[target].to_numpy(dtype=float), rcond=None)[0]
    return x_test @ beta


def expanding_nested_predictions(
    panel: pd.DataFrame,
    *,
    target: str,
    own_lag_features: Sequence[str],
    cross_lag_features: Sequence[str],
    holdout_start: str | pd.Timestamp,
    minimum_training_sessions: int = 252,
    test_block_sessions: int = 21,
    embargo_sessions: int = 1,
) -> pd.DataFrame:
    """Generate paired restricted and unrestricted development forecasts.

    Splits use unique session dates while retaining every eligible minute.
    The holdout boundary is enforced before filtering or model fitting. No
    shuffling, global scaling, or full-sample estimation is performed.
    """
    own_features = tuple(own_lag_features)
    cross_features = tuple(cross_lag_features)
    if not own_features or not cross_features:
        raise ValueError("Both own-lag and cross-lag feature sets are required")
    if set(own_features).intersection(cross_features):
        raise ValueError("Own-lag and cross-lag feature sets must be disjoint")
    if minimum_training_sessions < 2 or test_block_sessions < 1:
        raise ValueError("Invalid expanding-window parameters")
    if embargo_sessions < 0:
        raise ValueError("embargo_sessions must be non-negative")

    required = {"timestamp", "session_date", target, *own_features, *cross_features}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    columns = ["timestamp", "session_date", target, *own_features, *cross_features]
    clean = panel.loc[:, columns].copy()
    clean["timestamp"] = pd.to_datetime(clean["timestamp"], errors="coerce")
    clean["session_date"] = pd.to_datetime(clean["session_date"], errors="coerce")
    if clean[["timestamp", "session_date"]].isna().any().any():
        raise ValueError("Timestamps and session dates must be valid")
    if not clean["timestamp"].is_monotonic_increasing:
        raise ValueError("Panel must be chronologically ordered")
    if clean["timestamp"].duplicated().any():
        raise ValueError("Panel timestamps must be unique")

    boundary = pd.Timestamp(holdout_start)
    session_tz = clean["session_date"].dt.tz
    if session_tz is not None:
        boundary = boundary.tz_localize(session_tz) if boundary.tzinfo is None else boundary.tz_convert(session_tz)
    elif boundary.tzinfo is not None:
        boundary = boundary.tz_localize(None)
    boundary = boundary.normalize()
    if (clean["session_date"] >= boundary).any():
        raise ValueError("Final holdout access is prohibited")

    numeric = [target, *own_features, *cross_features]
    clean[numeric] = clean[numeric].apply(pd.to_numeric, errors="coerce")
    clean = clean.replace([np.inf, -np.inf], np.nan).dropna(subset=numeric)
    sessions = pd.Index(clean["session_date"].drop_duplicates())
    first_test = minimum_training_sessions + embargo_sessions
    if len(sessions) <= first_test:
        raise ValueError("Sample is too short for one evaluation fold")

    outputs = []
    fold = 0
    test_start = first_test
    while test_start < len(sessions):
        test_end = min(test_start + test_block_sessions, len(sessions))
        train_sessions = sessions[: test_start - embargo_sessions]
        test_sessions = sessions[test_start:test_end]
        train = clean.loc[clean["session_date"].isin(train_sessions)]
        test = clean.loc[clean["session_date"].isin(test_sessions)]
        restricted = _linear_forecast(train, test, features=own_features, target=target)
        unrestricted = _linear_forecast(
            train, test, features=(*own_features, *cross_features), target=target
        )
        outputs.append(pd.DataFrame({
            "timestamp": test["timestamp"].to_numpy(),
            "session_date": test["session_date"].to_numpy(),
            "actual": test[target].to_numpy(dtype=float),
            "restricted_forecast": restricted,
            "unrestricted_forecast": unrestricted,
            "fold": fold,
        }))
        fold += 1
        test_start = test_end
    return pd.concat(outputs, ignore_index=True)


def nested_forecast_loss_panel(predictions: pd.DataFrame) -> pd.DataFrame:
    """Add paired squared losses and unrestricted improvement to forecasts."""
    required = {"actual", "restricted_forecast", "unrestricted_forecast"}
    missing = sorted(required.difference(predictions.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    result = predictions.copy()
    result["restricted_loss"] = (result["actual"] - result["restricted_forecast"]) ** 2
    result["unrestricted_loss"] = (result["actual"] - result["unrestricted_forecast"]) ** 2
    result["loss_improvement"] = result["restricted_loss"] - result["unrestricted_loss"]
    return result
