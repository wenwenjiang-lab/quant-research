"""Cross-field integrity audit for the prospective Study 03 protocol."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from src.economic_validation import minimum_total_sessions_for_design


def audit_economic_protocol(protocol: Mapping[str, object]) -> tuple[str, ...]:
    """Return deterministic failures for an internally inconsistent protocol.

    The audit is deliberately data-free. It validates preregistration state and
    cross-field arithmetic without reading observations or performance output.
    """
    failures: list[str] = []
    required_sections = {
        "study",
        "research_boundary",
        "sample_eligibility",
        "signal",
        "costs",
        "validation",
        "metrics",
        "decision_rule",
        "interpretation",
    }
    missing = sorted(required_sections.difference(protocol))
    if missing:
        return tuple(f"missing section: {section}" for section in missing)

    study = protocol["study"]
    boundary = protocol["research_boundary"]
    sample = protocol["sample_eligibility"]
    signal = protocol["signal"]
    costs = protocol["costs"]
    validation = protocol["validation"]
    metrics = protocol["metrics"]
    decision = protocol["decision_rule"]
    interpretation = protocol["interpretation"]
    sections = (
        study,
        boundary,
        sample,
        signal,
        costs,
        validation,
        metrics,
        decision,
        interpretation,
    )
    if any(not isinstance(section, Mapping) for section in sections):
        return ("all protocol sections must be mappings",)

    try:
        expected_minimum = minimum_total_sessions_for_design(
            minimum_training_sessions=validation["minimum_training_sessions"],
            embargo_sessions=validation["embargo_sessions"],
            test_block_sessions=validation["test_block_sessions"],
            final_holdout_fraction=validation["final_holdout_fraction"],
        )
    except (KeyError, TypeError, ValueError) as error:
        failures.append(f"invalid validation design: {error}")
    else:
        if sample.get("minimum_new_sessions_before_development") != expected_minimum:
            failures.append(
                "minimum_new_sessions_before_development does not match validation design"
            )

    current = sample.get("current_new_session_count")
    minimum = sample.get("minimum_new_sessions_before_development")
    if not isinstance(current, int) or current < 0:
        failures.append("current_new_session_count must be a nonnegative integer")
    if isinstance(current, int) and isinstance(minimum, int):
        expected_eligibility = current >= minimum
        if sample.get("eligible_to_start") is not expected_eligibility:
            failures.append("eligible_to_start disagrees with the registered sample gate")

    try:
        date.fromisoformat(str(sample["parent_sample_end"]))
    except (KeyError, ValueError):
        failures.append("parent_sample_end must be an ISO calendar date")

    if study.get("status") == "preregistered_not_started":
        if boundary.get("results_available") is not False:
            failures.append("a not-started study cannot report results")
        if interpretation.get("alpha_claim_allowed") is not False:
            failures.append("a not-started study cannot allow an Alpha claim")
        if interpretation.get("trading_strategy_claim_allowed") is not False:
            failures.append("a not-started study cannot allow a strategy claim")

    if signal.get("same_interval_execution_forbidden") is not True:
        failures.append("same-interval execution must remain forbidden")
    latency = signal.get("minimum_latency_bars")
    if not isinstance(latency, int) or latency < 1:
        failures.append("minimum_latency_bars must be at least one")

    required_slippage = decision.get("must_survive_slippage_bps")
    stress_grid = costs.get("one_way_slippage_bps")
    if not isinstance(stress_grid, list) or required_slippage not in stress_grid:
        failures.append("slippage grid must include the decision-rule stress level")
    if metrics.get("primary") != "net_return_after_costs_relative_to_no_trade":
        failures.append("primary metric must remain net of costs and benchmarked")
    if validation.get("single_holdout_evaluation_only") is not True:
        failures.append("final holdout must remain single-use")
    if decision.get("retuning_after_holdout_forbidden") is not True:
        failures.append("post-holdout retuning must remain forbidden")

    return tuple(failures)
