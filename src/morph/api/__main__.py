"""Run the API server with ``python -m morph.api [--host H] [--port P]``."""

from __future__ import annotations

import argparse


def main() -> None:
    from morph.logging import configure_logging

    configure_logging()

    parser = argparse.ArgumentParser(description="Run the Morphological Analyser API")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", default=8000, type=int, help="Bind port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "morph.api:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
