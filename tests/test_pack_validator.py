"""Tests for the language pack validator."""

from __future__ import annotations

import pytest
from conftest import sample_pack_data

from morph.domain.pack import LanguagePack
from morph.engine.pack_validator import LanguagePackValidator, PackValidationError


@pytest.fixture
def validator() -> LanguagePackValidator:
    return LanguagePackValidator(engine_major=1)


def test_valid_pack_ok(validator: LanguagePackValidator) -> None:
    pack = validator.validate(sample_pack_data())
    assert isinstance(pack, LanguagePack)
    assert pack.code == "xx"
    assert pack.metadata.version == "1.0.0"


def test_missing_metadata_rejected(validator: LanguagePackValidator) -> None:
    data = sample_pack_data()
    data.pop("metadata")
    with pytest.raises(PackValidationError):
        validator.validate(data)


def test_missing_required_metadata_fields_rejected(
    validator: LanguagePackValidator,
) -> None:
    data = sample_pack_data()
    data["metadata"] = {"code": "xx"}  # missing name/version/compat
    with pytest.raises(PackValidationError) as excinfo:
        validator.validate(data)
    assert excinfo.value.errors


def test_invalid_semver_rejected(validator: LanguagePackValidator) -> None:
    data = sample_pack_data()
    data["metadata"]["version"] = "1.0"  # not full semver
    with pytest.raises(PackValidationError):
        validator.validate(data)


def test_engine_compatibility_mismatch_rejected() -> None:
    # Validator bound to engine major 2; pack declares 1.x
    validator = LanguagePackValidator(engine_major=2)
    data = sample_pack_data()
    with pytest.raises(PackValidationError) as excinfo:
        validator.validate(data)
    assert any("engine compatibility mismatch" in e for e in excinfo.value.errors)


def test_engine_compatibility_same_major_accepted() -> None:
    validator = LanguagePackValidator(engine_major=1)
    pack = validator.validate(sample_pack_data())
    assert pack.code == "xx"


def test_undefined_morpheme_in_morphotactic_rejected(
    validator: LanguagePackValidator,
) -> None:
    data = sample_pack_data()
    data["morphotactics"] = [{"sequence": "root bogus?", "id": "bad"}]
    with pytest.raises(PackValidationError) as excinfo:
        validator.validate(data)
    assert any("undefined morpheme id 'bogus'" in e for e in excinfo.value.errors)


def test_empty_lexicon_rejected(validator: LanguagePackValidator) -> None:
    data = sample_pack_data(lexicon=[])
    with pytest.raises(PackValidationError):
        validator.validate(data)


def test_empty_morphemes_rejected(validator: LanguagePackValidator) -> None:
    data = sample_pack_data(morphemes=[])
    with pytest.raises(PackValidationError):
        validator.validate(data)


def test_unknown_extra_top_level_key_ok(validator: LanguagePackValidator) -> None:
    # LanguagePack uses extra="forbid", so unknown keys should be rejected.
    data = sample_pack_data()
    data["unexpected_key"] = True
    with pytest.raises(PackValidationError):
        validator.validate(data)


def test_non_object_rejected(validator: LanguagePackValidator) -> None:
    with pytest.raises(PackValidationError):
        validator.validate(["not", "a", "dict"])  # type: ignore[arg-type]


def test_result_has_clear_error_messages(validator: LanguagePackValidator) -> None:
    data = sample_pack_data()
    data.pop("metadata")
    try:
        validator.validate(data)
    except PackValidationError as exc:
        assert exc.errors
