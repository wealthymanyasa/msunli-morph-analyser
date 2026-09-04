"""Shared test fixtures and sample language packs.

These are deliberately minimal, fictional language packs used to exercise the
engine without introducing real (Shona) linguistic content, per scope
discipline.
"""

from __future__ import annotations

from typing import Any

import pytest

from morph.domain.pack import LanguagePack


def sample_pack_data(**overrides: Any) -> dict[str, Any]:
    """A minimal valid, language-agnostic sample language pack.

    Lexicon surfaces are *stems* (no affixes). The morphotactic ``root plural?``
    tells the generic engine how stems and affixes compose into words. The
    ``root`` morpheme is marked ``sources_lexicon: true`` so the candidate
    generator matches it against lexicon entries rather than a fixed alias.
    """
    data: dict[str, Any] = {
        "metadata": {
            "code": "xx",
            "name": "Sample Language",
            "version": "1.0.0",
            "engine_compatibility": "1.x",
            "license": "MIT",
            "provenance": "test fixtures",
            "author": "test author",
        },
        "normalization": {
            "lowercase": True,
            "rules": [],
        },
        "lexicon": [
            {
                "surface": "kat",
                "lemma": "kat",
                "pos": "noun",
                "features": {"number": "singular", "class": "1"},
            },
            {
                "surface": "dog",
                "lemma": "dog",
                "pos": "noun",
                "features": {"number": "singular"},
            },
            {
                "surface": "duck",
                "lemma": "duck",
                "pos": "noun",
                "features": {"number": "singular"},
            },
        ],
        "morphemes": [
            {"id": "root", "sources_lexicon": True, "aliases": [], "features": {}},
            {"id": "plural", "aliases": ["s"], "features": {"number": "plural"}},
        ],
        "morphotactics": [
            {"sequence": "root plural?", "id": "noun_word"},
        ],
        "paradigms": [],
        "constraints": [],
        "ranking": {
            "prefer_lemmas": True,
            "penalties": {"no_lemma": 1.0, "longer_segmentation": 0.5},
        },
    }
    for key, value in overrides.items():
        data[key] = value
    return data


@pytest.fixture
def sample_pack_data_fixture() -> dict[str, Any]:
    return sample_pack_data()


@pytest.fixture
def sample_pack(sample_pack_data_fixture: dict[str, Any]) -> LanguagePack:
    return LanguagePack.model_validate(sample_pack_data_fixture)
