import numpy as np
import pandas as pd
import pytest

from src.model_stability import (
    class_distribution,
    feature_drift_table,
    leave_one_session_out_means,
    population_stability_index,
    standardized_mean_difference,
)


def test_standardized_mean_difference_uses_development_scale():
    development = pd.Series([0.0, 1.0, 2.0, 3.0])
    holdout = pd.Series([2.0, 3.0, 4.0, 5.0])
    expected = 2.0 / np.std(development, ddof=0)
    assert standardized_mean_difference(development, holdout) == pytest.approx(expected)


def test_population_stability_index_is_zero_for_same_distribution():
    sample = pd.Series(np.arange(100, dtype=float))
    assert population_stability_index(sample, sample) == pytest.approx(0.0)


def test_feature_drift_table_orders_largest_psi_first():
    development = pd.DataFrame({"stable": np.arange(20), "shifted": np.arange(20)})
    holdout = pd.DataFrame({"stable": np.arange(20), "shifted": np.arange(20) + 50})
    result = feature_drift_table(development, holdout, ["stable", "shifted"])
    assert result.iloc[0]["feature"] == "shifted"
    assert result.iloc[1]["population_stability_index"] == pytest.approx(0.0)


def test_class_distribution_uses_sorted_string_keys():
    result = class_distribution(pd.DataFrame({"y": [1, -1, 0, 0]}), "y")
    assert result == {"-1": 0.25, "0": 0.5, "1": 0.25}


def test_leave_one_session_out_means():
    values = pd.Series([1.0, 2.0, 6.0], index=["a", "b", "c"])
    result = leave_one_session_out_means(values)
    assert result.to_dict() == pytest.approx({"a": 4.0, "b": 3.5, "c": 1.5})


def test_leave_one_session_out_requires_two_sessions():
    with pytest.raises(ValueError, match="At least two"):
        leave_one_session_out_means(pd.Series([1.0]))
