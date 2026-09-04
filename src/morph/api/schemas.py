"""Typed request/response schemas for the morphological analysis REST API.

These models define the API contract. They are kept deliberately thin and
reuse the canonical domain models (:class:`~morph.domain.analysis.AnalysisResult`)
for responses so the wire format and the application-layer result are the same
object — there is exactly one representation of an analysis result.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from morph.domain.analysis import AnalysisResult

API_PREFIX = "/api/v1"


class AnalyzeRequest(BaseModel):
    """Request body for a single analysis (``POST /api/v1/analyze``)."""

    language: str = Field(
        min_length=1,
        max_length=16,
        description="Canonical language pack code (e.g. 'sn')",
        examples=["sn"],
    )
    word: str = Field(
        min_length=1,
        max_length=256,
        description="Surface form to analyse",
        examples=["murume"],
    )


class BatchAnalyzeRequest(BaseModel):
    """Request body for batch analysis (``POST /api/v1/analyze/batch``).

    All words are analysed for the same language. Results preserve input order.
    """

    language: str = Field(
        min_length=1,
        max_length=16,
        description="Canonical language pack code (e.g. 'sn')",
        examples=["sn"],
    )
    words: list[str] = Field(
        min_length=1,
        max_length=1000,
        description="Surface forms to analyse, in order",
    )


class BatchAnalyzeResponse(BaseModel):
    """Response for a batch analysis request."""

    language: str = Field(description="Language code the words were analysed for")
    results: list[AnalysisResult] = Field(
        description="One analysis result per requested word, in input order"
    )


class LanguageInfo(BaseModel):
    """A registered language pack, as exposed by ``GET /api/v1/languages``."""

    code: str = Field(description="Canonical language pack code")
    name: str = Field(description="Human-readable language name")
    version: str = Field(description="Language pack version")


class ErrorResponse(BaseModel):
    """Consistent error body returned for every failing request."""

    detail: str = Field(description="Human-readable description of the error")
