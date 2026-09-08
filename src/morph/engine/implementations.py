"""Concrete, language-agnostic implementations of the engine components.

These implementations interpret declarative language packs generically. They
contain no language-specific rules — all behaviour is driven by the data in a
language pack.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from morph.domain.analysis import Morpheme, MorphologicalAnalysis
from morph.domain.pack import Constraint, LanguagePack, LexicalEntry, MorphemeSpec
from morph.engine import interfaces


class ConfigDrivenNormalizer(interfaces.Normalizer):
    """Normalizes based purely on a pack's NormalizationConfig.

    Applies (in order): optional lowercasing, then each ordered
    ``[pattern, replacement]`` rule. Patterns are interpreted as regular
    expressions; replacements may reference capture groups.
    """

    def normalize(self, surface: str, pack: LanguagePack) -> tuple[str, bool]:
        result = surface
        if pack.normalization.lowercase:
            result = result.lower()
        for pattern, replacement in pack.normalization.rules:
            compiled = re.compile(pattern)
            result = compiled.sub(replacement, result)
        return result, result != surface


class DefaultFeatureUnifier(interfaces.FeatureUnifier):
    """Merges each morpheme's feature dict into a single surface analysis.

    Ordinarily, features are merged in morpheme order (later wins). However,
    for grammatical features that are *headed by the affix* on the surface —
    ``noun_class`` and ``number`` — an affix marker expresses the surface
    value directly (e.g. the plural class marked by a plural prefix), so it
    takes precedence over the stem's lemma-level value. Stems identified via
    the pack's ``sources_lexicon`` morphemes therefore yield to affixes for
    these keys.

    For stacked prefixes, the OUTERMOST (leftmost) prefix heads these features:
    the outer marker determines the surface noun class, so in ``ku-chi-koro``
    the analysis is class 17, not the inner class 7 (nor the stem's). Prefix
    ordering is surface-token order (prefixes precede the stem); suffixes still
    merge later-wins, so a plural suffix still overrides a singular stem.
    """

    _PREFIX_HEADED_FEATURES = frozenset({"noun_class", "number"})

    def unify(self, morphemes: list[Morpheme], pack: LanguagePack) -> dict[str, object]:
        stem_type_ids = {m.id for m in pack.morphemes if m.sources_lexicon}
        stem_idx = next(
            (i for i, m in enumerate(morphemes) if m.type in stem_type_ids),
            len(morphemes),
        )
        merged: dict[str, object] = {}
        for i, morpheme in enumerate(morphemes):
            is_stem = morpheme.type in stem_type_ids
            for key, value in morpheme.features.items():
                headed = key in self._PREFIX_HEADED_FEATURES
                if not headed:
                    merged[key] = value
                    continue
                if is_stem and key in merged:
                    continue  # stems yield to affixes for headed features
                if i < stem_idx and key in merged:
                    continue  # the outermost (leftmost) prefix heads these
                merged[key] = value
        return merged


class DefaultConstraintValidator(interfaces.ConstraintValidator):
    """Applies the simplest constraint kinds generically.

    Supported ``kind`` values (interpreted from pack data, not hard-coded to a
    language):
      - ``no_missing_required_features``: rejects candidates lacking every
        feature named in ``params.required``.
      - ``noun_class_agreement``: for nominal analyses, requires the noun class
        of every affix (prefix) to agree with the stem's class, where agreement
        means equal, or the stem's class is the declared ``singular_of`` or
        ``plural_of`` of the affix class. The pairings are read from the pack's
        ``noun_classes`` resource (declarative), so the engine knows nothing
        specific to any particular language. A pack may declare
        ``params.outer_classes`` — locative/diminutive-style classes that are
        exempt from agreement only when they stack EXTERNALLY over an inner
        agreeing prefix (e.g. class 17 ``ku-`` over class 7 ``chi-`` in
        ``ku-chi-koro``). A single such affix over a disagreeing stem is still
        rejected, and non-exempt affixes must still agree.
      - ``affix_stem_pos``: restricts which noun class affixes may attach to a
        stem of a given POS. ``params.stem_pos`` names the POS and
        ``params.affix_classes`` lists the permitted class ids for noun class
        prefixes on such stems. This lets a pack express e.g. that verbal stems
        only take the infinitive class and not a homophonous locative class,
        keeping the rule declarative and language-agnostic.
      - ``slot_stem_pos``: restricts which POS the anchoring stem may have when
        a specific construction is present. ``params.affix_ids`` names the
        affix morphemes that characterise the construction (e.g. subject
        agreement / tense-aspect markers) and ``params.stem_pos`` names the
        only POS allowed for the lexicon stem in those constructions. This lets
        a pack express e.g. that a conjugated-verb slot may only contain verb
        stems, so a subject-agreement prefix cannot attach to a noun stem.

    Unknown constraint kinds are ignored (their enforcement is out of scope).
    """

    def validate(
        self,
        analysis_candidates: list[MorphologicalAnalysis],
        pack: LanguagePack,
    ) -> list[MorphologicalAnalysis]:
        if not pack.constraints:
            return analysis_candidates

        stem_type_ids = {m.id for m in pack.morphemes if m.sources_lexicon}
        class_pairings = self._class_pairings(pack)

        valid: list[MorphologicalAnalysis] = []
        for candidate in analysis_candidates:
            accepted = True
            for constraint in pack.constraints:
                if not self._satisfied(
                    candidate, constraint, stem_type_ids, class_pairings
                ):
                    accepted = False
                    break
            if accepted:
                valid.append(candidate)
        return valid

    @staticmethod
    def _class_pairings(pack: LanguagePack) -> dict[str, list[str]]:
        """Map each class id to the set of classes it agrees with.

        A class agrees with itself, plus its declared singular and plural
        partners.
        """
        pairings: dict[str, list[str]] = {}
        for nc in pack.noun_classes:
            partners = {nc.identifier}
            if nc.singular_of:
                partners.add(nc.singular_of)
            if nc.plural_of:
                partners.add(nc.plural_of)
            pairings[nc.identifier] = sorted(partners)
        return pairings

    @staticmethod
    def _satisfied(
        candidate: MorphologicalAnalysis,
        constraint: Constraint,
        stem_type_ids: set[str],
        class_pairings: dict[str, list[str]],
    ) -> bool:
        if constraint.kind == "no_missing_required_features":
            required = set(constraint.params.get("required", []) or [])
            present = set(candidate.features)
            missing = required - present
            return not missing
        if constraint.kind == "noun_class_agreement":
            return DefaultConstraintValidator._noun_class_agreement(
                candidate, stem_type_ids, class_pairings, constraint.params
            )
        if constraint.kind == "affix_stem_pos":
            return DefaultConstraintValidator._affix_stem_pos(
                candidate, stem_type_ids, constraint.params
            )
        if constraint.kind == "slot_stem_pos":
            return DefaultConstraintValidator._slot_stem_pos(
                candidate, stem_type_ids, constraint.params
            )
        # Unknown constraint kinds: no-op (out of scope for V1).
        return True

    @staticmethod
    def _noun_class_agreement(
        candidate: MorphologicalAnalysis,
        stem_type_ids: set[str],
        class_pairings: dict[str, list[str]],
        params: dict[str, Any],
    ) -> bool:
        stem_class: str | None = None
        affix_classes: list[str] = []
        for m in candidate.morphemes:
            if "noun_class" not in m.features:
                continue
            if m.type in stem_type_ids:
                stem_class = str(m.features["noun_class"])
            else:
                affix_classes.append(str(m.features["noun_class"]))

        if stem_class is None or not affix_classes:
            return True

        # An outermost locative-style affix may override the stem's class, but
        # ONLY when it stacks over an inner agreeing prefix (ku-chi-koro is a
        # valid construction; a bare ku- over a class-7 stem is not). The exempt
        # classes are declared per-pack via params.outer_classes; exemption
        # applies to the left-most (outermost) affix and only when more than one
        # affix is present, so every other affix still has to agree.
        outer_classes = set(params.get("outer_classes", []) or [])
        first_required = 0
        if len(affix_classes) > 1 and affix_classes[0] in outer_classes:
            first_required = 1

        allowed = set(class_pairings.get(stem_class, [stem_class]))
        return all(ac in allowed for ac in affix_classes[first_required:])

    @staticmethod
    def _affix_stem_pos(
        candidate: MorphologicalAnalysis,
        stem_type_ids: set[str],
        params: dict[str, Any],
    ) -> bool:
        stem_pos = params.get("stem_pos")
        allowed = set(params.get("affix_classes", []) or [])
        if not stem_pos or not allowed:
            return True

        for m in candidate.morphemes:
            if m.type not in stem_type_ids:
                continue
            if m.pos != stem_pos:
                return True  # restriction applies only to this stem POS
            for affix in candidate.morphemes:
                if affix.type in stem_type_ids:
                    continue
                if (
                    "noun_class" in affix.features
                    and str(affix.features["noun_class"]) not in allowed
                ):
                    return False
        return True

    @staticmethod
    def _slot_stem_pos(
        candidate: MorphologicalAnalysis,
        stem_type_ids: set[str],
        params: dict[str, Any],
    ) -> bool:
        affix_ids = params.get("affix_ids")
        if not affix_ids:
            return True
        stem_pos = params.get("stem_pos")
        if not stem_pos:
            return True

        affix_id_set = set(affix_ids)
        construction_present = any(
            m.type not in stem_type_ids and m.type in affix_id_set
            for m in candidate.morphemes
        )
        if not construction_present:
            return True  # restriction applies only in this construction

        for m in candidate.morphemes:
            if m.type not in stem_type_ids:
                continue
            if m.pos != stem_pos:
                return False
        return True


class DefaultCandidateRanker(interfaces.CandidateRanker):
    """Deterministic ranking.

    Scores each candidate using pack.ranking.penalties. Lower score is better.
    Candidates with a resolved lemma are preferred when
    ``ranking.prefer_lemmas`` is set. Ties are broken by (stable) insertion
    order, keeping output deterministic.
    """

    def rank(
        self, candidates: list[MorphologicalAnalysis], pack: LanguagePack
    ) -> list[MorphologicalAnalysis]:
        scored: list[MorphologicalAnalysis] = []
        for candidate in candidates:
            score = self._score(candidate, pack)
            scored.append(candidate.model_copy(update={"score": score}))
        scored.sort(key=lambda c: c.score if c.score is not None else float("inf"))
        return scored

    def _score(self, candidate: MorphologicalAnalysis, pack: LanguagePack) -> float:
        score = 0.0
        config = pack.ranking
        if config.prefer_lemmas and candidate.lemma is None:
            score += config.penalties.get("no_lemma", 1.0)
        longer = len(candidate.morphemes) - 1
        if longer > 0:
            score += config.penalties.get("longer_segmentation", 0.0) * longer
        return score


# ── Morphotactics-driven candidate generation ──────────────────────────────────


@dataclass(frozen=True)
class _TokenSpec:
    """A single token in a parsed morphotactic rule sequence."""

    morpheme_id: str
    optional: bool


def _parse_morphotactic_tokens(sequence: str) -> list[_TokenSpec]:
    """Parse a morphotactic sequence string into ordered token specs.

    Grammar (space-separated tokens):
        ``foo``   — required single occurrence of morpheme ``foo``
        ``foo?``  — optional single occurrence of morpheme ``foo``
    """
    tokens: list[_TokenSpec] = []
    for raw in sequence.split():
        optional = raw.endswith("?")
        morpheme_id = raw.rstrip("?") if optional else raw
        if morpheme_id:
            tokens.append(_TokenSpec(morpheme_id=morpheme_id, optional=optional))
    return tokens


def _build_morpheme_index(pack: LanguagePack) -> dict[str, MorphemeSpec]:
    return {m.id: m for m in pack.morphemes}


class ConcatenativeCandidateGenerator(interfaces.CandidateGenerator):
    """Generates candidate segmentations driven by declarative morphotactics.

    For each morphotactic rule in the language pack, this generator attempts
    to segment the normalized surface form by matching tokens left-to-right:

    - **lexical tokens** (``sources_lexicon=True``): the span must match the
      surface of a lexicon entry; this segment becomes the stem/root.
    - **affix tokens** (``sources_lexicon=False``): the span must match one of
      the morpheme's declared ``aliases`` (surface realizations).
    - **optional tokens** may be skipped.

    In addition, closed-class entries (``pack.closed_class``) describe lexical
    units with **no segmentation**. When the whole normalized surface matches a
    closed-class entry exactly, that single whole-word candidate is returned
    and no affixal segmentation is attempted.

    All valid segmentations that cover the entire surface form are yielded;
    ambiguity is never silently discarded.
    """

    #: Type id assigned to whole-word closed-class morphemes in analyses. This
    #: is a generic engine concept, not a language-pack-defined morpheme id.
    CLOSED_CLASS_TYPE = "closed_class"

    def generate(
        self, surface: str, normalized: str, pack: LanguagePack
    ) -> list[list[Morpheme]]:
        closed_class = self._closed_class_candidate(normalized, pack)
        if closed_class is not None:
            return [[closed_class]]

        morpheme_index = _build_morpheme_index(pack)
        lexicon_stems = self._build_lexicon_stem_index(pack)

        all_candidates: list[list[Morpheme]] = []
        for rule in pack.morphotactics:
            token_specs = _parse_morphotactic_tokens(rule.sequence)
            if not token_specs:
                continue
            self._generate_for_rule(
                token_specs,
                normalized,
                morpheme_index,
                lexicon_stems,
                0,
                0,
                [],
                all_candidates,
            )
        return all_candidates

    @staticmethod
    def _closed_class_candidate(normalized: str, pack: LanguagePack) -> Morpheme | None:
        """Return a whole-word morpheme when ``normalized`` is a closed-class entry.

        Closed-class items are single lexical units: the morpheme carries the
        entry's lemma/POS/features and equals the whole surface span.
        """
        for entry in pack.closed_class:
            if entry.surface == normalized:
                return Morpheme(
                    surface=normalized,
                    type=ConcatenativeCandidateGenerator.CLOSED_CLASS_TYPE,
                    lemma=entry.lemma or normalized,
                    pos=entry.pos,
                    features=dict(entry.features),
                )
        return None

    @staticmethod
    def _build_lexicon_stem_index(
        pack: LanguagePack,
    ) -> dict[str, list[LexicalEntry]]:
        stems: dict[str, list[LexicalEntry]] = defaultdict(list)
        for entry in pack.lexicon:
            stems[entry.surface].append(entry)
        return dict(stems)

    def _generate_for_rule(
        self,
        token_specs: list[_TokenSpec],
        surface: str,
        morpheme_index: dict[str, MorphemeSpec],
        lexicon_stems: dict[str, list[LexicalEntry]],
        token_idx: int,
        offset: int,
        current: list[Morpheme],
        out: list[list[Morpheme]],
    ) -> None:
        if token_idx == len(token_specs):
            if offset == len(surface):
                out.append(list(current))
            return

        spec_token = token_specs[token_idx]
        morpheme_spec = morpheme_index.get(spec_token.morpheme_id)
        if morpheme_spec is None:
            return

        if morpheme_spec.sources_lexicon:
            # Try all lexicon stems that start at current offset
            remaining = surface[offset:]
            for stem_surface, entries in sorted(lexicon_stems.items()):
                if remaining.startswith(stem_surface):
                    for entry in entries:
                        morpheme = Morpheme(
                            surface=stem_surface,
                            type=spec_token.morpheme_id,
                            lemma=entry.lemma,
                            pos=entry.pos,
                            gloss=spec_token.morpheme_id,
                            features=dict(entry.features),
                        )
                        self._generate_for_rule(
                            token_specs,
                            surface,
                            morpheme_index,
                            lexicon_stems,
                            token_idx + 1,
                            offset + len(stem_surface),
                            current + [morpheme],
                            out,
                        )
        else:
            # Try all aliases at current offset
            remaining = surface[offset:]
            for alias in sorted(morpheme_spec.aliases):
                if remaining.startswith(alias):
                    morpheme = Morpheme(
                        surface=alias,
                        type=spec_token.morpheme_id,
                        gloss=spec_token.morpheme_id,
                        features=dict(morpheme_spec.features),
                    )
                    self._generate_for_rule(
                        token_specs,
                        surface,
                        morpheme_index,
                        lexicon_stems,
                        token_idx + 1,
                        offset + len(alias),
                        current + [morpheme],
                        out,
                    )

            # If optional, also try skipping this token
            if spec_token.optional:
                self._generate_for_rule(
                    token_specs,
                    surface,
                    morpheme_index,
                    lexicon_stems,
                    token_idx + 1,
                    offset,
                    current,
                    out,
                )
