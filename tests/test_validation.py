"""Tests for leakage-resistant chronological validation helpers."""

import pandas as pd
import pytest

from src.validation import IndexSplit, chronological_split, expanding_window_splits


def test_chronological_split_orders_and_separates_data() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2025-01-03 09:30:00-05:00", "2025-01-01 09:30:00-05:00", "2025-01-02 09:30:00-05:00"]
            ),
            "value": [3, 1, 2],
        }
    )

    train, test = chronological_split(frame, train_fraction=2 / 3)

    assert train["value"].tolist() == [1, 2]
    assert test["value"].tolist() == [3]
    assert train["timestamp"].max() < test["timestamp"].min()


def test_chronological_split_rejects_naive_timestamps() -> None:
    frame = pd.DataFrame({"timestamp": pd.to_datetime(["2025-01-01", "2025-01-02"])})

    with pytest.raises(ValueError, match="timezone-aware"):
        chronological_split(frame)


def test_expanding_window_boundaries_do_not_overlap() -> None:
    splits = expanding_window_splits(10, min_train_size=4, test_size=2)

    assert splits == [
        IndexSplit(0, 4, 4, 6),
        IndexSplit(0, 6, 6, 8),
        IndexSplit(0, 8, 8, 10),
    ]
    assert all(split.train_end == split.test_start for split in splits)


def test_expanding_window_requires_complete_split() -> None:
    with pytest.raises(ValueError, match="Not enough observations"):
        expanding_window_splits(5, min_train_size=4, test_size=2)
