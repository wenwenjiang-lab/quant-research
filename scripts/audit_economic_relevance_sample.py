"""Create a local, date-only Study 03 readiness report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.economic_relevance import audit_session_csv, write_eligibility_report


DEFAULT_PROTOCOL = PROJECT_ROOT / "configs" / "economic_relevance.toml"


def load_sample_gate(protocol_path: Path) -> tuple[str, int]:
    """Read the prospective sample boundary from the frozen protocol."""
    with protocol_path.open("rb") as file:
        protocol = tomllib.load(file)
    sample = protocol.get("sample_eligibility")
    if not isinstance(sample, dict):
        raise ValueError("Protocol is missing [sample_eligibility]")
    try:
        parent_end = str(sample["parent_sample_end"])
        minimum_sessions = int(sample["minimum_new_sessions_before_development"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Protocol contains an invalid prospective sample gate") from exc
    if minimum_sessions <= 0:
        raise ValueError("Prospective minimum session count must be positive")
    return parent_end, minimum_sessions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit whether Study 03 has enough genuinely new sessions."
    )
    parser.add_argument("panel", type=Path, help="Local CSV containing session dates")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/economic_relevance_sample_status.json"),
        help="Local JSON status destination",
    )
    parser.add_argument("--session-column", default="session_date")
    parser.add_argument(
        "--protocol",
        type=Path,
        default=DEFAULT_PROTOCOL,
        help="Frozen Study 03 TOML protocol supplying the sample gate",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parent_end, minimum_sessions = load_sample_gate(args.protocol)
    audit = audit_session_csv(
        args.panel,
        session_column=args.session_column,
        parent_sample_end=parent_end,
        minimum_required_sessions=minimum_sessions,
    )
    destination = write_eligibility_report(audit, args.output)
    print(f"Readiness report: {destination}")
    print(
        f"New sessions: {audit.new_session_count}/{audit.minimum_required_sessions}; "
        f"eligible: {audit.eligible}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
