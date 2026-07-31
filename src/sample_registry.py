"""Append-only local sample registry for prospective research."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from src.economic_relevance import audit_session_csv


def sha256_file(path: str | Path, *, chunk_size: int = 1 << 20) -> str:
    """Return a streaming SHA-256 digest without loading a dataset into memory."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Snapshot source does not exist: {source}")
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "snapshots": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(
        payload.get("snapshots"), list
    ):
        raise ValueError("Unsupported or malformed sample registry")
    return payload


def register_sample_snapshot(
    panel: str | Path,
    registry: str | Path,
    *,
    label: str,
    parent_sample_end: str = "2026-07-29",
    minimum_required_sessions: int = 274,
    recorded_at_utc: str | None = None,
) -> dict[str, Any]:
    """Append one immutable, date-only snapshot record.

    Reusing a label is idempotent only when the underlying file hash is
    unchanged. A changed hash under an existing label is rejected so a frozen
    snapshot cannot be silently replaced.
    """
    if not label.strip():
        raise ValueError("label must be non-empty")
    source = Path(panel)
    destination = Path(registry)
    digest = sha256_file(source)
    payload = _load_registry(destination)

    existing = [item for item in payload["snapshots"] if item.get("label") == label]
    if existing:
        if len(existing) != 1 or existing[0].get("sha256") != digest:
            raise ValueError("A frozen snapshot label cannot be replaced")
        return existing[0]

    audit = audit_session_csv(
        source,
        parent_sample_end=parent_sample_end,
        minimum_required_sessions=minimum_required_sessions,
    )
    audit_payload = asdict(audit)
    for key in ("parent_sample_end", "first_new_session", "last_new_session"):
        value = audit_payload[key]
        audit_payload[key] = value.isoformat() if value is not None else None

    timestamp = recorded_at_utc or datetime.now(timezone.utc).isoformat()
    record = {
        "label": label,
        "recorded_at_utc": timestamp,
        "sha256": digest,
        "file_size_bytes": source.stat().st_size,
        "eligibility": audit_payload,
    }
    payload["snapshots"].append(record)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return record
