"""Outcome-blind tests for the prospective Study 03 start gate."""

from copy import deepcopy
from pathlib import Path
import tomllib

import pandas as pd

from src.study03_preflight import run_study03_preflight


def _protocol() -> dict:
    path = Path(__file__).resolve().parents[1] / "configs" / "economic_relevance.toml"
    with path.open("rb") as file:
        return tomllib.load(file)


def test_current_registered_state_is_not_ready() -> None:
    result = run_study03_preflight(_protocol(), pd.Index(["2026-07-29"]))

    assert result.ready is False
    assert result.eligibility is not None
    assert result.eligibility.new_session_count == 0
    assert result.validation_plan is None


def test_unregistered_new_dates_fail_closed() -> None:
    result = run_study03_preflight(_protocol(), pd.Index(["2026-07-30"]))

    assert result.ready is False
    assert result.reason == "registered session count does not match supplied session dates"


def test_ready_state_requires_full_new_sample_and_complete_split() -> None:
    protocol = deepcopy(_protocol())
    protocol["sample_eligibility"]["current_new_session_count"] = 343
    protocol["sample_eligibility"]["eligible_to_start"] = True
    sessions = pd.date_range("2026-07-30", periods=343, freq="B")

    result = run_study03_preflight(protocol, sessions)

    assert result.ready is True
    assert result.validation_plan is not None
    assert len(result.validation_plan.development_sessions) == 274
    assert len(result.validation_plan.final_holdout_sessions) == 69
    assert len(result.validation_plan.folds) == 1


def test_protocol_failure_blocks_date_processing() -> None:
    protocol = deepcopy(_protocol())
    protocol["signal"]["same_interval_execution_forbidden"] = False

    result = run_study03_preflight(protocol, pd.Index(["not-a-date"]))

    assert result.ready is False
    assert result.eligibility is None
    assert result.validation_plan is None
    assert "same-interval execution must remain forbidden" in result.protocol_failures
