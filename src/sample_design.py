"""Chronological sample assignment that does not inspect outcome values."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChronologicalSplitReport:
    """Metadata for a deterministic development/final-holdout split."""

    eligible_sessions: int
    development_sessions: int
    holdout_sessions: int
    development_end: str
    holdout_start: str


def assign_chronological_samples(
    panel: pd.DataFrame,
    *,
    development_fraction: float = 0.70,
    eligibility_column: str = "complete_outcome_window",
) -> tuple[pd.DataFrame, ChronologicalSplitReport]:
    """Label eligible sessions as development or final holdout by date order."""
    required = {"session_date", eligibility_column}
    missing = sorted(required.difference(panel.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if not 0 < development_fraction < 1:
        raise ValueError("development_fraction must be between zero and one")

    result = panel.copy()
    dates = pd.to_datetime(result["session_date"], errors="coerce")
    if dates.isna().any() or dates.duplicated().any():
        raise ValueError("Session dates must be valid and unique")
    eligible = result[eligibility_column].astype(bool)
    eligible_positions = result.loc[eligible].assign(_date=dates[eligible]).sort_values(
        "_date"
    ).index
    if len(eligible_positions) < 2:
        raise ValueError("At least two eligible sessions are required")

    development_count = int(len(eligible_positions) * development_fraction)
    development_count = min(max(development_count, 1), len(eligible_positions) - 1)
    development_index = eligible_positions[:development_count]
    holdout_index = eligible_positions[development_count:]
    result["sample"] = "excluded"
    result.loc[development_index, "sample"] = "development"
    result.loc[holdout_index, "sample"] = "final_holdout"

    report = ChronologicalSplitReport(
        eligible_sessions=len(eligible_positions),
        development_sessions=len(development_index),
        holdout_sessions=len(holdout_index),
        development_end=str(dates.loc[development_index].max().date()),
        holdout_start=str(dates.loc[holdout_index].min().date()),
    )
    return result, report
