"""Tests for the append-only prospective sample registry."""

import json

import pytest

from src.sample_registry import register_sample_snapshot, sha256_file


def _write_panel(path, rows: list[str]) -> None:
    path.write_text(
        "session_date,market_value\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def test_snapshot_registration_is_date_only_and_reproducible(tmp_path) -> None:
    panel = tmp_path / "panel.csv"
    registry = tmp_path / "registry.json"
    _write_panel(panel, ["2026-07-30,999", "2026-07-31,1001"])

    record = register_sample_snapshot(
        panel,
        registry,
        label="batch-001",
        minimum_required_sessions=2,
        recorded_at_utc="2026-08-01T00:00:00+00:00",
    )
    payload = json.loads(registry.read_text(encoding="utf-8"))

    assert record["sha256"] == sha256_file(panel)
    assert record["eligibility"]["eligible"] is True
    assert len(payload["snapshots"]) == 1
    assert "999" not in registry.read_text(encoding="utf-8")
    assert "market_value" not in registry.read_text(encoding="utf-8")


def test_same_label_and_hash_is_idempotent(tmp_path) -> None:
    panel = tmp_path / "panel.csv"
    registry = tmp_path / "registry.json"
    _write_panel(panel, ["2026-07-30,1"])

    first = register_sample_snapshot(panel, registry, label="batch-001")
    second = register_sample_snapshot(panel, registry, label="batch-001")

    assert first == second
    assert len(json.loads(registry.read_text())["snapshots"]) == 1


def test_changed_file_cannot_replace_frozen_label(tmp_path) -> None:
    panel = tmp_path / "panel.csv"
    registry = tmp_path / "registry.json"
    _write_panel(panel, ["2026-07-30,1"])
    register_sample_snapshot(panel, registry, label="batch-001")
    _write_panel(panel, ["2026-07-30,2"])

    with pytest.raises(ValueError, match="cannot be replaced"):
        register_sample_snapshot(panel, registry, label="batch-001")


def test_registry_rejects_malformed_existing_document(tmp_path) -> None:
    panel = tmp_path / "panel.csv"
    registry = tmp_path / "registry.json"
    _write_panel(panel, ["2026-07-30,1"])
    registry.write_text('{"schema_version": 999}', encoding="utf-8")

    with pytest.raises(ValueError, match="malformed"):
        register_sample_snapshot(panel, registry, label="batch-001")
