"""Small, explicit statistical utilities for confirmatory research.

The functions in this module calculate statistical summaries only. They do not
interpret a result as economically meaningful or as evidence of tradable alpha.
"""

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class MeanTestResult:
    """Result of a two-sided one-sample mean test."""

    sample_size: int
    sample_mean: float
    standard_error: float
    t_statistic: float
    p_value: float
    confidence_low: float
    confidence_high: float


def one_sample_mean_test(
    values: Iterable[float],
    *,
    null_mean: float = 0.0,
    confidence: float = 0.95,
) -> MeanTestResult:
    """Estimate a mean and perform a two-sided one-sample t-test.

    Args:
        values: Independent observations for the proposed test. Dependence must
            be assessed by the caller before this test is used for inference.
        null_mean: Mean under the null hypothesis.
        confidence: Confidence level strictly between zero and one.

    Raises:
        ValueError: If inputs are non-finite, too short, or otherwise invalid.
    """
    sample = np.asarray(list(values), dtype=float)
    if sample.ndim != 1 or sample.size < 2:
        raise ValueError("At least two one-dimensional observations are required")
    if not np.isfinite(sample).all() or not np.isfinite(null_mean):
        raise ValueError("Observations and null_mean must be finite")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be strictly between zero and one")

    sample_mean = float(sample.mean())
    standard_error = float(stats.sem(sample))
    test = stats.ttest_1samp(sample, popmean=null_mean, alternative="two-sided")
    critical_value = float(stats.t.ppf((1.0 + confidence) / 2.0, df=sample.size - 1))
    margin = critical_value * standard_error

    return MeanTestResult(
        sample_size=int(sample.size),
        sample_mean=sample_mean,
        standard_error=standard_error,
        t_statistic=float(test.statistic),
        p_value=float(test.pvalue),
        confidence_low=sample_mean - margin,
        confidence_high=sample_mean + margin,
    )


def holm_adjust(p_values: Iterable[float]) -> np.ndarray:
    """Return Holm-adjusted p-values in their original order.

    The Holm procedure controls the family-wise error rate and is appropriate
    when several prespecified hypotheses form one test family.
    """
    values = np.asarray(list(p_values), dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("At least one one-dimensional p-value is required")
    if not np.isfinite(values).all() or ((values < 0.0) | (values > 1.0)).any():
        raise ValueError("p-values must be finite and between zero and one")

    order = np.argsort(values)
    ranked = values[order]
    scaled = (values.size - np.arange(values.size)) * ranked
    adjusted_ranked = np.minimum(1.0, np.maximum.accumulate(scaled))
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = adjusted_ranked
    return adjusted
