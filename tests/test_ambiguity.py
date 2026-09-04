"""Tests that the engine preserves genuine ambiguity.

Uses a small constructed (fictional) language pack so the test does not depend
on Shona-specific facts. The engine must never silently discard valid
candidates.
"""

from __future__ import annotations

from conftest import sample_pack_data

from morph.domain.analysis import AnalysisStatus
from morph.service.analysis import AnalysisService


def _build_ambiguous_service() -> AnalysisService:
    """A pack where 'su' realises two distinct classes over the same stem.

    The stem ``tin`` appears twice in the lexicon with the same surface but
    different lemmas/classes, so ``mutin`` has two valid class-1 stems and two
    class-3 stems, all of which pass the noun-class agreement constraint.
    This yields multiple valid analyses which must ALL be preserved.
    """
    data = sample_pack_data()  # base sample (has noun agreement machinery)
    data["lexicon"] = [
        {"surface": "tin", "lemma": "mufv", "pos": "noun",
         "features": {"noun_class": "1", "number": "singular"}},
        {"surface": "tin", "lemma": "mvo", "pos": "noun",
         "features": {"noun_class": "1", "number": "singular"}},
    ]
    data["morphemes"] = [
        {"id": "stem", "sources_lexicon": True, "aliases": [], "features": {}},
        {"id": "class-1", "aliases": ["mu"], "features": {"noun_class": "1",
         "number": "singular"}},
        {"id": "class-3", "aliases": ["mu"], "features": {"noun_class": "3",
         "number": "singular"}},
    ]
    data["morphotactics"] = [
        {"sequence": "class-1 stem", "id": "c1"},
        {"sequence": "class-3 stem", "id": "c3"},
    ]
    data["noun_classes"] = [
        {"identifier": "1", "plural_of": "2"},
        {"identifier": "3", "plural_of": "4"},
    ]
    data["constraints"] = [
        {"id": "agr", "kind": "noun_class_agreement", "params": {}}
    ]
    service = AnalysisService()
    service.register_pack(data)
    return service


def test_ambiguous_analysis_preserves_all_candidates() -> None:
    service = _build_ambiguous_service()
    result = service.analyze("mutin", "xx")
    # Two class-1 stem candidates survive the agreement constraint.
    assert result.status == AnalysisStatus.AMBIGUOUS
    assert len(result.analyses) == 2
    assert result.is_ambiguous is True
    lemmas = {a.lemma for a in result.analyses}
    assert lemmas == {"mufv", "mvo"}
