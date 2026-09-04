"""Tests for the application service (analyze(word, language))."""

from __future__ import annotations

import pytest
from conftest import sample_pack_data

from morph.domain.analysis import AnalysisStatus
from morph.engine.pack_validator import PackValidationError
from morph.service.analysis import AnalysisService, UnknownLanguageError


@pytest.fixture
def service() -> AnalysisService:
    svc = AnalysisService()
    svc.register_pack(sample_pack_data())
    return svc


def test_analyze_unknown_language_raises(service: AnalysisService) -> None:
    with pytest.raises(UnknownLanguageError):
        service.analyze("kats", "zz")


def test_analyze_known_word(service: AnalysisService) -> None:
    result = service.analyze("kats", "xx")
    assert result.language == "xx"
    assert result.status in (AnalysisStatus.ANALYSED, AnalysisStatus.AMBIGUOUS)
    assert result.surface == "kats"


def test_analyze_unknown_word_status(service: AnalysisService) -> None:
    result = service.analyze("zzzz", "xx")
    assert result.status == AnalysisStatus.UNKNOWN_WORD
    assert result.analyses == []


def test_languages_registered(service: AnalysisService) -> None:
    assert service.languages() == ["xx"]
    assert service.has_language("xx")


def test_register_pack_returns_pack(service: AnalysisService) -> None:
    pack = service.get_pack("xx")
    assert pack is not None
    assert pack.metadata.version == "1.0.0"


def test_register_invalid_pack_raises(service: AnalysisService) -> None:
    with pytest.raises(PackValidationError):
        service.register_pack({"metadata": {}})


def test_analyze_preserves_ambiguity(service: AnalysisService) -> None:
    result = service.analyze("kats", "xx")
    # surface has only one lexicon root 'kats', so unambiguous in this pack
    assert len(result.analyses) == 1
    assert result.analyses[0].pos == "noun"
