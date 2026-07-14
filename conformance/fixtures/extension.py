##############################################################################
# Module: extension.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the Extension-registry
#   graph-state assertions — DDR-002 §7 #26 (basis-declaration totality).
#
#   Modelling choice: confidence_basis and property_schema are T2 "structured,
#   validator-consumable" declarations (§2.6). Neo4j properties cannot nest maps,
#   so they are stored here as JSON-string properties (the validator-consumable
#   reading), parsed by the assertion. confidence_basis maps node-label ->
#   {"basis": <one of the four>, "freshness_operand": <str, iff basis == aging>};
#   property_schema maps node-label -> (opaque per-property detail; #26 reads only
#   its key-set). The real-schema representation binds at RBT-15.
#
#   Labels/properties match the committed DDR-002 v1.3.0 constants. No native
#   constraints installed.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation graph fixtures for the Extension-registry assertions."""

# --- #26 basis-declaration totality -------------------------------------------
# Conformant, two registrations:
#   plane-cost  — the §2.6 cost-plane exemplar: three non-aging labels
#                 (CapabilityCostEstimate native_confidence; RateCard / CostFactor
#                 non_citable), confidence_basis and property_schema label-sets
#                 equal, no stray operands;
#   plane-aging — an aging label carrying its freshness operand.
BASIS_DECLARATION_CONFORMANT: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-cost', version: 1, status: 'active',
        confidence_basis: '{"CapabilityCostEstimate": {"basis": "native_confidence"},
            "RateCard": {"basis": "non_citable"},
            "CostFactor": {"basis": "non_citable"}}',
        property_schema: '{"CapabilityCostEstimate": {"estimate_id": "string"},
            "RateCard": {"rate_card_id": "string"},
            "CostFactor": {"cost_factor_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-aging', version: 1, status: 'active',
        confidence_basis: '{"SensorReading": {"basis": "aging",
            "freshness_operand": "observed_at"}}',
        property_schema: '{"SensorReading": {"sensor_reading_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: property_schema declares a label (Extra) confidence_basis omits — a
# declared label with no basis.
LABEL_WITHOUT_BASIS: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-label-nobasis', version: 1,
        status: 'active',
        confidence_basis: '{"Known": {"basis": "flat_base"}}',
        property_schema: '{"Known": {"known_id": "string"}, "Extra": {"extra_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: confidence_basis declares a label (Ghost) property_schema omits — a
# basis for an undeclared label.
BASIS_FOR_UNDECLARED_LABEL: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-extrabasis', version: 1,
        status: 'active',
        confidence_basis: '{"Real": {"basis": "flat_base"}, "Ghost": {"basis": "non_citable"}}',
        property_schema: '{"Real": {"real_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a label whose basis is outside the four-way enumeration.
INVALID_BASIS_VALUE: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-badbasis', version: 1, status: 'active',
        confidence_basis: '{"Thing": {"basis": "made_up_basis"}}',
        property_schema: '{"Thing": {"thing_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: an aging label with no freshness operand.
AGING_WITHOUT_OPERAND: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-aging-noop', version: 1, status: 'active',
        confidence_basis: '{"Drifty": {"basis": "aging"}}',
        property_schema: '{"Drifty": {"drifty_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a non-aging label carrying a stray freshness operand.
STRAY_OPERAND_ON_NON_AGING: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-strayop', version: 1, status: 'active',
        confidence_basis: '{"Steady": {"basis": "flat_base", "freshness_operand": "observed_at"}}',
        property_schema: '{"Steady": {"steady_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a PlaneDefinition with no confidence_basis / property_schema at all —
# unverifiable for totality, must fail loud (the A-1/A-3 pattern; both are T2).
MISSING_DECLARATION: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-nodecl', version: 1, status: 'active',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a present-but-unparseable declaration (a non-JSON string) — likewise
# unverifiable, must fail loud rather than skip.
UNPARSEABLE_DECLARATION: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-unparseable', version: 1,
        status: 'active',
        confidence_basis: 'this is not valid json',
        property_schema: '{"X": {"x_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a duplicate label key in confidence_basis. json.loads keeps last-wins
# by default, silently collapsing the "exactly one basis per label" violation in
# the stored bytes; the parse's object_pairs_hook must reject it (A-4).
DUPLICATE_LABEL_KEY: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-dupkey', version: 1, status: 'active',
        confidence_basis: '{"Dup": {"basis": "flat_base"}, "Dup": {"basis": "aging"}}',
        property_schema: '{"Dup": {"dup_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a declaration stored as a non-string property (here an integer) —
# not a serialized declaration at all; unverifiable, fail loud.
NON_STRING_DECLARATION: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-nonstring', version: 1,
        status: 'active',
        confidence_basis: 42,
        property_schema: '{"X": {"x_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a declaration that is valid JSON but not an object (a JSON array) —
# the top-level label map is required.
NON_OBJECT_JSON_DECLARATION: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-nonobject', version: 1,
        status: 'active',
        confidence_basis: '[1, 2, 3]',
        property_schema: '{"X": {"x_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a label whose basis declaration is not an object (a bare string where
# a {"basis": ...} map is required) — malformed.
MALFORMED_LABEL_DECLARATION: list[str] = [
    """
    CREATE (:Extension:PlaneDefinition {plane_id: 'plane-malformed', version: 1,
        status: 'active',
        confidence_basis: '{"Thing": "flat_base"}',
        property_schema: '{"Thing": {"thing_id": "string"}}',
        origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]
