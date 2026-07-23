##############################################################################
# Module: test_envelope.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the §3.2 envelope assembler (app/domain/shared/
#   envelope.py) — assemble_envelope populating every ResultEnvelope field
#   from an EnvelopeAttribution, the catalog_eligibility named-forward slot
#   staying None, and build_disclosure_entry carrying only identity + reason.
##############################################################################

from app.domain.shared.envelope import (
    EnvelopeAttribution,
    assemble_envelope,
    build_disclosure_entry,
)
from app.models import ConditionalAdmissionStatus, DisclosureReason

_ATTRIBUTION = EnvelopeAttribution(
    node_id="node-1",
    node_kind="Technology",
    plane_labels=("Catalog",),
    origin_mechanism="promoted",
    derivation_class=None,
    version="3",
    effective_from="2026-01-01T00:00:00Z",
    effective_to=None,
    version_pin="v-3",
    confidences=(0.9,),
)


class TestAssembleEnvelope:
    """assemble_envelope populates every §3.2 field from the attribution."""

    def test_assemble_envelope_populates_identity_and_attribution_fields(self) -> None:
        # Act
        envelope = assemble_envelope(
            _ATTRIBUTION, conditional_admission=ConditionalAdmissionStatus.UNCONDITIONAL
        )

        # Assert
        assert envelope.node_id == "node-1"
        assert envelope.node_kind == "Technology"
        assert envelope.plane_labels == ["Catalog"]
        assert envelope.origin_mechanism == "promoted"
        assert envelope.derivation_class is None
        assert envelope.version == "3"
        assert envelope.effective_from == "2026-01-01T00:00:00Z"
        assert envelope.effective_to is None
        assert envelope.version_pin == "v-3"
        assert envelope.confidences == [0.9]

    def test_assemble_envelope_carries_the_conditional_admission_status(self) -> None:
        # Act
        envelope = assemble_envelope(
            _ATTRIBUTION,
            conditional_admission=ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED,
        )

        # Assert
        assert (
            envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )

    def test_assemble_envelope_leaves_catalog_eligibility_as_the_forward_slot(self) -> None:
        # Act — R2 computes no catalog-eligibility fit-rule; R3's slot.
        envelope = assemble_envelope(
            _ATTRIBUTION, conditional_admission=ConditionalAdmissionStatus.UNCONDITIONAL
        )

        # Assert
        assert envelope.applicability.catalog_eligibility is None

    def test_assemble_envelope_carries_multiple_composed_confidences(self) -> None:
        # Arrange — node confidence + composed edge confidence (DDR-002 §3/§4).
        attribution = EnvelopeAttribution(
            node_id="node-2",
            node_kind="Pattern",
            plane_labels=("Catalog", "Standards"),
            origin_mechanism="ingested",
            derivation_class="primary",
            version="1",
            effective_from=None,
            effective_to=None,
            version_pin="v-1",
            confidences=(0.8, 0.6),
        )

        # Act
        envelope = assemble_envelope(
            attribution, conditional_admission=ConditionalAdmissionStatus.UNCONDITIONAL
        )

        # Assert
        assert envelope.plane_labels == ["Catalog", "Standards"]
        assert envelope.derivation_class == "primary"
        assert envelope.confidences == [0.8, 0.6]


class TestBuildDisclosureEntry:
    """build_disclosure_entry carries only identity and reason — no content."""

    def test_build_disclosure_entry_carries_node_id_and_reason(self) -> None:
        # Act
        entry = build_disclosure_entry("node-9", DisclosureReason.CONDITION_UNSATISFIED)

        # Assert
        assert entry.node_id == "node-9"
        assert entry.reason == DisclosureReason.CONDITION_UNSATISFIED

    def test_build_disclosure_entry_has_no_content_payload_fields(self) -> None:
        # Act
        entry = build_disclosure_entry("node-9", DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT)

        # Assert — exactly the two fields the §3.2 contract permits.
        assert set(entry.model_dump()) == {"node_id", "reason"}
