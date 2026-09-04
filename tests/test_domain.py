"""Tests for the domain models and contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from morph.domain.analysis import (
    AnalysisResult,
    AnalysisStatus,
    Morpheme,
)
from morph.domain.pack import LanguagePack


def test_morpheme_defaults() -> None:
    m = Morpheme(surface="s", type="plural")
    assert m.gloss is None
    assert m.features == {}
    assert m.lemma is None


def test_analysis_result_frozen() -> None:
    result = AnalysisResult(surface="x", language="xx", status=AnalysisStatus.ANALYSED)
    with pytest.raises(ValueError):
        result.surface = "changed"  # frozen


def test_analysis_result_empty_analyses() -> None:
    result = AnalysisResult(
        surface="zzz", language="xx", status=AnalysisStatus.UNKNOWN_WORD
    )
    assert result.analyses == []
    assert result.is_ambiguous is False


def test_language_pack_rejects_unknown_keys() -> None:
    with pytest.raises(ValidationError):
        LanguagePack.model_validate(
            {
                "metadata": {
                    "code": "xx",
                    "name": "X",
                    "version": "1.0.0",
                    "engine_compatibility": "1.x",
                },
                "bogus_key": 1,
            }
        )


def test_language_pack_code_property() -> None:
    pack = LanguagePack(
        metadata={
            "code": "sn",
            "name": "Shona",
            "version": "1.0.0",
            "engine_compatibility": "1.x",
            "license": "MIT",
        }
    )
    assert pack.code == "sn"
