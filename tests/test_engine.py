"""Tests for the engine strategy and component implementations."""

from __future__ import annotations

from morph.domain.analysis import (
    AnalysisResult,
    AnalysisStatus,
    Morpheme,
    MorphologicalAnalysis,
)
from morph.domain.pack import (
    Constraint,
    LanguagePack,
    LexicalEntry,
    MorphemeSpec,
    MorphotacticRule,
)
from morph.engine.factory import default_engine
from morph.engine.implementations import (
    ConcatenativeCandidateGenerator,
    ConfigDrivenNormalizer,
    DefaultCandidateRanker,
    DefaultConstraintValidator,
    DefaultFeatureUnifier,
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


def _slot_stem_pos_pack(sample_pack: LanguagePack) -> LanguagePack:
    """A pack with a conjugated-verb slot that must contain verb stems."""
    return sample_pack.model_copy(
        update={
            "lexicon": [
                LexicalEntry(
                    surface="kat",
                    lemma="kat",
                    pos="noun",
                    features={"number": "singular", "class": "1"},
                ),
                LexicalEntry(
                    surface="gloom",
                    lemma="gloom",
                    pos="verb",
                    features={"number": "singular"},
                ),
            ],
            "morphemes": [
                MorphemeSpec(id="root", sources_lexicon=True, aliases=[], features={}),
                MorphemeSpec(id="sagr", aliases=["nd"], features={"role": "subject"}),
                MorphemeSpec(id="tam", aliases=["a"], features={"tense": "perfect"}),
            ],
            "morphotactics": [
                MorphotacticRule(sequence="sagr tam? root", id="conjugated"),
                MorphotacticRule(sequence="root plural?", id="noun_word"),
            ],
            "constraints": [
                Constraint(
                    id="verb-slot",
                    kind="slot_stem_pos",
                    params={"affix_ids": ["sagr", "tam"], "stem_pos": "verb"},
                )
            ],
        }
    )


def test_slot_stem_pos_rejects_noun_stem_in_verb_slot(
    sample_pack: LanguagePack,
) -> None:
    validator = DefaultConstraintValidator()
    pack = _slot_stem_pos_pack(sample_pack)
    noun_stem = MorphologicalAnalysis(
        surface="ndkat",
        morphemes=[
            Morpheme(surface="nd", type="sagr", features={"role": "subject"}),
            Morpheme(surface="kat", type="root", pos="noun"),
        ],
    )
    assert validator.validate([noun_stem], pack) == []


def test_slot_stem_pos_accepts_verb_stem_in_verb_slot(
    sample_pack: LanguagePack,
) -> None:
    validator = DefaultConstraintValidator()
    pack = _slot_stem_pos_pack(sample_pack)
    verb_stem = MorphologicalAnalysis(
        surface="ndagloom",
        morphemes=[
            Morpheme(surface="nd", type="sagr", features={"role": "subject"}),
            Morpheme(surface="a", type="tam", features={"tense": "perfect"}),
            Morpheme(surface="gloom", type="root", pos="verb"),
        ],
    )
    assert validator.validate([verb_stem], pack) == [verb_stem]


def test_slot_stem_pos_ignores_other_constructions(
    sample_pack: LanguagePack,
) -> None:
    validator = DefaultConstraintValidator()
    pack = _slot_stem_pos_pack(sample_pack)
    bare_noun = MorphologicalAnalysis(
        surface="kat",
        morphemes=[Morpheme(surface="kat", type="root", pos="noun")],
    )
    # No subject-agreement affix is present, so the restriction does not apply.
    assert validator.validate([bare_noun], pack) == [bare_noun]


def test_slot_stem_pos_end_to_end(sample_pack: LanguagePack) -> None:
    engine = default_engine()
    pack = _slot_stem_pos_pack(sample_pack)
    result = engine.strategy.analyse("ndkat", pack)
    assert result.status == AnalysisStatus.UNKNOWN_WORD
    result_ok = engine.strategy.analyse("ndagloom", pack)
    assert result_ok.status == AnalysisStatus.ANALYSED
    assert result_ok.analyses[0].lemma == "gloom"


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
