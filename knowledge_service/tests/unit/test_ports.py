##############################################################################
# Module: test_ports.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Tests for the port declarations (SDD-001 §4.2). These are pure
#   Protocols with no behavior of their own, so what is asserted here is the
#   seam itself: that each port is structurally checkable, and that an object
#   missing the contract does not satisfy it. That last point is what stops a
#   later adapter from being wired in half-implemented.
##############################################################################

from collections.abc import Mapping

from app.ports.graph_store import GraphStoragePort
from app.ports.predicate_eval import PredicateEvaluationPort


class TestGraphStoragePortDeclaration:
    """The substitution seam admits only objects carrying its surface."""

    def test_object_without_check_connectivity_does_not_satisfy_the_port(self) -> None:
        # Arrange
        class NotAGraphStore:
            pass

        # Act / Assert
        assert not isinstance(NotAGraphStore(), GraphStoragePort)

    def test_object_with_check_connectivity_satisfies_the_port(self) -> None:
        # Arrange
        class MinimalGraphStore:
            async def check_connectivity(self) -> bool:
                return True

        # Act / Assert
        assert isinstance(MinimalGraphStore(), GraphStoragePort)


class TestPredicateEvaluationPortDeclaration:
    """Declared at RBT-77, implemented nowhere — DDR-003 owns the grammar."""

    def test_object_without_evaluate_does_not_satisfy_the_port(self) -> None:
        # Arrange
        class NotAnEvaluator:
            pass

        # Act / Assert
        assert not isinstance(NotAnEvaluator(), PredicateEvaluationPort)

    def test_object_with_evaluate_satisfies_the_port(self) -> None:
        # Arrange
        class MinimalEvaluator:
            async def evaluate(
                self,
                predicate: Mapping[str, object],
                context: Mapping[str, object],
            ) -> bool:
                return False

        # Act / Assert
        assert isinstance(MinimalEvaluator(), PredicateEvaluationPort)

    def test_no_predicate_evaluation_adapter_ships_in_this_service_yet(self) -> None:
        # Arrange / Act — an implementation before DDR-003's vocabulary is
        # ratified would be a gateway-local fork of predicate semantics, which
        # SDD-001 §4.2 prohibits.
        import app.adapters as adapters_package

        module_names = dir(adapters_package)

        # Assert
        assert not any("predicate" in name.lower() for name in module_names)
