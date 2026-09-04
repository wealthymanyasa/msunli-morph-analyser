# Morphological Analyser — REST API

A versioned REST API exposes the morphological analyser over HTTP. The API is a
thin adapter over the application service — it contains **no morphology logic**.
Language packs are registered dynamically; the API never hard-codes a language.

## Running the server

```bash
# from the repository root (self-hosted development server)
python -m morph.api --host 127.0.0.1 --port 8000

# or with uvicorn directly
python -m uvicorn "morph.api:create_app" --factory --reload
```

Language packs are discovered under `languages/` by default. Override the
location with the `MORPH_LANGUAGES_DIR` environment variable.

- Interactive docs (Swagger UI): <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/api/v1/openapi.json>

The OpenAPI specification is generated automatically from the typed request and
response schemas in `src/morph/api/schemas.py` and the canonical domain models.

## Endpoints

| Method | Path                    | Purpose                                   |
| ------ | ----------------------- | ----------------------------------------- |
| GET    | `/api/v1/health`        | Health check                              |
| GET    | `/api/v1/languages`     | List registered language packs            |
| POST   | `/api/v1/analyze`       | Analyse a single surface form             |
| POST   | `/api/v1/analyze/batch` | Analyse many surface forms for one language|

## Examples

### Health

```http
GET /api/v1/health
```

```json
{ "status": "ok" }
```

### List languages

```http
GET /api/v1/languages
```

```json
[
  { "code": "sn", "name": "chiShona (Shona)", "version": "0.1.0" }
]
```

### Analyse a word

```http
POST /api/v1/analyze
Content-Type: application/json

{ "language": "sn", "word": "murume" }
```

```json
{
  "surface": "murume",
  "normalized": "murume",
  "language": "sn",
  "status": "analysed",
  "analyses": [
    {
      "surface": "murume",
      "normalized": "murume",
      "lemma": "murume",
      "pos": "noun",
      "morphemes": [
        { "surface": "mu", "type": "noun-class-1" },
        { "surface": "rume", "type": "stem" }
      ],
      "features": { "noun_class": "1", "number": "singular" },
      "score": 0.1
    }
  ],
  "error": null
}
```

### Batch analysis

```http
POST /api/v1/analyze/batch
Content-Type: application/json

{ "language": "sn", "words": ["murume", "varume"] }
```

```json
{
  "language": "sn",
  "results": [ { "...": "first result" }, { "...": "second result" } ]
}
```

Results are returned in the same order as the requested words.

## Behavioural guarantees

- **Dynamic languages**: any registered language pack code is accepted; unknown
  codes produce a `404`. No endpoint hard-codes a language.
- **Validation**: malformed requests return `422` with a standard error body.
- **Consistent errors**: every error response is `{ "detail": "..." }`.
- **Ambiguity preserved**: a surface form with multiple valid analyses is
  returned with `status: "ambiguous"` and all candidates in `analyses`.
- **Deterministic**: identical inputs always produce identical outputs.
- **Canonical result**: the response is the same `AnalysisResult` the
  application service returns — there is one representation everywhere.

## Error responses

| Code | Meaning                                          |
| ---- | ------------------------------------------------ |
| 404  | Requested language pack is not registered        |
| 422  | Request body failed validation                  |
| 503  | Analysis service is not initialised              |

```json
{ "detail": "no language pack registered for language 'zz'" }
```
