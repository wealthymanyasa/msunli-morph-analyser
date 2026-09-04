# MSUNLI Morph Analyser

A reusable, language-agnostic morphological analysis platform for building NLP tools for under-resourced languages.

The platform separates **generic morphology algorithms** from **declarative linguistic resources**, allowing new languages to be added as language packs without modifying the core morphology engine.

## V1 Status

**V1 development is complete and test-verified.**

* Deterministic, morphotactics-driven morphology engine
* Application service
* Declarative language-pack specification and validation
* First declarative Shona (`sn`) language pack
* REST API (`/api/v1`)
* CLI (`morph`)
* Language-independent testing and evaluation infrastructure
* 93 automated tests passing
* Ruff linting clean
* Mypy type checking clean

### V1 Scope

V1 intentionally does **not** include:

* ML models
* Hate-speech detection
* ZILDAT integration
* Language-specific executable code
* Unnecessary microservices or infrastructure

These are future integrations or applications of the platform rather than responsibilities of the core morphology engine.

## Architecture

The central design principle is:

> **Engine = generic algorithms and software. Language pack = declarative linguistic knowledge.**

```text
Client
  │
  ├── REST API
  │
  └── CLI
       │
       ▼
Application Service
       │
       ▼
Language Registry
       │
       ▼
Validated Language Pack
       │
       ▼
Generic Morphology Engine
       │
       ├── Normalizer
       ├── Lexicon
       ├── Candidate Generator
       ├── Segmenter
       ├── Feature Unifier
       ├── Constraint Validator
       └── Candidate Ranker
       │
       ▼
AnalysisResult
```

Language packs contain declarative resources such as:

* lexicons
* morphemes
* morphotactics
* paradigms
* constraints
* ranking rules
* normalization configuration
* noun-class information
* resource provenance

Language packs contain **no executable Python code**.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the detailed architecture.

## Current Language Support

### Shona (`sn`)

Shona is the first language pack and serves as the reference implementation of the language-pack contract.

Resources are located under:

```text
languages/shona/
```

The pack includes declarative representations of Shona morphological resources, including noun classes, lexical stems, morphotactics, constraints, and provenance.

See [`docs/LANGUAGE_PACK.md`](docs/LANGUAGE_PACK.md) for the language-pack specification.

Additional languages such as Ndebele and Tonga are intended to be added as independent language packs without modifying the generic morphology algorithms.

## Installation

Python **3.11+** is required.

For development:

```bash
pip install -e ".[dev]"
```

Run the complete test suite:

```bash
pytest
```

## Python API

The application service provides the primary programmatic interface:

```python
from morph.service.analysis import create_service

service = create_service()
service.load_language_directory("languages/shona")

result = service.analyze("murume", "sn")

print(result.status)
print(result.analyses)
```

The service is language-agnostic. The language is selected using its registered language code.

## REST API

The platform exposes a versioned REST API under:

```text
/api/v1
```

Start the development server:

```bash
pip install -e .
python -m morph.api --port 8000
```

### Endpoints

| Method | Endpoint                | Purpose                        |
| ------ | ----------------------- | ------------------------------ |
| GET    | `/api/v1/health`        | Service health                 |
| GET    | `/api/v1/languages`     | List registered language packs |
| POST   | `/api/v1/analyze`       | Analyze a single word          |
| POST   | `/api/v1/analyze/batch` | Analyze multiple words         |

Example request:

```json
{
  "language": "sn",
  "word": "murume"
}
```

Batch request:

```json
{
  "language": "sn",
  "words": ["murume", "varume", "muti", "miti"]
}
```

Interactive API documentation:

`http://127.0.0.1:8000/docs`

OpenAPI specification:

`http://127.0.0.1:8000/api/v1/openapi.json`

See [`docs/API.md`](docs/API.md) for the complete API contract.

## CLI

The `morph` command is a thin adapter over the same application service used by the REST API.

List available languages:

```bash
morph languages
```

Analyze a word:

```bash
morph analyze --language sn murume
```

Analyze a batch file:

```bash
morph analyze --language sn --file words.txt
```

See [`docs/CLI.md`](docs/CLI.md) for CLI usage and behavior.

## Example

```python
from morph.service.analysis import create_service

service = create_service()
service.load_language_directory("languages/shona")

for word in (
    "murume",
    "varume",
    "muti",
    "miti",
    "chikoro",
    "kuenda",
    "ndaenda",
):
    result = service.analyze(word, "sn")

    print(
        word,
        "->",
        result.status.value,
        [
            (
                analysis.pos,
                analysis.lemma,
                [m.type for m in analysis.morphemes],
            )
            for analysis in result.analyses
        ],
    )
```

## Testing and Quality

The project uses automated tests to protect both the generic engine and the language-pack boundary.

Current verification:

```text
93 tests passed
Ruff: clean
Mypy: clean
```

The test suite includes:

* unit tests
* domain tests
* engine tests
* language-pack validation tests
* Shona integration tests
* ambiguity tests
* API tests
* CLI tests
* end-to-end integration tests
* engine/language separation tests

The architecture is explicitly tested to ensure that language-specific executable code does not enter the generic engine or domain layers.

## Adding a Language

A new language should be added as a declarative language pack:

```text
New Language Pack
        │
        ▼
Declarative Resources
        │
        ▼
Manifest Validation
        │
        ▼
Language Registration
        │
        ▼
Existing Generic Engine
        │
        ▼
Existing REST API / CLI
```

Adding a language should not require modification of generic morphology algorithms.

The detailed language-pack contract is documented in [`docs/LANGUAGE_PACK.md`](docs/LANGUAGE_PACK.md).

## V1 Limitations

The current V1 is intentionally focused.

Known linguistic limitations include:

* limited Shona lexical coverage
* limited morphological paradigms
* limited derivational morphology
* limited morphophonological handling
* some conservative treatment of locative and disputed noun-class analyses
* evaluation coverage will expand as additional manually verified resources become available

These limitations do not change the language-agnostic architecture of the platform.

## Project Documentation

* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture
* [`docs/LANGUAGE_PACK.md`](docs/LANGUAGE_PACK.md) — language-pack specification
* [`docs/API.md`](docs/API.md) — REST API contract
* [`docs/CLI.md`](docs/CLI.md) — CLI documentation

## Roadmap

### V1

* Generic morphology engine
* Declarative Shona language pack
* REST API
* CLI
* Testing and evaluation
* Production hardening

### Future

* Additional Zimbabwean language packs
* Expanded linguistic resources
* Morphophonological processing
* Richer morphological paradigms
* Improved evaluation coverage
* Integration with downstream NLP applications

ML-based NLP applications, hate-speech detection, and ZILDAT integration will be implemented as downstream systems rather than embedded into the core morphology engine.

## License

See the repository license for usage and distribution terms.
