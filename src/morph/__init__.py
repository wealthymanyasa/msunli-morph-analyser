"""Public API for the morphological analysis platform.

This is the primary application interface, consumed by the REST API and any
UI client. It intentionally stays small and high-level.
"""

from morph.domain.analysis import (
    AnalysisResult,
    AnalysisStatus,
    Morpheme,
    MorphologicalAnalysis,
)
from morph.domain.pack import LanguagePack, NounClass
from morph.engine.factory import MorphologyEngine, default_engine
from morph.engine.pack_validator import (
    LanguagePackValidator,
    PackValidationError,
    validate_language_pack,
)
from morph.loading import load_language_pack
from morph.service.analysis import (
    AnalysisService,
    UnknownLanguageError,
    create_service,
)

__all__ = [
    "AnalysisResult",
    "AnalysisStatus",
    "Morpheme",
    "MorphologicalAnalysis",
    "LanguagePack",
    "NounClass",
    "MorphologyEngine",
    "default_engine",
    "PackValidationError",
    "LanguagePackValidator",
    "validate_language_pack",
    "load_language_pack",
    "AnalysisService",
    "UnknownLanguageError",
    "create_service",
]
