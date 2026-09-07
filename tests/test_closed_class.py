"""Tests for the declarative closed-class mechanism.

Closed-class words (pronouns, conjunctions, adverbs, determiners, ...) have NO
prefix/stem segmentation. The generic mechanism represents them as whole-word
lexical entries (``pack.closed_class``) that analyse as a single
``closed_class`` morpheme. This suite proves the mechanism end-to-end and
that existing noun/verb analyses and unknown-word behaviour are unchanged.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.domain.analysis import AnalysisStatus
from morph.domain.pack import LexicalEntry
from morph.engine.factory import default_engine
from morph.loading import load_language_pack
from morph.service.analysis import AnalysisService

LANGUAGES_DIR = Path(__file__).resolve().parents[1] / "languages"
SHONA_DIR = LANGUAGES_DIR / "shona"

# One representative surface per POS, with the expected (lemma, pos).
CLOSED_CLASS_WORDS: dict[str, tuple[str, str]] = {
    "ini": ("ini", "pron"),
    "kana": ("kana", "cconj"),
    "mangwanani": ("mangwanani", "adv"),
    "uyu": ("uyu", "det"),
}


@pytest.fixture(scope="module")
def shona_service() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(SHONA_DIR)
    return service


def test_closed_class_entries_loaded_with_provenance() -> None:
    pack = load_language_pack(SHONA_DIR)
    assert len(pack.closed_class) == 14
    for entry in pack.closed_class:
        assert entry.surface
        assert entry.lemma
        assert entry.pos
        assert entry.provenance == "shona-spacy (shona_lexicon.json)"


@pytest.mark.parametrize("surface", sorted(CLOSED_CLASS_WORDS))
def test_closed_class_word_analysed(
    shona_service: AnalysisService, surface: str
) -> None:
    expected_lemma, expected_pos = CLOSED_CLASS_WORDS[surface]
    result = shona_service.analyze(surface, "sn")
    assert result.status == AnalysisStatus.ANALYSED
    assert len(result.analyses) == 1
    analysis = result.analyses[0]
    assert analysis.lemma == expected_lemma
    assert analysis.pos == expected_pos
    # Whole word = one closed-class morpheme; no prefix/stem segmentation.
    assert [m.surface for m in analysis.morphemes] == [surface]
    assert [m.type for m in analysis.morphemes] == ["closed_class"]


def test_closed_class_features_preserved(shona_service: AnalysisService) -> None:
    ini = shona_service.analyze("ini", "sn")
    assert ini.analyses[0].features.get("person") == "1"
    assert ini.analyses[0].features.get("number") == "singular"

    uyu = shona_service.analyze("uyu", "sn")
    assert uyu.analyses[0].features.get("noun_class") == "1"
    assert uyu.analyses[0].features.get("proximity") == "near"


def test_closed_class_normalization(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("INI", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    assert result.normalized == "ini"
    assert result.analyses[0].pos == "pron"


def test_existing_noun_and_verb_analyses_unchanged(
    shona_service: AnalysisService,
) -> None:
    noun = shona_service.analyze("murume", "sn")
    assert noun.status == AnalysisStatus.ANALYSED
    assert noun.analyses[0].pos == "noun"
    assert noun.analyses[0].lemma == "murume"
    assert [m.type for m in noun.analyses[0].morphemes] == [
        "noun-class-1",
        "stem",
    ]

    verb = shona_service.analyze("kuenda", "sn")
    assert verb.status == AnalysisStatus.ANALYSED
    assert verb.analyses[0].pos == "verb"
    assert verb.analyses[0].lemma == "enda"
    assert [m.type for m in verb.analyses[0].morphemes] == [
        "noun-class-15",
        "stem",
    ]


def test_unknown_word_behaviour_unchanged(shona_service: AnalysisService) -> None:
    for surface in ("qqqq", "mumba", "zzz"):
        result = shona_service.analyze(surface, "sn")
        assert result.status == AnalysisStatus.UNKNOWN_WORD, surface
        assert result.analyses == [], surface


def test_closed_class_mechanism_is_language_independent(
    sample_pack,
) -> None:
    """The mechanism works on a fictional pack — no language-specific logic."""
    pack = sample_pack.model_copy(
        update={
            "closed_class": [
                LexicalEntry(
                    surface="hello",
                    lemma="hello",
                    pos="intj",
                    provenance="test fixture",
                )
            ]
        }
    )
    engine = default_engine()
    result = engine.strategy.analyse("hello", pack)
    assert result.status == AnalysisStatus.ANALYSED
    assert len(result.analyses) == 1
    analysis = result.analyses[0]
    assert analysis.lemma == "hello"
    assert analysis.pos == "intj"
    assert [m.type for m in analysis.morphemes] == ["closed_class"]

    # Non-closed-class words in the same pack still analyse/unknown normally.
    assert engine.strategy.analyse("kats", pack).status == AnalysisStatus.ANALYSED
    assert engine.strategy.analyse("qqqq", pack).status == AnalysisStatus.UNKNOWN_WORD