"""Leakage-resistant expanding-window splits for Phase II forecasting."""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ForecastFold:
    """Integer positions for one chronological train/test evaluation."""
    train_indices: np.ndarray
    test_indices: np.ndarray


def expanding_window_folds(session_dates: pd.Series, *, minimum_training_sessions: int = 504, test_block_sessions: int = 63, embargo_sessions: int = 1) -> list[ForecastFold]:
    """Create non-overlapping test blocks with a chronological embargo."""
    dates = pd.to_datetime(session_dates, errors="coerce")
    if dates.isna().any() or not dates.is_monotonic_increasing:
        raise ValueError("Session dates must be valid and chronologically ordered")
    if dates.duplicated().any():
        raise ValueError("Session dates must be unique")
    if minimum_training_sessions < 2 or test_block_sessions < 1 or embargo_sessions < 0:
        raise ValueError("Invalid expanding-window parameters")
    folds = []
    test_start = minimum_training_sessions + embargo_sessions
    while test_start < len(dates):
        test_end = min(test_start + test_block_sessions, len(dates))
        train_end = test_start - embargo_sessions
        folds.append(ForecastFold(np.arange(train_end), np.arange(test_start, test_end)))
        test_start = test_end
    if not folds:
        raise ValueError("Sample is too short for one evaluation fold")
    return folds


def assert_development_only(panel: pd.DataFrame, *, holdout_start: str = "2024-05-24") -> None:
    """Reject panels that reach the registered final-holdout boundary."""
    if "session_date" not in panel:
        raise ValueError("Missing required column: session_date")
    dates = pd.to_datetime(panel["session_date"], errors="coerce")
    if dates.isna().any():
        raise ValueError("Session dates must be valid")
    if (dates >= pd.Timestamp(holdout_start)).any():
        raise ValueError("Final holdout access is prohibited")
