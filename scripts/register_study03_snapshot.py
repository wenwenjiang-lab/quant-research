"""Register an immutable local data snapshot for prospective Study 03."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.sample_registry import register_sample_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/processed/study03_sample_registry.json"),
    )
    parser.add_argument("--parent-end", default="2026-07-29")
    parser.add_argument("--minimum-sessions", type=int, default=274)
    args = parser.parse_args()

    record = register_sample_snapshot(
        args.panel,
        args.registry,
        label=args.label,
        parent_sample_end=args.parent_end,
        minimum_required_sessions=args.minimum_sessions,
    )
    progress = record["eligibility"]
    print(f"Registered snapshot: {record['label']}")
    print(f"SHA-256: {record['sha256']}")
    print(
        f"New sessions: {progress['new_session_count']}/"
        f"{progress['minimum_required_sessions']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
