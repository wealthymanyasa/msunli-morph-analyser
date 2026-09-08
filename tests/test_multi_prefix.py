"""Tests for multi-prefix morphotactics (``prefix1 prefix2 stem``).

The morphotactic grammar is explicit sequential slots, so any number of prefix
slots may precede the anchoring stem. These tests certify that capability two
ways:

- generically, on a fictional language pack (no Shona-specific code anywhere);
- against the declared Shona multi-prefix rules, and that existing
  single-prefix analyses and the current noun-class-agreement behaviour are
  unchanged.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.domain.analysis import AnalysisStatus
from morph.domain.pack import (
    Constraint,
    LanguagePack,
    LexicalEntry,
    MorphemeSpec,
    MorphotacticRule,
)
from morph.engine.factory import default_engine
from morph.loading import load_language_pack
from morph.service.analysis import AnalysisService

SHONA_DIR = Path(__file__).resolve().parents[1] / "languages" / "shona"

MULTI_PREFIX_RULE_IDS = {
    "locative-17-over-class-7": "noun-class-17 noun-class-7 stem",
    "locative-18-over-class-1": "noun-class-18 noun-class-1 stem",
    "locative-18-over-class-3": "noun-class-18 noun-class-3 stem",
    "locative-18-over-class-11": "noun-class-18 noun-class-11 stem",
    "diminutive-12-over-class-1": "noun-class-12 noun-class-1 stem",
}


def _with_multi_prefix(pack: LanguagePack) -> LanguagePack:
    """A fictional pack whose only rule is a two-prefix noun construction."""
    return pack.model_copy(
        update={
            "closed_class": [],
            "constraints": [],
            "lexicon": [
                LexicalEntry(surface="tove", lemma="tove", pos="noun", features={})
            ],
            "morphemes": [
                MorphemeSpec(id="root", sources_lexicon=True, aliases=[], features={}),
                MorphemeSpec(id="pre1", aliases=["ka"], features={"position": "outer"}),
                MorphemeSpec(id="pre2", aliases=["mu"], features={"position": "inner"}),
            ],
            "morphotactics": [
                MorphotacticRule(sequence="pre1 pre2 root", id="two-prefix-noun"),
            ],
        }
    )


def test_two_prefix_structure_generated(sample_pack: LanguagePack) -> None:
    """prefix1 + prefix2 + stem produces analyses for fictional words."""
    pack = _with_multi_prefix(sample_pack)
    result = default_engine().strategy.analyse("kamutove", pack)
    assert result.status == AnalysisStatus.ANALYSED
    assert len(result.analyses) == 1
    analysis = result.analyses[0]
    assert [m.surface for m in analysis.morphemes] == ["ka", "mu", "tove"]
    assert analysis.lemma == "tove"
    assert analysis.pos == "noun"


def test_three_part_structure_generated(sample_pack: LanguagePack) -> None:
    """A two-prefix + stem word is a three-morpheme analysis."""
    pack = _with_multi_prefix(sample_pack)
    result = default_engine().strategy.analyse("kamutove", pack)
    assert [m.type for m in result.analyses[0].morphemes] == [
        "pre1",
        "pre2",
        "root",
    ]
    assert len(result.analyses[0].morphemes) == 3


def test_morpheme_order_preserved(sample_pack: LanguagePack) -> None:
    """The surface-token order (prefixes then stem) is preserved exactly."""
    pack = _with_multi_prefix(sample_pack)
    result = default_engine().strategy.analyse("kamutove", pack)
    types = [m.type for m in result.analyses[0].morphemes]
    surfaces = [m.surface for m in result.analyses[0].morphemes]
    assert types == ["pre1", "pre2", "root"]
    assert surfaces == ["ka", "mu", "tove"]


def test_invalid_prefix_sequences_rejected(sample_pack: LanguagePack) -> None:
    pack = _with_multi_prefix(sample_pack)
    engine = default_engine().strategy
    # Missing the outer prefix slot.
    assert engine.analyse("mutove", pack).status == AnalysisStatus.UNKNOWN_WORD
    # Prefixes present but the stem is not in the lexicon.
    assert engine.analyse("kamubogus", pack).status == AnalysisStatus.UNKNOWN_WORD
    # Neither prefix present.
    assert engine.analyse("tove", pack).status == AnalysisStatus.UNKNOWN_WORD


def test_single_prefix_analysis_still_works(sample_pack: LanguagePack) -> None:
    """A pack rule with one prefix is unaffected by the multi-prefix rule."""
    pack = _with_multi_prefix(sample_pack).model_copy(
        update={
            "morphotactics": [
                MorphotacticRule(sequence="pre1 pre2 root", id="two-prefix-noun"),
                MorphotacticRule(sequence="pre2 root", id="single-prefix-noun"),
            ]
        }
    )
    engine = default_engine().strategy
    multi = engine.analyse("kamutove", pack)
    assert multi.status == AnalysisStatus.ANALYSED
    assert [m.type for m in multi.analyses[0].morphemes] == ["pre1", "pre2", "root"]
    single = engine.analyse("mutove", pack)
    assert single.status == AnalysisStatus.ANALYSED
    assert [m.type for m in single.analyses[0].morphemes] == ["pre2", "root"]


def test_multiple_prefixes_use_existing_engine_with_no_shona_code(
    sample_pack: LanguagePack,
) -> None:
    """Same mechanism reached through the stock factory — fully generic."""
    assert _with_multi_prefix(sample_pack).metadata.code == "xx"


def _with_outer_locative(pack: LanguagePack) -> LanguagePack:
    """A fictional pack exercising the generic outer-locative mechanism.

    ``loc`` is an outer locative class (``L``) allowed to stack over an inner
    agreeing class; ``cl7``/``cl1`` are ordinary agreeing noun classes and
    ``cl15`` is the only class permitted on verb stems, enforced through the
    generic ``affix_stem_pos`` constraint. No Shona-specific code is involved.
    """
    return pack.model_copy(
        update={
            "closed_class": [],
            "constraints": [
                Constraint(
                    id="noun-class-agreement",
                    kind="noun_class_agreement",
                    params={"outer_classes": ["L"]},
                ),
                Constraint(
                    id="affix-stem-pos",
                    kind="affix_stem_pos",
                    params={"stem_pos": "verb", "affix_classes": ["15"]},
                ),
            ],
            "lexicon": [
                LexicalEntry(
                    surface="koro",  # class 7 nominal stem
                    lemma="koro",
                    pos="noun",
                    features={"noun_class": "7", "number": "singular"},
                ),
                LexicalEntry(
                    surface="rume",  # class 1 nominal stem
                    lemma="rume",
                    pos="noun",
                    features={"noun_class": "1", "number": "singular"},
                ),
                LexicalEntry(
                    surface="famba",  # verbal stem
                    lemma="famba",
                    pos="verb",
                    features={},
                ),
            ],
            "morphemes": [
                MorphemeSpec(id="root", sources_lexicon=True, aliases=[], features={}),
                MorphemeSpec(id="loc", aliases=["ku"], features={"noun_class": "L"}),
                MorphemeSpec(
                    id="cl7",
                    aliases=["chi"],
                    features={"noun_class": "7", "number": "singular"},
                ),
                MorphemeSpec(
                    id="cl1",
                    aliases=["mu"],
                    features={"noun_class": "1", "number": "singular"},
                ),
                MorphemeSpec(
                    id="cl15",
                    aliases=["ku"],
                    features={"noun_class": "15", "number": "singular"},
                ),
            ],
            "morphotactics": [
                MorphotacticRule(sequence="loc cl7 root", id="outer-locative"),
                MorphotacticRule(sequence="cl1 root", id="class-1-noun"),
                MorphotacticRule(sequence="cl7 root", id="class-7-noun"),
                MorphotacticRule(sequence="cl15 root", id="infinitive"),
            ],
            "noun_classes": [],
        }
    )


def test_outer_locative_stacked_nominal_analysed(sample_pack: LanguagePack) -> None:
    """An exempt outer class stacks over an inner agreeing prefix (ku-chi-koro)."""
    pack = _with_outer_locative(sample_pack)
    result = default_engine().strategy.analyse("kuchikoro", pack)
    assert result.status == AnalysisStatus.ANALYSED
    analysis = result.analyses[0]
    assert [m.type for m in analysis.morphemes] == ["loc", "cl7", "root"]
    assert [m.surface for m in analysis.morphemes] == ["ku", "chi", "koro"]
    assert analysis.features["noun_class"] == "L"


def test_outer_locative_heads_final_class(sample_pack: LanguagePack) -> None:
    """The outer prefix heads the surface noun class, not the inner one."""
    pack = _with_outer_locative(sample_pack)
    analysis = default_engine().strategy.analyse("kuchikoro", pack).analyses[0]
    assert analysis.features["noun_class"] == "L"
    assert analysis.features["noun_class"] != "7"
    assert analysis.features["number"] == "singular"


def test_ordinary_single_prefix_agreement_unchanged(sample_pack: LanguagePack) -> None:
    """Single agreeing prefixes still analyse exactly as before."""
    pack = _with_outer_locative(sample_pack)
    engine = default_engine().strategy
    murume = engine.analyse("murume", pack)
    assert murume.status == AnalysisStatus.ANALYSED
    assert murume.analyses[0].features["noun_class"] == "1"
    chikoro = engine.analyse("chikoro", pack)
    assert chikoro.status == AnalysisStatus.ANALYSED
    assert chikoro.analyses[0].features["noun_class"] == "7"


def test_single_outer_locative_prefix_still_rejected(sample_pack: LanguagePack) -> None:
    """ku-(L) alone over a class-7 stem is invalid: the exemption only applies
    to a genuinely stacked outer prefix."""
    pack = _with_outer_locative(sample_pack)
    result = default_engine().strategy.analyse("kukoro", pack)
    assert result.status == AnalysisStatus.UNKNOWN_WORD


def test_inner_prefix_must_still_agree(sample_pack: LanguagePack) -> None:
    """An exempt outer locative does not license a disagreeing inner prefix."""
    pack = _with_outer_locative(sample_pack)
    # loc + cl7 over a class-1 stem: the inner class 7 does not agree with the
    # class-1 stem, so kuchirume must stay unknown.
    result = default_engine().strategy.analyse("kuchirume", pack)
    assert result.status == AnalysisStatus.UNKNOWN_WORD


def test_verb_stem_rejects_outer_locative(sample_pack: LanguagePack) -> None:
    """The outer locative cannot ride a verb stem; the class-15 infinitive can."""
    pack = _with_outer_locative(sample_pack)
    engine = default_engine().strategy
    assert engine.analyse("kuchifamba", pack).status == AnalysisStatus.UNKNOWN_WORD
    kufamba = engine.analyse("kufamba", pack)
    assert kufamba.status == AnalysisStatus.ANALYSED
    assert kufamba.analyses[0].features["noun_class"] == "15"


# ── Shona pack ────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def shona_service() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(SHONA_DIR)
    return service


def test_shona_declares_multi_prefix_rules() -> None:
    pack = load_language_pack(SHONA_DIR)
    by_id = {rule.id: rule.sequence for rule in pack.morphotactics}
    for rule_id, expected_sequence in MULTI_PREFIX_RULE_IDS.items():
        assert rule_id in by_id, rule_id
        assert by_id[rule_id] == expected_sequence
        # Three explicit sequential slots: prefix, prefix, stem.
        assert len(expected_sequence.split()) == 3


def test_shona_conjugated_verb_is_two_prefixes(shona_service: AnalysisService) -> None:
    """The pack's working two-prefix structure: nd- + a- + stem."""
    result = shona_service.analyze("ndaenda", "sn")
    assert result.status == AnalysisStatus.ANALYSED
    assert [m.type for m in result.analyses[0].morphemes] == [
        "sagr-1sg",
        "tam-perfect",
        "stem",
    ]
    assert [m.surface for m in result.analyses[0].morphemes] == ["nd", "a", "enda"]


def test_shona_stacked_locative_nominal_prefixes_analyse(
    shona_service: AnalysisService,
) -> None:
    """Stacked locative rules analyse: the outer locative class (17/18) is
    declared exempt in constraints.yaml (outer_classes) and heads the surface;
    the diminutive (class 12) is not exempt, so ka-mu-kadzi stays unknown."""
    kuchikoro = shona_service.analyze("kuchikoro", "sn")
    assert kuchikoro.status == AnalysisStatus.ANALYSED
    analysis = kuchikoro.analyses[0]
    assert [m.type for m in analysis.morphemes] == [
        "noun-class-17",
        "noun-class-7",
        "stem",
    ]
    assert [m.surface for m in analysis.morphemes] == ["ku", "chi", "koro"]
    assert analysis.lemma == "chikoro"
    assert analysis.features["noun_class"] == "17"
    assert analysis.features["number"] == "singular"

    mumurume = shona_service.analyze("mumurume", "sn")
    assert mumurume.status == AnalysisStatus.ANALYSED
    analysis = mumurume.analyses[0]
    assert [m.type for m in analysis.morphemes] == [
        "noun-class-18",
        "noun-class-1",
        "stem",
    ]
    assert [m.surface for m in analysis.morphemes] == ["mu", "mu", "rume"]
    assert analysis.lemma == "murume"
    assert analysis.features["noun_class"] == "18"

    mumusha = shona_service.analyze("mumusha", "sn")
    assert mumusha.status == AnalysisStatus.ANALYSED
    analysis = mumusha.analyses[0]
    assert [m.type for m in analysis.morphemes] == [
        "noun-class-18",
        "noun-class-3",
        "stem",
    ]
    assert [m.surface for m in analysis.morphemes] == ["mu", "mu", "sha"]
    assert analysis.lemma == "musha"
    assert analysis.features["noun_class"] == "18"
    assert analysis.features["number"] == "singular"

    murwizi = shona_service.analyze("murwizi", "sn")
    assert murwizi.status == AnalysisStatus.ANALYSED
    analysis = murwizi.analyses[0]
    assert [m.type for m in analysis.morphemes] == [
        "noun-class-18",
        "noun-class-11",
        "stem",
    ]
    assert [m.surface for m in analysis.morphemes] == ["mu", "rw", "izi"]
    assert analysis.lemma == "rwizi"
    assert analysis.features["noun_class"] == "18"
    assert analysis.features["number"] == "singular"

    kamukadzi = shona_service.analyze("kamukadzi", "sn")
    assert kamukadzi.status == AnalysisStatus.UNKNOWN_WORD, "kamukadzi"
    assert kamukadzi.analyses == [], "kamukadzi"


def test_shona_class_11_keeps_ru_allomorph() -> None:
    """The declarative class-11 allomorph set preserves `ru` alongside `rw`."""
    pack = load_language_pack(SHONA_DIR)
    aliases = {m.id: m.aliases for m in pack.morphemes}
    assert aliases["noun-class-11"] == ["ru", "rw"]


def test_shona_single_prefix_nouns_unchanged(shona_service: AnalysisService) -> None:
    for surface, lemma in (("murume", "murume"), ("chikoro", "chikoro")):
        result = shona_service.analyze(surface, "sn")
        assert result.status == AnalysisStatus.ANALYSED, surface
        assert result.analyses[0].lemma == lemma
        assert result.analyses[0].morphemes[-1].type == "stem"
