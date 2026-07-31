"""Chronological validation plan for prospective Study 03."""

from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class WalkForwardFold:
    """One expanding-window fold with an explicit session embargo."""

    train_sessions: tuple[pd.Timestamp, ...]
    embargo_sessions: tuple[pd.Timestamp, ...]
    test_sessions: tuple[pd.Timestamp, ...]


@dataclass(frozen=True)
class ValidationPlan:
    """Development folds plus a permanently separate final holdout."""

    development_sessions: tuple[pd.Timestamp, ...]
    final_holdout_sessions: tuple[pd.Timestamp, ...]
    folds: tuple[WalkForwardFold, ...]


def minimum_total_sessions_for_design(
    *,
    minimum_training_sessions: int = 252,
    embargo_sessions: int = 1,
    test_block_sessions: int = 21,
    final_holdout_fraction: float = 0.20,
) -> int:
    """Return the smallest sample supporting one fold and the final holdout."""
    integer_values = (
        minimum_training_sessions,
        embargo_sessions,
        test_block_sessions,
    )
    if any(not isinstance(value, int) or value < 0 for value in integer_values):
        raise ValueError("Session counts must be nonnegative integers")
    if minimum_training_sessions < 1 or test_block_sessions < 1:
        raise ValueError("Training and test blocks must contain sessions")
    if not 0 < final_holdout_fraction < 1:
        raise ValueError("final_holdout_fraction must lie between zero and one")

    development_required = sum(integer_values)
    total = development_required
    while total - math.ceil(total * final_holdout_fraction) < development_required:
        total += 1
    return total


def build_validation_plan(
    sessions: pd.Series | pd.Index,
    *,
    minimum_training_sessions: int = 252,
    embargo_sessions: int = 1,
    test_block_sessions: int = 21,
    final_holdout_fraction: float = 0.20,
) -> ValidationPlan:
    """Build expanding chronological folds without exposing outcome columns."""
    labels = pd.Series(pd.Index(sessions), dtype="string").str.slice(0, 10)
    parsed = pd.to_datetime(labels, format="%Y-%m-%d", errors="coerce")
    if parsed.isna().any():
        raise ValueError("Session labels must all be valid dates")
    ordered = tuple(pd.DatetimeIndex(parsed).normalize().unique().sort_values())
    required = minimum_total_sessions_for_design(
        minimum_training_sessions=minimum_training_sessions,
        embargo_sessions=embargo_sessions,
        test_block_sessions=test_block_sessions,
        final_holdout_fraction=final_holdout_fraction,
    )
    if len(ordered) < required:
        raise ValueError(f"At least {required} distinct sessions are required")

    holdout_count = math.ceil(len(ordered) * final_holdout_fraction)
    development = ordered[:-holdout_count]
    holdout = ordered[-holdout_count:]
    folds: list[WalkForwardFold] = []
    test_start = minimum_training_sessions + embargo_sessions
    while test_start + test_block_sessions <= len(development):
        embargo_start = test_start - embargo_sessions
        folds.append(
            WalkForwardFold(
                train_sessions=development[:embargo_start],
                embargo_sessions=development[embargo_start:test_start],
                test_sessions=development[
                    test_start : test_start + test_block_sessions
                ],
            )
        )
        test_start += test_block_sessions
    return ValidationPlan(
        development_sessions=development,
        final_holdout_sessions=holdout,
        folds=tuple(folds),
    )
