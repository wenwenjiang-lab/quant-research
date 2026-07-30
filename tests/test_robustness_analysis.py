"""Tests for development-only robustness diagnostics."""

import numpy as np
import pandas as pd
import pytest

from src.robustness_analysis import (
    exclude_roll_sessions_sensitivity,
    influence_trimmed_sensitivity,
    quadratic_form_sensitivity,
    theil_sen_sensitivity,
    volatility_regime_sensitivities,
)


def _panel() -> pd.DataFrame:
    x = np.arange(1.0, 61.0)
    return pd.DataFrame(
        {
            "sample": "development",
            "opening_range_width_bps": x,
            "post_opening_abs_return_bps": 3 + 0.7 * x + 0.002 * x**2 + np.sin(x),
            "lag5_mean_session_range_bps": 20 + x + np.cos(x),
            "contract_switch": x % 20 == 0,
            "mixed_contract_session": False,
        }
    )


def test_robust_estimators_remain_finite() -> None:
    panel = _panel()
    trimmed = influence_trimmed_sensitivity(panel, max_lags=3)
    theil_sen = theil_sen_sensitivity(panel)

    assert trimmed.sample_size <= len(panel)
    assert np.isfinite(trimmed.slope)
    assert np.isfinite(theil_sen.slope)
    assert theil_sen.confidence_low < theil_sen.confidence_high


def test_quadratic_and_regime_diagnostics_are_defined() -> None:
    panel = _panel()
    quadratic = quadratic_form_sensitivity(panel, max_lags=3)
    regimes = volatility_regime_sensitivities(panel, max_lags=3)

    assert quadratic.sample_size == 60
    assert np.isfinite(quadratic.quadratic_coefficient)
    assert [result.label for result in regimes] == [
        "low trailing volatility",
        "middle trailing volatility",
        "high trailing volatility",
    ]
    assert sum(result.sample_size for result in regimes) == 60


def test_roll_exclusion_removes_flagged_sessions() -> None:
    result = exclude_roll_sessions_sensitivity(_panel(), max_lags=3)

    assert result.sample_size == 57
    assert np.isfinite(result.slope)


@pytest.mark.parametrize(
    "analysis",
    [
        influence_trimmed_sensitivity,
        theil_sen_sensitivity,
        quadratic_form_sensitivity,
        volatility_regime_sensitivities,
        exclude_roll_sessions_sensitivity,
    ],
)
def test_every_diagnostic_rejects_holdout_rows(analysis) -> None:
    panel = _panel()
    panel.loc[0, "sample"] = "final_holdout"

    with pytest.raises(ValueError, match="development sessions only"):
        analysis(panel)
