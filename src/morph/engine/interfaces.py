"""Core engine interfaces.

These are pure, language-agnostic contracts. Each component operates against a
:class:`morph.domain.pack.LanguagePack` and produces inputs/outputs for the
next component. No component contains language-specific rules — all such
knowledge arrives via the language pack and is interpreted generically.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from morph.domain.analysis import (
    AnalysisResult,
    Morpheme,
    MorphologicalAnalysis,
)
from morph.domain.pack import LanguagePack


class Normalizer(ABC):
    """Normalizes a raw surface string based on the pack's normalization config.

    Returns a tuple of ``(normalized, changed)`` where ``changed`` indicates
    whether normalization altered the string (so the analysis can record a
    normalized form distinctly from the surface form).
    """

    @abstractmethod
    def normalize(self, surface: str, pack: LanguagePack) -> tuple[str, bool]:
        """Return ``(normalized_string, changed)`` for the given surface form."""


class CandidateGenerator(ABC):
    """Generates candidate morpheme segmentations for a surface form.

    Returns all candidate segmentations (each a list of morphemes); the engine
    does not silently discard any candidate here. A candidate may also be a
    single whole-word ``closed_class`` morpheme for lexical items that have no
    segmentation (see ``pack.closed_class``).
    """

    @abstractmethod
    def generate(
        self, surface: str, normalized: str, pack: LanguagePack
    ) -> list[list[Morpheme]]:
        """Return candidate segmentations (list of morpheme lists)."""


class FeatureUnifier(ABC):
    """Aggregates grammatical features contributed by each morpheme."""

    @abstractmethod
    def unify(self, morphemes: list[Morpheme], pack: LanguagePack) -> dict[str, object]:
        """Return the merged feature dict for a set of morphemes."""


class ConstraintValidator(ABC):
    """Validates candidate analyses against the pack's declared constraints."""

    @abstractmethod
    def validate(
        self,
        analysis_candidates: list[MorphologicalAnalysis],
        pack: LanguagePack,
    ) -> list[MorphologicalAnalysis]:
        """Return the subset of candidates that satisfy the pack constraints."""


class CandidateRanker(ABC):
    """Deterministically ranks candidate analyses.

    ``rank`` returns candidates ordered best-first along with an explicit score.
    Ranking must be deterministic.
    """

    @abstractmethod
    def rank(
        self, candidates: list[MorphologicalAnalysis], pack: LanguagePack
    ) -> list[MorphologicalAnalysis]:
        """Return ranked candidates (best first) with scores populated."""


class AnalysisStrategy(ABC):
    """Top-level engine strategy orchestrating the full pipeline.

    The application service depends on this abstraction, keeping the engine
    decoupled from the service layer.
    """

    @abstractmethod
    def analyse(self, word: str, pack: LanguagePack) -> AnalysisResult:
        """Analyse a single word against a language pack."""
