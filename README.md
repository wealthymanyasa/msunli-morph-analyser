# msunli-morph-analyser

A reusable, language-agnostic morphological analysis platform.

- **V1 scope**: deterministic engine + application service + declarative
  language-pack contract/validator, plus a first declarative Shona (`sn`)
  language pack. No ML, no hate-speech detection, no ZILDAT.
- **Architecture**: see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- **Language packs**: see [docs/LANGUAGE_PACK.md](docs/LANGUAGE_PACK.md) and
  the Shona resources under `languages/shona/`.
- **Stack**: Python 3.11+, Pydantic v2, PyYAML, pytest.

## Quickstart (dev)

```bash
pip install -e ".[dev]"
pytest
```

## Primary operation

```python
from morph.service.analysis import create_service

service = create_service()
service.load_language_directory("languages/shona")   # declarative Shona pack
result = service.analyze("murume", "sn")              # -> AnalysisResult
print(result.status, result.analyses)
```

## REST API

Exposes the analyser over a versioned API (`/api/v1`). See
[docs/API.md](docs/API.md) for the full contract and examples.

```bash
pip install -e .            # installs dependencies + the `morph` CLI
python -m morph.api --port 8000
```

Then:

- `GET  /api/v1/health`
- `GET  /api/v1/languages`
- `POST /api/v1/analyze`        `{ "language": "sn", "word": "murume" }`
- `POST /api/v1/analyze/batch`  `{ "language": "sn", "words": ["..."] }`
- Interactive docs: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/api/v1/openapi.json>

## CLI

The `morph` command is a thin adapter over the application service. See
[docs/CLI.md](docs/CLI.md).

```bash
morph languages
morph analyze --language sn murume
morph analyze --language sn --file words.txt
```

## Example: analyse Shona words

```python
from morph.service.analysis import create_service

svc = create_service()
svc.load_language_directory("languages/shona")

for word in ("murume", "varume", "muti", "miti", "chikoro", "kuenda", "ndaenda"):
    r = svc.analyze(word, "sn")
    print(word, "->", r.status.value,
          [(a.pos, a.lemma, [m.type for m in a.morphemes]) for a in r.analyses])
```
