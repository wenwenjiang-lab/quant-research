"""Create a local, date-only Study 03 readiness report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.economic_relevance import audit_session_csv, write_eligibility_report


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
    parser.add_argument("--parent-end", default="2026-07-29")
    parser.add_argument("--minimum-sessions", type=int, default=274)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = audit_session_csv(
        args.panel,
        session_column=args.session_column,
        parent_sample_end=args.parent_end,
        minimum_required_sessions=args.minimum_sessions,
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
