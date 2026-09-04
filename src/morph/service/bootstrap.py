"""Application-service bootstrapping shared by the API and CLI.

Both the REST API and the command-line interface are thin adapters over
:class:`~morph.service.analysis.AnalysisService`. To avoid duplicating service
construction and language-pack discovery between them, this module provides a
single ``build_service`` helper that every adapter uses.
"""

from __future__ import annotations

import os
from pathlib import Path

from morph.service.analysis import AnalysisService

_DEFAULT_LANGUAGES_ENV = "MORPH_LANGUAGES_DIR"


def default_languages_dir() -> Path:
    """Resolve the default language-packs root directory.

    Prefers the ``MORPH_LANGUAGES_DIR`` environment variable, falling back to
    the ``languages/`` directory at the repository root
    (``src/morph/service/bootstrap.py`` -> repository root).
    """
    env = os.environ.get(_DEFAULT_LANGUAGES_ENV)
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "languages"


def build_service(languages_dir: str | Path | None = None) -> AnalysisService:
    """Build an AnalysisService and register every language pack found.

    Args:
        languages_dir: Directory to scan for language packs. Defaults to
            :func:`default_languages_dir`.
    """
    service = AnalysisService()
    base = Path(languages_dir) if languages_dir else default_languages_dir()
    if base.is_dir():
        for child in sorted(base.iterdir()):
            if child.is_dir():
                service.load_language_directory(child)
    return service
