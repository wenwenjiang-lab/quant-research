"""Tests for the guarded primary development-sample analysis."""

import numpy as np
import pandas as pd
import pytest

from src.primary_analysis import (
    diagnose_primary_model,
    fit_controlled_hac_regression,
    fit_primary_hac_regression,
    moving_block_bootstrap_slope,
)


def _development_panel() -> pd.DataFrame:
    x = np.arange(1.0, 31.0)
    noise = np.sin(x) * 0.25
    return pd.DataFrame(
        {
            "sample": ["development"] * len(x),
            "opening_range_width_bps": x,
            "post_opening_abs_return_bps": 1.0 + 2.0 * x + noise,
            "lag5_mean_session_range_bps": 5.0 + 0.5 * x + np.cos(x),
        }
    )


def test_hac_regression_recovers_synthetic_slope() -> None:
    result = fit_primary_hac_regression(_development_panel(), max_lags=3)

    assert result.sample_size == 30
    assert result.slope == pytest.approx(2.0, abs=0.01)
    assert result.confidence_low < result.slope < result.confidence_high


def test_analysis_rejects_any_holdout_row() -> None:
    panel = _development_panel()
    panel.loc[0, "sample"] = "final_holdout"

    with pytest.raises(ValueError, match="development sessions only"):
        fit_primary_hac_regression(panel)


def test_block_bootstrap_is_deterministic() -> None:
    first = moving_block_bootstrap_slope(
        _development_panel(), block_length=3, resamples=200, seed=7
    )
    second = moving_block_bootstrap_slope(
        _development_panel(), block_length=3, resamples=200, seed=7
    )

    assert first == second
    assert first.confidence_low < 2.0 < first.confidence_high


def test_controlled_model_and_diagnostics_are_finite() -> None:
    controlled = fit_controlled_hac_regression(_development_panel(), max_lags=3)
    diagnostics = diagnose_primary_model(_development_panel())

    assert controlled.sample_size == 30
    assert np.isfinite(controlled.focal_slope)
    assert np.isfinite(controlled.lagged_volatility_slope)
    assert 0 <= diagnostics.influential_session_count <= 30
    assert np.isfinite(diagnostics.durbin_watson)
