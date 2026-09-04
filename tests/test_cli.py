"""CLI tests for the ``morph`` command.

The CLI is a thin adapter over the application service. These tests use
Typer's CliRunner to exercise the command against the real language packs
registered via the shared bootstrap, mirroring the REST API semantics.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from morph.cli import app

runner = CliRunner()


def test_cli_analyze_single_word() -> None:
    result = runner.invoke(app, ["analyze", "--language", "sn", "murume"])
    assert result.exit_code == 0, result.output
    assert "murume" in result.output
    assert "status:" in result.output
    assert "analysed" in result.output
    assert "lemma=murume" in result.output
    assert "noun-class-1" in result.output


def test_cli_analyze_unknown_language_fails() -> None:
    result = runner.invoke(app, ["analyze", "--language", "zz", "murume"])
    assert result.exit_code == 2
    assert "no language pack registered" in result.stderr


def test_cli_analyze_unknown_word_is_reported(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", "--language", "sn", "qqqqqq"])
    assert result.exit_code == 0
    assert "unknown_word" in result.output


def test_cli_analyze_batch_from_file(tmp_path: Path) -> None:
    batch_file = tmp_path / "words.txt"
    batch_file.write_text("murume\nvarume\n\nmai\n", encoding="utf-8")
    result = runner.invoke(
        app, ["analyze", "--language", "sn", "--file", str(batch_file)]
    )
    assert result.exit_code == 0, result.output
    for surface in ("murume", "varume", "mai"):
        assert f"surface:  {surface}" in result.output


def test_cli_analyze_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "nope.txt"
    result = runner.invoke(
        app, ["analyze", "--language", "sn", "--file", str(missing)]
    )
    assert result.exit_code == 2
    assert "file not found" in result.stderr


def test_cli_analyze_requires_word_or_file() -> None:
    result = runner.invoke(app, ["analyze", "--language", "sn"])
    # No positional word and no --file -> usage error (non-zero exit).
    assert result.exit_code != 0


def test_cli_languages_lists_sn() -> None:
    result = runner.invoke(app, ["languages"])
    assert result.exit_code == 0, result.output
    assert "sn" in result.output
