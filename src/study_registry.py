"""Validation and reporting for the public quantitative-research registry."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {
    "closed_negative",
    "closed_confirmed_statistical",
    "preregistered_not_started",
    "closed_failed_replication",
}
ALLOWED_HOLDOUT_STATES = {
    "sealed_unopened",
    "opened_once_closed",
    "unavailable_not_started",
}
REQUIRED_FIELDS = {
    "id",
    "title",
    "question",
    "design",
    "sample",
    "status",
    "holdout",
    "decision",
    "primary_evidence",
    "protocol",
}


def load_registry(path: str | Path) -> dict[str, Any]:
    """Load and structurally validate a study registry TOML document."""
    source = Path(path)
    with source.open("rb") as stream:
        registry = tomllib.load(stream)
    if registry.get("schema_version") != 1:
        raise ValueError("Unsupported study registry schema version")
    studies = registry.get("studies")
    if not isinstance(studies, list) or not studies:
        raise ValueError("Study registry must contain at least one study")

    seen: set[str] = set()
    for study in studies:
        missing = REQUIRED_FIELDS.difference(study)
        if missing:
            raise ValueError(f"{study.get('id', 'unknown')} missing fields: {sorted(missing)}")
        study_id = str(study["id"])
        if study_id in seen:
            raise ValueError(f"Duplicate study identifier: {study_id}")
        seen.add(study_id)
        if study["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status for {study_id}: {study['status']}")
        if study["holdout"] not in ALLOWED_HOLDOUT_STATES:
            raise ValueError(f"Invalid holdout state for {study_id}: {study['holdout']}")
    return registry


def audit_evidence_paths(registry: dict[str, Any], repository_root: str | Path) -> None:
    """Fail if a registered public evidence or protocol path is unavailable."""
    root = Path(repository_root)
    for study in registry["studies"]:
        for field in ("primary_evidence", "protocol"):
            relative = Path(study[field])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Unsafe {field} path for {study['id']}: {relative}")
            if not (root / relative).is_file():
                raise FileNotFoundError(f"Missing {field} for {study['id']}: {relative}")


def render_markdown(registry: dict[str, Any]) -> str:
    """Render a concise human-readable evidence ledger."""
    lines = [
        "# Study Registry",
        "",
        "> Machine-readable source: `configs/study_registry.toml`. Statuses record",
        "> research decisions, not trading performance.",
        "",
    ]
    for study in registry["studies"]:
        lines.extend(
            [
                f"## {study['id']} — {study['title']}",
                "",
                f"- **Question:** {study['question']}",
                f"- **Design:** {study['design']}",
                f"- **Sample:** {study['sample']}",
                f"- **Status:** `{study['status']}`",
                f"- **Holdout:** `{study['holdout']}`",
                f"- **Decision:** {study['decision']}",
                f"- **Evidence:** [`{study['primary_evidence']}`](../{study['primary_evidence']})",
                f"- **Protocol:** [`{study['protocol']}`](../{study['protocol']})",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "A confirmed statistical relationship is not automatically executable Alpha.",
            "Closed studies cannot be reopened for tuning, and prospective studies cannot",
            "report outcomes before their registered sample and access gates are satisfied.",
            "",
        ]
    )
    return "\n".join(lines)
