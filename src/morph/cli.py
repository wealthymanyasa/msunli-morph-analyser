"""Command-line interface for the morphological analysis platform.

The CLI is a thin adapter over :class:`morph.service.analysis.AnalysisService` —
the same application layer the REST API consumes. It contains no morphology
logic: it only resolves language packs, calls ``AnalysisService.analyze``, and
renders the resulting canonical :class:`~morph.domain.analysis.AnalysisResult`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from morph.domain.analysis import AnalysisResult, AnalysisStatus
from morph.logging import configure_logging
from morph.service.analysis import AnalysisService, UnknownLanguageError
from morph.service.bootstrap import build_service
from morph.version import __version__

logger = logging.getLogger("morph.cli")

app = typer.Typer(
    name="morph",
    help="Reusable, language-agnostic morphological analysis platform.",
    no_args_is_help=True,
)


def _service() -> AnalysisService:
    return build_service()


def _render_analysis(result: AnalysisResult) -> str:
    """Render a canonical AnalysisResult as human-readable text.

    This is pure presentation — it reads the result model and formats it. No
    morphology is performed here.
    """
    lines = [f"surface:  {result.surface}"]
    if result.normalized is not None:
        lines.append(f"normalized: {result.normalized}")
    lines.append(f"language: {result.language}")
    lines.append(f"status:   {result.status.value}")
    if result.error:
        lines.append(f"error:    {result.error}")

    for i, analysis in enumerate(result.analyses, start=1):
        tags = []
        if analysis.lemma is not None:
            tags.append(f"lemma={analysis.lemma}")
        if analysis.pos is not None:
            tags.append(f"pos={analysis.pos}")
        if analysis.score is not None:
            tags.append(f"score={analysis.score:.3f}")
        lines.append(f"  [{i}] {', '.join(tags)}")
        for m in analysis.morphemes:
            gloss = f" <{m.gloss}>" if m.gloss else ""
            lines.append(f"      {m.surface}  (type={m.type}){gloss}")
        if analysis.features:
            feats = ", ".join(f"{k}={v}" for k, v in analysis.features.items())
            lines.append(f"      features: {feats}")

    if not result.analyses and result.status == AnalysisStatus.UNKNOWN_WORD:
        lines.append("      (no analysis found)")
    return "\n".join(lines)


def _print_error(message: str) -> None:
    typer.echo(f"error: {message}", err=True)
    raise typer.Exit(code=2)


@app.command("version")
def version() -> None:
    """Show the morph-analyser version."""
    typer.echo(f"morph-analyser {__version__}")


@app.command("languages")
def languages() -> None:
    """List the registered language packs."""
    service = _service()
    for code in service.languages():
        pack = service.get_pack(code)
        if pack is None:
            continue
        typer.echo(f"{code}\t{pack.metadata.name}\t{pack.metadata.version}")


@app.command("analyze")
def analyze(
    word: str | None = typer.Argument(
        None, help="Surface form to analyse (omit when using --file)"
    ),
    language: str = typer.Option(..., "--language", "-l", help="Language pack code"),
    file: Path | None = typer.Option(
        None,
        "--file",
        "-f",
        help="Text file of surface forms (one per line) to analyse in batch",
    ),
) -> None:
    """Analyse a surface form, or a batch from a file, for a given language."""
    service = _service()

    # Validate the language up-front (shared application-layer behaviour).
    if service.get_pack(language) is None:
        _print_error(f"no language pack registered for language '{language}'")

    if file is not None and word is not None:
        _print_error("provide either WORD or --file, not both")
    if file is None and word is None:
        _print_error("provide a WORD or a --file to analyse")

    words: list[str]
    source_label: str
    if file is not None:
        if not file.exists():
            _print_error(f"file not found: {file}")
        words = [
            line.strip()
            for line in file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        source_label = str(file)
    else:
        assert word is not None
        words = [word]
        source_label = word

    failures = 0
    for item in words:
        try:
            result = service.analyze(item, language)
        except UnknownLanguageError as exc:  # pragma: no cover - defensive
            _print_error(str(exc))
        typer.echo(_render_analysis(result))
        typer.echo(f"--- {source_label} ---")
        if result.status == AnalysisStatus.ERROR:
            failures += 1

    if failures:
        _print_error(f"{failures} word(s) failed to analyse")


def main() -> None:
    """Console-script entry point (``morph ...``)."""
    configure_logging()
    logger.info("morph CLI starting (version=%s)", __version__)
    app()
