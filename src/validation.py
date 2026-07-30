"""Chronological validation helpers that make time ordering explicit."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class IndexSplit:
    """Half-open integer boundaries for one expanding-window split."""

    train_start: int
    train_end: int
    test_start: int
    test_end: int


def chronological_split(
    frame: pd.DataFrame,
    *,
    timestamp_column: str = "timestamp",
    train_fraction: float = 0.7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a time-ordered frame without shuffling or overlap.

    Timestamps must be valid, unique, and timezone-aware. The function sorts a
    copy chronologically and returns non-empty train and test partitions.
    """
    if timestamp_column not in frame.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_column}")
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be strictly between zero and one")
    if len(frame) < 2:
        raise ValueError("At least two observations are required")

    timestamps = pd.to_datetime(frame[timestamp_column], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("Timestamps must be valid")
    if timestamps.dt.tz is None:
        raise ValueError("Timestamps must be timezone-aware")
    if timestamps.duplicated().any():
        raise ValueError("Timestamps must be unique")

    ordered = frame.assign(**{timestamp_column: timestamps}).sort_values(timestamp_column)
    split_at = int(len(ordered) * train_fraction)
    split_at = min(max(split_at, 1), len(ordered) - 1)
    train = ordered.iloc[:split_at].reset_index(drop=True)
    test = ordered.iloc[split_at:].reset_index(drop=True)
    return train, test


def expanding_window_splits(
    n_observations: int,
    *,
    min_train_size: int,
    test_size: int,
    step_size: int | None = None,
) -> list[IndexSplit]:
    """Build expanding-training, fixed-test window boundaries.

    Each test window begins after every training observation, preventing direct
    train/test overlap. Incomplete final test windows are omitted.
    """
    if n_observations <= 0 or min_train_size <= 0 or test_size <= 0:
        raise ValueError("Sizes must be positive integers")
    step = test_size if step_size is None else step_size
    if step <= 0:
        raise ValueError("step_size must be positive")
    if min_train_size + test_size > n_observations:
        raise ValueError("Not enough observations for one complete split")

    splits: list[IndexSplit] = []
    test_start = min_train_size
    while test_start + test_size <= n_observations:
        splits.append(
            IndexSplit(
                train_start=0,
                train_end=test_start,
                test_start=test_start,
                test_end=test_start + test_size,
            )
        )
        test_start += step
    return splits
