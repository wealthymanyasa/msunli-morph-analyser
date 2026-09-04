"""API tests for the versioned REST surface.

These tests exercise the endpoints through FastAPI's TestClient against a real
``AnalysisService``. They assert the API contract: typed requests, consistent
errors, dynamic language acceptance, determinism, ambiguity preservation, and
OpenAPI discoverability.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from conftest import sample_pack_data
from fastapi.testclient import TestClient

from morph.api import create_app
from morph.service.analysis import AnalysisService

LANGUAGES_DIR = Path(__file__).resolve().parents[1] / "languages"


def _service_with_shona() -> AnalysisService:
    service = AnalysisService()
    service.load_language_directory(LANGUAGES_DIR / "shona")
    return service


def _ambiguous_service() -> AnalysisService:
    """A pack where 'mutin' has two valid analyses (see test_ambiguity)."""
    data: dict[str, Any] = sample_pack_data()
    data["lexicon"] = [
        {"surface": "tin", "lemma": "mufv", "pos": "noun",
         "features": {"noun_class": "1", "number": "singular"}},
        {"surface": "tin", "lemma": "mvo", "pos": "noun",
         "features": {"noun_class": "1", "number": "singular"}},
    ]
    data["morphemes"] = [
        {"id": "stem", "sources_lexicon": True, "aliases": [], "features": {}},
        {"id": "class-1", "aliases": ["mu"], "features": {"noun_class": "1",
         "number": "singular"}},
        {"id": "class-3", "aliases": ["mu"], "features": {"noun_class": "3",
         "number": "singular"}},
    ]
    data["morphotactics"] = [
        {"sequence": "class-1 stem", "id": "c1"},
        {"sequence": "class-3 stem", "id": "c3"},
    ]
    data["noun_classes"] = [
        {"identifier": "1", "plural_of": "2"},
        {"identifier": "3", "plural_of": "4"},
    ]
    data["constraints"] = [
        {"id": "agr", "kind": "noun_class_agreement", "params": {}}
    ]
    service = AnalysisService()
    service.register_pack(data)
    return service


@pytest.fixture
def shona_client() -> TestClient:
    app = create_app(service=_service_with_shona())
    return TestClient(app)


@pytest.fixture
def sample_client() -> TestClient:
    service = AnalysisService()
    service.register_pack(sample_pack_data())
    app = create_app(service=service)
    return TestClient(app)


@pytest.fixture
def ambiguous_client() -> TestClient:
    app = create_app(service=_ambiguous_service())
    return TestClient(app)


# ── health ──────────────────────────────────────────────────────────────────
def test_health_ok(shona_client: TestClient) -> None:
    response = shona_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── languages ───────────────────────────────────────────────────────────────
def test_languages_returns_registered_codes(shona_client: TestClient) -> None:
    response = shona_client.get("/api/v1/languages")
    assert response.status_code == 200
    payload = response.json()
    codes = {item["code"] for item in payload}
    assert "sn" in codes
    assert all({"code", "name", "version"} <= set(item) for item in payload)


# ── single analyze ──────────────────────────────────────────────────────────
def test_analyze_known_word(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze",
        json={"language": "sn", "word": "murume"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "sn"
    assert payload["surface"] == "murume"
    assert payload["status"] == "analysed"
    assert payload["analyses"]
    analysis = payload["analyses"][0]
    assert analysis["pos"] == "noun"
    assert analysis["lemma"] == "murume"
    assert [m["type"] for m in analysis["morphemes"]] == [
        "noun-class-1",
        "stem",
    ]


def test_analyze_deterministic(shona_client: TestClient) -> None:
    r1 = shona_client.post(
        "/api/v1/analyze", json={"language": "sn", "word": "mukadzi"}
    ).json()
    r2 = shona_client.post(
        "/api/v1/analyze", json={"language": "sn", "word": "mukadzi"}
    ).json()
    assert r1 == r2


def test_analyze_unknown_word_is_explicit(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze", json={"language": "sn", "word": "zzzzzz"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "unknown_word"
    assert response.json()["analyses"] == []


def test_analyze_unknown_language_returns_404(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze", json={"language": "zz", "word": "murume"}
    )
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "zz" in body["detail"]


def test_analyze_validation_error_422(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze", json={"language": "sn", "word": ""}
    )
    assert response.status_code == 422


def test_analyze_missing_fields_422(shona_client: TestClient) -> None:
    response = shona_client.post("/api/v1/analyze", json={})
    assert response.status_code == 422


def test_analyze_accepts_dynamic_language_code(shona_client: TestClient) -> None:
    # Endpoint logic must not require a fixed language; only registered packs
    # produce analyses, but the endpoint must accept any string and 404 if absent.
    # Here we assert a registered code plus a present-but-unregistered one 404s.
    assert shona_client.post(
        "/api/v1/analyze", json={"language": "sn", "word": "mai"}
    ).status_code == 200
    assert shona_client.post(
        "/api/v1/analyze", json={"language": "not-a-language", "word": "x"}
    ).status_code == 404


def test_analyze_preserves_ambiguity(ambiguous_client: TestClient) -> None:
    response = ambiguous_client.post(
        "/api/v1/analyze", json={"language": "xx", "word": "mutin"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ambiguous"
    assert len(payload["analyses"]) == 2
    assert {a["lemma"] for a in payload["analyses"]} == {"mufv", "mvo"}


# ── batch ───────────────────────────────────────────────────────────────────
def test_batch_analyze_returns_in_order(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze/batch",
        json={"language": "sn", "words": ["murume", "varume", "mai"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "sn"
    assert [r["surface"] for r in payload["results"]] == [
        "murume",
        "varume",
        "mai",
    ]
    assert payload["results"][0]["status"] == "analysed"


def test_batch_analyze_unknown_language_404(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze/batch",
        json={"language": "zz", "words": ["murume"]},
    )
    assert response.status_code == 404


def test_batch_analyze_empty_list_422(shona_client: TestClient) -> None:
    response = shona_client.post(
        "/api/v1/analyze/batch",
        json={"language": "sn", "words": []},
    )
    assert response.status_code == 422


# ── OpenAPI / docs ──────────────────────────────────────────────────────────
def test_openapi_schema_documents_endpoints(shona_client: TestClient) -> None:
    response = shona_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.")
    paths = schema["paths"]
    assert "/api/v1/analyze" in paths
    assert "/api/v1/analyze/batch" in paths
    assert "/api/v1/languages" in paths
    assert "/api/v1/health" in paths
    assert "AnalyzeRequest" in schema["components"]["schemas"]
    assert "AnalysisResult" in schema["components"]["schemas"]


def test_docs_ui_available(shona_client: TestClient) -> None:
    assert shona_client.get("/docs").status_code == 200
