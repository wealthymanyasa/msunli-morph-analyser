"""Tests for the language-independent evaluation framework.

The gold dataset is derived from the engine's own verified output, so the
full-dataset run is expected to be perfect — the point of these tests is to
verify the *framework* computes metrics correctly (including detecting
failures), and that the gold-run invariant holds.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.evaluation import (
    _features_contain,
    _token_overlap,
    evaluate_record,
    load_dataset,
    run_evaluation,
)
from morph.service.analysis import AnalysisService

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "languages" / "shona" / "evaluation" / "gold.yaml"


@pytest.fixture
def shona_service() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(str(ROOT / "languages" / "shona"))
    return service


def yaml_records(tmp_path: Path, records: list[dict]) -> Path:
    import yaml

    p = tmp_path / "gold.yaml"
    p.write_text(yaml.safe_dump(records, sort_keys=False), encoding="utf-8")
    return p


def test_token_overlap_multiset() -> None:
    # exact match
    g = [("a", "x"), ("a", "x"), ("b", "y")]
    p = [("a", "x"), ("a", "x"), ("b", "y")]
    assert _token_overlap(g, p) == (3, 0, 0)
    # partial overlap / substitutions
    p2 = [("a", "x"), ("c", "z"), ("b", "y")]
    assert _token_overlap(g, p2) == (2, 1, 1)


def test_features_contain() -> None:
    assert _features_contain({"a": 1, "b": 2}, {"a": 1})
    assert not _features_contain({"a": 1, "b": 2}, {"a": 2})
    assert not _features_contain({"a": 1}, {"a": 1, "b": 2})


def test_metric_math_detects_failures(
    shona_service: AnalysisService, tmp_path: Path
) -> None:
    # A dataset with one deliberately-wrong gold analysis must produce
    # sub-perfect metrics (verifies the framework measures, not rubber-stamps).
    wrong = [
        {
            "surface": "murume",
            "status": "analysed",
            "analyses": [
                {
                    "lemma": "murume",
                    "pos": "noun",
                    "morphemes": [
                        {"surface": "mu", "type": "noun-class-1"},
                        {"surface": "rume", "type": "stem"},
                    ],
                    "features": {"noun_class": "1", "number": "singular"},
                }
            ],
        },
    ]
    path = yaml_records(tmp_path, wrong)
    report = run_evaluation(shona_service, "sn", path)
    assert report.analysis_accuracy == 1.0

    # now introduce a wrong lemma -> must drop accuracy
    wrong[0]["analyses"][0]["lemma"] = "bogusLemma"
    path2 = yaml_records(tmp_path, wrong)
    report2 = run_evaluation(shona_service, "sn", path2)
    assert report2.analysis_accuracy == 0.0
    assert report2.lemma_accuracy == 0.0
    assert report2.n_correct == 0
    assert report2.n_failed == 1


def test_gold_dataset_loads_and_is_complete() -> None:
    records = load_dataset(GOLD)
    assert len(records) >= 100, "gold dataset must be substantive (>=100 records)"
    statuses = {r.status for r in records}
    assert statuses <= {"analysed", "unknown_word"}
    analysed = [r for r in records if r.status == "analysed"]
    unknown = [r for r in records if r.status == "unknown_word"]
    assert len(analysed) >= 50
    assert len(unknown) >= 10
    for r in analysed:
        assert r.analyses, f"analysed record {r.surface!r} missing gold analysis"
        assert r.analyses[0].lemma is not None
        assert r.analyses[0].pos is not None


def test_gold_run_invariant(shona_service: AnalysisService) -> None:
    report = run_evaluation(shona_service, "sn", GOLD)
    assert report.n_records == len(load_dataset(GOLD))
    # The dataset is derived from verified engine output, so every asserted
    # metric must be perfect. This pins the dataset/framework/engine contract.
    assert report.analysis_accuracy == 1.0
    assert report.status_accuracy == 1.0
    assert report.lemma_accuracy == 1.0
    assert report.pos_accuracy == 1.0
    assert report.segmentation_accuracy == 1.0
    assert report.feature_accuracy == 1.0
    assert report.morpheme_f1 == 1.0
    assert report.n_failed == 0


def test_distinct_surfaces_in_dataset() -> None:
    records = load_dataset(GOLD)
    surfaces = [r.surface for r in records]
    assert len(surfaces) == len(set(surfaces)), "duplicate surface in gold dataset"


def test_evaluate_record_single(shona_service: AnalysisService) -> None:
    from morph.evaluation import GoldAnalysis, GoldMorpheme, GoldRecord

    good = GoldRecord(
        surface="murume",
        status="analysed",
        analyses=[
            GoldAnalysis(
                lemma="murume",
                pos="noun",
                morphemes=[
                    GoldMorpheme(surface="mu", type="noun-class-1"),
                    GoldMorpheme(surface="rume", type="stem"),
                ],
                features={"noun_class": "1", "number": "singular"},
            )
        ],
    )
    ok, _ = evaluate_record(shona_service, "sn", good)
    assert ok is True
