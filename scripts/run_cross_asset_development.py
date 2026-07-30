"""Run the frozen cross-asset specification on a local development panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.cross_asset_evaluation import (
    confirmation_gate,
    session_clustered_loss_test,
    summarize_nested_forecasts,
)
from src.cross_asset_models import expanding_nested_predictions, nested_forecast_loss_panel


HOLDOUT_START = "2025-02-20"
LAGS = tuple(range(1, 6))


def evaluate(panel: pd.DataFrame, *, target: str, own_prefix: str, cross_prefix: str, cross_lags=LAGS):
    predictions = expanding_nested_predictions(
        panel,
        target=target,
        own_lag_features=[f"{own_prefix}{lag}" for lag in LAGS],
        cross_lag_features=[f"{cross_prefix}{lag}" for lag in cross_lags],
        holdout_start=HOLDOUT_START,
        minimum_training_sessions=252,
        test_block_sessions=21,
        embargo_sessions=1,
    )
    losses = nested_forecast_loss_panel(predictions)
    return {
        "summary": summarize_nested_forecasts(losses, hac_max_lag=5),
        "session_clustered": session_clustered_loss_test(losses, session_hac_max_lag=5),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path, help="Local pre-holdout panel CSV")
    parser.add_argument("--output", type=Path, help="Optional aggregate JSON output")
    args = parser.parse_args()
    panel = pd.read_csv(args.panel)

    results = {
        "mnq_to_qqq": evaluate(
            panel, target="qqq_return", own_prefix="qqq_return_lag",
            cross_prefix="futures_return_lag",
        ),
        "qqq_to_mnq": evaluate(
            panel, target="futures_return", own_prefix="futures_return_lag",
            cross_prefix="qqq_return_lag",
        ),
        "mnq_to_qqq_latency_2min": evaluate(
            panel, target="qqq_return", own_prefix="qqq_return_lag",
            cross_prefix="futures_return_lag", cross_lags=(2, 3, 4, 5),
        ),
        "mnq_to_qqq_latency_5min": evaluate(
            panel, target="qqq_return", own_prefix="qqq_return_lag",
            cross_prefix="futures_return_lag", cross_lags=(5,),
        ),
    }
    results["development_gate"] = confirmation_gate(
        results["mnq_to_qqq"]["summary"],
        reverse_direction_reported=True,
        latency_sensitivity_reported=True,
        protocol_and_code_frozen=True,
    )
    payload = json.dumps(results, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
