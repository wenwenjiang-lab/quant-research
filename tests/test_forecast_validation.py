import numpy as np
import pandas as pd
import pytest
from src.forecast_validation import assert_development_only, expanding_window_folds


def test_expanding_folds_are_chronological_and_embargoed() -> None:
    dates = pd.Series(pd.bdate_range("2019-01-01", periods=800))
    folds = expanding_window_folds(dates)
    assert len(folds) == 5
    for fold in folds:
        assert fold.train_indices.max() + 1 < fold.test_indices.min()
        assert np.intersect1d(fold.train_indices, fold.test_indices).size == 0


def test_folds_reject_shuffle_and_duplicate_dates() -> None:
    shuffled = pd.Series(pd.to_datetime(["2023-01-03", "2023-01-02", "2023-01-04"]))
    duplicated = pd.Series(pd.to_datetime(["2023-01-02", "2023-01-02", "2023-01-03"]))
    with pytest.raises(ValueError, match="chronologically ordered"):
        expanding_window_folds(shuffled, minimum_training_sessions=2)
    with pytest.raises(ValueError, match="unique"):
        expanding_window_folds(duplicated, minimum_training_sessions=2)


def test_holdout_guard_accepts_development_and_rejects_boundary() -> None:
    assert_development_only(pd.DataFrame({"session_date": ["2024-05-22", "2024-05-23"]}))
    with pytest.raises(ValueError, match="Final holdout access is prohibited"):
        assert_development_only(pd.DataFrame({"session_date": ["2024-05-23", "2024-05-24"]}))
