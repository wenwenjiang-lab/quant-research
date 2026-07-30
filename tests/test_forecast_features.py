import pandas as pd
import pytest

from src.forecast_features import (
    FEATURE_AVAILABILITY,
    assert_no_target_in_features,
    audit_feature_cutoff,
    build_phase2_features,
)


def test_historical_features_are_strictly_lagged() -> None:
    panel = pd.DataFrame({
        "session_date": pd.bdate_range("2023-01-02", periods=25),
        "session_range_bps": range(1, 26),
    })
    features = build_phase2_features(panel)
    assert features.loc[20, "previous_session_range_bps"] == 20
    assert features.loc[20, "lag5_mean_session_range_bps"] == 18
    assert features.loc[20, "lag20_mean_session_range_bps"] == 10.5


def test_cutoff_audit_accepts_registry_and_rejects_late_feature() -> None:
    audit_feature_cutoff(FEATURE_AVAILABILITY)
    with pytest.raises(ValueError, match="unavailable"):
        audit_feature_cutoff({"future_close": "16:00"})


def test_target_leakage_guard() -> None:
    assert_no_target_in_features(["opening_range_width_bps"], "post_1000_realized_range_bps")
    with pytest.raises(ValueError, match="Target leakage"):
        assert_no_target_in_features(["post_1000_realized_range_bps"], "post_1000_realized_range_bps")
    with pytest.raises(ValueError, match="Target leakage"):
        assert_no_target_in_features(["post_1000_high"], "post_1000_realized_range_bps")
