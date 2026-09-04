"""Tests for the generic YAML language-pack loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.domain.pack import LanguagePack
from morph.engine.pack_validator import PackValidationError
from morph.loading import load_language_pack

SHONA_DIR = Path(__file__).resolve().parents[1] / "languages" / "shona"


def test_loads_shona_pack() -> None:
    pack = load_language_pack(SHONA_DIR)
    assert isinstance(pack, LanguagePack)
    assert pack.code == "sn"


def test_shona_metadata() -> None:
    pack = load_language_pack(SHONA_DIR)
    md = pack.metadata
    assert md.code == "sn"
    assert md.version == "0.1.0"
    assert md.engine_compatibility == "1.x"
    assert md.provenance


def test_shona_resources_loaded() -> None:
    pack = load_language_pack(SHONA_DIR)
    assert pack.lexicon
    assert pack.morphemes
    assert pack.morphotactics
    assert pack.noun_classes


def test_shona_morphemes_include_class_prefixes() -> None:
    pack = load_language_pack(SHONA_DIR)
    ids = {m.id for m in pack.morphemes}
    assert "stem" in ids
    assert "noun-class-1" in ids
    assert "noun-class-3" in ids
    # shared surface allomorphs declared on class 1 and 3
    cl1 = next(m for m in pack.morphemes if m.id == "noun-class-1")
    cl3 = next(m for m in pack.morphemes if m.id == "noun-class-3")
    assert "mu" in cl1.aliases
    assert "mu" in cl3.aliases
    assert cl1.sources_lexicon is False
    stem = next(m for m in pack.morphemes if m.id == "stem")
    assert stem.sources_lexicon is True


def test_shona_noun_classes_structured() -> None:
    pack = load_language_pack(SHONA_DIR)
    by_id = {nc.identifier: nc for nc in pack.noun_classes}
    cl1 = by_id["1"]
    assert cl1.surface_allomorphs  # mu/mw/m
    assert cl1.plural_of == "2"
    assert cl1.has_zero_prefix is False
    cl1a = by_id["1a"]
    assert cl1a.has_zero_prefix is True
    assert "" in cl1a.surface_allomorphs
    # Disputed classes carry a status so we don't silently assert them.
    assert by_id["19"].status == "disputed"
    assert by_id["21"].status == "disputed"


def test_load_missing_directory_raises() -> None:
    with pytest.raises(PackValidationError):
        load_language_pack(SHONA_DIR / "does_not_exist")


def test_load_directory_without_manifest_raises(tmp_path: Path) -> None:
    (tmp_path / "other.yaml").write_text("a: 1\n", encoding="utf-8")
    with pytest.raises(PackValidationError):
        load_language_pack(tmp_path)
