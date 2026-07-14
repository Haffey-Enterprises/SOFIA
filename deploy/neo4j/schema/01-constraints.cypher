// ============================================================================
// File: deploy/neo4j/schema/01-constraints.cypher   (proposed repo location)
// Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
// Ticket: RBT-58 (BUILD prep — graph-store provisioning + KG seed dataset)
// Purpose: Schema bootstrap — the DDR-002 §7 DB-ENFORCED constraint set + the
//   lean provisional index set, applied to the provisioned Neo4j *Enterprise*
//   instance BEFORE the ground-truth seed load. This is the "DDR-002 §7
//   DB-enforced set applied and verified" acceptance leg.
//
// Authority (fresh-fetch, do not recall): DDR-002 v1.3.0 §1, §2.1–§2.6, §4, §5,
//   §6, §7 — docs/ddr/DDR-002-graph-schema.md, content sha256
//   8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16.
//   Label/property names conform to conformance/schema_constants.py (the M-2
//   single-source parity mitigation); re-verify the pin above before any refresh.
//
// EDITION DEPENDENCY (ADR-002 §2.2 warrant, verified 2026-07-14): the EXISTENCE
//   constraints below (Sections 3–4) are Neo4j *Enterprise*-only. Uniqueness
//   (Sections 1–2) runs on both editions; existence is the Enterprise-only half
//   the store is provisioned for. This split is deliberate and left visible.
//
// SCOPE — this file is the DB-EXPRESSIBLE set ONLY. The DDR-002 §7 CI-only
//   invariants (#1,#7,#9,#10,#13,#14,#15,#16,#17,#19,#20,#21,#22,#23,#24,#25,
//   #26,#27, plus "one active version per business_key" #4) are NOT expressible
//   as Neo4j constraints and are enforced by the conformance harness / gateway —
//   NOT here. See conformance/ and SDD-001. Do not attempt to add them below.
//
// Idempotent: every statement uses IF NOT EXISTS. Safe to re-run.
// ============================================================================


// ----------------------------------------------------------------------------
// SECTION 1 — PK UNIQUENESS  (DDR-002 §7 "Uniqueness on every PK"; both editions)
//   One per entity label. PK = <entity>_id per the §1 naming convention.
// ----------------------------------------------------------------------------

// Catalog plane (§2.1)
CREATE CONSTRAINT uniq_pattern_pk       IF NOT EXISTS FOR (n:Pattern)              REQUIRE n.pattern_id          IS UNIQUE;
CREATE CONSTRAINT uniq_capability_pk    IF NOT EXISTS FOR (n:Capability)           REQUIRE n.capability_id       IS UNIQUE;
CREATE CONSTRAINT uniq_technology_pk    IF NOT EXISTS FOR (n:Technology)           REQUIRE n.technology_id       IS UNIQUE;
CREATE CONSTRAINT uniq_iactemplate_pk   IF NOT EXISTS FOR (n:IacTemplate)          REQUIRE n.iac_template_id     IS UNIQUE;

// Environment plane (§2.2)
CREATE CONSTRAINT uniq_deployedsvc_pk   IF NOT EXISTS FOR (n:DeployedService)      REQUIRE n.deployed_service_id IS UNIQUE;
CREATE CONSTRAINT uniq_deployenv_pk     IF NOT EXISTS FOR (n:DeploymentEnvironment) REQUIRE n.environment_id      IS UNIQUE;
CREATE CONSTRAINT uniq_configitem_pk    IF NOT EXISTS FOR (n:ConfigurationItem)    REQUIRE n.ci_id               IS UNIQUE;

// Operational plane (§2.3)
CREATE CONSTRAINT uniq_observedpat_pk   IF NOT EXISTS FOR (n:ObservedPattern)      REQUIRE n.observed_pattern_id IS UNIQUE;

// Governance plane (§2.4) — decision_id lives on the :Decision supertype
CREATE CONSTRAINT uniq_decision_pk      IF NOT EXISTS FOR (n:Decision)             REQUIRE n.decision_id         IS UNIQUE;
CREATE CONSTRAINT uniq_actor_pk         IF NOT EXISTS FOR (n:Actor)                REQUIRE n.actor_id            IS UNIQUE;
CREATE CONSTRAINT uniq_role_pk          IF NOT EXISTS FOR (n:Role)                 REQUIRE n.role_id             IS UNIQUE;
CREATE CONSTRAINT uniq_attestation_pk   IF NOT EXISTS FOR (n:Attestation)          REQUIRE n.attestation_id      IS UNIQUE;
CREATE CONSTRAINT uniq_condition_pk     IF NOT EXISTS FOR (n:Condition)            REQUIRE n.condition_id        IS UNIQUE;

// Standards plane (§2.5)
CREATE CONSTRAINT uniq_standard_pk      IF NOT EXISTS FOR (n:Standard)             REQUIRE n.standard_id         IS UNIQUE;
CREATE CONSTRAINT uniq_policyrule_pk    IF NOT EXISTS FOR (n:PolicyRule)           REQUIRE n.policy_rule_id      IS UNIQUE;
CREATE CONSTRAINT uniq_control_pk       IF NOT EXISTS FOR (n:ComplianceControl)    REQUIRE n.control_id          IS UNIQUE;

// Extension registry + Cost plane (§2.6)
CREATE CONSTRAINT uniq_planedef_pk      IF NOT EXISTS FOR (n:PlaneDefinition)      REQUIRE n.plane_id            IS UNIQUE;
CREATE CONSTRAINT uniq_ratecard_pk      IF NOT EXISTS FOR (n:RateCard)             REQUIRE n.rate_card_id        IS UNIQUE;
CREATE CONSTRAINT uniq_costfactor_pk    IF NOT EXISTS FOR (n:CostFactor)           REQUIRE n.cost_factor_id      IS UNIQUE;
CREATE CONSTRAINT uniq_costestimate_pk  IF NOT EXISTS FOR (n:CapabilityCostEstimate) REQUIRE n.estimate_id       IS UNIQUE;

// Reasoning Graph (§4) — authored + surrogate + derived + candidate
CREATE CONSTRAINT uniq_session_pk       IF NOT EXISTS FOR (n:ReasoningSession)     REQUIRE n.session_id          IS UNIQUE;
CREATE CONSTRAINT uniq_progress_pk      IF NOT EXISTS FOR (n:ReasoningProgress)    REQUIRE n.progress_id         IS UNIQUE;
CREATE CONSTRAINT uniq_evidence_pk      IF NOT EXISTS FOR (n:Evidence)             REQUIRE n.evidence_id         IS UNIQUE;
CREATE CONSTRAINT uniq_rejectedalt_pk   IF NOT EXISTS FOR (n:RejectedAlternative)  REQUIRE n.rejected_id         IS UNIQUE;
CREATE CONSTRAINT uniq_provsummary_pk   IF NOT EXISTS FOR (n:ProvenanceSummary)    REQUIRE n.provenance_summary_id IS UNIQUE;
CREATE CONSTRAINT uniq_candidate_pk     IF NOT EXISTS FOR (n:CandidatePromotion)   REQUIRE n.candidate_id        IS UNIQUE;

// Artifact family (§5) — artifact_id is the family PK (Solution etc.)
CREATE CONSTRAINT uniq_artifact_pk      IF NOT EXISTS FOR (n:Artifact)             REQUIRE n.artifact_id         IS UNIQUE;


// ----------------------------------------------------------------------------
// SECTION 2 — VERSIONED-GROUND-TRUTH (business_key, version) UNIQUENESS
//   DDR-002 §7 + §6: scoped EXACTLY to the versioned-ground-truth types —
//   Catalog (all four), Standards {Standard, PolicyRule}, RateCard, CostFactor,
//   PlaneDefinition. (ComplianceControl, CapabilityCostEstimate, Solution are
//   NOT versioned-ground-truth — §2.5/§2.6/§6 — so no composite here.)
//   "Exactly one active version per business_key" is CI-only (#4) — not here.
// ----------------------------------------------------------------------------

CREATE CONSTRAINT uniq_pattern_bk_ver     IF NOT EXISTS FOR (n:Pattern)         REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_capability_bk_ver  IF NOT EXISTS FOR (n:Capability)      REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_technology_bk_ver  IF NOT EXISTS FOR (n:Technology)      REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_iactemplate_bk_ver IF NOT EXISTS FOR (n:IacTemplate)     REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_standard_bk_ver    IF NOT EXISTS FOR (n:Standard)        REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_policyrule_bk_ver  IF NOT EXISTS FOR (n:PolicyRule)      REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_ratecard_bk_ver    IF NOT EXISTS FOR (n:RateCard)        REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_costfactor_bk_ver  IF NOT EXISTS FOR (n:CostFactor)      REQUIRE (n.business_key, n.version) IS UNIQUE;
CREATE CONSTRAINT uniq_planedef_bk_ver    IF NOT EXISTS FOR (n:PlaneDefinition) REQUIRE (n.business_key, n.version) IS UNIQUE;


// ----------------------------------------------------------------------------
// SECTION 3 — EXISTENCE: PROVENANCE GROUP  (ENTERPRISE-ONLY)
//   DDR-002 §7 + §4 (RG-provenance posture): (origin_mechanism, recorded_at)
//   NOT NULL on every KG node + the three authored RG types + ProvenanceSummary
//   + the Artifact family. Applied per PLANE label for KG nodes (every KG node
//   carries a plane label, §1) — the lean form of "every KG node".
//
//   EXCLUDED, by design:
//     - :Evidence — the SOLE surrogate-only RG type; its provenance is
//       STRUCTURAL (SOURCED_FROM + version pin, atomic capture-unit), CI-only
//       #14 — NOT a property group (§4).
//     - :CandidatePromotion — §5 lists it as carrying provenance(T1), but §7's
//       existence scope enumeration does NOT include it. Following §7 (the
//       constraint authority) literally: no existence constraint here.
//       >> FLAG for Tad/DDR-002 next-touch: §5-provenance-T1 vs §7-existence-scope
//          for CandidatePromotion is a genuine ambiguity; resolve in the record,
//          not by inventing a constraint the §7 contract doesn't list.
// ----------------------------------------------------------------------------

// KG planes (§2) — covers Catalog/Environment/Operational/Governance/Standards/Extension/Cost
CREATE CONSTRAINT exist_catalog_origin     IF NOT EXISTS FOR (n:Catalog)     REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_catalog_recorded   IF NOT EXISTS FOR (n:Catalog)     REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_env_origin         IF NOT EXISTS FOR (n:Environment) REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_env_recorded       IF NOT EXISTS FOR (n:Environment) REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_op_origin          IF NOT EXISTS FOR (n:Operational) REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_op_recorded        IF NOT EXISTS FOR (n:Operational) REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_gov_origin         IF NOT EXISTS FOR (n:Governance)  REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_gov_recorded       IF NOT EXISTS FOR (n:Governance)  REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_std_origin         IF NOT EXISTS FOR (n:Standards)   REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_std_recorded       IF NOT EXISTS FOR (n:Standards)   REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_ext_origin         IF NOT EXISTS FOR (n:Extension)   REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_ext_recorded       IF NOT EXISTS FOR (n:Extension)   REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_cost_origin        IF NOT EXISTS FOR (n:Cost)        REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_cost_recorded      IF NOT EXISTS FOR (n:Cost)        REQUIRE n.recorded_at      IS NOT NULL;

// Authored RG types + derived ProvenanceSummary (no plane label, §4)
CREATE CONSTRAINT exist_session_origin     IF NOT EXISTS FOR (n:ReasoningSession)    REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_session_recorded   IF NOT EXISTS FOR (n:ReasoningSession)    REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_progress_origin    IF NOT EXISTS FOR (n:ReasoningProgress)   REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_progress_recorded  IF NOT EXISTS FOR (n:ReasoningProgress)   REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_rejalt_origin      IF NOT EXISTS FOR (n:RejectedAlternative) REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_rejalt_recorded    IF NOT EXISTS FOR (n:RejectedAlternative) REQUIRE n.recorded_at      IS NOT NULL;
CREATE CONSTRAINT exist_provsum_origin     IF NOT EXISTS FOR (n:ProvenanceSummary)   REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_provsum_recorded   IF NOT EXISTS FOR (n:ProvenanceSummary)   REQUIRE n.recorded_at      IS NOT NULL;

// Artifact family (§5)
CREATE CONSTRAINT exist_artifact_origin    IF NOT EXISTS FOR (n:Artifact)            REQUIRE n.origin_mechanism IS NOT NULL;
CREATE CONSTRAINT exist_artifact_recorded  IF NOT EXISTS FOR (n:Artifact)            REQUIRE n.recorded_at      IS NOT NULL;


// ----------------------------------------------------------------------------
// SECTION 4 — EXISTENCE: T1 REQUIRED PROPS  (ENTERPRISE-ONLY)
//   DDR-002 §7 "plus each node's T1 required props": the PK on every label, and
//   business_key + version on the versioned-ground-truth types (Section 2 set)
//   + Solution.version (T1, §5). Makes the PK truly required (uniqueness alone
//   does not imply existence in Neo4j).
// ----------------------------------------------------------------------------

// PK existence — one per entity label (mirrors Section 1)
CREATE CONSTRAINT exist_pattern_pk      IF NOT EXISTS FOR (n:Pattern)               REQUIRE n.pattern_id          IS NOT NULL;
CREATE CONSTRAINT exist_capability_pk   IF NOT EXISTS FOR (n:Capability)            REQUIRE n.capability_id       IS NOT NULL;
CREATE CONSTRAINT exist_technology_pk   IF NOT EXISTS FOR (n:Technology)            REQUIRE n.technology_id       IS NOT NULL;
CREATE CONSTRAINT exist_iactemplate_pk  IF NOT EXISTS FOR (n:IacTemplate)           REQUIRE n.iac_template_id     IS NOT NULL;
CREATE CONSTRAINT exist_deployedsvc_pk  IF NOT EXISTS FOR (n:DeployedService)       REQUIRE n.deployed_service_id IS NOT NULL;
CREATE CONSTRAINT exist_deployenv_pk    IF NOT EXISTS FOR (n:DeploymentEnvironment) REQUIRE n.environment_id      IS NOT NULL;
CREATE CONSTRAINT exist_configitem_pk   IF NOT EXISTS FOR (n:ConfigurationItem)     REQUIRE n.ci_id               IS NOT NULL;
CREATE CONSTRAINT exist_observedpat_pk  IF NOT EXISTS FOR (n:ObservedPattern)       REQUIRE n.observed_pattern_id IS NOT NULL;
CREATE CONSTRAINT exist_decision_pk     IF NOT EXISTS FOR (n:Decision)              REQUIRE n.decision_id         IS NOT NULL;
CREATE CONSTRAINT exist_actor_pk        IF NOT EXISTS FOR (n:Actor)                 REQUIRE n.actor_id            IS NOT NULL;
CREATE CONSTRAINT exist_role_pk         IF NOT EXISTS FOR (n:Role)                  REQUIRE n.role_id             IS NOT NULL;
CREATE CONSTRAINT exist_attestation_pk  IF NOT EXISTS FOR (n:Attestation)           REQUIRE n.attestation_id      IS NOT NULL;
CREATE CONSTRAINT exist_condition_pk    IF NOT EXISTS FOR (n:Condition)             REQUIRE n.condition_id        IS NOT NULL;
CREATE CONSTRAINT exist_standard_pk     IF NOT EXISTS FOR (n:Standard)              REQUIRE n.standard_id         IS NOT NULL;
CREATE CONSTRAINT exist_policyrule_pk   IF NOT EXISTS FOR (n:PolicyRule)            REQUIRE n.policy_rule_id      IS NOT NULL;
CREATE CONSTRAINT exist_control_pk      IF NOT EXISTS FOR (n:ComplianceControl)     REQUIRE n.control_id          IS NOT NULL;
CREATE CONSTRAINT exist_planedef_pk     IF NOT EXISTS FOR (n:PlaneDefinition)       REQUIRE n.plane_id            IS NOT NULL;
CREATE CONSTRAINT exist_ratecard_pk     IF NOT EXISTS FOR (n:RateCard)              REQUIRE n.rate_card_id        IS NOT NULL;
CREATE CONSTRAINT exist_costfactor_pk   IF NOT EXISTS FOR (n:CostFactor)            REQUIRE n.cost_factor_id      IS NOT NULL;
CREATE CONSTRAINT exist_costestimate_pk IF NOT EXISTS FOR (n:CapabilityCostEstimate) REQUIRE n.estimate_id        IS NOT NULL;
CREATE CONSTRAINT exist_session_pk      IF NOT EXISTS FOR (n:ReasoningSession)      REQUIRE n.session_id          IS NOT NULL;
CREATE CONSTRAINT exist_progress_pk     IF NOT EXISTS FOR (n:ReasoningProgress)     REQUIRE n.progress_id         IS NOT NULL;
CREATE CONSTRAINT exist_evidence_pk     IF NOT EXISTS FOR (n:Evidence)              REQUIRE n.evidence_id         IS NOT NULL;
CREATE CONSTRAINT exist_rejectedalt_pk  IF NOT EXISTS FOR (n:RejectedAlternative)   REQUIRE n.rejected_id         IS NOT NULL;
CREATE CONSTRAINT exist_provsummary_pk  IF NOT EXISTS FOR (n:ProvenanceSummary)     REQUIRE n.provenance_summary_id IS NOT NULL;
CREATE CONSTRAINT exist_candidate_pk    IF NOT EXISTS FOR (n:CandidatePromotion)    REQUIRE n.candidate_id        IS NOT NULL;
CREATE CONSTRAINT exist_artifact_pk     IF NOT EXISTS FOR (n:Artifact)              REQUIRE n.artifact_id         IS NOT NULL;

// business_key + version existence — versioned-ground-truth types (Section 2 set)
CREATE CONSTRAINT exist_pattern_bk       IF NOT EXISTS FOR (n:Pattern)         REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_pattern_ver      IF NOT EXISTS FOR (n:Pattern)         REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_capability_bk    IF NOT EXISTS FOR (n:Capability)      REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_capability_ver   IF NOT EXISTS FOR (n:Capability)      REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_technology_bk    IF NOT EXISTS FOR (n:Technology)      REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_technology_ver   IF NOT EXISTS FOR (n:Technology)      REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_iactemplate_bk   IF NOT EXISTS FOR (n:IacTemplate)     REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_iactemplate_ver  IF NOT EXISTS FOR (n:IacTemplate)     REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_standard_bk      IF NOT EXISTS FOR (n:Standard)        REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_standard_ver     IF NOT EXISTS FOR (n:Standard)        REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_policyrule_bk    IF NOT EXISTS FOR (n:PolicyRule)      REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_policyrule_ver   IF NOT EXISTS FOR (n:PolicyRule)      REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_ratecard_bk      IF NOT EXISTS FOR (n:RateCard)        REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_ratecard_ver     IF NOT EXISTS FOR (n:RateCard)        REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_costfactor_bk    IF NOT EXISTS FOR (n:CostFactor)      REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_costfactor_ver   IF NOT EXISTS FOR (n:CostFactor)      REQUIRE n.version      IS NOT NULL;
CREATE CONSTRAINT exist_planedef_bk      IF NOT EXISTS FOR (n:PlaneDefinition) REQUIRE n.business_key IS NOT NULL;
CREATE CONSTRAINT exist_planedef_ver     IF NOT EXISTS FOR (n:PlaneDefinition) REQUIRE n.version      IS NOT NULL;

// Solution carries version (T1, §5) though it is not versioned-ground-truth (dual-home)
CREATE CONSTRAINT exist_artifact_ver     IF NOT EXISTS FOR (n:Artifact)        REQUIRE n.version      IS NOT NULL;


// ----------------------------------------------------------------------------
// SECTION 5 — LEAN INDEX SET  (DDR-002 §7 "flagged T2 traversal/filter props only")
//   PROVISIONAL per §7 ("revisitable once the SDDs surface real query patterns").
//   Plane secondary-labels are inherently indexed — not repeated here.
//   DEFERRED to RBT-15 (knowledge-service SDD retrieval patterns), NOT here:
//     - the reverse SOURCED_FROM lookup index (KG-node -> citing Evidence), §7.
//     - Capability l1/l2/l3_taxonomy retrieval-substrate indexing (§2.1 -> SDD).
//     - applicability_state index (set at promotion; §5) -> gateway build.
// ----------------------------------------------------------------------------

CREATE INDEX idx_pattern_type        IF NOT EXISTS FOR (n:Pattern)               ON (n.pattern_type);
CREATE INDEX idx_pattern_status      IF NOT EXISTS FOR (n:Pattern)               ON (n.status);
CREATE INDEX idx_technology_approval IF NOT EXISTS FOR (n:Technology)            ON (n.approval_status);
CREATE INDEX idx_deployedsvc_life    IF NOT EXISTS FOR (n:DeployedService)       ON (n.lifecycle_state);
CREATE INDEX idx_deployenv_class     IF NOT EXISTS FOR (n:DeploymentEnvironment) ON (n.environment_class);
CREATE INDEX idx_configitem_type     IF NOT EXISTS FOR (n:ConfigurationItem)     ON (n.ci_type);
CREATE INDEX idx_observedpat_pol     IF NOT EXISTS FOR (n:ObservedPattern)       ON (n.polarity);
CREATE INDEX idx_observedpat_type    IF NOT EXISTS FOR (n:ObservedPattern)       ON (n.pattern_type);
CREATE INDEX idx_observedpat_status  IF NOT EXISTS FOR (n:ObservedPattern)       ON (n.status);
CREATE INDEX idx_gatedecision_gate   IF NOT EXISTS FOR (n:GateDecision)          ON (n.gate);
CREATE INDEX idx_actor_type          IF NOT EXISTS FOR (n:Actor)                 ON (n.actor_type);
CREATE INDEX idx_attestation_result  IF NOT EXISTS FOR (n:Attestation)           ON (n.result);
CREATE INDEX idx_policyrule_domain   IF NOT EXISTS FOR (n:PolicyRule)            ON (n.domain);
CREATE INDEX idx_policyrule_status   IF NOT EXISTS FOR (n:PolicyRule)            ON (n.status);
CREATE INDEX idx_control_framework   IF NOT EXISTS FOR (n:ComplianceControl)     ON (n.framework);
CREATE INDEX idx_planedef_status     IF NOT EXISTS FOR (n:PlaneDefinition)       ON (n.status);
CREATE INDEX idx_progress_conclusion IF NOT EXISTS FOR (n:ReasoningProgress)     ON (n.conclusion_type);
CREATE INDEX idx_progress_reasoner   IF NOT EXISTS FOR (n:ReasoningProgress)     ON (n.reasoner_category);
CREATE INDEX idx_progress_authorit   IF NOT EXISTS FOR (n:ReasoningProgress)     ON (n.authoritative);
CREATE INDEX idx_candidate_kind      IF NOT EXISTS FOR (n:CandidatePromotion)    ON (n.proposal_kind);
CREATE INDEX idx_candidate_promotype IF NOT EXISTS FOR (n:CandidatePromotion)    ON (n.promotion_type);
CREATE INDEX idx_candidate_status    IF NOT EXISTS FOR (n:CandidatePromotion)    ON (n.status);
CREATE INDEX idx_solution_lifecycle  IF NOT EXISTS FOR (n:Artifact)              ON (n.lifecycle_state);
CREATE INDEX idx_ratecard_status     IF NOT EXISTS FOR (n:RateCard)              ON (n.status);
CREATE INDEX idx_costfactor_scope    IF NOT EXISTS FOR (n:CostFactor)            ON (n.factor_scope);
CREATE INDEX idx_costfactor_type     IF NOT EXISTS FOR (n:CostFactor)            ON (n.factor_type);
CREATE INDEX idx_rejectedalt_type    IF NOT EXISTS FOR (n:RejectedAlternative)   ON (n.candidate_type);


// ----------------------------------------------------------------------------
// SECTION 6 — VERIFICATION  (the "and verified" half of the acceptance leg)
//   Run after the statements above; confirm the applied set matches §7.
// ----------------------------------------------------------------------------
//   SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties;
//   SHOW INDEXES     YIELD name, labelsOrTypes, properties, state;
//
//   Expected (this file): 27 PK-uniqueness + 9 (business_key,version)-uniqueness
//     + 24 provenance-existence (12 label-scopes × {origin_mechanism, recorded_at})
//     + (27 PK + 18 bk/ver + 1 Solution.version)=46 T1-existence
//     = 106 constraints; 27 indexes.
//   A NODE-property-existence constraint FAILS TO CREATE on Community — its
//   presence is the live proof the instance is Enterprise (ADR-002 §2.2 warrant).
// ============================================================================
