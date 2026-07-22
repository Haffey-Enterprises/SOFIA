##############################################################################
# Module: config.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Typed runtime configuration for knowledge-service (SDD-001
#   §4.6) — service identity, the platform-injected listen port, log level, and
#   the Neo4j URI/database/credential/pool-sizing surface. Every value arrives
#   from the environment through this class; no module elsewhere reads
#   os.environ directly. The graph credential is held as a SecretStr so the
#   Tier 4 value cannot reach a log line, an error message, or a response by
#   accident.
##############################################################################

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Environment-sourced configuration for the knowledge-service process.

    Values bind from environment variables under the `KS_` prefix, with one
    deliberate exception: `port` binds from the bare `PORT` variable, because
    the serverless runtime injects the listen port under that unprefixed name.

    Credentials are environment-delivered only. In deployed environments they
    arrive from GCP Secret Manager under Workload Identity Federation — never
    from a key file, a committed config, or a Kubernetes Secret (SDD-001 §4.6).
    """

    model_config = SettingsConfigDict(
        env_prefix="KS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Service identity --------------------------------------------------
    service_name: str = "knowledge-service"
    service_version: str = "0.1.0"
    app_env: str = "development"

    # --- HTTP --------------------------------------------------------------
    port: int = Field(default=8080, ge=1, le=65535, validation_alias="PORT")

    # --- Logging -----------------------------------------------------------
    log_level: LogLevel = "INFO"

    # --- Neo4j (the graph system of record) --------------------------------
    # The URI is opaque configuration by design: production topology is
    # deferred upstream (ADR-002 §5.2), so this service pins no cluster scheme.
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_database: str = "neo4j"
    neo4j_username: str = "neo4j"
    neo4j_password: SecretStr = SecretStr("")
    neo4j_max_connection_pool_size: int = Field(default=50, ge=1)
    neo4j_connection_acquisition_timeout_seconds: float = Field(default=60.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide Settings instance.

    Memoised: configuration is read once at startup and never mutated
    thereafter, which keeps the service stateless across requests.

    Returns:
        The single Settings instance for this process.
    """
    return Settings()
