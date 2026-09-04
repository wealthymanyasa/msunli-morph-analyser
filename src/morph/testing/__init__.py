"""Generic, language-agnostic test harness for language-pack expectations.

Language packs ship their own ``tests/analyses.yaml`` expectation files. This
harness reads them and validates that the engine's output matches the declared
expectations. It contains NO language-specific logic — adding a language means
adding a pack and an expectations file, never modifying the engine or tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise ImportError("PyYAML is required for language pack testing") from exc

from morph.domain.analysis import (
    AnalysisResult,
    MorphologicalAnalysis,
)
from morph.domain.analysis import (
    AnalysisStatus as AnalysisStatus,
)
from morph.service.analysis import AnalysisService


class ExpectationMismatchError(AssertionError):
    """Raised when an analysis does not match a declared expectation."""


def _expectations_from_path(path: str | Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ExpectationMismatchError("expectations file must be a YAML list")
    return data


def run_expectations(
    service: AnalysisService,
    language: str,
    expectations_path: str | Path,
) -> int:
    """Run all expectations in a file and return the number checked.

    Raises :class:`ExpectationMismatchError` on the first mismatch.
    """
    expectations = _expectations_from_path(expectations_path)
    checked = 0
    for expectation in expectations:
        result = service.analyze(expectation["surface"], language)
        _validate_one(expectation, result)
        checked += 1
    return checked


def _validate_one(expectation: dict[str, Any], result: AnalysisResult) -> None:
    expected_status = expectation["status"]
    if result.status.value != expected_status:
        raise ExpectationMismatchError(
            f"surface '{expectation['surface']}': expected status "
            f"'{expected_status}', got '{result.status.value}'"
        )

    if expected_status == "analysed" or expected_status == "ambiguous":
        expected_analyses = expectation.get("analyses", [])
        if not expected_analyses and not result.analyses:
            # No specific analyses asserted — still require at least one.
            raise ExpectationMismatchError(
                f"surface '{expectation['surface']}': expected some analysis, got none"
            )
        # Find at least one candidate that matches every assertion group.
        for asserted in expected_analyses:
            matched = any(
                _candidate_matches(asserted, cand)
                for cand in result.analyses
            )
            if not matched:
                raise ExpectationMismatchError(
                    f"surface '{expectation['surface']}': no candidate matched "
                    f"assertion {asserted}"
                )

    elif expected_status == "unknown_word":
        if result.analyses:
            raise ExpectationMismatchError(
                f"surface '{expectation['surface']}': expected unknown, got analyses"
            )


def _candidate_matches(
    asserted: dict[str, Any], candidate: MorphologicalAnalysis
) -> bool:
    if "pos" in asserted and candidate.pos != asserted["pos"]:
        return False
    if "lemma" in asserted and candidate.lemma != asserted["lemma"]:
        return False
    if "features" in asserted:
        for key, value in asserted["features"].items():
            if candidate.features.get(key) != value:
                return False
    if "morphemes" in asserted:
        expected_morphemes = asserted["morphemes"]
        actual = [
            {"surface": m.surface, "type": m.type}
            for m in candidate.morphemes
        ]
        if actual != expected_morphemes:
            return False
    return True
