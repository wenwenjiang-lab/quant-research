import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "make_market_microstructure_stability_figure.py"


def test_stability_figure_is_valid_and_auditable(tmp_path: Path) -> None:
    payload = {
        "feature_drift": [
            {"feature": "ask_depth_5", "population_stability_index": 0.3},
            {"feature": "spread_ticks", "population_stability_index": 0.03},
        ],
        "session_influence": {
            "registered_mean_log_loss_delta": -0.00022,
            "leave_one_out_minimum": -0.00029,
            "leave_one_out_maximum": -0.00017,
        },
    }
    source = tmp_path / "diagnostics.json"
    output = tmp_path / "diagnostics.svg"
    source.write_text(json.dumps(payload), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(source), "--output", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )

    root = ET.parse(output).getroot()
    rendered = output.read_text(encoding="utf-8")
    assert root.tag.endswith("svg")
    assert "Study 04 stability diagnosis" in rendered
    assert "Ask depth, levels 1-5" in rendered
    assert "threshold -0.001" in rendered
    assert "failed replication" in rendered
    assert "observations" not in rendered.lower()
