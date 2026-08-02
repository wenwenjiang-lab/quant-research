"""Data-lineage checks linking source exceptions to analytical exclusions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pandas as pd


@dataclass(frozen=True)
class GapExclusionAudit:
    """Evidence that source sessions with intraday gaps cannot enter analysis."""

    gap_event_count: int
    gap_session_count: int
    analytical_session_count: int
    overlapping_session_count: int
    overlapping_sessions: tuple[str, ...]
    passed: bool


def audit_intraday_gap_exclusions(
    panel: pd.DataFrame,
    diagnostics: Mapping[str, Any],
    *,
    session_column: str = "session_date",
) -> GapExclusionAudit:
    """Compare source gap dates with the exact analytical-session list.

    The check is date-only: it does not inspect prices, outcomes, forecasts, or
    holdout results. A pass requires zero overlap between any session containing
    a recorded intraday gap and the supplied panel.
    """
    if session_column not in panel.columns:
        raise ValueError(f"Missing session column: {session_column}")
    events = diagnostics.get("intraday_gaps")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise ValueError("diagnostics.intraday_gaps must be a sequence")
    declared_count = diagnostics.get("intraday_gap_count")
    if declared_count != len(events):
        raise ValueError("Declared intraday_gap_count does not match event list")

    gap_dates: set[str] = set()
    for event in events:
        if not isinstance(event, Mapping) or "session_date" not in event:
            raise ValueError("Each intraday-gap event requires session_date")
        parsed = pd.to_datetime(event["session_date"], errors="raise")
        gap_dates.add(str(parsed.date()))

    sessions = pd.to_datetime(panel[session_column], errors="raise")
    if sessions.isna().any():
        raise ValueError("Analytical session dates cannot be missing")
    analytical_dates = {str(value.date()) for value in sessions}
    overlap = tuple(sorted(gap_dates.intersection(analytical_dates)))
    return GapExclusionAudit(
        gap_event_count=len(events),
        gap_session_count=len(gap_dates),
        analytical_session_count=len(analytical_dates),
        overlapping_session_count=len(overlap),
        overlapping_sessions=overlap,
        passed=not overlap,
    )
