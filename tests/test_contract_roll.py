"""Tests for contract-identity and roll-transition auditing."""

import pandas as pd

from src.contract_roll import build_contract_roll_audit


def test_flags_contract_transition_and_mixed_session() -> None:
    bars = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2025-03-19T13:30:00Z",
                    "2025-03-19T13:31:00Z",
                    "2025-03-20T13:30:00Z",
                    "2025-03-20T13:31:00Z",
                    "2025-03-20T13:32:00Z",
                ],
                utc=True,
            ),
            "instrument_id": [100, 100, 100, 200, 200],
        }
    )

    audit = build_contract_roll_audit(bars)

    assert audit["primary_instrument_id"].tolist() == [100, 200]
    assert audit["mixed_contract_session"].tolist() == [False, True]
    assert audit["contract_switch"].tolist() == [False, True]
