"""Language pack contract.

A language pack is a declarative, data-only description of how to analyse a
specific language. It must contain **zero executable Python code** — all
linguistic knowledge (lexicon, morphemes, morphotactics, paradigms,
constraints, ranking configuration) is expressed as configuration that the
generic engine interprets.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class LanguageMetadata(BaseModel):
    """Basic identity and provenance metadata for a language pack."""

    model_config = ConfigDict(frozen=True)

    code: str = Field(
        description="Short canonical language code, e.g. 'sn' for a specific language"
    )
    name: str = Field(description="Human-readable language name, e.g. 'Zulu'")
    version: str = Field(description="Semantic version of this pack, e.g. '1.0.0'")
    engine_compatibility: str = Field(
        description="Semantic version range of the engine this pack supports"
    )
    license: str = Field(description="SPDX license identifier or description")
    provenance: str | None = Field(
        default=None,
        description="Where the linguistic resources were sourced from",
    )
    author: str | None = Field(default=None)

    @field_validator("version")
    @classmethod
    def _valid_semver(cls, v: str) -> str:
        if not _SEMVER_RE.match(v):
            raise ValueError(f"version must be semantic version, got '{v}'")
        return v


class NormalizationConfig(BaseModel):
    """Declarative normalization rules.

    Rules are simple string replacements applied in order. This is deliberately
    generic; language-specific behaviour is expressed through the config.
    """

    model_config = ConfigDict(frozen=True)

    lowercase: bool = Field(default=False)
    rules: list[list[str]] = Field(
        default_factory=list,
        description="Ordered [pattern, replacement] pairs applied sequentially",
    )


class LexicalEntry(BaseModel):
    """A single lexical entry (root/lemma) with its features."""

    model_config = ConfigDict(frozen=True)

    surface: str = Field(description="Surface form of the lexical entry")
    lemma: str | None = Field(default=None)
    pos: str | None = Field(default=None)
    features: dict[str, Any] = Field(default_factory=dict)


class MorphemeSpec(BaseModel):
    """Declarative specification of a morpheme type available in a language.

    ``sources_lexicon`` marks a morpheme that is realised by lexical stem
    surfaces (e.g. ``stem``) rather than by a fixed ``aliases`` list. Exactly
    one such anchoring morpheme is expected per morphotactic path so the
    candidate generator can look up the lexicon for that span.
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(description="Unique identifier of the morpheme type")
    aliases: list[str] = Field(
        default_factory=list,
        description="Surface strings that realize this morpheme (e.g. a suffix). "
        "An empty string ('') declares a zero/null realization.",
    )
    sources_lexicon: bool = Field(
        default=False,
        description="True if this morpheme is realised by lexical stem surfaces "
        "matched from the lexicon rather than a fixed alias list.",
    )
    features: dict[str, Any] = Field(
        default_factory=dict,
        description="Features contributed when this morpheme is present",
    )


class MorphotacticRule(BaseModel):
    """Declarative morphotactic rule describing a legal morpheme sequence.

    A rule string is provided by the language pack (e.g. ``prefix* root suffix?``).
    The engine parses and interprets it; it contains no logic itself.
    """

    model_config = ConfigDict(frozen=True)

    sequence: str = Field(description="Morphotactic pattern over morpheme type ids")
    id: str | None = Field(default=None)


class Paradigm(BaseModel):
    """Declarative inflectional paradigm."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str | None = None
    cells: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Paradigm cells; shape defined by the language pack",
    )


class Constraint(BaseModel):
    """Declarative constraint a valid analysis must satisfy."""

    model_config = ConfigDict(frozen=True)

    id: str
    description: str | None = None
    kind: str = Field(description="Constraint kind interpreted by the engine")
    params: dict[str, Any] = Field(default_factory=dict)


class RankingConfig(BaseModel):
    """Deterministic ranking configuration for candidate analyses."""

    model_config = ConfigDict(frozen=True)

    prefer_lemmas: bool = Field(default=False)
    penalties: dict[str, float] = Field(
        default_factory=dict,
        description="Named penalties (e.g. 'longer_segmentation') with weights",
    )


class NounClass(BaseModel):
    """A structured representation of a noun class.

    Noun classes are deliberately NOT reduced to a flat ``prefix -> class``
    dictionary. Multiple surface forms may realise the same class (allomorphy),
    and the same surface form may appear under several classes (shared/null
    forms). Those distinctions are expressed declaratively here and interpreted
    by the generic engine.
    """

    model_config = ConfigDict(frozen=True)

    identifier: str = Field(
        description="Canonical noun class identifier, e.g. '1', '7', '2a'"
    )
    label: str | None = Field(
        default=None, description="Human-readable class label, e.g. 'mu/va'"
    )
    subclass: str | None = Field(
        default=None, description="Subclass identifier, e.g. 'a' within class 1"
    )
    prefixes: list[str] = Field(
        default_factory=list,
        description="Underlying morpheme(s) that realise this class",
    )
    surface_allomorphs: list[str] = Field(
        default_factory=list,
        description="Surface/allomorphic variants including zero where applicable",
    )
    has_zero_prefix: bool = Field(
        default=False,
        description="True if this class may be realised by a null/zero prefix",
    )
    singular_of: str | None = Field(
        default=None,
        description="Plural class this class pairs with (for singular classes)",
    )
    plural_of: str | None = Field(
        default=None,
        description="Singular class this class pairs with (for plural classes)",
    )
    semantic_tendencies: list[str] = Field(
        default_factory=list,
        description="Semantic tendencies described for this class",
    )
    agreement: list[str] = Field(
        default_factory=list,
        description="Agreement markers/concords described for this class",
    )
    examples: list[str] = Field(
        default_factory=list,
        description="Representative lexical examples",
    )
    dialectal_register: str | None = Field(
        default=None,
        description="Dialectal or register notes",
    )
    provenance: str | None = Field(default=None)
    status: str | None = Field(
        default=None,
        description="Confidence/status, e.g. 'draft', 'attested', 'disputed'",
    )


class ResourceProvenance(BaseModel):
    """Provenance for a named resource within a language pack."""

    model_config = ConfigDict(frozen=True)

    resource: str = Field(description="Resource section name, e.g. 'lexicon'")
    source: str = Field(description="Source of the linguistic data")
    notes: str | None = None


class LanguagePack(BaseModel):
    """The complete declarative contract for a language.

    Contained entirely as data; never Python code.
    """

    model_config = ConfigDict(frozen=False, extra="forbid")

    # Declared separately (not nested) so the validator can check metadata that
    # duplicates required fields. Kept simple: metadata carries the identity.
    metadata: LanguageMetadata
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    lexicon: list[LexicalEntry] = Field(default_factory=list)
    morphemes: list[MorphemeSpec] = Field(default_factory=list)
    morphotactics: list[MorphotacticRule] = Field(default_factory=list)
    paradigms: list[Paradigm] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    ranking: RankingConfig = Field(default_factory=RankingConfig)
    noun_classes: list[NounClass] = Field(
        default_factory=list,
        description="Structured noun class resource",
    )
    resources: list[ResourceProvenance] = Field(
        default_factory=list,
        description="Provenance notes for the pack's individual resources",
    )
    raw: dict[str, Any] | None = Field(
        default=None,
        description="Optional original raw pack for provenance/inspection",
    )

    @property
    def code(self) -> str:
        return self.metadata.code
