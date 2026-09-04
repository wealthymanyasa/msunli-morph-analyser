"""Language-independent evaluation framework.

The evaluator measures how accurately the engine reproduces a hand-verified
*gold dataset* of morphological analyses. It is fully generic: it consumes a
YAML dataset of ``GoldRecord`` entries and an :class:`AnalysisService`, and
computes metrics against whatever language pack the service has registered.
Adding a future language means adding a pack and a gold dataset — never
modifying this module.

Metrics (all deterministic):

- **status accuracy**: the engine's predicted ``AnalysisStatus`` equals gold.
- **analysis accuracy**: status is correct and (for analysable words) the
  top-ranked candidate matches gold on lemma, POS, segmentation and features.
- **lemma accuracy**, **POS accuracy**, **segmentation accuracy**,
  **feature accuracy**: per-slot correctness of the top-ranked candidate.
- **morpheme precision / recall / F1**: token-level overlap between the
  predicted and gold morpheme sequences, aggregated across the dataset.

The framework never tunes the engine to reach a target score; it reports the
actual measured quality.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from morph.domain.analysis import AnalysisResult, MorphologicalAnalysis
from morph.service.analysis import AnalysisService

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyYAML is required for evaluation datasets") from exc

# Version of the generic evaluation framework / engine contract this module
# scores against. Bumped only when the scoring semantics change.
ENGINE_VERSION = "1.0.0"


class GoldMorpheme(BaseModel):
    """A gold morpheme (surface + type) expected in the segmentation."""

    surface: str
    type: str


class GoldAnalysis(BaseModel):
    """A single canonical gold analysis for a surface form."""

    lemma: str | None = None
    pos: str | None = None
    morphemes: list[GoldMorpheme] = Field(default_factory=list)
    features: dict[str, Any] = Field(default_factory=dict)


class GoldRecord(BaseModel):
    """One manually verified gold record.

    ``status`` follows :class:`~morph.domain.analysis.AnalysisStatus`. For
    analysable forms one or more ``analyses`` are given; the first is the
    canonical reference used for the accuracy metrics. ``alternative_analyses``
    and ``provenance`` are optional documentation fields that do not affect
    scoring.
    """

    surface: str
    status: str
    analyses: list[GoldAnalysis] = Field(default_factory=list)
    alternative_analyses: list[GoldAnalysis] = Field(default_factory=list)
    provenance: str | None = None


class Metrics(BaseModel):
    """Aggregate token/record counts used to derive rates."""

    n_records: int = 0
    n_analysed: int = 0
    n_unknown: int = 0

    status_correct: int = 0
    analysis_correct: int = 0
    lemma_correct: int = 0
    pos_correct: int = 0
    seg_correct: int = 0
    feat_correct: int = 0

    # morpheme token counts (micro-aggregate)
    tp_morphemes: int = 0
    fp_morphemes: int = 0
    fn_morphemes: int = 0


def load_dataset(path: str | Path) -> list[GoldRecord]:
    """Load and validate a gold dataset from a YAML file."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, list):
        raise ValueError(f"evaluation dataset must be a list, got {type(raw).__name__}")
    return [GoldRecord.model_validate(item) for item in raw]


def _morpheme_tokens(analysis: MorphologicalAnalysis | None) -> list[tuple[str, str]]:
    if analysis is None:
        return []
    return [(m.surface, m.type) for m in analysis.morphemes]


def _top_analysis(result: AnalysisResult) -> MorphologicalAnalysis | None:
    if not result.analyses:
        return None
    return result.analyses[0]


def _is_analysable(status: str) -> bool:
    return status in {"analysed", "ambiguous"}


def evaluate_record(
    service: AnalysisService,
    language: str,
    record: GoldRecord,
) -> tuple[bool, Metrics]:
    """Run one gold record and return ``(fully_correct, metrics_delta)``.

    ``fully_correct`` reflects analysis accuracy for this single record and is
    used by callers that want exact per-record pass/fail aggregates.
    """
    result = service.analyze(record.surface, language)
    gold: GoldAnalysis | None = record.analyses[0] if record.analyses else None
    predicted = _top_analysis(result)

    m = Metrics(n_records=1)

    status_ok = result.status.value == record.status
    if status_ok:
        m.status_correct = 1
    m.n_analysed += 1 if _is_analysable(record.status) else 0
    m.n_unknown += 1 if record.status == "unknown_word" else 0

    analysis_ok = status_ok
    if gold is not None:
        m.n_analysed = 1
        # per-slot accuracy for the top-ranked candidate
        if predicted is not None:
            if gold.lemma is not None and predicted.lemma == gold.lemma:
                m.lemma_correct = 1
            if gold.pos is not None and predicted.pos == gold.pos:
                m.pos_correct = 1
            gold_tokens = [(g.surface, g.type) for g in gold.morphemes]
            pred_tokens = _morpheme_tokens(predicted)
            if gold.morphemes and pred_tokens == gold_tokens:
                m.seg_correct = 1
            if gold.features and _features_contain(predicted.features, gold.features):
                m.feat_correct = 1
            # analysis correct requires all asserted slots match
            analysis_ok = (
                status_ok
                and predicted is not None
                and (gold.lemma is None or predicted.lemma == gold.lemma)
                and (gold.pos is None or predicted.pos == gold.pos)
                and (not gold.morphemes or pred_tokens == gold_tokens)
                and (not gold.features or _features_contain(predicted.features, gold.features))
            )
    elif record.status == "unknown_word":
        analysis_ok = status_ok and result.analyses == []

    if analysis_ok:
        m.analysis_correct = 1

    # morpheme-level P/R/F1 (token overlap with multiplicity)
    if gold is not None and predicted is not None and gold.morphemes:
        gold_tokens = [(g.surface, g.type) for g in gold.morphemes]
        pred_tokens = _morpheme_tokens(predicted)
        tp, fp, fn = _token_overlap(gold_tokens, pred_tokens)
        m.tp_morphemes = tp
        m.fp_morphemes = fp
        m.fn_morphemes = fn

    return analysis_ok, m


def _features_contain(have: dict[str, Any], want: dict[str, Any]) -> bool:
    return all(have.get(k) == v for k, v in want.items())


def _token_overlap(
    gold: list[tuple[str, str]],
    pred: list[tuple[str, str]],
) -> tuple[int, int, int]:
    """Return ``(true_positives, false_positives, false_negatives)``.

    Uses multiset (bag) overlap so repeated morphemes are counted correctly.
    """
    from collections import Counter

    gold_counts = Counter(gold)
    pred_counts = Counter(pred)
    tp = sum((gold_counts & pred_counts).values())
    fp = sum((pred_counts - gold_counts).values())
    fn = sum((gold_counts - pred_counts).values())
    return tp, fp, fn


def run_evaluation(
    service: AnalysisService,
    language: str,
    dataset_path: str | Path,
) -> "EvaluationReport":
    """Run the full evaluation and produce a report."""
    records = load_dataset(dataset_path)
    aggregate = Metrics()
    failures: list[dict[str, Any]] = []

    for record in records:
        correct, delta = evaluate_record(service, language, record)
        _add_metrics(aggregate, delta)
        if not correct:
            failures.append(
                {
                    "surface": record.surface,
                    "expected_status": record.status,
                    "actual": _format_result(
                        service.analyze(record.surface, language)
                    ),
                    "provenance": record.provenance,
                }
            )

    return _build_report(service, language, str(dataset_path), records, aggregate, failures)


def _add_metrics(total: Metrics, delta: Metrics) -> None:
    for field in (
        "n_records",
        "n_analysed",
        "n_unknown",
        "status_correct",
        "analysis_correct",
        "lemma_correct",
        "pos_correct",
        "seg_correct",
        "feat_correct",
        "tp_morphemes",
        "fp_morphemes",
        "fn_morphemes",
    ):
        setattr(total, field, getattr(total, field) + getattr(delta, field))


def _format_result(result: AnalysisResult) -> dict[str, Any]:
    return {
        "status": result.status.value,
        "analyses": [
            {
                "lemma": a.lemma,
                "pos": a.pos,
                "morphemes": [{"surface": m.surface, "type": m.type} for m in a.morphemes],
                "features": a.features,
            }
            for a in result.analyses
        ],
    }


def _rate(numerator: int, denominator: int) -> float:
    return (numerator / denominator) if denominator else 0.0


def _build_report(
    service: AnalysisService,
    language: str,
    dataset_path: str,
    records: list[GoldRecord],
    agg: Metrics,
    failures: list[dict[str, Any]],
) -> "EvaluationReport":
    recall = _rate(agg.tp_morphemes, agg.tp_morphemes + agg.fn_morphemes)
    precision = _rate(agg.tp_morphemes, agg.tp_morphemes + agg.fp_morphemes)
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) else 0.0
    )
    return EvaluationReport(
        language=language,
        dataset_path=dataset_path,
        engine_version=_engine_version(service),
        pack_version=_pack_version(service, language),
        n_records=agg.n_records,
        n_analysed=agg.n_analysed,
        n_unknown=agg.n_unknown,
        status_accuracy=_rate(agg.status_correct, agg.n_records),
        analysis_accuracy=_rate(agg.analysis_correct, agg.n_records),
        lemma_accuracy=_rate(agg.lemma_correct, agg.n_analysed),
        pos_accuracy=_rate(agg.pos_correct, agg.n_analysed),
        segmentation_accuracy=_rate(agg.seg_correct, agg.n_analysed),
        feature_accuracy=_rate(agg.feat_correct, agg.n_analysed),
        morpheme_precision=precision,
        morpheme_recall=recall,
        morpheme_f1=f1,
        n_correct=agg.analysis_correct,
        n_failed=agg.n_records - agg.analysis_correct,
        failures=failures,
    )


def _engine_version(service: AnalysisService) -> str:
    return ENGINE_VERSION


def _pack_version(service: AnalysisService, language: str) -> str:
    pack = service.get_pack(language)
    if pack is None:
        return "unknown"
    return pack.metadata.version


class EvaluationReport(BaseModel):
    """Result of running the evaluator against a gold dataset."""

    language: str
    dataset_path: str
    engine_version: str
    pack_version: str

    n_records: int
    n_analysed: int
    n_unknown: int
    n_correct: int
    n_failed: int

    status_accuracy: float
    analysis_accuracy: float
    lemma_accuracy: float
    pos_accuracy: float
    segmentation_accuracy: float
    feature_accuracy: float
    morpheme_precision: float
    morpheme_recall: float
    morpheme_f1: float

    failures: list[dict[str, Any]] = Field(default_factory=list)

    def render_markdown(self) -> str:
        """Render the report as Markdown (for an evaluation report / CI)."""
        lines = [
            f"# Evaluation report — `{self.language}`",
            "",
            f"- Engine version: `{self.engine_version}`",
            f"- Language pack version: `{self.pack_version}`",
            f"- Dataset: `{self.dataset_path}`",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Records | {self.n_records} |",
            f"| Analysed | {self.n_analysed} |",
            f"| Unknown words | {self.n_unknown} |",
            f"| **Analysis accuracy** | **{self.analysis_accuracy:.3f}** |",
            f"| Status accuracy | {self.status_accuracy:.3f} |",
            f"| Lemma accuracy | {self.lemma_accuracy:.3f} |",
            f"| POS accuracy | {self.pos_accuracy:.3f} |",
            f"| Segmentation accuracy | {self.segmentation_accuracy:.3f} |",
            f"| Feature accuracy | {self.feature_accuracy:.3f} |",
            f"| Morpheme precision | {self.morpheme_precision:.3f} |",
            f"| Morpheme recall | {self.morpheme_recall:.3f} |",
            f"| Morpheme F1 | {self.morpheme_f1:.3f} |",
            "",
            f"Correct: {self.n_correct} / {self.n_records} (failed: {self.n_failed})",
            "",
        ]
        if self.failures:
            lines.append("## Failure cases")
            lines.append("")
            for f in self.failures:
                lines.append(f"- `{f['surface']}`: expected `{f['expected_status']}`, got `{f['actual']['status']}`")
        else:
            lines.append("No failures recorded.")
        return "\n".join(lines)
