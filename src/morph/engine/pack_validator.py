"""Language pack validation.

Validates that a loaded language pack is well-formed, versioned, engine-
compatible and internally consistent before it is used by the engine.
Invalid or incompatible packs are rejected with clear, structured errors.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from morph.domain.pack import (
    LanguagePack,
)

_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")

# Simple engine compatibility encoding: major only for now. A pack declaring
# engine_compatibility "1.x" is accepted by any engine whose major version is 1.
_ENGINE_COMPAT_RE = re.compile(r"^\d+\.x$|^\d+\.\d+\.\d+$")


class PackValidationError(Exception):
    """Raised when a language pack fails validation.

    ``errors`` is a flat, human-readable list describing each problem found.
    """

    def __init__(
        self,
        message: str = "Invalid language pack",
        errors: list[str] | None = None,
    ) -> None:
        self.errors: list[str] = errors or []
        super().__init__(
            message if not self.errors else f"{message}: {'; '.join(self.errors)}"
        )


class LanguagePackValidator:
    """Validates the declarative language pack contract.

    Usage:
        validator = LanguagePackValidator(engine_major=1)
        pack = validator.validate(data)  # raises PackValidationError
    """

    def __init__(self, engine_major: int = 1) -> None:
        self.engine_major = engine_major

    def validate(self, data: dict[str, Any]) -> LanguagePack:
        """Validate raw pack data and return a :class:`LanguagePack`.

        Raises :class:`PackValidationError` describing every problem found.
        """
        errors: list[str] = []

        if not isinstance(data, dict):
            raise PackValidationError(errors=["language pack must be a JSON object"])

        metadata_raw = data.get("metadata")
        errors.extend(self._validate_metadata(metadata_raw))

        if errors:
            # Fail fast on identity problems before attempting schema validation.
            raise PackValidationError(errors=errors)

        try:
            pack = LanguagePack.model_validate(data)
        except ValidationError as exc:
            errors.extend(self._pydantic_errors(exc))
            raise PackValidationError(errors=errors) from exc

        errors.extend(self._validate_consistency(pack))

        if errors:
            raise PackValidationError(errors=errors)

        return pack

    def _validate_metadata(self, metadata_raw: Any) -> list[str]:
        errors: list[str] = []
        if not isinstance(metadata_raw, dict):
            return ["'metadata' must be a JSON object"]

        for field in ("code", "name", "version", "engine_compatibility"):
            if not metadata_raw.get(field):
                errors.append(f"metadata requires '{field}'")

        if errors:
            return errors

        version = metadata_raw["version"]
        if not _SEMVER_RE.match(version):
            errors.append(f"metadata.version must be semantic version, got '{version}'")

        compat = metadata_raw["engine_compatibility"]
        if not _ENGINE_COMPAT_RE.match(compat):
            errors.append(
                "metadata.engine_compatibility must match 'MAJOR.x' or "
                f"full semver, got '{compat}'"
            )
        else:
            try:
                major = int(compat.split(".")[0])
            except (TypeError, ValueError):
                major = -1
            if major != self.engine_major:
                errors.append(
                    f"engine compatibility mismatch: pack requires engine {compat}, "
                    f"this engine is {self.engine_major}.x"
                )
        return errors

    def _validate_consistency(self, pack: LanguagePack) -> list[str]:
        errors: list[str] = []

        morpheme_ids = {m.id for m in pack.morphemes}
        if not pack.morphemes:
            errors.append("pack declares no morphemes; analysis impossible")
        if not pack.lexicon:
            errors.append("pack declares an empty lexicon")

        # Every morpheme type id referenced by a morphotactic rule should exist.
        referenced = self._referenced_morpheme_ids(pack)
        for ref in sorted(referenced - morpheme_ids):
            errors.append(f"morphotactic rule references undefined morpheme id '{ref}'")

        # Constraints of known kinds must declare the params the generic engine
        # actually interprets, so a mis-written constraint can never silently
        # degrade into a no-op.
        errors.extend(self._validate_constraints(pack, morpheme_ids))

        # Lexicon entries must be non-empty strings.
        for entry in pack.lexicon:
            if not entry.surface:
                errors.append("lexicon contains an entry with an empty surface")

        return errors

    @staticmethod
    def _referenced_morpheme_ids(pack: LanguagePack) -> set[str]:
        referenced: set[str] = set()
        for rule in pack.morphotactics:
            for token in re.split(r"[\s*?+|()\[\]]+", rule.sequence):
                token = token.strip()
                if token:
                    referenced.add(token)
        return referenced

    @staticmethod
    def _validate_constraints(pack: LanguagePack, morpheme_ids: set[str]) -> list[str]:
        errors: list[str] = []
        for constraint in pack.constraints:
            prefix = f"constraint '{constraint.id}'"
            params = constraint.params

            if constraint.kind == "affix_stem_pos":
                if not params.get("stem_pos"):
                    errors.append(
                        f"{prefix} (kind 'affix_stem_pos') requires params.stem_pos"
                    )
                if not params.get("affix_classes"):
                    errors.append(
                        f"{prefix} (kind 'affix_stem_pos') requires non-empty "
                        "params.affix_classes"
                    )
            elif constraint.kind == "slot_stem_pos":
                affix_ids = params.get("affix_ids")
                if not affix_ids:
                    errors.append(
                        f"{prefix} (kind 'slot_stem_pos') requires non-empty "
                        "params.affix_ids"
                    )
                if not params.get("stem_pos"):
                    errors.append(
                        f"{prefix} (kind 'slot_stem_pos') requires params.stem_pos"
                    )
                unknown = sorted(set(affix_ids or []) - morpheme_ids)
                for morpheme_id in unknown:
                    errors.append(
                        f"{prefix} references undefined morpheme id '{morpheme_id}' "
                        "in params.affix_ids"
                    )
        return errors

    @staticmethod
    def _pydantic_errors(exc: ValidationError) -> list[str]:
        return [
            f"{'.'.join(str(loc) for loc in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]


def validate_language_pack(data: dict[str, Any], engine_major: int = 1) -> LanguagePack:
    """Functional entry point for validating a language pack."""
    return LanguagePackValidator(engine_major=engine_major).validate(data)
