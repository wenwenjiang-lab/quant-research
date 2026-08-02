"""Create aggregate post-hoc Study 04 stability diagnostics.

This script reads licensed local panels but writes only aggregate statistics.
It does not fit, select, or tune a model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.model_stability import (
    class_distribution,
    feature_drift_table,
    leave_one_session_out_means,
)


FEATURES = [
    "spread_ticks",
    "microprice_deviation_ticks",
    "imbalance_1",
    "imbalance_5",
    "imbalance_10",
    "bid_depth_5",
    "ask_depth_5",
    "bid_depth_10",
    "ask_depth_10",
    "event_count_100ms",
    "recent_mid_change_ticks_1s",
    "recent_volatility_1s",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-panel", type=Path, required=True)
    parser.add_argument("--holdout-panel", type=Path, required=True)
    parser.add_argument("--holdout-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    development = pd.read_csv(args.development_panel)
    holdout = pd.read_csv(args.holdout_panel)
    registered = json.loads(args.holdout_results.read_text(encoding="utf-8"))
    if registered.get("registered_holdout_replication") is not False:
        raise RuntimeError("This diagnostic is restricted to the closed failed holdout")

    drift = feature_drift_table(development, holdout, FEATURES)
    sessions = pd.DataFrame(registered["session_detail"]).set_index("session_date")
    loo = leave_one_session_out_means(sessions["log_loss_delta"])
    output = {
        "status": "post_hoc_descriptive_diagnostic",
        "model_refit_or_selection_performed": False,
        "registered_decision_changed": False,
        "development": {
            "sessions": int(development.session_date.nunique()),
            "observations": int(len(development)),
            "class_distribution": class_distribution(development, "future_direction_1s"),
        },
        "holdout": {
            "sessions": int(holdout.session_date.nunique()),
            "observations": int(len(holdout)),
            "class_distribution": class_distribution(holdout, "future_direction_1s"),
        },
        "feature_drift": drift.to_dict(orient="records"),
        "session_influence": {
            "registered_mean_log_loss_delta": float(sessions.log_loss_delta.mean()),
            "leave_one_out_minimum": float(loo.min()),
            "leave_one_out_maximum": float(loo.max()),
            "most_favorable_omission": str(loo.idxmin()),
            "least_favorable_omission": str(loo.idxmax()),
            "sign_reversals": int((np.sign(loo) != np.sign(sessions.log_loss_delta.mean())).sum()),
        },
        "interpretation_guard": (
            "Post-hoc description only. These diagnostics do not rescue the failed "
            "holdout, validate Alpha, or authorize model tuning."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
