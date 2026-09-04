"""Centralized logging configuration for the morphological analysis platform.

Provides a ``configure_logging`` helper that sets up a consistent, structured
logging format suitable for both development and production. Called once at
application startup (by the API server or CLI).
"""

from __future__ import annotations

import logging
import os
import sys
from typing import IO, Literal

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

LevelStr = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def configure_logging(
    level: LevelStr | int = "INFO",
    *,
    stream: IO[str] | None = None,
) -> None:
    """Configure the root logger for the application.

    Args:
        level: Logging level (name or integer). Defaults to the ``MORPH_LOG_LEVEL``
            environment variable, or ``"INFO"``.
        stream: Output stream (default ``sys.stderr``).
    """
    env_level = os.environ.get("MORPH_LOG_LEVEL", "").upper()
    if env_level and env_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        level = env_level  # type: ignore[assignment]

    handler = logging.StreamHandler(stream or sys.stderr)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT))

    root = logging.getLogger("morph")
    root.setLevel(level)
    root.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
