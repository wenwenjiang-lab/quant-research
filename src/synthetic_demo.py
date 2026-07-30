"""Deterministic synthetic demonstration; not market evidence."""

import json
import numpy as np
import pandas as pd
from .forecast_models import expanding_linear_predictions, qlike_loss


def make_synthetic_panel(*, sessions: int = 800, seed: int = 20260730) -> pd.DataFrame:
    """Create a reproducible positive volatility panel with no licensed data."""
    if sessions < 600:
        raise ValueError("At least 600 sessions are required")
    rng = np.random.default_rng(seed)
    latent = np.empty(sessions); latent[0] = 80.0
    for index in range(1, sessions):
        latent[index] = max(5, 20 + .72 * latent[index - 1] + rng.normal(0, 7))
    overnight = rng.normal(0, latent * .12)
    opening = np.maximum(1, .45 * latent + rng.normal(0, 8, sessions))
    target = np.maximum(5, .65 * latent + .12 * np.abs(overnight) + rng.normal(0, 10, sessions))
    return pd.DataFrame({"session_date": pd.bdate_range("2019-01-02", periods=sessions), "previous_session_range_bps": pd.Series(latent).shift(1), "lag5_mean_session_range_bps": pd.Series(latent).shift(1).rolling(5).mean(), "lag20_mean_session_range_bps": pd.Series(latent).shift(1).rolling(20).mean(), "overnight_return_bps": overnight, "overnight_range_bps": np.abs(overnight) + 5, "opening_gap_bps": overnight * .4, "opening_range_width_bps": opening, "opening_range_return_bps": rng.normal(0, 12, sessions), "post_1000_realized_range_bps": target})


def run_synthetic_demo() -> dict[str, float | int | str]:
    """Run the registered baseline/candidate path on synthetic data."""
    panel = make_synthetic_panel(); target = "post_1000_realized_range_bps"
    baseline = ["previous_session_range_bps", "lag5_mean_session_range_bps", "lag20_mean_session_range_bps", "overnight_return_bps", "overnight_range_bps", "opening_gap_bps"]
    candidate = baseline + ["opening_range_width_bps", "opening_range_return_bps"]
    bp = expanding_linear_predictions(panel, features=baseline, target=target)
    cp = expanding_linear_predictions(panel, features=candidate, target=target)
    aligned = cp.merge(bp[["session_date", "forecast"]], on="session_date", suffixes=("_candidate", "_baseline"))
    actual = aligned["actual"].to_numpy()
    return {"data": "synthetic_only", "evaluation_sessions": len(aligned), "baseline_qlike": float(qlike_loss(actual, aligned["forecast_baseline"].to_numpy()).mean()), "candidate_qlike": float(qlike_loss(actual, aligned["forecast_candidate"].to_numpy()).mean())}


if __name__ == "__main__":
    print(json.dumps(run_synthetic_demo(), indent=2))
