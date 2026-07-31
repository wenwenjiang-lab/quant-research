"""Point-in-time execution and cost primitives for prospective Study 03.

These functions operate on synthetic or user-supplied inputs. They do not
contain market observations, a fitted signal, or an empirical result.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExecutionCosts:
    """Prespecified one-way implementation-cost assumptions."""

    commission_per_share_usd: float = 0.005
    minimum_commission_per_order_usd: float = 1.0
    spread_bps: float = 0.0
    slippage_bps: float = 1.0

    def __post_init__(self) -> None:
        values = (
            self.commission_per_share_usd,
            self.minimum_commission_per_order_usd,
            self.spread_bps,
            self.slippage_bps,
        )
        if not all(np.isfinite(value) and value >= 0 for value in values):
            raise ValueError("Execution-cost assumptions must be finite and nonnegative")


@dataclass(frozen=True)
class SampleEligibility:
    """Date-only audit result for a prospective protected sample."""

    eligible: bool
    parent_sample_end: date
    first_new_session: date | None
    last_new_session: date | None
    new_session_count: int
    minimum_required_sessions: int
    reason: str


def assess_new_sample_eligibility(
    sessions: pd.Series | pd.Index,
    *,
    parent_sample_end: str | date | pd.Timestamp,
    minimum_required_sessions: int,
) -> SampleEligibility:
    """Audit whether dates form a genuinely new protected sample.

    Only session labels are examined; prices, forecasts, returns, and outcomes
    are never accessed. Sessions on or before ``parent_sample_end`` are treated
    as previously exposed and cannot qualify for Study 03.
    """
    if not isinstance(minimum_required_sessions, int) or minimum_required_sessions < 1:
        raise ValueError("minimum_required_sessions must be a positive integer")

    cutoff = pd.Timestamp(parent_sample_end)
    if pd.isna(cutoff):
        raise ValueError("parent_sample_end must be a valid date")
    if cutoff.tzinfo is not None:
        cutoff = cutoff.tz_localize(None)
    cutoff = cutoff.normalize()

    labels = pd.Series(pd.Index(sessions), dtype="string").str.slice(0, 10)
    parsed_series = pd.to_datetime(labels, format="%Y-%m-%d", errors="coerce")
    if parsed_series.isna().any():
        raise ValueError("Session labels must all be valid dates")
    unique_sessions = (
        pd.DatetimeIndex(parsed_series).normalize().unique().sort_values()
    )
    new_sessions = unique_sessions[unique_sessions > cutoff]
    count = len(new_sessions)
    eligible = count >= minimum_required_sessions
    reason = (
        "new protected sample meets the prespecified session minimum"
        if eligible
        else "insufficient sessions strictly after the completed parent sample"
    )
    return SampleEligibility(
        eligible=eligible,
        parent_sample_end=cutoff.date(),
        first_new_session=new_sessions[0].date() if count else None,
        last_new_session=new_sessions[-1].date() if count else None,
        new_session_count=count,
        minimum_required_sessions=minimum_required_sessions,
        reason=reason,
    )


def audit_session_csv(
    path: str | Path,
    *,
    session_column: str = "session_date",
    parent_sample_end: str | date | pd.Timestamp = "2026-07-29",
    minimum_required_sessions: int = 343,
) -> SampleEligibility:
    """Audit a local panel while loading only its session-date column."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Session source does not exist: {source}")
    try:
        session_frame = pd.read_csv(source, usecols=[session_column])
    except ValueError as exc:
        raise ValueError(
            f"Required session column {session_column!r} is missing"
        ) from exc
    return assess_new_sample_eligibility(
        session_frame[session_column],
        parent_sample_end=parent_sample_end,
        minimum_required_sessions=minimum_required_sessions,
    )


def write_eligibility_report(
    audit: SampleEligibility,
    destination: str | Path,
) -> Path:
    """Write a date-only readiness report without market observations."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "eligible": audit.eligible,
        "parent_sample_end": audit.parent_sample_end.isoformat(),
        "first_new_session": (
            audit.first_new_session.isoformat() if audit.first_new_session else None
        ),
        "last_new_session": (
            audit.last_new_session.isoformat() if audit.last_new_session else None
        ),
        "new_session_count": audit.new_session_count,
        "minimum_required_sessions": audit.minimum_required_sessions,
        "remaining_sessions": max(
            audit.minimum_required_sessions - audit.new_session_count,
            0,
        ),
        "reason": audit.reason,
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target


def _aligned_frame(
    *,
    signal: pd.Series | None = None,
    position: pd.Series | None = None,
    price: pd.Series | None = None,
    session: pd.Series,
) -> pd.DataFrame:
    """Return validated, index-aligned inputs without silently reindexing."""
    series = {"session": session}
    if signal is not None:
        series["signal"] = signal
    if position is not None:
        series["position"] = position
    if price is not None:
        series["price"] = price

    reference = session.index
    if not reference.is_unique:
        raise ValueError("Input index must be unique")
    if any(not item.index.equals(reference) for item in series.values()):
        raise ValueError("Inputs must have identical indexes")
    frame = pd.DataFrame(series)
    if frame["session"].isna().any():
        raise ValueError("Session labels cannot be missing")
    return frame


def delayed_intraday_positions(
    signal: pd.Series,
    session: pd.Series,
    *,
    threshold: float = 0.0,
    minimum_latency_bars: int = 1,
) -> pd.Series:
    """Convert forecasts to delayed, session-flat positions.

    A signal observed in bar ``t`` cannot affect the position until at least
    ``minimum_latency_bars`` later. Shifts never cross a session boundary, and
    the last observed bar of every session is forced flat.
    """
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    if not isinstance(minimum_latency_bars, int) or minimum_latency_bars < 1:
        raise ValueError("minimum_latency_bars must be a positive integer")

    frame = _aligned_frame(signal=signal, session=session)
    numeric = pd.to_numeric(frame["signal"], errors="coerce")
    desired = pd.Series(
        np.where(numeric.abs() > threshold, np.sign(numeric), 0.0),
        index=frame.index,
        dtype=float,
        name="position",
    )
    delayed = desired.groupby(frame["session"], sort=False).shift(
        minimum_latency_bars
    )
    delayed = delayed.fillna(0.0)
    last_rows = frame.groupby("session", sort=False).tail(1).index
    delayed.loc[last_rows] = 0.0
    return delayed.rename("position")


def cost_aware_pnl(
    position: pd.Series,
    execution_price: pd.Series,
    session: pd.Series,
    *,
    costs: ExecutionCosts | None = None,
) -> pd.DataFrame:
    """Calculate gross and net P&L for an already delayed share position.

    Positions are interpreted as shares established at each row's execution
    price. P&L for a price change is therefore earned by the prior row's
    position. Trading costs are charged when the position changes.
    """
    assumptions = costs or ExecutionCosts()
    frame = _aligned_frame(
        position=position,
        price=execution_price,
        session=session,
    )
    frame["position"] = pd.to_numeric(frame["position"], errors="coerce")
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    if not np.isfinite(frame[["position", "price"]].to_numpy(dtype=float)).all():
        raise ValueError("Position and execution price must be finite")
    if (frame["price"] <= 0).any():
        raise ValueError("Execution prices must be positive")

    grouped_position = frame["position"].groupby(frame["session"], sort=False)
    grouped_price = frame["price"].groupby(frame["session"], sort=False)
    prior_position = grouped_position.shift(1).fillna(0.0)
    price_change = grouped_price.diff().fillna(0.0)
    trade_quantity = grouped_position.diff().fillna(frame["position"])
    traded_shares = trade_quantity.abs()
    active_trade = traded_shares > 0

    commission = pd.Series(0.0, index=frame.index)
    commission.loc[active_trade] = np.maximum(
        traded_shares.loc[active_trade] * assumptions.commission_per_share_usd,
        assumptions.minimum_commission_per_order_usd,
    )
    traded_notional = traded_shares * frame["price"]
    spread_cost = traded_notional * assumptions.spread_bps / 10_000.0
    slippage_cost = traded_notional * assumptions.slippage_bps / 10_000.0
    total_cost = commission + spread_cost + slippage_cost
    gross_pnl = prior_position * price_change

    return pd.DataFrame(
        {
            "position": frame["position"],
            "trade_quantity": trade_quantity,
            "traded_notional": traded_notional,
            "gross_pnl": gross_pnl,
            "commission": commission,
            "spread_cost": spread_cost,
            "slippage_cost": slippage_cost,
            "total_cost": total_cost,
            "net_pnl": gross_pnl - total_cost,
        },
        index=frame.index,
    )
