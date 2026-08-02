from pathlib import Path

import pytest

from src.study_registry import audit_evidence_paths, load_registry, render_markdown


ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "configs" / "study_registry.toml"


def test_public_registry_is_complete_and_links_resolve() -> None:
    registry = load_registry(REGISTRY)
    audit_evidence_paths(registry, ROOT)
    assert [study["id"] for study in registry["studies"]] == [
        "STUDY-01",
        "STUDY-02",
        "STUDY-03",
        "STUDY-04",
    ]


def test_rendered_registry_matches_committed_report() -> None:
    rendered = render_markdown(load_registry(REGISTRY))
    committed = (ROOT / "reports" / "study_registry.md").read_text(encoding="utf-8")
    assert committed == rendered


def test_registry_rejects_unknown_status(tmp_path: Path) -> None:
    text = REGISTRY.read_text(encoding="utf-8").replace(
        'status = "closed_negative"', 'status = "overstated_result"', 1
    )
    malformed = tmp_path / "registry.toml"
    malformed.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid status"):
        load_registry(malformed)


def test_readme_exposes_each_registered_study() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for study in load_registry(REGISTRY)["studies"]:
        assert study["id"] in readme
