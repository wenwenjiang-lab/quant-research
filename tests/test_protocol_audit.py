"""Tests for Study 03 cross-field protocol integrity."""

from copy import deepcopy
from pathlib import Path
import tomllib

from src.protocol_audit import audit_economic_protocol


def _protocol() -> dict:
    path = Path(__file__).resolve().parents[1] / "configs" / "economic_relevance.toml"
    with path.open("rb") as file:
        return tomllib.load(file)


def test_registered_protocol_is_internally_consistent() -> None:
    assert audit_economic_protocol(_protocol()) == ()


def test_changed_validation_design_requires_a_new_sample_minimum() -> None:
    protocol = deepcopy(_protocol())
    protocol["validation"]["test_block_sessions"] = 42

    assert audit_economic_protocol(protocol) == (
        "minimum_new_sessions_before_development does not match validation design",
    )


def test_readiness_flag_cannot_disagree_with_sample_count() -> None:
    protocol = deepcopy(_protocol())
    protocol["sample_eligibility"]["eligible_to_start"] = True

    assert "eligible_to_start disagrees with the registered sample gate" in (
        audit_economic_protocol(protocol)
    )


def test_required_slippage_must_exist_in_stress_grid() -> None:
    protocol = deepcopy(_protocol())
    protocol["costs"]["one_way_slippage_bps"] = [0.5, 2.0]

    assert audit_economic_protocol(protocol) == (
        "slippage grid must include the decision-rule stress level",
    )


def test_not_started_study_cannot_expose_results_or_claims() -> None:
    protocol = deepcopy(_protocol())
    protocol["research_boundary"]["results_available"] = True
    protocol["interpretation"]["alpha_claim_allowed"] = True

    failures = audit_economic_protocol(protocol)

    assert "a not-started study cannot report results" in failures
    assert "a not-started study cannot allow an Alpha claim" in failures
