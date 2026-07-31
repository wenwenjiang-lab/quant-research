"""Integrity checks for the prospective economic-relevance study."""

from pathlib import Path
import tomllib


def _protocol() -> dict:
    path = Path(__file__).resolve().parents[1] / "configs" / "economic_relevance.toml"
    with path.open("rb") as file:
        return tomllib.load(file)


def test_protocol_is_prospective_and_does_not_reopen_parent_holdout() -> None:
    protocol = _protocol()

    assert protocol["study"]["status"] == "preregistered_not_started"
    assert protocol["research_boundary"]["results_available"] is False
    assert protocol["research_boundary"]["new_evaluation_sample_required"] is True
    assert (
        protocol["research_boundary"]["completed_parent_holdout_must_not_be_reused"]
        is True
    )


def test_protocol_forbids_same_interval_execution_and_repeat_evaluation() -> None:
    protocol = _protocol()

    assert protocol["signal"]["same_interval_execution_forbidden"] is True
    assert protocol["signal"]["minimum_latency_bars"] >= 1
    assert protocol["validation"]["single_holdout_evaluation_only"] is True
    assert protocol["decision_rule"]["retuning_after_holdout_forbidden"] is True


def test_protocol_requires_cost_aware_confirmation() -> None:
    protocol = _protocol()

    assert protocol["metrics"]["primary"] == "net_return_after_costs_relative_to_no_trade"
    assert protocol["metrics"]["report_gross_and_net_results"] is True
    assert protocol["metrics"]["report_cost_break_even"] is True
    assert protocol["decision_rule"]["must_survive_slippage_bps"] >= 1.0
    assert protocol["decision_rule"]["failure_is_publishable"] is True
