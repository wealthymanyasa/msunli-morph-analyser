"""Architectural regression tests.

These tests guard the critical invariant that the *generic engine* contains no
Shona-specific linguistic data or procedural rules. All Shona linguistic
knowledge must originate from the declarative language pack in ``languages/``.

If these tests fail, the engine/package-separation invariant is broken.
"""

from __future__ import annotations

import re
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1] / "src" / "morph" / "engine"
ENGINE_PY_FILES = list(ENGINE_DIR.rglob("*.py"))

# Shona-specific surface forms, words and class identifiers that must NEVER
# appear in the generic engine code.
_SHONA_SPECIFIC_TERMS = [
    "murume",
    "mukadzi",
    "muti",
    "chikoro",
    "kuenda",
    "ndaenda",
    "noun-class",  # Shona's class-1/2/... representations
    "mipanda",
    "shona",
    "sagr-1sg",
    "chiShona",
]


def test_engine_directory_has_no_py_files_with_shona_terms() -> None:
    assert ENGINE_PY_FILES, "expected engine Python files to exist"
    for py_file in ENGINE_PY_FILES:
        text = py_file.read_text(encoding="utf-8")
        for term in _SHONA_SPECIFIC_TERMS:
            assert term.lower() not in text.lower(), (
                f"Shona-specific term {term!r} found in generic engine file "
                f"{py_file.relative_to(ENGINE_DIR)}"
            )


def test_engine_has_no_shona_python_modules() -> None:
    for py_file in ENGINE_PY_FILES:
        name = py_file.name
        assert not re.search(r"shona", name, re.IGNORECASE), (
            f"Shona-specific module name found in engine: {py_file}"
        )


def test_language_pack_directory_is_declarative_only() -> None:
    """Packs under languages/ must contain zero executable Python."""
    languages_dir = Path(__file__).resolve().parents[1] / "languages"
    for py in languages_dir.rglob("*.py"):
        raise AssertionError(
            f"Executable Python inside language pack is forbidden: {py}"
        )


def test_engine_domain_contains_no_shona_terms() -> None:
    domain_dir = Path(__file__).resolve().parents[1] / "src" / "morph" / "domain"
    for py_file in domain_dir.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for term in _SHONA_SPECIFIC_TERMS:
            assert term.lower() not in text.lower(), (
                f"Shona-specific term {term!r} in domain model {py_file.name}"
            )
