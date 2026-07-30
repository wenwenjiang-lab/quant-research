"""Construct a session-level opening-range research panel without look-ahead."""

from dataclasses import dataclass
from datetime import time

import pandas as pd

from .opening_range import calculate_opening_range


@dataclass(frozen=True)
class OpeningRangeStudySpec:
    """Frozen clock-time definitions for one opening-range specification."""

    opening_start: time = time(9, 30)
    opening_end: time = time(10, 0)
    outcome_end: time = time(16, 0)
    timezone: str = "America/New_York"
    expected_opening_bars: int = 30
    expected_outcome_bars: int = 360


@dataclass(frozen=True)
class SessionScreeningReport:
    """Counts from deterministic session-level eligibility screening."""

    observed_sessions: int
    eligible_sessions: int
    excluded_incomplete_opening: int
    excluded_missing_outcome: int
    incomplete_outcome_sessions: int


def build_opening_range_panel(
    bars: pd.DataFrame,
    *,
    spec: OpeningRangeStudySpec = OpeningRangeStudySpec(),
) -> pd.DataFrame:
    """Return one deterministic feature/outcome row per eligible session.

    Opening-range features use only bars in ``[opening_start, opening_end)``.
    Outcomes use bars in ``[opening_end, outcome_end)``. A session with missing
    opening bars is rejected rather than silently included.
    """
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if not (spec.opening_start < spec.opening_end < spec.outcome_end):
        raise ValueError("Study clock times must be strictly increasing")

    timestamps = pd.to_datetime(bars["timestamp"], errors="coerce")
    if timestamps.isna().any() or timestamps.dt.tz is None:
        raise ValueError("Timestamps must be valid and timezone-aware")

    localized = bars.copy()
    localized["timestamp"] = timestamps.dt.tz_convert(spec.timezone)
    localized["session_date"] = localized["timestamp"].dt.date
    rows: list[dict[str, object]] = []

    for session_date, session in localized.groupby("session_date", sort=True):
        session = session.sort_values("timestamp").reset_index(drop=True)
        opening = calculate_opening_range(
            session,
            start=spec.opening_start,
            end=spec.opening_end,
        )
        if opening.bar_count != spec.expected_opening_bars:
            raise ValueError(
                f"Session {session_date} has {opening.bar_count} opening bars; "
                f"expected {spec.expected_opening_bars}"
            )

        clock = session["timestamp"].dt.time
        outcome = session.loc[
            (clock >= spec.opening_end) & (clock < spec.outcome_end)
        ].copy()
        if outcome.empty:
            raise ValueError(f"Session {session_date} has no outcome bars")

        first_outcome_open = float(outcome.iloc[0]["open"])
        session_close = float(outcome.iloc[-1]["close"])
        session_open = float(session.iloc[0]["open"])
        session_range_bps = (
            (float(session["high"].max()) - float(session["low"].min()))
            / session_open
            * 10_000.0
        )
        opening_width_bps = opening.width / opening.midpoint * 10_000.0
        post_opening_return_bps = (
            (session_close - first_outcome_open) / first_outcome_open * 10_000.0
        )
        first_break = "none"
        first_break_time = pd.NaT
        for bar in outcome.itertuples(index=False):
            breaks_high = float(bar.high) > opening.high
            breaks_low = float(bar.low) < opening.low
            if breaks_high or breaks_low:
                first_break = (
                    "both" if breaks_high and breaks_low else "up" if breaks_high else "down"
                )
                first_break_time = bar.timestamp
                break

        rows.append(
            {
                "session_date": session_date,
                "opening_range_high": opening.high,
                "opening_range_low": opening.low,
                "opening_range_midpoint": opening.midpoint,
                "opening_range_width_points": opening.width,
                "opening_range_width_bps": opening_width_bps,
                "opening_range_bar_count": opening.bar_count,
                "post_opening_start_price": first_outcome_open,
                "session_open": session_open,
                "session_close": session_close,
                "session_range_bps": session_range_bps,
                "outcome_bar_count": len(outcome),
                "complete_outcome_window": len(outcome) == spec.expected_outcome_bars,
                "post_opening_return_points": session_close - first_outcome_open,
                "post_opening_return_bps": post_opening_return_bps,
                "post_opening_abs_return_bps": abs(post_opening_return_bps),
                "post_opening_realized_range_bps": (
                    (float(outcome["high"].max()) - float(outcome["low"].min()))
                    / first_outcome_open
                    * 10_000.0
                ),
                "post_opening_max_up_points": float(outcome["high"].max()) - first_outcome_open,
                "post_opening_max_down_points": float(outcome["low"].min()) - first_outcome_open,
                "first_break_direction": first_break,
                "first_break_timestamp": first_break_time,
            }
        )

    return pd.DataFrame(rows)


def build_screened_opening_range_panel(
    bars: pd.DataFrame,
    *,
    spec: OpeningRangeStudySpec = OpeningRangeStudySpec(),
) -> tuple[pd.DataFrame, SessionScreeningReport]:
    """Screen sessions, build the panel, and return explicit exclusion counts.

    Sessions missing any prespecified opening bar or all outcome bars are
    excluded before feature construction. Shortened outcome windows remain in
    the panel with ``complete_outcome_window=False`` so later analyses can apply
    the frozen protocol without losing the audit trail.
    """
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required.difference(bars.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    timestamps = pd.to_datetime(bars["timestamp"], errors="coerce")
    if timestamps.isna().any() or timestamps.dt.tz is None:
        raise ValueError("Timestamps must be valid and timezone-aware")
    localized = bars.copy()
    localized["timestamp"] = timestamps.dt.tz_convert(spec.timezone)
    localized["session_date"] = localized["timestamp"].dt.date
    clock = localized["timestamp"].dt.time
    localized["is_opening"] = (clock >= spec.opening_start) & (
        clock < spec.opening_end
    )
    localized["is_outcome"] = (clock >= spec.opening_end) & (
        clock < spec.outcome_end
    )

    counts = localized.groupby("session_date", sort=True)[
        ["is_opening", "is_outcome"]
    ].sum()
    complete_opening = counts["is_opening"] == spec.expected_opening_bars
    has_outcome = counts["is_outcome"] > 0
    eligible_dates = counts.index[complete_opening & has_outcome]
    screened = localized.loc[localized["session_date"].isin(eligible_dates)].drop(
        columns=["session_date", "is_opening", "is_outcome"]
    )
    panel = build_opening_range_panel(screened, spec=spec)

    report = SessionScreeningReport(
        observed_sessions=len(counts),
        eligible_sessions=len(eligible_dates),
        excluded_incomplete_opening=int((~complete_opening).sum()),
        excluded_missing_outcome=int((complete_opening & ~has_outcome).sum()),
        incomplete_outcome_sessions=int((~panel["complete_outcome_window"]).sum()),
    )
    return panel, report
