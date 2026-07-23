##############################################################################
# Module: test_exceptions.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the domain exception layer (app/domain/
#   exceptions.py) — GatewayError carrying a member of the SDD-001 §3.2
#   taxonomy, and the ErrorType -> HTTP status resolver. RBT-78 seeds only
#   TARGET_NOT_FOUND; the resolver's fail-loud default guards a type raised
#   without a declared status (a build defect, RBT-79+ raising sites). The
#   ErrorResponse contract test pins the wire shape the handler renders.
##############################################################################

from app.domain.exceptions import DomainError, GatewayError, resolve_http_status
from app.models import ErrorResponse, ErrorType


class TestGatewayError:
    """GatewayError carries one taxonomy member plus its message and detail."""

    def test_gateway_error_carries_type_message_and_detail(self) -> None:
        # Arrange / Act
        error = GatewayError(
            ErrorType.TARGET_NOT_FOUND, "no such version node", detail="version_id=v-9"
        )

        # Assert
        assert error.error_type is ErrorType.TARGET_NOT_FOUND
        assert error.message == "no such version node"
        assert error.detail == "version_id=v-9"

    def test_gateway_error_detail_defaults_to_none(self) -> None:
        # Arrange / Act
        error = GatewayError(ErrorType.TARGET_NOT_FOUND, "no such node")

        # Assert
        assert error.detail is None

    def test_gateway_error_is_a_domain_error(self) -> None:
        # Arrange / Act / Assert — the handler binds on the DomainError base.
        assert isinstance(GatewayError(ErrorType.TARGET_NOT_FOUND, "x"), DomainError)

    def test_gateway_error_str_is_its_message(self) -> None:
        # Arrange / Act / Assert
        assert str(GatewayError(ErrorType.TARGET_NOT_FOUND, "the message")) == "the message"


class TestResolveHttpStatus:
    """The ErrorType -> HTTP status map: the seeded read type + fail-loud default."""

    def test_resolve_http_status_target_not_found_is_404(self) -> None:
        # Act / Assert — the one read-side raising site RBT-78 wires (point 2b).
        assert resolve_http_status(ErrorType.TARGET_NOT_FOUND) == 404

    def test_resolve_http_status_unmapped_type_defaults_to_500(self) -> None:
        # Act / Assert — a raised-but-unmapped type is a build defect, not a
        # client fault; the default fails loud rather than guessing a 4xx.
        assert resolve_http_status(ErrorType.AUTHOR_VIOLATION) == 500


class TestErrorResponseContract:
    """The §3.2 error envelope renders the taxonomy member as error_code."""

    def test_error_response_serialises_error_code_as_the_taxonomy_value(self) -> None:
        # Arrange
        body = ErrorResponse(
            error_code=ErrorType.TARGET_NOT_FOUND,
            message="no such node",
            correlation_id="cid-1",
        )

        # Act
        dumped = body.model_dump(mode="json")

        # Assert
        assert dumped["success"] is False
        assert dumped["error_code"] == "TARGET_NOT_FOUND"
        assert dumped["message"] == "no such node"
        assert dumped["detail"] is None
        assert dumped["correlation_id"] == "cid-1"
        assert dumped["fault_class"] is None
