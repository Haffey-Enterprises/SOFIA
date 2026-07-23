##############################################################################
# Module: app/domain/shared/catalog_eligibility.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The Catalog-eligibility fit-rule (SDD-001 §4.4; DDR-002 §2.1,
#   §5) — shared because more than one Catalog read op computes it (resolve-
#   technology now, select-patterns next). A pure function over primitives, not
#   a class: there is no state to carry between calls, and every future
#   Catalog-eligibility consumer supplies its own Technology's field values.
#   Annotation only (§4.4) — this function has no opinion on exclusion; it is
#   the caller's job to still return an ineligible candidate, merely annotated.
##############################################################################

from collections.abc import Sequence

from app.models import CatalogEligibility


def compute_catalog_eligibility(
    *,
    tier_applicability: Sequence[str],
    approved_data_classifications: Sequence[str],
    environment_class: str,
    data_classification: str,
) -> CatalogEligibility:
    """Compute the Catalog-eligibility verdict for one Technology (DDR-002 §2.1).

    Args:
        tier_applicability: The Technology's declared `tier_applicability[]`.
        approved_data_classifications: The Technology's declared
            `approved_data_classifications[]`.
        environment_class: The consuming context's `environment_class`.
        data_classification: The consuming context's `data_classification`.

    Returns:
        `eligible=True` iff both fields fit; otherwise `eligible=False` with
        `failing_fields` naming every check that failed (never invented beyond
        the two declared fields).
    """
    failing_fields: list[str] = []

    if environment_class not in tier_applicability:
        failing_fields.append("tier_applicability")

    if data_classification not in approved_data_classifications:
        failing_fields.append("approved_data_classifications")

    return CatalogEligibility(eligible=not failing_fields, failing_fields=failing_fields)
