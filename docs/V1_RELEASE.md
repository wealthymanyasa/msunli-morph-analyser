# MSUNLI Morph Analyser — V1 Release Documentation

A reusable, **language-agnostic** morphological analysis platform for building
NLP tools for under-resourced languages.

---

## 1. Executive Summary

The MSUNLI Morph Analyser V1 is a deterministic, morphotactics-driven
morphological analysis engine that separates **generic morphology algorithms**
from **declarative linguistic resources**. New languages are added as language
packs (YAML data only, zero executable Python) without modifying the core
engine.

**V1 delivers:**

- Generic morphology engine with 7 configurable pipeline components
- Declarative Shona (`sn`) language pack (108 gold-standard test records)
- REST API (`/api/v1`) with interactive OpenAPI documentation
- CLI (`morph`) for terminal-based analysis
- Language-independent evaluation framework
- 102 automated tests, all passing
- Clean ruff lint, clean mypy type checking
- Docker support, CI/CD pipeline, dependency locking

---

## 2. V1 Release Status

**Status: COMPLETE AND TEST-VERIFIED**

| Metric | Value |
| --- | --- |
| Version | `1.0.0` |
| Source files | 24 |
| Test files | 15 |
| Tests passing | 102 |
| Gold records | 108 (84 analysed, 24 unknown) |
| Analysis accuracy | 100.0% |
| Morpheme F1 | 100.0% |
| Ruff lint | Clean |
| Mypy type check | Clean (24 source files) |

### V1 Scope

V1 intentionally does **not** include:

- ML models
- Hate-speech detection
- ZILDAT integration
- Language-specific executable code
- Unnecessary microservices or infrastructure

---

## 3. Architecture

The central design principle is:

> **Engine = generic algorithms and software. Language pack = declarative
> linguistic knowledge.**

```text
Client
  |
  +-- REST API (FastAPI, /api/v1)
  |
  +-- CLI (Typer, `morph`)
       |
       v
Application Service (AnalysisService)
       |
       v
Language Registry
       |
       v
Validated Language Pack (declarative YAML)
       |
       v
Generic Morphology Engine
       |
       +-- Normalizer
       +-- Lexicon
       +-- Candidate Generator
       +-- Segmenter
       +-- Feature Unifier
       +-- Constraint Validator
       +-- Candidate Ranker
       |
       v
AnalysisResult
```

### Design Principles

- **API-first**: the application service is the contract
- **Language packs are data-only**: no executable Python in packs
- **Ambiguity preserved**: engine never drops valid candidates
- **Deterministic**: ranking is explicit and stable; no randomness
- **Strong typing**: Pydantic v2 models, ABCs, strict mypy
- **No scope creep**: focused V1 scope

---

## 4. Package Layout

```text
src/morph/
    __init__.py              Public API surface
    version.py               Single source of truth for version
    logging.py               Centralized logging configuration
    cli.py                   CLI (Typer adapter)
    domain/
        analysis.py          AnalysisResult, MorphologicalAnalysis, Morpheme
        pack.py              LanguagePack, NounClass, morphotactic models
    engine/
        interfaces.py        ABC contracts (Normalizer, Lexicon, etc.)
        implementations.py   Config-driven generic implementations
        strategy.py          DefaultAnalysisStrategy (pipeline orchestration)
        pack_validator.py    LanguagePackValidator
        factory.py           MorphologyEngine facade + default_engine()
    loading/
        __init__.py          YAML language-pack loader
    service/
        analysis.py          AnalysisService (application service)
        bootstrap.py         Shared service construction
    api/
        __init__.py          create_app()
        app.py               FastAPI application + endpoints
        schemas.py           Request/response contracts
        middleware.py         Request logging middleware
        __main__.py          python -m morph.api entry point
    evaluation/
        __init__.py          Evaluation framework + gold dataset scoring
    testing/
        __init__.py          Language-independent test harness

languages/
    shona/                   Declarative Shona language pack
        manifest.yaml
        normalization.yaml
        lexicon.yaml
        morphemes.yaml
        morphotactics.yaml
        paradigms.yaml
        constraints.yaml
        ranking.yaml
        noun_classes.yaml
        resources.yaml
        tests/analyses.yaml
        evaluation/gold.yaml

tests/                       15 test files, 102 tests
docs/                        4 existing docs + this document
```

---

## 5. Domain Models

### LanguagePack

The complete declarative contract for a language. Contains:

- `metadata` (code, name, version, engine_compatibility, license, provenance)
- `normalization` (lowercase flag, custom rules)
- `lexicon` (surface/lemma/POS/features per stem)
- `morphemes` (affix/stem definitions with aliases and features)
- `morphotactics` (valid morpheme sequences)
- `paradigms` (reserved for future use)
- `constraints` (declarative validation rules)
- `ranking` (deterministic scoring configuration)
- `noun_classes` (mipanda structure with agreement relations)
- `resources` (per-resource provenance)

### AnalysisResult

Per-word outcome preserving ambiguity:

- `surface`: original input
- `normalized`: post-normalization form
- `language`: language code
- `status`: `analysed` | `ambiguous` | `unknown_word` | `error`
- `analyses`: zero, one, or many `MorphologicalAnalysis` candidates
- `error`: optional error message

### MorphologicalAnalysis

One candidate analysis:

- `surface`, `normalized`
- `lemma`, `pos` (from anchoring stem morpheme)
- `morphemes`: ordered list of `Morpheme` objects
- `features`: unified grammatical features
- `score`: deterministic ranking score

### Morpheme

A single morpheme in an analysis:

- `surface`: realized form
- `type`: morpheme type id (e.g. `stem`, `noun-class-1`)
- `gloss`: optional human-readable gloss
- `features`: morpheme-level features
- `lemma`, `pos`: optional lexical information

---

## 6. Engine Components

| Component | Interface | Implementation | Role |
| --- | --- | --- | --- |
| Normalizer | `Normalizer` | `ConfigDrivenNormalizer` | Lowercase + custom rules |
| Lexicon | `Lexicon` | `PackLexicon` | Stem lookup |
| Candidate Generator | `CandidateGenerator` | `ConcatenativeCandidateGenerator` | Morphotactics-driven segmentation |
| Feature Unifier | `FeatureUnifier` | `DefaultFeatureUnifier` | Merge morpheme features |
| Constraint Validator | `ConstraintValidator` | `DefaultConstraintValidator` | Apply pack constraints |
| Candidate Ranker | `CandidateRanker` | `DefaultCandidateRanker` | Deterministic scoring |

### Morphotactics-Driven Generation

The `ConcatenativeCandidateGenerator` interprets morphotactic rules as ordered
sequences of morpheme tokens:

- **Lexical tokens** (`sources_lexicon: true`) match lexicon stems
- **Affix tokens** match declared surface aliases (including zero-realization)
- Trailing `?` marks optional tokens

All valid segmentations are produced; ambiguity is preserved.

### Declarative Constraints

Pack-declared constraint kinds include:

- `no_missing_required_features`: candidates must carry required features
- `noun_class_agreement`: prefix-stem agreement via noun class relations
- `affix_stem_pos`: affix restricted to specific POS

---

## 7. Language Pack Contract

Each pack is a directory of YAML files under `languages/<code>/`:

```text
languages/<code>/
    manifest.yaml        Required - metadata
    normalization.yaml   Optional - normalization config
    lexicon.yaml         Optional - stem inventory
    morphemes.yaml       Optional - affix/stem definitions
    morphotactics.yaml   Optional - valid morpheme sequences
    paradigms.yaml       Optional - reserved
    constraints.yaml     Optional - declarative constraints
    ranking.yaml         Optional - scoring config
    noun_classes.yaml    Optional - noun class resource
    resources.yaml       Optional - provenance
    tests/analyses.yaml  Language-specific test expectations
```

### Validation

Packs are validated by `LanguagePackValidator` before use:

- Required metadata (code, name, version, engine_compatibility)
- Schema validity (Pydantic `extra="forbid"`)
- Semantic version validation
- Engine compatibility (major-version match)
- Resource integrity (non-empty lexicon/morphemes, no undefined refs)

Invalid packs are rejected with structured errors.

---

## 8. Shona Language Pack

Shona (`sn`) is the first language pack and reference implementation.

### Resources

| Resource | Description |
| --- | --- |
| `lexicon.yaml` | Shona noun/verb stems with POS and features |
| `morphemes.yaml` | Noun class prefixes, verb extensions, derivational affixes |
| `morphotactics.yaml` | Noun and verb word formation patterns |
| `constraints.yaml` | Noun class agreement, affix POS constraints |
| `noun_classes.yaml` | 16+ noun classes with singular/plural pairings |
| `ranking.yaml` | Lemma preference, scoring penalties |

### Evaluation

Gold dataset: 108 records (84 analysed, 24 unknown words).

| Metric | Value |
| --- | --- |
| Status accuracy | 100.0% |
| Analysis accuracy | 100.0% |
| Lemma accuracy | 100.0% |
| POS accuracy | 100.0% |
| Segmentation accuracy | 100.0% |
| Feature accuracy | 100.0% |
| Morpheme F1 | 100.0% |

---

## 9. Application Service

`AnalysisService` is the primary application interface:

```python
from morph.service.analysis import create_service

service = create_service()
service.load_language_directory("languages/shona")

result = service.analyze("murume", "sn")
print(result.status)       # AnalysisStatus.ANALYSED
print(result.analyses[0].lemma)  # "murume"
```

### Methods

- `register_pack(data)`: validate and register from dict
- `load_language_directory(path)`: load from YAML directory
- `analyze(word, language)`: primary analysis operation
- `languages()`: list registered language codes
- `get_pack(code)`: retrieve a registered pack

### Errors

- `UnknownLanguageError`: unregistered language code
- `PackValidationError`: invalid language pack data

---

## 10. REST API

Versioned REST API under `/api/v1`:

```bash
python -m morph.api --port 8000
```

### Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Health check (version, uptime, languages) |
| GET | `/api/v1/languages` | List registered language packs |
| POST | `/api/v1/analyze` | Analyse a single word |
| POST | `/api/v1/analyze/batch` | Analyse multiple words |

### Health Response

```json
{
  "status": "ok",
  "version": "1.0.0",
  "commit": "unknown",
  "uptime_seconds": 12.3,
  "languages_count": 1,
  "languages": [{"code": "sn", "version": "0.1.0"}]
}
```

### Features

- Request/response logging middleware
- Structured error responses (422 validation, 404 not found, 503 unavailable)
- Interactive Swagger UI at `/docs`
- OpenAPI JSON at `/api/v1/openapi.json`

---

## 11. CLI

The `morph` command:

```bash
morph version                    # Show version
morph languages                  # List registered packs
morph analyze --language sn murume     # Analyse one word
morph analyze --language sn --file words.txt  # Batch from file
```

### Output Format

```text
surface:  murume
normalized: murume
language: sn
status:   analysed
  [1] lemma=murume, pos=noun, score=0.100
      mu  (type=noun-class-1)
      rume  (type=stem)
      features: noun_class=1, number=singular
--- murume ---
```

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 2 | Usage/application error |

---

## 12. Evaluation Framework

Language-independent evaluation (`src/morph/evaluation/`):

### Metrics

- **Status accuracy**: predicted status equals gold
- **Analysis accuracy**: status + lemma + POS + segmentation + features match
- **Per-slot accuracy**: lemma, POS, segmentation, feature individually
- **Morpheme P/R/F1**: token-level overlap with multiset handling

### Usage

```python
from morph.evaluation import run_evaluation

report = run_evaluation(service, "sn", "languages/shona/evaluation/gold.yaml")
print(report.render_markdown())
```

### Gold Dataset

- Format: YAML list of `GoldRecord` entries
- Each record: surface, status, analyses (with lemma, POS, morphemes, features)
- Shona: 108 records, 100% accuracy against verified engine output

---

## 13. Testing & Quality Assurance

### Test Suite

| Test File | Purpose |
| --- | --- |
| `test_domain.py` | Domain model validation |
| `test_engine.py` | Engine component tests |
| `test_pack_validator.py` | Pack validation logic |
| `test_service.py` | Application service |
| `test_loader.py` | YAML pack loading |
| `test_shona.py` | Shona integration |
| `test_ambiguity.py` | Ambiguity preservation |
| `test_separation.py` | Engine/language separation invariant |
| `test_api.py` | REST API contract |
| `test_cli.py` | CLI behaviour |
| `test_integration.py` | Cross-layer integration |
| `test_evaluation.py` | Evaluation framework |
| `test_language_expansion.py` | Language-agnostic proof |
| `test_testing.py` | Test harness itself |

### Quality Gates

- **Ruff**: lint + format checks
- **Mypy**: strict type checking (Python 3.11)
- **Pytest**: 102 tests, all passing

### Separation Invariant

`tests/test_separation.py` enforces:

- `src/morph/engine/` contains **no** Shona-specific content
- `src/morph/domain/` contains **no** Shona-specific content
- `languages/**` contains **no** executable Python

---

## 14. Operational Readiness

### Versioning

- Single source of truth: `src/morph/version.py` (`__version__ = "1.0.0"`)
- Consistent across `pyproject.toml`, FastAPI metadata, evaluation framework
- CLI exposes `morph version` command

### Logging

- Centralized configuration: `src/morph/logging.py`
- Request/response middleware: `src/morph/api/middleware.py`
- Environment variable: `MORPH_LOG_LEVEL` (default: INFO)
- Applied to API server and CLI

### Health Check

Enhanced `/api/v1/health` returns:

- `version`: application version
- `commit`: git commit hash (from `MORPH_GIT_COMMIT` env)
- `uptime_seconds`: process uptime
- `languages_count`: registered pack count
- `languages`: list with code and version

### CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- Triggers: push to main/master, pull requests
- Matrix: Python 3.11, 3.12
- Steps: ruff check, ruff format, mypy, pytest, build
- Build artifact upload

### Dependency Locking

- `uv.lock` for reproducible installs
- `uv` as the package manager

### Docker

- Multi-stage `Dockerfile` (builder + runtime)
- Non-root user (`morph`)
- Health check built-in
- `docker-compose.yml` for local development

### Packaging

- `pyproject.toml` with setuptools backend
- Console script: `morph`
- Project URLs, license (MIT), classifiers

---

## 15. V1 Limitations & Known Issues

### Linguistic Limitations

- Limited Shona lexical coverage (expandable via `lexicon.yaml`)
- Limited morphological paradigms (paradigms section reserved)
- Limited derivational morphology
- Limited morphophonological handling
- Conservative treatment of locative and disputed noun-class analyses
- Evaluation coverage will expand with additional verified resources

### Technical Limitations

- Single-threaded analysis (no async engine pipeline)
- No caching layer for repeated analyses
- No persistence/database
- No streaming for large batch requests
- No authentication/authorization on API

### Scope Exclusions

These are **intentionally** excluded from V1:

- ML models and neural approaches
- Hate-speech detection
- ZILDAT integration
- Language-specific executable code in packs
- Microservices architecture

---

## 16. Roadmap & Future Work

### Immediate (Post-V1)

- Expand Shona lexicon and morphotactics
- Add paradigms and derivational morphology
- Improve morphophonological handling
- Expand evaluation gold datasets

### Short-Term

- Additional Zimbabwean language packs (Ndebele, Tonga)
- Language pack authoring tools
- Batch streaming API
- Authentication/authorization

### Medium-Term

- FST-based engine strategy
- Two-level morphology support
- Non-concatenative morphology
- Richer morphological paradigms

### Long-Term

- ML-based NLP integration (downstream, not in core engine)
- Hate-speech detection (downstream application)
- ZILDAT integration (downstream system)
- UI client (Next.js or similar)

### Philosophy

ML-based NLP applications, hate-speech detection, and ZILDAT integration will be
implemented as **downstream systems** rather than embedded into the core
morphology engine. The engine remains a clean, generic, reusable foundation.

---

## Appendix: Project Documentation

| Document | Description |
| --- | --- |
| [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | Detailed system architecture |
| [`docs/LANGUAGE_PACK.md`](LANGUAGE_PACK.md) | Language pack specification |
| [`docs/API.md`](API.md) | REST API contract |
| [`docs/CLI.md`](CLI.md) | CLI documentation |
| `README.md` | Project overview and quickstart |
| `V1_RELEASE.md` | This document |

---

## Appendix: File Inventory

### Source Files (24)

```text
src/morph/__init__.py
src/morph/version.py
src/morph/logging.py
src/morph/cli.py
src/morph/domain/__init__.py
src/morph/domain/analysis.py
src/morph/domain/pack.py
src/morph/engine/__init__.py
src/morph/engine/interfaces.py
src/morph/engine/implementations.py
src/morph/engine/strategy.py
src/morph/engine/pack_validator.py
src/morph/engine/factory.py
src/morph/loading/__init__.py
src/morph/service/__init__.py
src/morph/service/analysis.py
src/morph/service/bootstrap.py
src/morph/api/__init__.py
src/morph/api/app.py
src/morph/api/schemas.py
src/morph/api/middleware.py
src/morph/api/__main__.py
src/morph/evaluation/__init__.py
src/morph/testing/__init__.py
```

### Test Files (15)

```text
tests/conftest.py
tests/test_domain.py
tests/test_engine.py
tests/test_pack_validator.py
tests/test_service.py
tests/test_loader.py
tests/test_shona.py
tests/test_ambiguity.py
tests/test_separation.py
tests/test_api.py
tests/test_cli.py
tests/test_integration.py
tests/test_evaluation.py
tests/test_language_expansion.py
tests/test_testing.py
```

### Configuration Files

```text
pyproject.toml
uv.lock
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
.gitignore
```
