##############################################################################
# Module: test_catalog_eligibility.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the shared Catalog-eligibility fit-rule (app/
#   domain/shared/catalog_eligibility.py, SDD-001 §4.4; DDR-002 §2.1) — tier
#   fit, classification fit, both failing named, and the eligible case naming
#   nothing.
##############################################################################

from app.domain.shared.catalog_eligibility import compute_catalog_eligibility


class TestComputeCatalogEligibility:
    """Eligible iff both tier fit and classification fit pass."""

    def test_eligible_when_both_fields_fit(self) -> None:
        # Act
        verdict = compute_catalog_eligibility(
            tier_applicability=("production", "staging"),
            approved_data_classifications=("internal", "confidential"),
            environment_class="production",
            data_classification="internal",
        )

        # Assert
        assert verdict.eligible is True
        assert verdict.failing_fields == []

    def test_ineligible_when_tier_does_not_fit_names_tier_applicability(self) -> None:
        # Act
        verdict = compute_catalog_eligibility(
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
            environment_class="dev",
            data_classification="internal",
        )

        # Assert
        assert verdict.eligible is False
        assert verdict.failing_fields == ["tier_applicability"]

    def test_ineligible_when_classification_does_not_fit_names_it(self) -> None:
        # Act
        verdict = compute_catalog_eligibility(
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
            environment_class="production",
            data_classification="restricted",
        )

        # Assert
        assert verdict.eligible is False
        assert verdict.failing_fields == ["approved_data_classifications"]

    def test_ineligible_when_both_fields_fail_names_both(self) -> None:
        # Act
        verdict = compute_catalog_eligibility(
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
            environment_class="dev",
            data_classification="restricted",
        )

        # Assert
        assert verdict.eligible is False
        assert verdict.failing_fields == ["tier_applicability", "approved_data_classifications"]

    def test_ineligible_when_tier_applicability_is_empty(self) -> None:
        # Arrange / Act — no declared tiers means no context fits.
        verdict = compute_catalog_eligibility(
            tier_applicability=(),
            approved_data_classifications=("internal",),
            environment_class="production",
            data_classification="internal",
        )

        # Assert
        assert verdict.eligible is False
        assert verdict.failing_fields == ["tier_applicability"]
