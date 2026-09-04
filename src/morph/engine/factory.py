"""Engine facade and dependency wiring.

Provides a factory that constructs a fully wired, language-agnostic analysis
engine. The engine is constructed with the engine major version so that
incompatible language packs are rejected.
"""

from __future__ import annotations

from morph.engine.implementations import (
    ConcatenativeCandidateGenerator,
    ConfigDrivenNormalizer,
    DefaultCandidateRanker,
    DefaultConstraintValidator,
    DefaultFeatureUnifier,
)
from morph.engine.interfaces import AnalysisStrategy
from morph.engine.pack_validator import LanguagePackValidator
from morph.engine.strategy import DefaultAnalysisStrategy


class MorphologyEngine:
    """A ready-to-use morphology engine bound to a fixed engine version."""

    def __init__(self, engine_major: int = 1) -> None:
        self.validator = LanguagePackValidator(engine_major=engine_major)
        self._strategy = DefaultAnalysisStrategy(
            normalizer=ConfigDrivenNormalizer(),
            candidate_generator=ConcatenativeCandidateGenerator(),
            feature_unifier=DefaultFeatureUnifier(),
            constraint_validator=DefaultConstraintValidator(),
            candidate_ranker=DefaultCandidateRanker(),
        )

    @property
    def strategy(self) -> AnalysisStrategy:
        return self._strategy


def default_engine(engine_major: int = 1) -> MorphologyEngine:
    """Construct a fully wired engine using the default implementations."""
    return MorphologyEngine(engine_major=engine_major)
