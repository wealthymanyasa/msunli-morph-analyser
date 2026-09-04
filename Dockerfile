# ── builder ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir .

# ── runtime ──────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="MSUNLI" \
      description="Morphological Analyser — reusable, language-agnostic morphological analysis platform"

RUN groupadd -r morph && useradd --no-log-init -r -g morph morph

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/morph /usr/local/bin/morph
COPY languages/ /app/languages/

ENV MORPH_LANGUAGES_DIR=/app/languages \
    MORPH_LOG_LEVEL=INFO

USER morph

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["python", "-m", "morph.api", "--host", "0.0.0.0", "--port", "8000"]
