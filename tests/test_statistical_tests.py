"""Tests for statistical utilities using deterministic synthetic values."""

import numpy as np
import pytest

from src.statistical_tests import holm_adjust, one_sample_mean_test


def test_mean_test_reports_expected_summary() -> None:
    result = one_sample_mean_test([1.0, 2.0, 3.0, 4.0], null_mean=0.0)

    assert result.sample_size == 4
    assert result.sample_mean == pytest.approx(2.5)
    assert result.p_value < 0.05
    assert result.confidence_low < result.sample_mean < result.confidence_high


def test_mean_test_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        one_sample_mean_test([1.0, np.nan])


def test_holm_adjust_preserves_original_order() -> None:
    adjusted = holm_adjust([0.04, 0.01, 0.03])

    assert adjusted == pytest.approx([0.06, 0.03, 0.06])


def test_holm_adjust_rejects_invalid_probability() -> None:
    with pytest.raises(ValueError, match="between zero and one"):
        holm_adjust([0.1, 1.2])
