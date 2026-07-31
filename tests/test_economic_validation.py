"""Tests for prospective chronological validation boundaries."""

import pandas as pd
import pytest

from src.economic_validation import (
    build_validation_plan,
    minimum_total_sessions_for_design,
)


def test_minimum_includes_final_holdout_reservation() -> None:
    assert minimum_total_sessions_for_design() == 343


def test_minimum_sample_supports_one_nonoverlapping_fold() -> None:
    sessions = pd.date_range("2026-07-30", periods=343, freq="B")

    plan = build_validation_plan(sessions)

    assert len(plan.development_sessions) == 274
    assert len(plan.final_holdout_sessions) == 69
    assert len(plan.folds) == 1
    fold = plan.folds[0]
    assert len(fold.train_sessions) == 252
    assert len(fold.embargo_sessions) == 1
    assert len(fold.test_sessions) == 21
    assert fold.train_sessions[-1] < fold.embargo_sessions[0]
    assert fold.embargo_sessions[-1] < fold.test_sessions[0]
    assert fold.test_sessions[-1] < plan.final_holdout_sessions[0]


def test_expanding_folds_never_train_on_their_test_block() -> None:
    sessions = pd.date_range("2026-07-30", periods=400, freq="B")

    plan = build_validation_plan(sessions)

    assert len(plan.folds) >= 2
    for fold in plan.folds:
        assert set(fold.train_sessions).isdisjoint(fold.embargo_sessions)
        assert set(fold.train_sessions).isdisjoint(fold.test_sessions)
        assert set(fold.test_sessions).isdisjoint(plan.final_holdout_sessions)
    assert len(plan.folds[1].train_sessions) > len(plan.folds[0].train_sessions)


def test_insufficient_sample_is_rejected_before_any_split() -> None:
    sessions = pd.date_range("2026-07-30", periods=342, freq="B")

    with pytest.raises(ValueError, match="At least 343"):
        build_validation_plan(sessions)


def test_invalid_design_parameters_are_rejected() -> None:
    with pytest.raises(ValueError, match="between zero and one"):
        minimum_total_sessions_for_design(final_holdout_fraction=1.0)
    with pytest.raises(ValueError, match="must contain sessions"):
        minimum_total_sessions_for_design(minimum_training_sessions=0)
