"""Validate the research registry and render its public evidence ledger."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.study_registry import audit_evidence_paths, load_registry, render_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("configs/study_registry.toml"))
    parser.add_argument("--output", type=Path, default=Path("reports/study_registry.md"))
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    registry = load_registry(args.registry)
    audit_evidence_paths(registry, args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(registry), encoding="utf-8")
    print(f"Validated {len(registry['studies'])} studies; wrote {args.output}")


if __name__ == "__main__":
    main()
