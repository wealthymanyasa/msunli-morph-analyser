# Morphological Analyser — V1 Foundation

A reusable, **language-agnostic** morphological analysis platform. The core
engine contains **no language-specific linguistic rules**; all linguistic
knowledge lives in declarative **language packs** (data/configuration only,
zero executable Python code).

## Architecture

```
Client / Next.js UI
        ↓
     REST API            (src/morph/api/ — versioned /api/v1)
        ↓
 Application Service    (src/morph/service/analysis.py)
        ↓
 Morphology Engine      (src/morph/engine/)
        ↓
 Language Pack          (src/morph/domain/pack.py — declarative data)
```

The primary application operation is:

```text
analyze(word, language) -> AnalysisResult
```

## Package Layout

```
src/morph/
  __init__.py            Public API surface
  domain/
    __init__.py
    analysis.py          AnalysisResult, MorphologicalAnalysis, Morpheme, status
    pack.py              LanguagePack contract (declarative data models)
  engine/
    __init__.py
    interfaces.py        Normalizer, Lexicon, CandidateGenerator, Segmenter,
                         FeatureUnifier, ConstraintValidator, CandidateRanker,
                         AnalysisStrategy (ABCs)
    implementations.py   ConfigDriven, generic implementations
    strategy.py          DefaultAnalysisStrategy (pipeline orchestration)
    pack_validator.py    LanguagePackValidator
    factory.py           MorphologyEngine + default_engine() wiring
  loading/
    __init__.py          Generic YAML language-pack loader
  testing/
    __init__.py          Generic language-pack expectation harness
  service/
    analysis.py          AnalysisService (application service)
    bootstrap.py         Shared service construction for API + CLI
  api/
    __init__.py          create_app()
    app.py               FastAPI application (endpoints + OpenAPI)
    schemas.py           Typed request/response contracts
    __main__.py          python -m morph.api run entry point
  cli.py                 morph CLI (thin adapter over AnalysisService)
languages/
  shona/                 Declarative Shona language pack (YAML only)
tests/
  conftest.py            Sample (non-Shona) language pack fixtures
  test_domain.py
  test_pack_validator.py
  test_service.py
  test_engine.py
  test_loader.py
  test_shona.py
  test_ambiguity.py
  test_separation.py     Engine/language separation invariant
  test_testing.py        Generic expectation harness
  test_api.py            REST API contract tests
  test_cli.py            CLI tests
  test_integration.py    API/CLI consistency + bootstrap tests
```

## Domain Models

- **`LanguagePack`** — the complete declarative contract: metadata (code, name,
  semver `version`, `engine_compatibility`, `license`, `provenance`),
  `normalization`, `lexicon`, `morphemes`, `morphotactics`, `paradigms`,
  `constraints`, `ranking`, `noun_classes`, `resources` (per-resource
  provenance).
- **`Morpheme`** — a single ordered morpheme (surface, type, gloss, features,
  optional lemma).
- **`NounClass`** — a structured noun-class (mipanda) entry: identifier, label,
  subclass, underlying prefix(es), surface allomorphs, zero-prefix flag,
  singular/plural pairings, semantic tendencies, agreement, examples,
  provenance, confidence.
- **`MorphologicalRule`** — represented declaratively via `MorphotacticRule`
  (a pattern string interpreted by the engine).
- **`MorphologicalAnalysis`** — one candidate (surface, normalized, lemma, POS,
  ordered morphemes, features, score).
- **`AnalysisResult`** — per-word outcome preserving ambiguity: `surface`,
  `normalized`, `language`, `status`, `analyses` (zero, one or many), `error`.

Ambiguity is preserved: `AnalysisResult.analyses` may hold multiple candidates
and `AnalysisResult.is_ambiguous` reflects it. Valid candidates are **never
silently discarded**.

## Language Pack Loading

Packs ship as directories of YAML files (see `languages/shona/`). The generic
loader `morph.loading.load_language_pack` reads them and produces a validated
`LanguagePack`. Packs contain **zero executable Python**; the engine interprets
them generically.

## Engine Components

Each component is an interface (ABC) with a generic, config-driven
implementation. All behaviour is driven by the pack:

| Component (interface) | Implementation | Role |
| --- | --- | --- |
| `Normalizer` | `ConfigDrivenNormalizer` | applies pack normalization (lowercase + rules) |
| `Lexicon` | `PackLexicon` | looks up pack lexical entries |
| `CandidateGenerator` | `ConcatenativeCandidateGenerator` | morphotactics-driven segmentation |
| `Segmenter` | `PackSegmenter` | builds rich `Morpheme`s from codes |
| `FeatureUnifier` | `DefaultFeatureUnifier` | merges morpheme features |
| `ConstraintValidator` | `DefaultConstraintValidator` | applies pack constraints |
| `CandidateRanker` | `DefaultCandidateRanker` | deterministic ranking (lower score = better) |

`DefaultAnalysisStrategy` orchestrates the pipeline; `MorphologyEngine` is the
facade wiring everything together.

### Morphotactics-driven candidate generation

The `ConcatenativeCandidateGenerator` interprets each morphotactic rule as an
ordered sequence of morpheme tokens:
- **lexical tokens** (`sources_lexicon: true`, e.g. `stem`) match one of the
  lexicon stem surfaces;
- **affix tokens** match one of the morpheme's declared surface `aliases`
  (including empty-string zero realizations);
- a trailing `?` marks a token optional.

All valid segmentations covering the whole surface are produced; ambiguity is
preserved. This is a clean seam for future strategies
(`FSTStrategy`, `TwoLevelStrategy`, `NonConcatenativeStrategy`) without
touching the domain or API.

### Declarative constraints

The generic constraint validator interprets pack-declared constraint kinds,
including:
- `no_missing_required_features`: candidates must carry a required feature.
- `noun_class_agreement`: nominal prefix and stem must agree on noun class,
  where agreement (equal / `singular_of` / `plural_of`) is read from the pack's
  `noun_classes` resource. This rejects spurious shared-prefix (allomorph)
  readings without hard-coding Shona.

## Application Service

`AnalysisService` exposes the primary operation:

```python
from morph.service.analysis import create_service

service = create_service()
service.register_pack(pack_data)          # validated + registered by code
service.load_language_directory("languages/shona")  # or from YAML dir
result = service.analyze("word", "lang")  # -> AnalysisResult
service.languages()                       # registered language codes
```

Raises `UnknownLanguageError` for unregistered languages, and
`PackValidationError` for invalid packs. The API is the primary interface; a
future REST layer will consume this service directly.

## Language Pack Validation

A language pack is pure declarative data, validated by `LanguagePackValidator`
before use (both on manual registration and on YAML load), verifying:

- required metadata (code, name, version, engine_compatibility)
- schema validity (Pydantic `extra="forbid"`)
- semantic version of the pack
- engine compatibility (major-version match)
- resource integrity (non-empty lexicon/morphemes, no undefined morpheme refs)

Invalid or incompatible packs are rejected with clear, structured errors
(`PackValidationError` with a flat `errors` list).

## Engines / Language Separation

A dedicated architectural regression suite (`tests/test_separation.py`)
enforces the critical invariant: `src/morph/engine/` and `src/morph/domain/`
contain **no** Shona-specific linguistic content, and `languages/**` contains
**no** executable Python.

## Design Decisions

- **API-first**: the application service is the contract; frontend/UI is a
  consumer and never duplicates linguistic logic.
- **Language packs are data-only**: no executable Python in packs. The engine
  interprets them generically.
- **Ambiguity preserved**: engine never drops valid candidates.
- **Deterministic**: ranking is explicit and stable; no randomness.
- **Strong typing**: Pydantic v2 models for all contracts; ABCs for interfaces;
  strict mypy.
- **No scope creep**: no ML, hate-speech detection, ZILDAT integration, DBs or
  microservices in V1.

## Tests

```
pytest
```

Covers the validator, domain models, engine strategy/components, the
application service, the YAML loader, the Shona language pack (via its own
expectations file), ambiguity preservation, and the engine/language separation
invariant.

## Remaining V1 Work

- REST API layer consuming `AnalysisService` (FastAPI).
- Next.js UI as an API consumer.
- Expand the Shona lexicon/morphotactics and add paradigms/derivation.
- Structured logging and health checks.
- Packaging/CI readiness.

See `docs/LANGUAGE_PACK.md` for the language-pack and Shona-resource details.
