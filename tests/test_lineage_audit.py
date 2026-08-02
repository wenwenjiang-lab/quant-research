"""Tests for source-exception to analytical-panel lineage checks."""

import pandas as pd
import pytest

from src.lineage_audit import audit_intraday_gap_exclusions


def _diagnostics() -> dict:
    return {
        "intraday_gap_count": 2,
        "intraday_gaps": [
            {"session_date": "2025-01-02", "delta_minutes": 2.0},
            {"session_date": "2025-01-02", "delta_minutes": 3.0},
        ],
    }


def test_gap_audit_passes_when_exception_session_is_excluded() -> None:
    panel = pd.DataFrame({"session_date": ["2025-01-03", "2025-01-06"]})
    result = audit_intraday_gap_exclusions(panel, _diagnostics())
    assert result.gap_event_count == 2
    assert result.gap_session_count == 1
    assert result.overlapping_session_count == 0
    assert result.passed


def test_gap_audit_fails_closed_on_analytical_overlap() -> None:
    panel = pd.DataFrame({"session_date": ["2025-01-02", "2025-01-03"]})
    result = audit_intraday_gap_exclusions(panel, _diagnostics())
    assert result.overlapping_sessions == ("2025-01-02",)
    assert not result.passed


def test_gap_audit_rejects_inconsistent_metadata() -> None:
    diagnostics = _diagnostics()
    diagnostics["intraday_gap_count"] = 3
    with pytest.raises(ValueError, match="does not match"):
        audit_intraday_gap_exclusions(
            pd.DataFrame({"session_date": ["2025-01-03"]}), diagnostics
        )
