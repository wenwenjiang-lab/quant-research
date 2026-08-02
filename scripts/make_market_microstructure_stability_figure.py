"""Render the aggregate Study 04 stability diagnosis as an auditable SVG.

The script reads only committed summary statistics. It never reads licensed
market observations and it does not fit, select, or evaluate a model.
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("reports/market_microstructure_stability_diagnostics.json")
DEFAULT_OUTPUT = Path("figures/market_microstructure_stability.svg")
REPLICATION_THRESHOLD = -0.001


def _label(feature: str) -> str:
    labels = {
        "ask_depth_5": "Ask depth, levels 1-5",
        "ask_depth_10": "Ask depth, levels 1-10",
        "bid_depth_5": "Bid depth, levels 1-5",
        "bid_depth_10": "Bid depth, levels 1-10",
        "recent_volatility_1s": "Recent volatility (1 s)",
        "imbalance_5": "Imbalance, levels 1-5",
        "spread_ticks": "Spread (ticks)",
        "event_count_100ms": "Events per 100 ms",
    }
    return labels.get(feature, feature.replace("_", " ").title())


def render_stability_svg(payload: dict[str, Any]) -> str:
    """Return an SVG summarizing feature drift and session influence."""
    drift = sorted(
        payload["feature_drift"],
        key=lambda row: float(row["population_stability_index"]),
        reverse=True,
    )[:8]
    influence = payload["session_influence"]
    maximum_psi = max(float(row["population_stability_index"]) for row in drift)

    width, height = 1200, 650
    left_x, plot_x, plot_width = 70, 285, 420
    row_y, row_gap = 150, 43
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        "<style>text{font-family:Arial,sans-serif;fill:#172033}.title{font-size:25px;font-weight:700}.sub{font-size:14px;fill:#596579}.panel{font-size:17px;font-weight:700}.label{font-size:13px}.axis{font-size:12px;fill:#596579}.value{font-size:12px;font-weight:700}.note{font-size:13px;fill:#364152}.callout{font-size:15px;font-weight:700}</style>",
        '<text x="70" y="42" class="title">Study 04 stability diagnosis after failed replication</text>',
        '<text x="70" y="67" class="sub">Post-hoc description only · no refit, model selection, or change to the registered decision</text>',
        '<line x1="70" y1="88" x2="1130" y2="88" stroke="#d9e1ea"/>',
        '<text x="70" y="119" class="panel">A · Measured input drift</text>',
        '<text x="760" y="119" class="panel">B · Leave-one-session-out influence</text>',
        '<text x="70" y="141" class="axis">Population stability index (PSI); descriptive, not a hypothesis test</text>',
    ]

    for index, row in enumerate(drift):
        y = row_y + index * row_gap
        psi = float(row["population_stability_index"])
        bar_width = plot_width * psi / maximum_psi
        color = "#167d6d" if "depth" in str(row["feature"]) else "#9ab0c3"
        elements.extend(
            [
                f'<text x="{left_x}" y="{y + 16}" class="label">{escape(_label(str(row["feature"])))}</text>',
                f'<rect x="{plot_x}" y="{y}" width="{plot_width}" height="23" rx="2" fill="#eef2f6"/>',
                f'<rect x="{plot_x}" y="{y}" width="{bar_width:.2f}" height="23" rx="2" fill="{color}"/>',
                f'<text x="{plot_x + bar_width + 8:.2f}" y="{y + 16}" class="value">{psi:.3f}</text>',
            ]
        )

    registered = float(influence["registered_mean_log_loss_delta"])
    loo_min = float(influence["leave_one_out_minimum"])
    loo_max = float(influence["leave_one_out_maximum"])
    axis_left, axis_right, axis_y = 780, 1110, 280
    scale_min, scale_max = -0.0011, 0.0001

    def x_position(value: float) -> float:
        return axis_left + (value - scale_min) / (scale_max - scale_min) * (axis_right - axis_left)

    threshold_x = x_position(REPLICATION_THRESHOLD)
    registered_x = x_position(registered)
    loo_min_x, loo_max_x = x_position(loo_min), x_position(loo_max)
    zero_x = x_position(0.0)
    elements.extend(
        [
            '<text x="760" y="151" class="sub">Log-loss delta: multi-level candidate minus top-of-book baseline</text>',
            '<text x="760" y="174" class="sub">Negative values favor the candidate; the preregistered threshold was -0.001.</text>',
            f'<line x1="{axis_left}" y1="{axis_y}" x2="{axis_right}" y2="{axis_y}" stroke="#8795a8" stroke-width="2"/>',
            f'<line x1="{threshold_x:.2f}" y1="220" x2="{threshold_x:.2f}" y2="340" stroke="#c65d35" stroke-width="2" stroke-dasharray="5 4"/>',
            f'<text x="{threshold_x:.2f}" y="210" text-anchor="middle" class="axis">threshold -0.001</text>',
            f'<line x1="{zero_x:.2f}" y1="240" x2="{zero_x:.2f}" y2="320" stroke="#cbd5e1"/>',
            f'<line x1="{loo_min_x:.2f}" y1="{axis_y}" x2="{loo_max_x:.2f}" y2="{axis_y}" stroke="#167d6d" stroke-width="10" stroke-linecap="round"/>',
            f'<circle cx="{registered_x:.2f}" cy="{axis_y}" r="8" fill="#172033"/>',
            f'<text x="{registered_x:.2f}" y="{axis_y - 18}" text-anchor="middle" class="value">mean {registered:.6f}</text>',
            f'<text x="{(loo_min_x + loo_max_x) / 2:.2f}" y="{axis_y + 34}" text-anchor="middle" class="axis">leave-one-out range [{loo_min:.6f}, {loo_max:.6f}]</text>',
            '<rect x="760" y="375" width="370" height="106" rx="7" fill="#f4f7fa" stroke="#d9e1ea"/>',
            '<text x="785" y="408" class="callout">No single session explains the failure.</text>',
            '<text x="785" y="434" class="note">All 19 leave-one-out estimates remained slightly favorable,</text>',
            '<text x="785" y="456" class="note">but every estimate remained far short of the threshold.</text>',
            '<line x1="70" y1="530" x2="1130" y2="530" stroke="#d9e1ea"/>',
            '<text x="70" y="565" class="callout">Interpretation</text>',
            '<text x="70" y="591" class="note">Displayed-depth distributions shifted between Development and July. This is an observable association, not a causal explanation.</text>',
            '<text x="70" y="616" class="note">The registered outcome remains failed replication; these diagnostics do not validate Alpha or justify model tuning.</text>',
            '</svg>',
        ]
    )
    return "\n".join(elements) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_stability_svg(payload), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
