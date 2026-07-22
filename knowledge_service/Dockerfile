# File: knowledge_service/Dockerfile
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-22
# Description: Multi-stage container build for knowledge-service per the house
#   application-code standard (01-code-structure §9): hash-verified dependency
#   install in the builder, no build toolchain in the runtime image (actively
#   purged — see the runtime stage), non-root runtime user, and a listen port
#   taken from the environment (Cloud Run injects PORT; 8080 is the default).

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

# Purge the installer toolchain — "no build toolchain in the final image"
# (application-code 01-code-structure §9). Two independent sources put it here,
# which is why the purge is ACTIVE rather than a narrower COPY: the runtime base
# image `python:3.11-slim` ships pip/setuptools/wheel natively, AND the blanket
# site-packages copy above carries the builder's set in on top. Narrowing the
# COPY would leave the base image's copies untouched.
#
# This is not hygiene for its own sake. The first governed build of this image
# failed its Trivy gate on two HIGH, fixed-upstream CVEs — CVE-2026-23949
# (jaraco.context) and CVE-2026-24049 (wheel) — both vendored inside setuptools,
# neither an application dependency. Removing the toolchain removes the class,
# not just those two CVEs, and leaves no package installer in a container that
# has no business installing packages at runtime.
#
# Placement is load-bearing: after every COPY, so nothing re-introduces it; and
# before USER, because removal needs root. `pkg_resources` goes with setuptools
# — the trailing assertions are what prove nothing in the dependency set still
# imports it, failing the BUILD rather than the deploy if the purge is wrong.
RUN rm -rf \
      /usr/local/lib/python3.11/site-packages/pip \
      /usr/local/lib/python3.11/site-packages/pip-*.dist-info \
      /usr/local/lib/python3.11/site-packages/setuptools \
      /usr/local/lib/python3.11/site-packages/setuptools-*.dist-info \
      /usr/local/lib/python3.11/site-packages/pkg_resources \
      /usr/local/lib/python3.11/site-packages/wheel \
      /usr/local/lib/python3.11/site-packages/wheel-*.dist-info \
      /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.* \
      /usr/local/bin/wheel \
    && ! python -c "import pip" 2>/dev/null \
    && ! python -c "import setuptools" 2>/dev/null \
    && ! python -c "import wheel" 2>/dev/null \
    && ! python -c "import pkg_resources" 2>/dev/null \
    && python -c "import app.main" \
    && echo "installer toolchain purged; application imports intact"

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# Shell form so the platform-injected PORT is expanded at start; `exec` keeps
# uvicorn as PID 1 so SIGTERM reaches it directly for graceful shutdown.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
