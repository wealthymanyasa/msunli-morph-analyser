"""Language-expansion demonstration: a minimal future-language pack.

Proves the engine, service and evaluation framework are language-independent:
a *new* (fictional) language pack with a different grammar registers and is
scored with zero changes to the generic code — the framework iterates over
whatever pack is registered.
"""

from __future__ import annotations

from pathlib import Path

from morph.evaluation import run_evaluation
from morph.service.analysis import AnalysisService


def _future_pack() -> dict:
    """A minimal fictional agglutinative-ish grammar (unrelated to Shona).

    Grammar: ``(noun)`` / ``(verb)`` stems combine with a plural infix ``-oj-``
    (nouns) and a tense prefix ``le-`` (verbs). This exercises the generic
    engine against affixes/classes Shona does not use.
    """
    return {
        "metadata": {
            "code": "fk",
            "name": "Futureko (fictional demo language)",
            "version": "0.1.0",
            "engine_compatibility": "1.x",
            "license": "MIT",
            "provenance": "Prompt 4 language-expansion fixture (fictional)",
            "author": "platform",
        },
        "normalization": {"lowercase": True, "rules": []},
        "lexicon": [
            {
                "surface": "hop",
                "lemma": "hop",
                "pos": "noun",
                "features": {"class": "1"},
            },
            {
                "surface": "tok",
                "lemma": "tok",
                "pos": "noun",
                "features": {"class": "3"},
            },
            {
                "surface": "glam",
                "lemma": "glam",
                "pos": "verb",
                "features": {},
            },
        ],
        "morphemes": [
            {"id": "root", "sources_lexicon": True, "aliases": [], "features": {}},
            {"id": "pl", "aliases": ["oj"], "features": {"number": "plural"}},
            {"id": "past", "aliases": ["le"], "features": {"tense": "past"}},
        ],
        "morphotactics": [
            {"sequence": "root pl?", "id": "noun_word"},
            {"sequence": "past root", "id": "verb_word"},
        ],
        "paradigms": [],
        "constraints": [
            {
                "id": "pl-noun-only",
                "kind": "slot_stem_pos",
                "params": {"affix_ids": ["pl"], "stem_pos": "noun"},
            },
            {
                "id": "past-verb-only",
                "kind": "slot_stem_pos",
                "params": {"affix_ids": ["past"], "stem_pos": "verb"},
            },
        ],
        "ranking": {
            "prefer_lemmas": True,
            "penalties": {"no_lemma": 1.0, "longer_segmentation": 0.5},
        },
    }


def test_future_pack_registers_and_analyses() -> None:
    service = AnalysisService()
    service.register_pack(_future_pack())
    assert service.has_language("fk")

    r = service.analyze("hopoj", "fk")
    assert r.status.value == "analysed"
    a = r.analyses[0]
    assert a.lemma == "hop"
    assert a.pos == "noun"
    assert [(m.surface, m.type) for m in a.morphemes] == [("hop", "root"), ("oj", "pl")]
    assert a.features.get("number") == "plural"

    r2 = service.analyze("leglam", "fk")
    a2 = r2.analyses[0]
    assert a2.lemma == "glam"
    assert a2.pos == "verb"
    assert a2.features.get("tense") == "past"


def test_future_pack_slot_position_restriction_enforced() -> None:
    """Affixes may only combine with stems of the declared POS.

    Regression guard: this pack previously declared a constraint whose params
    the engine did not interpret, so the constraint silently did nothing.
    """
    service = AnalysisService()
    service.register_pack(_future_pack())

    # The plural infix -oj- is restricted to noun stems; 'lehop' conjugates a
    # noun stem, so the past marker must reject it.
    r = service.analyze("lehop", "fk")
    assert r.status.value == "unknown_word"

    # Valid combinations still analyse.
    assert service.analyze("hopoj", "fk").status.value == "analysed"
    assert service.analyze("leglam", "fk").status.value == "analysed"


def test_evaluation_framework_works_on_future_pack(tmp_path: Path) -> None:
    import yaml

    service = AnalysisService()
    service.register_pack(_future_pack())

    dataset = [
        {
            "surface": "hop",
            "status": "analysed",
            "analyses": [
                {
                    "lemma": "hop",
                    "pos": "noun",
                    "morphemes": [{"surface": "hop", "type": "root"}],
                    "features": {"class": "1"},
                }
            ],
        },
        {
            "surface": "hopoj",
            "status": "analysed",
            "analyses": [
                {
                    "lemma": "hop",
                    "pos": "noun",
                    "morphemes": [
                        {"surface": "hop", "type": "root"},
                        {"surface": "oj", "type": "pl"},
                    ],
                    "features": {"class": "1", "number": "plural"},
                }
            ],
        },
        {"surface": "unknownword", "status": "unknown_word"},
    ]
    gold = tmp_path / "fk_gold.yaml"
    gold.write_text(yaml.safe_dump(dataset, sort_keys=False), encoding="utf-8")

    report = run_evaluation(service, "fk", gold)
    assert report.language == "fk"
    assert report.n_records == 3
    assert report.analysis_accuracy == 1.0
    assert report.status_accuracy == 1.0
