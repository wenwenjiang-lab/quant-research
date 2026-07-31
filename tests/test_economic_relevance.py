"""Synthetic tests for prospective Study 03 execution primitives."""

import pandas as pd
import pytest

from src.economic_relevance import (
    ExecutionCosts,
    assess_new_sample_eligibility,
    cost_aware_pnl,
    delayed_intraday_positions,
)


def test_completed_parent_dates_cannot_be_reused_as_new_sample() -> None:
    sessions = pd.Index(["2026-07-28", "2026-07-29"])

    audit = assess_new_sample_eligibility(
        sessions,
        parent_sample_end="2026-07-29",
        minimum_required_sessions=2,
    )

    assert not audit.eligible
    assert audit.new_session_count == 0
    assert audit.first_new_session is None


def test_only_dates_strictly_after_parent_sample_are_counted() -> None:
    sessions = pd.Series(
        ["2026-07-29", "2026-07-30", "2026-07-30", "2026-07-31"]
    )

    audit = assess_new_sample_eligibility(
        sessions,
        parent_sample_end="2026-07-29",
        minimum_required_sessions=2,
    )

    assert audit.eligible
    assert audit.new_session_count == 2
    assert audit.first_new_session.isoformat() == "2026-07-30"
    assert audit.last_new_session.isoformat() == "2026-07-31"


def test_sample_gate_rejects_invalid_session_labels() -> None:
    with pytest.raises(ValueError, match="valid dates"):
        assess_new_sample_eligibility(
            pd.Index(["2026-07-30", "not-a-date"]),
            parent_sample_end="2026-07-29",
            minimum_required_sessions=1,
        )


def test_signal_is_delayed_and_each_session_finishes_flat() -> None:
    index = pd.date_range("2025-01-02 09:30", periods=6, freq="min")
    signal = pd.Series([1.0, -1.0, 1.0, -1.0, 1.0, 1.0], index=index)
    session = pd.Series(["A", "A", "A", "B", "B", "B"], index=index)

    position = delayed_intraday_positions(signal, session)

    assert position.tolist() == [0.0, 1.0, 0.0, 0.0, -1.0, 0.0]


def test_threshold_and_latency_are_applied_before_execution() -> None:
    index = pd.RangeIndex(5)
    signal = pd.Series([0.1, 0.8, -0.9, 0.7, 1.0], index=index)
    session = pd.Series("A", index=index)

    position = delayed_intraday_positions(
        signal,
        session,
        threshold=0.5,
        minimum_latency_bars=2,
    )

    assert position.tolist() == [0.0, 0.0, 0.0, 1.0, 0.0]


def test_costs_are_charged_only_when_share_position_changes() -> None:
    index = pd.RangeIndex(4)
    position = pd.Series([0.0, 10.0, 10.0, 0.0], index=index)
    price = pd.Series([100.0, 100.0, 101.0, 101.0], index=index)
    session = pd.Series("A", index=index)
    assumptions = ExecutionCosts(
        commission_per_share_usd=0.01,
        minimum_commission_per_order_usd=1.0,
        spread_bps=1.0,
        slippage_bps=2.0,
    )

    result = cost_aware_pnl(position, price, session, costs=assumptions)

    assert result["trade_quantity"].tolist() == [0.0, 10.0, 0.0, -10.0]
    assert result["commission"].tolist() == [0.0, 1.0, 0.0, 1.0]
    assert result.loc[1, "total_cost"] == pytest.approx(1.30)
    assert result.loc[3, "total_cost"] == pytest.approx(1.303)
    assert result["gross_pnl"].sum() == pytest.approx(10.0)
    assert result["net_pnl"].sum() == pytest.approx(7.397)


def test_position_cannot_profit_from_price_change_before_it_exists() -> None:
    index = pd.RangeIndex(3)
    position = pd.Series([0.0, 1.0, 0.0], index=index)
    price = pd.Series([100.0, 110.0, 111.0], index=index)
    session = pd.Series("A", index=index)

    result = cost_aware_pnl(
        position,
        price,
        session,
        costs=ExecutionCosts(
            commission_per_share_usd=0.0,
            minimum_commission_per_order_usd=0.0,
            slippage_bps=0.0,
        ),
    )

    assert result["gross_pnl"].tolist() == [0.0, 0.0, 1.0]


def test_misaligned_inputs_are_rejected_instead_of_reindexed() -> None:
    with pytest.raises(ValueError, match="identical indexes"):
        cost_aware_pnl(
            pd.Series([0.0, 1.0], index=[0, 1]),
            pd.Series([100.0, 101.0], index=[1, 2]),
            pd.Series(["A", "A"], index=[0, 1]),
        )


def test_invalid_cost_assumption_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        ExecutionCosts(slippage_bps=-1.0)
