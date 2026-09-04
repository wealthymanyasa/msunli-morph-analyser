"""Tests for the generic language-pack expectation harness."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import sample_pack_data

from morph.service.analysis import AnalysisService
from morph.testing import ExpectationMismatchError, run_expectations

SHONA_EXPECTATIONS = (
    Path(__file__).resolve().parents[1]
    / "languages"
    / "shona"
    / "tests"
    / "analyses.yaml"
)


def _generic_service() -> AnalysisService:
    """A service loaded ONLY with the fictional sample pack (no Shona)."""
    service = AnalysisService()
    service.register_pack(sample_pack_data())
    return service


def test_harness_against_generic_sample_pack(tmp_path: Path) -> None:
    """A second 'language' needs only its own pack + expectations data."""
    service = _generic_service()
    expectations = tmp_path / "analyses.yaml"
    expectations.write_text(
        """
- surface: kats
  status: analysed
  analyses:
    - pos: noun
      lemma: kat
      morphemes: [{surface: kat, type: root}, {surface: s, type: plural}]
- surface: zzzz
  status: unknown_word
  analyses: []
""".lstrip(),
        encoding="utf-8",
    )
    assert run_expectations(service, "xx", expectations) == 2


def test_harness_detects_mismatch(tmp_path: Path) -> None:
    service = _generic_service()
    expectations = tmp_path / "analyses.yaml"
    expectations.write_text(
        """
- surface: kats
  status: analysed
  analyses:
    - pos: verb
""".lstrip(),
        encoding="utf-8",
    )
    with pytest.raises(ExpectationMismatchError):
        run_expectations(service, "xx", expectations)


def test_harness_works_for_shona_pack() -> None:
    service = AnalysisService()
    service.load_language_directory(
        Path(__file__).resolve().parents[1] / "languages" / "shona"
    )
    assert run_expectations(service, "sn", SHONA_EXPECTATIONS) > 0
