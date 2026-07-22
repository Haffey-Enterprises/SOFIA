##############################################################################
# Module: test_config.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for the knowledge-service Settings surface (SDD-001
#   §4.6) — service identity, the platform-injected PORT, log level, the Neo4j
#   URI/database/pool-sizing tunables, and the discipline that keeps the graph
#   credential out of source, logs, and repr output.
##############################################################################

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings

# mypy note: pydantic-settings accepts `_env_file` at runtime, but the model's
# generated __init__ signature does not declare it, so `--strict` flags every
# call. The argument is load-bearing here: it isolates the suite from a
# developer's local .env. Hence the narrow, coded ignores below.


class TestSettingsDefaults:
    """The defaults a developer gets with an empty environment."""

    def test_settings_with_no_environment_uses_documented_defaults(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.delenv("PORT", raising=False)

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.service_name == "knowledge-service"
        assert settings.app_env == "development"
        assert settings.port == 8080
        assert settings.log_level == "INFO"
        assert settings.neo4j_database == "neo4j"
        assert settings.neo4j_max_connection_pool_size == 50


class TestSettingsEnvironmentBinding:
    """Every value is environment-overridable; PORT binds by its bare name."""

    def test_settings_reads_prefixed_variables_from_the_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("KS_SERVICE_NAME", "knowledge-service-canary")
        monkeypatch.setenv("KS_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("KS_NEO4J_URI", "neo4j+s://graph.example.internal:7687")
        monkeypatch.setenv("KS_NEO4J_DATABASE", "sofia")
        monkeypatch.setenv("KS_NEO4J_MAX_CONNECTION_POOL_SIZE", "17")

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.service_name == "knowledge-service-canary"
        assert settings.log_level == "DEBUG"
        assert settings.neo4j_uri == "neo4j+s://graph.example.internal:7687"
        assert settings.neo4j_database == "sofia"
        assert settings.neo4j_max_connection_pool_size == 17

    def test_settings_binds_port_from_the_unprefixed_platform_variable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange — Cloud Run injects a bare `PORT`, not a service-prefixed one.
        monkeypatch.setenv("PORT", "9091")

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert settings.port == 9091

    def test_settings_with_out_of_range_port_raises_validation_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("PORT", "70000")

        # Act / Assert
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]

    def test_settings_with_unrecognised_log_level_raises_validation_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("KS_LOG_LEVEL", "CHATTY")

        # Act / Assert
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]


class TestSettingsCredentialDiscipline:
    """The graph credential is Tier 4: it must not leak through repr or logs."""

    def test_settings_neo4j_password_is_not_exposed_by_repr_or_str(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        monkeypatch.setenv("KS_NEO4J_PASSWORD", "super-secret-value")

        # Act
        settings = Settings(_env_file=None)  # type: ignore[call-arg]

        # Assert
        assert "super-secret-value" not in repr(settings)
        assert "super-secret-value" not in str(settings)
        assert settings.neo4j_password.get_secret_value() == "super-secret-value"


class TestGetSettings:
    """The factory is memoised so configuration is fixed once at startup."""

    def test_get_settings_returns_the_same_instance_on_repeated_calls(self) -> None:
        # Arrange
        get_settings.cache_clear()

        # Act
        first = get_settings()
        second = get_settings()

        # Assert
        assert first is second
