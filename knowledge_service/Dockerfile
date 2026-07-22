# File: knowledge_service/Dockerfile
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Multi-stage container build for knowledge-service per the house
#   application-code standard (01-code-structure §9): hash-verified dependency
#   install in the builder, no build toolchain in the runtime image, non-root
#   runtime user, and a listen port taken from the environment (Cloud Run
#   injects PORT; 8080 is the default).

# ---------------------------------------------------------------------------
# Builder — hash-verified dependency install only.
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --require-hashes --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Runtime — installed environment plus application code, nothing else.
# ---------------------------------------------------------------------------
FROM python:3.11-slim

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --chown=appuser:appuser app/ ./app/

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# Shell form so the platform-injected PORT is expanded at start; `exec` keeps
# uvicorn as PID 1 so SIGTERM reaches it directly for graceful shutdown.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
