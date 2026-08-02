"""Repository-level safeguards for public research artifacts."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote
import xml.etree.ElementTree as ET


_MARKDOWN_TARGET = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_EXTERNAL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_ALLOWED_DATA_FILENAMES = {".gitkeep"}
_MOJIBAKE_MARKERS = ("â€", "â€“", "â€”", "Ã", "Â", "ðŸ", "�")


def _is_local_artifact(path: Path, root: Path) -> bool:
    """Identify non-public cache directories created by local tooling."""

    return any(
        part == ".git" or part.startswith(".pytest_")
        for part in path.relative_to(root).parts
    )


def mojibake_in_markdown(root: Path) -> list[str]:
    """Return public Markdown files containing common encoding-corruption markers."""
    failures: list[str] = []
    for document in sorted(root.rglob("*.md")):
        if _is_local_artifact(document, root):
            continue
        text = document.read_text(encoding="utf-8")
        if any(marker in text for marker in _MOJIBAKE_MARKERS):
            relative = document.relative_to(root).as_posix()
            failures.append(f"possible mojibake in {relative}")
    return failures


def broken_relative_links(root: Path) -> list[str]:
    """Return Markdown links whose repository-relative targets do not exist."""
    failures: list[str] = []
    for document in sorted(root.rglob("*.md")):
        if _is_local_artifact(document, root):
            continue
        text = document.read_text(encoding="utf-8")
        for raw_target in _MARKDOWN_TARGET.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith("#")
                or target.startswith("/")
                or _EXTERNAL_SCHEME.match(target)
            ):
                continue
            path_text = unquote(target.split("#", 1)[0])
            if path_text and not (document.parent / path_text).resolve().exists():
                failures.append(
                    f"broken link in {document.relative_to(root).as_posix()}: {target}"
                )
    return failures


def invalid_svg_files(root: Path) -> list[str]:
    """Return public SVG artifacts that are not well-formed XML."""
    failures: list[str] = []
    for svg in sorted(root.rglob("*.svg")):
        if _is_local_artifact(svg, root):
            continue
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            failures.append(f"invalid SVG {svg.relative_to(root).as_posix()}: {exc}")
    return failures


def tracked_files(root: Path) -> tuple[str, ...]:
    """Return Git-tracked paths using NUL-safe parsing."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return tuple(
        item.decode("utf-8") for item in result.stdout.split(b"\0") if item
    )


def forbidden_tracked_data(paths: tuple[str, ...]) -> list[str]:
    """Return tracked licensed-data paths that violate repository policy."""
    failures: list[str] = []
    for raw_path in paths:
        path = PurePosixPath(raw_path)
        if len(path.parts) < 3 or path.parts[0] != "data":
            continue
        if path.parts[1] not in {"raw", "processed"}:
            continue
        if path.name not in _ALLOWED_DATA_FILENAMES:
            failures.append(f"forbidden tracked data file: {path.as_posix()}")
    return failures


def audit_publication(root: Path) -> list[str]:
    """Run all deterministic public-repository integrity checks."""
    repository = root.resolve()
    return [
        *broken_relative_links(repository),
        *invalid_svg_files(repository),
        *mojibake_in_markdown(repository),
        *forbidden_tracked_data(tracked_files(repository)),
    ]
