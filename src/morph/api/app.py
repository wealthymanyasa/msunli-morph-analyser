"""FastAPI application for the morphological analysis platform.

The application exposes a small, versioned REST surface over the application
service. Endpoint handlers contain no morphology logic — they parse/validate
requests, call :class:`~morph.service.analysis.AnalysisService`, and translate
application exceptions into consistent HTTP error responses.

OpenAPI documentation is generated automatically by FastAPI from the typed
schemas in :mod:`morph.api.schemas`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, status

from morph.api.schemas import (
    API_PREFIX,
    AnalyzeRequest,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    ErrorResponse,
    LanguageInfo,
)
from morph.domain.analysis import AnalysisResult
from morph.service.analysis import AnalysisService, UnknownLanguageError
from morph.service.bootstrap import build_service

_TAG_ANALYZE = "analyze"
_TAG_LANGUAGES = "languages"
_TAG_HEALTH = "health"


def _get_service(request: Request) -> AnalysisService:
    service: AnalysisService | None = getattr(request.app.state, "service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="analysis service is not initialised",
        )
    return service


def create_app(
    service: AnalysisService | None = None,
    languages_dir: str | Path | None = None,
) -> FastAPI:
    """Construct the configured FastAPI application.

    Args:
        service: An already-configured application service. When omitted, a new
            service is built and every language pack under ``languages_dir``
            (or the default languages directory) is registered.
        languages_dir: Override the directory scanned for language packs.
            Ignored when ``service`` is supplied.
    """
    if service is None:
        service = build_service(languages_dir)

    app = FastAPI(
        title="Morphological Analyser API",
        description=(
            "Versioned REST API for reusable, language-agnostic morphological "
            "analysis. Language packs are registered dynamically — the API never "
            "hard-codes a specific language."
        ),
        version="1.0.0",
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url="/docs",
    )
    app.state.service = service

    _register_routes(app)
    return app


def _register_routes(app: FastAPI) -> None:
    @app.get(
        f"{API_PREFIX}/health",
        tags=[_TAG_HEALTH],
        summary="Health check",
        response_model=dict[str, Any],
        responses={
            status.HTTP_200_OK: {
                "description": "Service is healthy",
                "content": {"application/json": {"example": {"status": "ok"}}},
            }
        },
    )
    def health() -> dict[str, Any]:
        return {"status": "ok"}

    @app.get(
        f"{API_PREFIX}/languages",
        tags=[_TAG_LANGUAGES],
        summary="List registered languages",
        response_model=list[LanguageInfo],
    )
    def languages(
        service: AnalysisService = Depends(_get_service),
    ) -> list[LanguageInfo]:
        infos: list[LanguageInfo] = []
        for code in service.languages():
            pack = service.get_pack(code)
            if pack is None:
                continue
            infos.append(
                LanguageInfo(
                    code=code,
                    name=pack.metadata.name,
                    version=pack.metadata.version,
                )
            )
        return infos

    @app.post(
        f"{API_PREFIX}/analyze",
        tags=[_TAG_ANALYZE],
        summary="Analyse a single surface form",
        response_model=AnalysisResult,
        responses=_analysis_error_responses(),
    )
    def analyze(
        payload: AnalyzeRequest,
        service: AnalysisService = Depends(_get_service),
    ) -> AnalysisResult:
        return _analyze_or_404(service, payload.language, payload.word)

    @app.post(
        f"{API_PREFIX}/analyze/batch",
        tags=[_TAG_ANALYZE],
        summary="Analyse many surface forms for one language",
        response_model=BatchAnalyzeResponse,
        responses=_analysis_error_responses(),
    )
    def analyze_batch(
        payload: BatchAnalyzeRequest,
        service: AnalysisService = Depends(_get_service),
    ) -> BatchAnalyzeResponse:
        _ensure_language(service, payload.language)
        results = [
            service.analyze(word, payload.language) for word in payload.words
        ]
        return BatchAnalyzeResponse(
            language=payload.language,
            results=results,
        )


def _ensure_language(service: AnalysisService, language: str) -> None:
    """Raise a 404 if the requested language is not registered."""
    if service.get_pack(language) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no language pack registered for language '{language}'",
        )


def _analyze_or_404(
    service: AnalysisService,
    language: str,
    word: str,
) -> AnalysisResult:
    try:
        return service.analyze(word, language)
    except UnknownLanguageError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


def _analysis_error_responses() -> dict[int | str, dict[str, Any]]:
    return {
        422: {
            "model": ErrorResponse,
            "description": "Validation error in the request body",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "No language pack is registered for the requested code",
        },
    }
