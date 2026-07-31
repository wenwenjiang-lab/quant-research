"""Fail-closed preflight gate for prospective Study 03 development."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

from src.economic_relevance import SampleEligibility, assess_new_sample_eligibility
from src.economic_validation import ValidationPlan, build_validation_plan
from src.protocol_audit import audit_economic_protocol


@dataclass(frozen=True)
class Study03Preflight:
    """Outcome-blind decision on whether empirical development may begin."""

    ready: bool
    protocol_failures: tuple[str, ...]
    eligibility: SampleEligibility | None
    validation_plan: ValidationPlan | None
    reason: str


def run_study03_preflight(
    protocol: Mapping[str, object],
    sessions: pd.Series | pd.Index,
) -> Study03Preflight:
    """Require protocol, date registry, and split design to agree exactly.

    Only session labels are inspected. Market values, forecasts, returns, and
    outcome columns are neither accepted nor accessed by this interface.
    """
    failures = audit_economic_protocol(protocol)
    if failures:
        return Study03Preflight(
            ready=False,
            protocol_failures=failures,
            eligibility=None,
            validation_plan=None,
            reason="protocol integrity audit failed",
        )

    sample = protocol["sample_eligibility"]
    validation = protocol["validation"]
    if not isinstance(sample, Mapping) or not isinstance(validation, Mapping):
        raise TypeError("Audited protocol sections must be mappings")

    eligibility = assess_new_sample_eligibility(
        sessions,
        parent_sample_end=sample["parent_sample_end"],
        minimum_required_sessions=sample[
            "minimum_new_sessions_before_development"
        ],
    )
    registered_count = sample["current_new_session_count"]
    if eligibility.new_session_count != registered_count:
        return Study03Preflight(
            ready=False,
            protocol_failures=(),
            eligibility=eligibility,
            validation_plan=None,
            reason="registered session count does not match supplied session dates",
        )
    if not eligibility.eligible:
        return Study03Preflight(
            ready=False,
            protocol_failures=(),
            eligibility=eligibility,
            validation_plan=None,
            reason=eligibility.reason,
        )

    cutoff = pd.Timestamp(sample["parent_sample_end"]).normalize()
    labels = pd.Series(pd.Index(sessions), dtype="string").str.slice(0, 10)
    parsed = pd.to_datetime(labels, format="%Y-%m-%d", errors="raise")
    new_sessions = parsed.loc[parsed > cutoff]
    plan = build_validation_plan(
        new_sessions,
        minimum_training_sessions=validation["minimum_training_sessions"],
        embargo_sessions=validation["embargo_sessions"],
        test_block_sessions=validation["test_block_sessions"],
        final_holdout_fraction=validation["final_holdout_fraction"],
    )
    return Study03Preflight(
        ready=True,
        protocol_failures=(),
        eligibility=eligibility,
        validation_plan=plan,
        reason="protocol, registered dates, and validation design are consistent",
    )
