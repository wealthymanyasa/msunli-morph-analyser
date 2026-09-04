"""Core domain models for morphological analysis.

These models are fully language-agnostic. They describe the shape of analysis
outputs and the minimal data structures shared across the engine. No
language-specific linguistic knowledge lives here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalysisStatus(StrEnum):
    """Outcome status of a single analysis attempt."""

    ANALYSED = "analysed"
    UNKNOWN_WORD = "unknown_word"
    AMBIGUOUS = "ambiguous"
    NOT_ANALYSABLE = "not_analysable"
    ERROR = "error"


class Morpheme(BaseModel):
    """A single morpheme identified during segmentation of a surface form.

    Morphemes are ordered; the ordering is preserved in the list that contains
    them. ``type`` is intentionally a free-form string whose allowed values are
    defined by a language pack (e.g. ``root``, ``prefix``, ``suffix``).
    """

    model_config = ConfigDict(frozen=True)

    surface: str = Field(description="Surface (orthographic) form of the morpheme")
    type: str = Field(description="Morpheme type as defined by the language pack")
    gloss: str | None = Field(
        default=None, description="Optional gloss / label supplied by the language pack"
    )
    features: dict[str, Any] = Field(
        default_factory=dict,
        description="Grammatical features contributed by this morpheme",
    )
    lemma: str | None = Field(
        default=None,
        description="Lemma associated with this morpheme (typically roots only)",
    )
    pos: str | None = Field(
        default=None,
        description="Part of speech associated with this morpheme (typically stems)",
    )


class MorphologicalAnalysis(BaseModel):
    """A single candidate analysis of a surface form.

    Attributes:
        surface: The original surface form analysed.
        normalized: The normalized form when normalization was applied.
        lemma: The canonical lemma for this analysis, if resolved.
        pos: Part of speech, as defined by the language pack.
        morphemes: Ordered list of morphemes (`Morpheme`).
        features: Aggregated grammatical features across all morphemes.
        score: Deterministic ranking score. Lower is better. Computed by the
            engine's candidate ranker.
    """

    model_config = ConfigDict(frozen=True)

    surface: str
    normalized: str | None = None
    lemma: str | None = None
    pos: str | None = None
    morphemes: list[Morpheme] = Field(default_factory=list)
    features: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class AnalysisResult(BaseModel):
    """Result of analysing a single surface form.

    Ambiguity is preserved on purpose: a surface form may map to zero, one or
    many candidate analyses. We never silently discard valid candidates.
    """

    model_config = ConfigDict(frozen=True)

    surface: str
    normalized: str | None = None
    language: str = Field(description="Language code resolved for this analysis")
    status: AnalysisStatus
    analyses: list[MorphologicalAnalysis] = Field(default_factory=list)
    error: str | None = None

    @property
    def is_ambiguous(self) -> bool:
        return len(self.analyses) > 1
