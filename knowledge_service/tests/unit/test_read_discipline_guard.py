##############################################################################
# Module: test_read_discipline_guard.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the promoted-only-state contradiction guard
#   (app/domain/shared/read_discipline_guard.py, DDR-002 §5 / §7 #21) — the
#   full truth table: a promoted-origin node may carry retracted/conditional
#   state; any other origin_mechanism claiming either is a contradiction.
##############################################################################

from app.domain.shared.read_discipline_guard import is_promoted_only_state_contradiction


class TestIsPromotedOnlyStateContradiction:
    """The full truth table over origin_mechanism x retracted x applicability_state."""

    def test_promoted_and_retracted_is_not_a_contradiction(self) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="promoted",
                retracted=True,
                applicability_state="unconditional",
            )
            is False
        )

    def test_non_promoted_and_retracted_is_a_contradiction(self) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="ingested",
                retracted=True,
                applicability_state="unconditional",
            )
            is True
        )

    def test_non_promoted_and_conditional_is_a_contradiction(self) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="ingested",
                retracted=False,
                applicability_state="conditional",
            )
            is True
        )

    def test_non_promoted_and_neither_is_not_a_contradiction(self) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="ingested",
                retracted=False,
                applicability_state="unconditional",
            )
            is False
        )

    def test_promoted_and_conditional_is_not_a_contradiction(self) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="promoted",
                retracted=False,
                applicability_state="conditional",
            )
            is False
        )

    def test_promoted_and_both_retracted_and_conditional_is_not_a_contradiction(
        self,
    ) -> None:
        # Act / Assert — a promoted node may legitimately carry both states at
        # once (a retracted, previously-conditional promotion).
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="promoted",
                retracted=True,
                applicability_state="conditional",
            )
            is False
        )

    def test_non_promoted_and_both_retracted_and_conditional_is_a_contradiction(
        self,
    ) -> None:
        # Act / Assert
        assert (
            is_promoted_only_state_contradiction(
                origin_mechanism="derived",
                retracted=True,
                applicability_state="conditional",
            )
            is True
        )
