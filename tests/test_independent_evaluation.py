"""Tests for the independent Shona evaluation set.

Unlike ``gold.yaml`` (derived from the engine's own output and therefore
perfect by construction), ``independent.yaml`` is curated from an EXTERNAL
reference lexicon (shona-spacy). The whole point of the independent set is to
measure the engine against a source it did not generate, so it is expected
to contain genuine disagreements. These tests pin that the framework:

* loads the independent set (30-50 records, no duplicate surfaces);
* surfaces the reference annotation and verification status on every record
  (so disagreements are *reported*, never silently converted to gold); and
* reports at least one real failure on the independent run — proving the
  evaluator does not rubber-stamp an independent dataset.

So the independent run is deliberately NOT perfect, and no engine change is
made to force it to be so.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from morph.evaluation import load_dataset, run_evaluation
from morph.service.analysis import AnalysisService

ROOT = Path(__file__).resolve().parent.parent
INDEPENDENT = ROOT / "languages" / "shona" / "evaluation" / "independent.yaml"
GOLD = ROOT / "languages" / "shona" / "evaluation" / "gold.yaml"


@pytest.fixture
def shona_service() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(str(ROOT / "languages" / "shona"))
    return service


def test_independent_dataset_loads_and_is_substantive() -> None:
    records = load_dataset(INDEPENDENT)
    assert 30 <= len(records) <= 50
    statuses = {r.status for r in records}
    assert statuses <= {"analysed", "unknown_word"}
    surfaces = [r.surface for r in records]
    assert len(surfaces) == len(set(surfaces)), "duplicate surface in independent set"
    for r in records:
        assert r.source_annotation, f"{r.surface!r} missing source_annotation"
        assert r.verification_status, f"{r.surface!r} missing verification_status"
        assert r.provenance, f"{r.surface!r} missing provenance"


def test_independent_dataset_is_distinct_from_gold() -> None:
    independent = {r.surface for r in load_dataset(INDEPENDENT)}
    gold = {r.surface for r in load_dataset(GOLD)}
    # The independent set must not merely duplicate the self-derived gold: it
    # should contain surfaces the gold dataset considers unknown (or does not
    # cover), which is where the honest disagreements live.
    assert not independent <= gold, "independent set is a strict subset of gold"


def test_independent_run_reports_disagreements(
    shona_service: AnalysisService,
) -> None:
    report = run_evaluation(shona_service, "sn", INDEPENDENT)
    assert report.n_records == len(load_dataset(INDEPENDENT))
    # Independent (externally curated) data must expose genuine disagreements:
    # at least one record that MSUNLI does not reproduce. This proves the
    # evaluator reports disagreements rather than hiding them.
    assert report.n_failed > 0, "independent run should expose disagreements"
    assert report.failures, "disagreements must appear in the failure report"

    # Every failure must carry the reference annotation + verification status
    # so the divergence is fully traceable (reported, not erased).
    for failure in report.failures:
        assert "source_annotation" in failure
        assert "verification_status" in failure
        assert failure["verification_status"] is not None


def test_agree_records_are_reported_not_silently_failed(
    shona_service: AnalysisService,
) -> None:
    # The agree records in the independent set represent analyses MSUNLI does
    # reproduce; checking the engine matches them confirms the independent
    # dataset actually contains *agreement* as well as disagreement, and that
    # the reported failures correspond to the known divergent cases.
    records = load_dataset(INDEPENDENT)
    report = run_evaluation(shona_service, "sn", INDEPENDENT)
    agree_surfaces = {
        r.surface for r in records if r.verification_status == "agree"
    }
    failed_surfaces = {f["surface"] for f in report.failures}
    # No 'agree' record should be a failure: those are the reproduced cases.
    assert agree_surfaces.isdisjoint(failed_surfaces)
