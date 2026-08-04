"""Audit append-only shadow records and flag forecast-window deviations."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.baseball_research import PredictionRecord, canonical_hash, validate_prediction


def main() -> None:
    ledger = ROOT / "data" / "baseball" / "shadow_predictions.jsonl"
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    keys: set[str] = set()
    games = defaultdict(list)
    deviations = []
    ny = ZoneInfo("America/New_York")
    for line_number, row in enumerate(rows, start=1):
        if row["record_key"] in keys:
            raise ValueError(f"duplicate record key at line {line_number}")
        keys.add(row["record_key"])
        claimed_hash = row["record_sha256"]
        payload = {key: value for key, value in row.items() if key != "record_sha256"}
        if canonical_hash(payload) != claimed_hash:
            raise ValueError(f"record hash mismatch at line {line_number}")
        record_fields = {
            key: value for key, value in row.items() if key not in {"record_key", "record_sha256"}
        }
        validate_prediction(PredictionRecord(**record_fields))
        group_key = (
            row["game_id"],
            row["forecast_kind"],
            row["model_version"],
        )
        games[group_key].append(row)
        predicted = datetime.fromisoformat(row["prediction_time"].replace("Z", "+00:00")).astimezone(ny)
        scheduled = datetime.fromisoformat(row["scheduled_start"].replace("Z", "+00:00")).astimezone(ny)
        morning_deviation = row["forecast_kind"] == "morning" and (
            predicted.date() != scheduled.date() or not 8 <= predicted.hour < 10
        )
        daily_deviation = row["forecast_kind"] == "daily" and (
            predicted.date() != scheduled.date() or predicted.hour != 14
        )
        if morning_deviation or daily_deviation:
            deviations.append(row["record_key"])
    for (game_id, forecast_kind, model_version), game_rows in games.items():
        if len(game_rows) != 2:
            raise ValueError(
    f"game {game_id} kind {forecast_kind} model {model_version} "
    "does not contain two team probabilities"
)
        probabilities = [record["win_probability"] for record in game_rows]
        if all(probability is None for probability in probabilities):
            continue
        if any(probability is None for probability in probabilities):
            raise ValueError(f"game {game_id} has a partial probability pair")
        if abs(sum(probabilities) - 1.0) > 1e-12:
            raise ValueError(f"game {game_id} probabilities are not complementary")
    result = {
        "rows": len(rows),
        "games": len(games),
        "hash_and_schema_failures": 0,
        "forecast_window_deviation_rows": len(deviations),
        "confirmatory_eligible_rows": len(rows) - len(deviations),
        "deviation_rule": "record was outside its locked New York forecast window",
    }
    output = ROOT / "outputs" / "baseball" / "shadow_ledger_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
