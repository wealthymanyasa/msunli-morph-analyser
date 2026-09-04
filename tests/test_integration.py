"""Integration tests across the application adapters.

These tests verify the adapters share a single source of truth — the
``AnalysisService`` — so the REST API and CLI can never diverge in their
analysis results, and that the shared bootstrap loads the same language packs
the API and CLI use at runtime.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from morph.api import create_app
from morph.cli import app
from morph.service.analysis import AnalysisService
from morph.service.bootstrap import build_service

LANGUAGES_DIR = Path(__file__).resolve().parents[1] / "languages"

cli_runner = CliRunner()


def _api_analyze(word: str, language: str = "sn") -> str:
    service = AnalysisService()
    service.load_language_directory(LANGUAGES_DIR / "shona")
    client = TestClient(create_app(service=service))
    response = client.post("/api/v1/analyze", json={"language": language, "word": word})
    assert response.status_code == 200
    return response.json()


def test_api_and_cli_agree_on_analysis() -> None:
    """The API and CLI must yield identical canonical results."""
    api = _api_analyze("mukadzi")
    cli = cli_runner.invoke(app, ["analyze", "--language", "sn", "mukadzi"])

    assert api["status"] == "analysed"
    assert "analysed" in cli.output
    assert "lemma=mukadzi" in cli.output
    # Both view the same analysis: class-1 prefix + kadzi stem, noun.
    assert api["analyses"][0]["pos"] == "noun"
    assert "pos=noun" in cli.output
    assert [m["type"] for m in api["analyses"][0]["morphemes"]] == [
        "noun-class-1",
        "stem",
    ]


def test_api_and_cli_agree_on_plural_class() -> None:
    api = _api_analyze("varume")
    cli = cli_runner.invoke(app, ["analyze", "--language", "sn", "varume"])
    assert api["analyses"][0]["features"]["noun_class"] == "2"
    assert "noun_class=2" in cli.output


def test_bootstrap_loads_the_real_shona_pack() -> None:
    service = build_service(LANGUAGES_DIR)
    assert service.has_language("sn")
    assert "sn" in service.languages()


def test_create_app_default_loads_languages() -> None:
    app_instance = create_app(languages_dir=str(LANGUAGES_DIR))
    client = TestClient(app_instance)
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    assert "sn" in {item["code"] for item in response.json()}
