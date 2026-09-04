"""Versioned REST API for the morphological analysis platform.

The API layer is a thin adapter over :class:`morph.service.analysis.AnalysisService`.
It contains no morphology logic — every endpoint delegates to the application
service, which in turn drives the language-agnostic engine against declarative
language packs.
"""

from morph.api.app import create_app

__all__ = ["create_app"]
