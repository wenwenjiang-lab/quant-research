"""Synthetic tests for the frozen Study 03 evaluation layer."""

from dataclasses import replace

import pandas as pd
import pytest

from src.economic_evaluation import (
    EconomicSummary,
    evaluate_preregistered_rule,
    session_bootstrap_total_ci,
    summarize_economic_performance,
)


def _summary(**overrides) -> EconomicSummary:
    base = EconomicSummary(
        gross_pnl=10.0,
        net_pnl=5.0,
        traded_notional=10_000.0,
        turnover_shares=100.0,
        maximum_drawdown=1.0,
        positive_session_fraction=0.75,
        net_session_sharpe=1.0,
        net_pnl_ci_lower=1.0,
        net_pnl_ci_upper=9.0,
        break_even_one_way_bps=10.0,
        session_count=4,
    )
    return replace(base, **overrides)


def test_session_bootstrap_is_deterministic_and_clustered() -> None:
    pnl = pd.Series([1.0, 2.0, 3.0, 4.0])

    first = session_bootstrap_total_ci(pnl, resamples=500, seed=17)
    second = session_bootstrap_total_ci(pnl, resamples=500, seed=17)

    assert first == second
    assert first[0] < pnl.sum() < first[1]


def test_summary_aggregates_by_session_and_reports_cost_capacity() -> None:
    index = pd.RangeIndex(6)
    pnl = pd.DataFrame(
        {
            "gross_pnl": [1.0, 1.0, -1.0, 2.0, 1.0, 1.0],
            "net_pnl": [0.5, 0.5, -1.5, 1.5, 0.5, 0.5],
            "trade_quantity": [1.0, 0.0, -1.0, 2.0, 0.0, -2.0],
            "traded_notional": [100.0, 0.0, 100.0, 200.0, 0.0, 200.0],
        },
        index=index,
    )
    session = pd.Series(["A", "A", "B", "B", "C", "C"], index=index)

    result = summarize_economic_performance(
        pnl,
        session,
        bootstrap_resamples=500,
        bootstrap_seed=3,
    )

    assert result.gross_pnl == pytest.approx(5.0)
    assert result.net_pnl == pytest.approx(2.0)
    assert result.turnover_shares == pytest.approx(6.0)
    assert result.traded_notional == pytest.approx(600.0)
    assert result.break_even_one_way_bps == pytest.approx(83.3333333333)
    assert result.positive_session_fraction == pytest.approx(2 / 3)
    assert result.session_count == 3


def test_maximum_drawdown_uses_chronological_session_equity() -> None:
    pnl = pd.DataFrame(
        {
            "gross_pnl": [3.0, -5.0, 4.0],
            "net_pnl": [3.0, -5.0, 4.0],
            "trade_quantity": [1.0, 1.0, 1.0],
            "traded_notional": [100.0, 100.0, 100.0],
        }
    )
    session = pd.Series(["A", "B", "C"])

    result = summarize_economic_performance(
        pnl, session, bootstrap_resamples=200
    )

    assert result.maximum_drawdown == pytest.approx(5.0)


def test_decision_rule_requires_every_preregistered_condition() -> None:
    passing = _summary()
    assert evaluate_preregistered_rule(passing, passing).passed

    failures = [
        _summary(net_pnl=0.0),
        _summary(net_pnl_ci_lower=0.0),
        _summary(positive_session_fraction=0.50),
    ]
    for failed_base in failures:
        assert not evaluate_preregistered_rule(failed_base, passing).passed
    assert not evaluate_preregistered_rule(
        passing, _summary(net_pnl=0.0)
    ).passed


def test_evaluation_rejects_misaligned_or_incomplete_inputs() -> None:
    incomplete = pd.DataFrame({"net_pnl": [1.0, 2.0]})
    with pytest.raises(ValueError, match="Missing required"):
        summarize_economic_performance(incomplete, pd.Series(["A", "B"]))

    complete = pd.DataFrame(
        {
            "gross_pnl": [1.0, 2.0],
            "net_pnl": [1.0, 2.0],
            "trade_quantity": [1.0, 1.0],
            "traded_notional": [100.0, 100.0],
        },
        index=[0, 1],
    )
    with pytest.raises(ValueError, match="identical indexes"):
        summarize_economic_performance(
            complete, pd.Series(["A", "B"], index=[1, 2])
        )
