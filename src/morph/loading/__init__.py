"""Generic YAML-based language-pack loader.

Loads a language pack from a directory of YAML files. The loader is entirely
language-agnostic — it reads declarative data and produces a validated
:class:`LanguagePack` instance. No linguistic logic is performed here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise ImportError(
        "PyYAML is required for language pack loading. Install with: pip install pyyaml"
    ) from exc

from morph.domain.pack import LanguagePack
from morph.engine.pack_validator import LanguagePackValidator, PackValidationError

# Files we recognise in a language-pack directory. Each maps to the
# corresponding top-level key in the LanguagePack model.
_SECTION_FILES: dict[str, str] = {
    "manifest": "metadata",           # metadata is required
    "normalization": "normalization",
    "lexicon": "lexicon",
    "morphemes": "morphemes",
    "morphotactics": "morphotactics",
    "paradigms": "paradigms",
    "constraints": "constraints",
    "ranking": "ranking",
    "noun_classes": "noun_classes",
    "resources": "resources",
}


def load_language_pack(
    directory: str | Path,
    engine_major: int = 1,
) -> LanguagePack:
    """Load and validate a language pack from a directory of YAML files.

    The directory must contain at least a ``manifest.yaml`` (metadata) and
    optionally any of the section files listed in ``_SECTION_FILES``.

    Raises :class:`PackValidationError` if any file is malformed, the pack
    fails validation, or required files are missing.
    """
    pack_dir = Path(directory)
    errors: list[str] = []

    if not pack_dir.is_dir():
        raise PackValidationError(errors=[f"not a directory: {pack_dir}"])

    # ── load manifest ─────────────────────────────────────────────────────
    manifest_path = pack_dir / "manifest.yaml"
    if not manifest_path.exists():
        raise PackValidationError(errors=["manifest.yaml is required but not found"])

    manifest = _load_yaml(manifest_path, errors)
    if errors:
        raise PackValidationError(errors=errors)

    pack_data: dict[str, Any] = dict(manifest)

    # ── load section files ────────────────────────────────────────────────
    for filename, key in _SECTION_FILES.items():
        if key == "metadata":
            continue  # already loaded from manifest
        yml = pack_dir / f"{filename}.yaml"
        if not yml.exists():
            continue
        section = _load_yaml(yml, errors)
        if errors:
            raise PackValidationError(errors=errors)
        pack_data[key] = _unwrap_section(section, key)

    # ── validate ──────────────────────────────────────────────────────────
    validator = LanguagePackValidator(engine_major=engine_major)
    return validator.validate(pack_data)


def load_all_packs(
    languages_dir: str | Path,
    engine_major: int = 1,
) -> dict[str, LanguagePack]:
    """Discover and load all language packs under a languages/ root directory.

    Each immediate subdirectory of ``languages_dir`` is treated as a language
    pack directory.

    Returns a dict keyed by language code.
    """
    base = Path(languages_dir)
    packs: dict[str, LanguagePack] = {}
    for child in sorted(base.iterdir()):
        if child.is_dir():
            pack = load_language_pack(child, engine_major=engine_major)
            packs[pack.code] = pack
    return packs


def _load_yaml(path: Path, errors: list[str]) -> Any:
    """Load a single YAML file, appending to errors on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: YAML parse error: {exc}")
        return None
    if data is None:
        errors.append(f"{path.name}: file is empty")
        return None
    if not isinstance(data, dict):
        errors.append(
            f"{path.name}: expected a YAML mapping, got {type(data).__name__}"
        )
        return None
    return data


def _unwrap_section(section: Any, key: str) -> Any:
    """Unwrap a section file whose single top-level key repeats the pack key.

    Pack section files may be written either nested (``lexicon: [...]``) or as
    the bare value. When the loaded mapping contains exactly the expected key,
    return its value so the pack field receives the correct type (e.g. a list
    for ``lexicon`` rather than a wrapping dict). Otherwise return the mapping
    unchanged.
    """
    if (
        isinstance(section, dict)
        and len(section) == 1
        and key in section
    ):
        return section[key]
    return section
