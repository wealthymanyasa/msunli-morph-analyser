"""Tests for the engine strategy and component implementations."""

from __future__ import annotations

import pytest

from morph.domain.analysis import (
    AnalysisResult,
    AnalysisStatus,
    Morpheme,
    MorphologicalAnalysis,
)
from morph.domain.pack import Constraint, LanguagePack
from morph.engine.factory import default_engine
from morph.engine.implementations import (
    ConcatenativeCandidateGenerator,
    ConfigDrivenNormalizer,
    DefaultCandidateRanker,
    DefaultConstraintValidator,
    DefaultFeatureUnifier,
    DirectCandidateGenerator,
    PackLexicon,
    PackSegmenter,
)


def test_engine_factory_builds_strategy() -> None:
    engine = default_engine()
    assert engine.strategy is not None
    assert callable(engine.strategy.analyse)


def test_normalizer_lowercases_when_configured(
    sample_pack: LanguagePack,
) -> None:
    normalizer = ConfigDrivenNormalizer()
    normalized, changed = normalizer.normalize("KATS", sample_pack)
    assert normalized == "kats"
    assert changed is True


def test_normalizer_applies_rules(sample_pack: LanguagePack) -> None:
    pack = sample_pack.model_copy(
        update={
            "normalization": sample_pack.normalization.model_copy(
                update={"rules": [["a", "e"]]}
            )
        }
    )
    normalizer = ConfigDrivenNormalizer()
    normalized, changed = normalizer.normalize("kat", pack)
    assert normalized == "ket"
    assert changed is True


def test_lexicon_lookup(sample_pack: LanguagePack) -> None:
    lexicon = PackLexicon()
    matches = lexicon.lookup("kat", sample_pack)
    assert len(matches) == 1
    assert matches[0].lemma == "kat"
    assert lexicon.lookup("missing", sample_pack) == []


def test_concatenative_candidate_generator_basic(
    sample_pack: LanguagePack,
) -> None:
    gen = ConcatenativeCandidateGenerator()
    candidates = gen.generate("kats", "kats", sample_pack)
    assert len(candidates) == 1
    morphemes = candidates[0]
    assert [m.type for m in morphemes] == ["root", "plural"]
    assert morphemes[0].surface == "kat"
    assert morphemes[1].surface == "s"
    assert morphemes[0].features == {"number": "singular", "class": "1"}
    assert morphemes[1].features == {"number": "plural"}


def test_concatenative_candidate_generator_root_only(
    sample_pack: LanguagePack,
) -> None:
    gen = ConcatenativeCandidateGenerator()
    candidates = gen.generate("kat", "kat", sample_pack)
    assert len(candidates) == 1
    assert [m.type for m in candidates[0]] == ["root"]
    assert candidates[0][0].surface == "kat"


def test_concatenative_candidate_generator_no_match(
    sample_pack: LanguagePack,
) -> None:
    gen = ConcatenativeCandidateGenerator()
    candidates = gen.generate("zzzz", "zzzz", sample_pack)
    assert candidates == []


def test_concatenative_candidate_generator_multi_root(
    sample_pack: LanguagePack,
) -> None:
    gen = ConcatenativeCandidateGenerator()
    dogs = gen.generate("dogs", "dogs", sample_pack)
    assert len(dogs) == 1
    assert dogs[0][0].lemma == "dog"
    assert dogs[0][0].pos == "noun"


def test_concatenative_candidate_generator_deterministic(
    sample_pack: LanguagePack,
) -> None:
    gen = ConcatenativeCandidateGenerator()
    c1 = gen.generate("kats", "kats", sample_pack)
    c2 = gen.generate("kats", "kats", sample_pack)
    assert c1 == c2


def test_candidate_generator_root_match(sample_pack: LanguagePack) -> None:
    """DirectCandidateGenerator does exact lexicon surface lookup (full-word)."""
    gen = DirectCandidateGenerator()
    candidates = gen.generate("kat", "kat", sample_pack)
    assert len(candidates) == 1
    assert candidates[0][0].type == "root"
    assert candidates[0][0].features == {"number": "singular", "class": "1"}


def test_candidate_generator_no_match(sample_pack: LanguagePack) -> None:
    gen = DirectCandidateGenerator()
    candidates = gen.generate("zzzz", "zzzz", sample_pack)
    assert candidates == []


def test_feature_unifier_merges(sample_pack: LanguagePack) -> None:
    unifier = DefaultFeatureUnifier()
    morphemes = [
        Morpheme(surface="a", type="root", lemma="x", features={"number": "singular"}),
        Morpheme(surface="s", type="plural", features={"number": "plural"}),
    ]
    merged = unifier.unify(morphemes, sample_pack)
    assert merged["number"] == "plural"  # later wins


def test_analysis_result_ambiguity_flag() -> None:
    result = AnalysisResult(
        surface="x",
        language="xx",
        status=AnalysisStatus.AMBIGUOUS,
        analyses=[
            MorphologicalAnalysis(surface="x"),
            MorphologicalAnalysis(surface="x"),
        ],
    )
    assert result.is_ambiguous is True


def test_segmenter_builds_morphemes(sample_pack: LanguagePack) -> None:
    seg = PackSegmenter()
    morphemes = seg.segment(["root", "plural"], "kats", sample_pack)
    assert [m.type for m in morphemes] == ["root", "plural"]
    assert morphemes[1].features == {"number": "plural"}


def test_segmenter_rejects_undefined(sample_pack: LanguagePack) -> None:
    seg = PackSegmenter()
    with pytest.raises(ValueError):
        seg.segment(["root", "nope"], "kats", sample_pack)


def test_constraint_validator_required_features(
    sample_pack: LanguagePack,
) -> None:
    validator = DefaultConstraintValidator()
    candidate = MorphologicalAnalysis(
        surface="kats",
        features={"number": "singular"},
        morphemes=[
            Morpheme(surface="kats", type="root", features={"number": "singular"})
        ],
    )
    pack = sample_pack.model_copy(
        update={
            "constraints": [
                Constraint(
                    id="c1",
                    kind="no_missing_required_features",
                    params={"required": ["number"]},
                )
            ]
        }
    )
    assert validator.validate([candidate], pack) == [candidate]

    missing = MorphologicalAnalysis(surface="x", features={})
    assert validator.validate([missing], pack) == []


def test_ranker_prefers_lemma(sample_pack: LanguagePack) -> None:
    ranker = DefaultCandidateRanker()
    no_lemma = MorphologicalAnalysis(surface="x", lemma=None, morphemes=[])
    has_lemma = MorphologicalAnalysis(surface="x", lemma="y", morphemes=[])
    ranked = ranker.rank([no_lemma, has_lemma], sample_pack)
    assert ranked[0].lemma == "y"
    assert ranked[0].score < ranked[1].score


def test_ranker_is_deterministic(sample_pack: LanguagePack) -> None:
    ranker = DefaultCandidateRanker()
    c1 = MorphologicalAnalysis(surface="x", lemma=None, morphemes=[])
    c2 = MorphologicalAnalysis(surface="x", lemma="y", morphemes=[])
    r1 = [a.score for a in ranker.rank([c1, c2], sample_pack)]
    r2 = [a.score for a in ranker.rank([c1, c2], sample_pack)]
    assert r1 == r2
