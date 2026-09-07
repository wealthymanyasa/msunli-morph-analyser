"""Default analysis strategy that orchestrates the full engine pipeline.

This is the generic, language-agnostic orchestration. It wires together the
normalizer, candidate generator, feature unifier, constraint validator and
candidate ranker against a single language pack.
"""

from __future__ import annotations

from morph.domain.analysis import (
    AnalysisResult,
    AnalysisStatus,
    Morpheme,
    MorphologicalAnalysis,
)
from morph.domain.pack import LanguagePack
from morph.engine import interfaces


class DefaultAnalysisStrategy(interfaces.AnalysisStrategy):
    """Orchestrates the engine pipeline for a given language pack."""

    def __init__(
        self,
        normalizer: interfaces.Normalizer,
        candidate_generator: interfaces.CandidateGenerator,
        feature_unifier: interfaces.FeatureUnifier,
        constraint_validator: interfaces.ConstraintValidator,
        candidate_ranker: interfaces.CandidateRanker,
    ) -> None:
        self._normalizer = normalizer
        self._generator = candidate_generator
        self._unifier = feature_unifier
        self._constraints = constraint_validator
        self._ranker = candidate_ranker

    def analyse(self, word: str, pack: LanguagePack) -> AnalysisResult:
        normalized, _changed = self._normalizer.normalize(word, pack)

        # Candidate generation.
        raw_candidates = self._generator.generate(word, normalized, pack)

        # Build MorphologicalAnalysis candidates.
        analyses: list[MorphologicalAnalysis] = []
        for morphemes in raw_candidates:
            analysis = self._build_analysis(
                surface=word,
                normalized=normalized,
                morphemes=morphemes,
                pack=pack,
            )
            analyses.append(analysis)

        # Constraint validation.
        analyses = self._constraints.validate(analyses, pack)

        # Ranking.
        analyses = self._ranker.rank(analyses, pack)

        status = self._status(analyses)
        return AnalysisResult(
            surface=word,
            normalized=normalized,
            language=pack.code,
            status=status,
            analyses=analyses,
        )

    def _build_analysis(
        self,
        surface: str,
        normalized: str | None,
        morphemes: list[Morpheme],
        pack: LanguagePack,
    ) -> MorphologicalAnalysis:
        features: dict[str, object] = self._unifier.unify(morphemes, pack)
        lemma = None
        pos = None
        # The lemma/POS of an analysis come from the anchoring stem morpheme —
        # the morpheme type(s) the pack marks with `sources_lexicon: true`.
        stem_type_ids = {m.id for m in pack.morphemes if m.sources_lexicon}
        for morpheme in morphemes:
            if morpheme.type in stem_type_ids:
                lemma = morpheme.lemma or lemma
                pos = morpheme.pos or pos
        return MorphologicalAnalysis(
            surface=surface,
            normalized=normalized,
            lemma=lemma,
            pos=pos,
            morphemes=morphemes,
            features=features,
        )

    @staticmethod
    def _status(analyses: list[MorphologicalAnalysis]) -> AnalysisStatus:
        if not analyses:
            return AnalysisStatus.UNKNOWN_WORD
        if len(analyses) == 1:
            return AnalysisStatus.ANALYSED
        return AnalysisStatus.AMBIGUOUS
