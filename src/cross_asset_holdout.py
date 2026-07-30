"""Single-use final-holdout evaluation with explicit execution safeguards."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from .cross_asset_models import _linear_forecast


EXECUTION_PHRASE = "CONFIRM_SINGLE_HOLDOUT_EVALUATION"


def sealed_holdout_predictions(
    panel: pd.DataFrame,
    *,
    target: str,
    own_lag_features: Sequence[str],
    cross_lag_features: Sequence[str],
    holdout_start: str | pd.Timestamp,
    expected_holdout_sessions: int,
    embargo_sessions: int = 1,
    execution_allowed: bool = False,
    execution_phrase: str = "",
) -> pd.DataFrame:
    """Fit once on development data and predict the complete sealed holdout.

    This function intentionally requires both a configuration-level boolean
    and an exact execution phrase. It performs no tuning and returns paired
    forecasts only after validating the frozen boundary and session count.
    """
    if not execution_allowed or execution_phrase != EXECUTION_PHRASE:
        raise PermissionError("Final holdout evaluation is sealed")
    own_features = tuple(own_lag_features)
    cross_features = tuple(cross_lag_features)
    if not own_features or not cross_features:
        raise ValueError("Both own-lag and cross-lag features are required")
    if set(own_features).intersection(cross_features):
        raise ValueError("Own-lag and cross-lag feature sets must be disjoint")
    if expected_holdout_sessions < 1 or embargo_sessions < 0:
        raise ValueError("Invalid holdout parameters")

    required = {"timestamp", "session_date", target, *own_features, *cross_features}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    clean = panel.loc[:, ["timestamp", "session_date", target, *own_features, *cross_features]].copy()
    clean["timestamp"] = pd.to_datetime(clean["timestamp"], errors="coerce", utc=True).dt.tz_convert(
        "America/New_York"
    )
    if clean["session_date"].dtype == object:
        session_dates = pd.to_datetime(
            clean["session_date"].astype(str).str.slice(0, 10), errors="coerce"
        ).dt.tz_localize("America/New_York")
    else:
        session_dates = pd.to_datetime(clean["session_date"], errors="coerce")
    clean["session_date"] = session_dates
    if clean[["timestamp", "session_date"]].isna().any().any():
        raise ValueError("Timestamps and session dates must be valid")
    if not clean["timestamp"].is_monotonic_increasing or clean["timestamp"].duplicated().any():
        raise ValueError("Panel timestamps must be ordered and unique")

    boundary = pd.Timestamp(holdout_start)
    session_tz = clean["session_date"].dt.tz
    boundary = boundary.tz_localize(session_tz) if boundary.tzinfo is None else boundary.tz_convert(session_tz)
    boundary = boundary.normalize()
    numeric = [target, *own_features, *cross_features]
    clean[numeric] = clean[numeric].apply(pd.to_numeric, errors="coerce")
    clean = clean.replace([np.inf, -np.inf], np.nan).dropna(subset=numeric)

    development = clean.loc[clean["session_date"] < boundary]
    holdout = clean.loc[clean["session_date"] >= boundary]
    development_sessions = pd.Index(development["session_date"].drop_duplicates())
    holdout_sessions = pd.Index(holdout["session_date"].drop_duplicates())
    if len(holdout_sessions) != expected_holdout_sessions:
        raise ValueError(
            f"Expected {expected_holdout_sessions} holdout sessions; found {len(holdout_sessions)}"
        )
    if len(development_sessions) <= embargo_sessions:
        raise ValueError("Insufficient development sessions before embargo")
    training_sessions = development_sessions[: len(development_sessions) - embargo_sessions]
    train = development.loc[development["session_date"].isin(training_sessions)]

    restricted = _linear_forecast(train, holdout, features=own_features, target=target)
    unrestricted = _linear_forecast(
        train, holdout, features=(*own_features, *cross_features), target=target
    )
    return pd.DataFrame({
        "timestamp": holdout["timestamp"].to_numpy(),
        "session_date": holdout["session_date"].to_numpy(),
        "actual": holdout[target].to_numpy(dtype=float),
        "restricted_forecast": restricted,
        "unrestricted_forecast": unrestricted,
    })
