"""Application service layer.

The application service is the primary application interface and exposes the
core operation ``analyze(word, language)``. It is API-first: the REST API and
any UI consume this service rather than duplicating logic. The service
resolves a registered language pack for the requested language code and
delegates to the language-agnostic engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from morph.domain.analysis import AnalysisResult
from morph.domain.pack import LanguagePack
from morph.engine.factory import MorphologyEngine, default_engine
from morph.engine.interfaces import AnalysisStrategy
from morph.loading import load_language_pack


class UnknownLanguageError(Exception):
    """Raised when a requested language has no registered language pack."""


class AnalysisService:
    """Entry point for morphological analysis against registered language packs.

    Language packs are registered by their canonical code. The service keeps
    the engine language-agnostic: it only resolves which pack to use.
    """

    def __init__(self, engine: MorphologyEngine | None = None) -> None:
        self._engine = engine or default_engine()
        self._packs: dict[str, LanguagePack] = {}
        self._strategy: AnalysisStrategy = self._engine.strategy

    def register_pack(self, data: dict[str, Any]) -> LanguagePack:
        """Validate and register a language pack, keyed by its code."""
        pack = self._engine.validator.validate(data)
        self._packs[pack.code] = pack
        return pack

    def load_language_directory(self, directory: str | Path) -> LanguagePack:
        """Load a language pack from a YAML directory and register it."""
        pack = load_language_pack(directory, engine_major=self._engine_major())
        self._packs[pack.code] = pack
        return pack

    def _engine_major(self) -> int:
        return self._engine.validator.engine_major

    def register_pack_object(self, pack: LanguagePack) -> LanguagePack:
        """Register an already-constructed language pack object."""
        self._packs[pack.code] = pack
        return pack

    def has_language(self, code: str) -> bool:
        return code in self._packs

    def languages(self) -> list[str]:
        return sorted(self._packs)

    def get_pack(self, code: str) -> LanguagePack | None:
        return self._packs.get(code)

    def analyze(self, word: str, language: str) -> AnalysisResult:
        """Analyse a word for the given language code.

        Raises:
            UnknownLanguageError: if no pack is registered for the language.
        """
        pack = self._packs.get(language)
        if pack is None:
            raise UnknownLanguageError(
                f"no language pack registered for language '{language}'"
            )
        return self._strategy.analyse(word, pack)

    def validate_pack(self, data: dict[str, Any]) -> LanguagePack:
        """Validate a language pack's data without registering it."""
        return self._engine.validator.validate(data)


def create_service() -> AnalysisService:
    """Construct an AnalysisService backed by the default engine."""
    return AnalysisService(default_engine())
