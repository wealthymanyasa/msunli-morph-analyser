"""Tests for the Shona language pack and the generic analysis pipeline.

These tests exercise the engine against the declarative Shona pack. The test
framework is generic — assertions come from the pack's own expectations file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.domain.analysis import AnalysisStatus
from morph.service.analysis import AnalysisService
from morph.testing import run_expectations

LANGUAGES_DIR = Path(__file__).resolve().parents[1] / "languages"
SHONA_DIR = LANGUAGES_DIR / "shona"
SHONA_EXPECTATIONS = SHONA_DIR / "tests" / "analyses.yaml"


@pytest.fixture(scope="module")
def shona_service() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(SHONA_DIR)
    return service


def test_shona_pack_loads_and_registers(shona_service: AnalysisService) -> None:
    assert shona_service.has_language("sn")
    assert "sn" in shona_service.languages()


def test_shona_pack_passes_full_expectations(shona_service: AnalysisService) -> None:
    """Run every declared expectation — the pack's own regression suite."""
    checked = run_expectations(shona_service, "sn", SHONA_EXPECTATIONS)
    assert checked > 0


def test_noun_morphology_analysed(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("murume", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    assert result.language == "sn"
    assert result.normalized == "murume"
    analysis = result.analyses[0]
    assert analysis.pos == "noun"
    assert analysis.lemma == "murume"
    assert [m.type for m in analysis.morphemes] == ["noun-class-1", "stem"]
    assert analysis.features.get("noun_class") == "1"
    assert analysis.features.get("number") == "singular"


def test_plural_noun_morphology(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("varume", "sn")
    analysis = result.analyses[0]
    assert analysis.lemma == "murume"
    assert [m.type for m in analysis.morphemes] == ["noun-class-2", "stem"]
    assert analysis.features.get("noun_class") == "2"
    assert analysis.features.get("number") == "plural"


def test_zero_prefix_noun(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("mai", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    assert result.analyses[0].lemma == "mai"
    assert result.analyses[0].pos == "noun"


def test_infinitive_verb(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("kuenda", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    analysis = result.analyses[0]
    assert analysis.pos == "verb"
    assert analysis.lemma == "enda"
    assert [m.type for m in analysis.morphemes] == ["noun-class-15", "stem"]


def test_conjugated_verb(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("ndaenda", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    analysis = result.analyses[0]
    assert analysis.pos == "verb"
    assert analysis.lemma == "enda"
    assert [m.type for m in analysis.morphemes] == [
        "sagr-1sg",
        "tam-perfect",
        "stem",
    ]


def test_verb_slot_rejects_noun_stem(shona_service: AnalysisService) -> None:
    """1sg perfect conjugations only combine with verb stems.

    Non-words like ``ndamai`` (nd-a-mai, a noun stem in the verb slot) must
    not be analysed. Regressed: previously the verb slot accepted any stem,
    producing spurious analyses for nouns.
    """
    for surface in ("ndamai", "ndababa", "ndazai", "ndati", "ndapata"):
        result = shona_service.analyze(surface, "sn")
        assert result.status == AnalysisStatus.UNKNOWN_WORD, surface


def test_unknown_word_no_crash(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("zzzzz", "sn")
    assert result.status == AnalysisStatus.UNKNOWN_WORD
    assert result.analyses == []


def test_analysis_is_deterministic(shona_service: AnalysisService) -> None:
    r1 = shona_service.analyze("murume", "sn")
    r2 = shona_service.analyze("murume", "sn")
    assert r1.model_dump() == r2.model_dump()


def test_normalization_lowercases(shona_service: AnalysisService) -> None:
    result = shona_service.analyze("MURUME", "sn")
    assert result.normalized == "murume"
    assert result.status == AnalysisStatus.ANALYSED
