"""Tests for public portfolio integrity and data-governance guards."""

from pathlib import Path

from src.publication_integrity import (
    audit_publication,
    broken_relative_links,
    forbidden_tracked_data,
    invalid_svg_files,
    mojibake_in_markdown,
)


def test_public_repository_artifacts_pass_integrity_audit() -> None:
    root = Path(__file__).resolve().parents[1]

    assert audit_publication(root) == []


def test_broken_relative_markdown_link_is_reported(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("[missing](reports/missing.md)", encoding="utf-8")

    failures = broken_relative_links(tmp_path)

    assert failures == ["broken link in README.md: reports/missing.md"]


def test_invalid_svg_is_reported(tmp_path: Path) -> None:
    figure = tmp_path / "figure.svg"
    figure.write_text("<svg><text></svg>", encoding="utf-8")

    failures = invalid_svg_files(tmp_path)

    assert len(failures) == 1
    assert failures[0].startswith("invalid SVG figure.svg:")


def test_mojibake_in_markdown_is_reported(tmp_path: Path) -> None:
    document = tmp_path / "report.md"
    document.write_text("Window: 09:30â€“10:00", encoding="utf-8")

    assert mojibake_in_markdown(tmp_path) == ["possible mojibake in report.md"]


def test_licensed_data_paths_cannot_be_tracked() -> None:
    paths = (
        "data/raw/.gitkeep",
        "data/processed/.gitkeep",
        "data/raw/licensed-bars.csv",
        "src/data_loader.py",
    )

    assert forbidden_tracked_data(paths) == [
        "forbidden tracked data file: data/raw/licensed-bars.csv"
    ]
