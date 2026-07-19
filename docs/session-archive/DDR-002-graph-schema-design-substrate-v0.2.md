# DDR-002 Graph Schema — Ratified Design Substrate (v0.2)

**Status:** Ratified design substrate (pre-authoring). Not the DDR itself.
**Carrier:** RBT-13 (DDR-002 Graph Schema) — the R8 schema half.
**Authoring route:** Claude Code authors `docs/ddr/DDR-002-graph-schema.md` from this substrate via the `author-decision-record` skill (DIRECTIVE-026); claude.ai designs/authors, Code executes git.
**Source:** claude.ai RBT-13 pre-authoring design session, 2026-06-19 — ratified section by section, one ratification per turn.
**Authoring postures:** single-artifact per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED, single original-authoring Change Log row); reference flows architecture → schema only (R8), DDR-001 not re-opened. Author DDR-002 with the current identity string *Executive Architect, Haffey Enterprises LLC* (per RBT-36).

**Revision (v0.2, 2026-06-19):** Pass-1 three-hat findings folded — M-1 (five-core-+-Extension framing), M-2 (§9→§8 cross-refs), M-3 (ADR-002 §2.6 disambiguation), M-4 (§5 owns/cites delimiter), M-5 (provenance-scope reconciliation + RG-provenance posture), M-6 (R9 added to §0), C-1/C-2 (citation precision). One design call — M-5's RG-provenance posture — is folded as recommended and **flagged for confirmation** (see §4).

---

## 0. Frame

DDR-002 fixes the **node / relationship / constraint / index contract** for the SOFIA graph system-of-record. It owns the schema; it does **not** own architecture (DDR-001), feedback-loop governance (DDR-003), or service realization (the SDDs). Where a concern is named here but owned elsewhere, it is routed in §8.

Two graphs in one Neo4j Enterprise instance (R3, R5): the **Knowledge Graph** (enterprise ground truth — **five core planes plus the Extension plane**) and the **Reasoning Graph** (captured reasoning), with first-class cross-graph traversal. Cost is realized as the *first Extension registration*, not a sixth core plane (R23).

Governing rulings: **R3** (Neo4j Enterprise edition), **R5** (five logical planes + Extension), **R6** (no vector store), **R8** (architecture/schema split), **R9** (three-store), **R10** (no-PHI-by-design enforced constraint), **R18** (single-artifact authoring), **R20** (Enterprise self-managed on GKE), **R22** (feedback architecture/governance split), **R23** (cost via Extension), **R24** (durable knowledge, not transient telemetry), **R25** (completeness posture).

---

## 1. Schema grammar & global conventions

**Naming.** Node labels `PascalCase`; relationship types `SCREAMING_SNAKE`; properties `snake_case`; primary keys `<entity>_id`.

**Provenance.** Every **KG** node carries a provenance group — minimally `source_class` + `ingested_at` (and source-record ref where applicable); DB-existence-constrained (§7). RG nodes carry provenance differently: the authored `ReasoningSession`/`ReasoningProgress` carry the group; the derived `Evidence`/`RejectedAlternative` inherit it *structurally* rather than carrying a redundant group (see §4 — M-5 posture).

**No vectors (R6).** No node or edge carries vector/embedding properties. Documented invariant + conformance check.

**Classification / no-PHI (R10).** Data classification is gateway-enforced at ingestion; SOFIA stores no PHI *data*. Note the distinction: PHI/PCI *policies* are legitimate Standards knowledge (rules about architectures that handle such data); R10 strips the data, not the rules.

**Plane membership — hybrid.** Every KG node carries a **secondary plane label** (enables cheap label-scoped traversal) **and** the plane is declared in a `PlaneDefinition` registry node (§2.6). Core planes are fixed by DDR-001; the registry is the Extension surface.

**Completeness posture (R25) — the tiering that governs every node/edge.** Scope by *reversibility*, not a uniform dial:
- **T1** — identity / structural keys, constraints, edge-binding properties. *Expensive to reverse → complete now.*
- **T2** — invariant- or traversal-bearing properties (filters, discriminators, version pins, status). *Drives behavior → complete now, indexed where it drives traversal.*
- **T3** — descriptive payload. *Cheap to add (schema-on-write) → minimal now, gaps named not padded.*
- **T4** — rich application payload. *SDD-level, not schema.*

Cross-plane concerns stay in their owning plane, reached by traversal — never duplicated onto a node.

---

## 2. The planes — node schemas (five core planes §2.1–§2.5 + the Extension plane §2.6)

Property tier in parentheses. `provenance (T1)` denotes the provenance group. §2.1–§2.5 are the five core planes fixed by DDR-001; §2.6 is the Extension surface, where cost registers first per R23.

### 2.1 Catalog — the selection graph (versioned ground truth)

- **`(:Catalog:Pattern)`** — `pattern_id` (T1 PK) · `version` (T1) · `pattern_type` (T2, indexed) · `status` (T2, indexed, versioned) · `effective_from`/`superseded_by` (T2) · `name` (T3) · provenance (T1)
- **`(:Catalog:Capability)`** — `capability_id` (T1 PK) · `version` (T1) · `name` (T3) · `l1_taxonomy`/`l2_taxonomy`/`l3_taxonomy` (T2) · `status` (T2) · `description` (T3) · provenance (T1)
- **`(:Catalog:Technology)`** — `technology_id` (T1 PK) · `version` (T1) · `name` (T3) · `vendor` (T3) · `platform` (T3) · `approval_status` (T2, indexed) · `version_constraint`/`min`/`max` (T2) · `deprecation_date` (T2) · `tier_applicability[]` (T2) · `approved_data_classifications[]` (T2) · provenance (T1)
- **`(:Catalog:IacTemplate)`** — `iac_template_id` (T1 PK) · `template_type` (T2) · `name` (T3) · `version` (T1) · `status` (T2) · provenance (T1)

*Redistributed out (POC conflation resolved):* `cost_tier` → cost plane; `required_capabilities`/`options`/`preferred_over`/`replacement` → edges; `policy_rules`/`gate_requirements` → Standards/Governance; embedding block → retired (R6). Org/vendor specifics genericized (name-by-class, R2). The ASD/solution is **not** a Catalog node (it is the `(:Artifact:Solution)` keystone, §5).

### 2.2 Environment — the as-running graph (POC-absent; ages via freshness)

- **`(:Environment:DeployedService)`** — `deployed_service_id` (T1 PK) · `service_type` (T3) · `lifecycle_state` (T2, indexed) · `observed_at` (T2) · provenance (T1, `source_class` = runtime/CMDB class)
- **`(:Environment:DeploymentEnvironment)`** — `environment_id` (T1 PK) · `name` (T3) · `environment_class` (T2, indexed — production/staging/dev) · provenance (T1)
- **`(:Environment:ConfigurationItem)`** — `ci_id` (T1 PK) · `ci_type` (T2, indexed) · `name` (T3) · `observed_at` (T2) · provenance (T1)

*Plane signature:* freshness (`observed_at`) — runtime facts are less authoritative than catalog ground truth; this lets the RG weight environment evidence lower. *Lifecycle distinction:* `DeploymentEnvironment` is the **realized** runtime environment, distinct from a solution's design-time `target_environment` (§5).

### 2.3 Operational — the track-record graph (POC-absent; durable distillation, not telemetry)

- **`(:Operational:ObservedPattern)`** — `observed_pattern_id` (T1 PK) · `polarity` (T2, indexed — `strength` / `weakness` / optional `neutral`) · `pattern_type` (T2, indexed) · `description` (T3) · `observation_window` (T3) · `confidence` (T2) · `first_observed_at`/`last_observed_at` (T2) · `status` (T2, indexed — active/superseded/resolved) · provenance (T1)

*Per R24:* the KG does **not** mirror transient SoR telemetry (ServiceNow/Datadog). It holds the durable distilled lesson — a recurring operational pattern, of **dual polarity** (a clean track record is as informative as a weakness). No TTL. Detection (reading the SoR, distilling patterns) → detection SDD; weakness/strength entry into the KG is EA-gated via the feedback loop (§5), not auto-ingested.

### 2.4 Governance — the decision/audit graph (immutable append-only; references, not records)

- **`(:Governance:GateDecision)`** — `gate_decision_id` (T1 PK) · `gate` (T2, indexed — gate_0/1/2 discriminator) · `decision` (T2, indexed — approved/approved_conditional/rejected) · `origin` (T2 — `external_captured` / `self_issued`) · `source_class` (T2 — per-gate SoR, e.g. EAMS for design, ITSM for change/release) · `external_record_ref` (T3 — pointer to the authoritative external record) · `all_hard_constraints_passed` (T2) · `decision_date`/`created_at` (T2) · `approval_token_id` (T3) · `rejection_reason` (T3, conditional) · provenance (T1, carries `workflow_id`)
- **`(:Governance:Actor)`** — `actor_id` (T1 PK) · `actor_type` (T2, indexed — `human` / `system`) · `name` (T3) · provenance (T1)
- **`(:Governance:Role)`** — `role_id` (T1 PK) · `name` (T3) · provenance (T1)
- **`(:Governance:Attestation)`** — `attestation_id` (T1 PK) · `result` (T2, indexed — pass/fail) · `attested_at` (T2) · provenance (T1) *(closes obligation↔satisfaction, §3)*

*Key postures:* the external entity is **always** the system of record for governance decisions; `GateDecision` is a **captured/issued reference**, not SOFIA's authoritative record (the `origin` + `external_record_ref` carry inbound-capture vs. self-issue-then-transmit, covering the near-term inbound flow and the future SOFIA-as-approver / third-party-agent-approver cases). `Actor` generalizes the POC's "User" so any decider — human, SOFIA, or another external system — has a structural home. The per-action **disposition-event stream is excluded** (transient → orchestration/observability SoR, per R24). `User`/`Role` are governance-participating identities, **not** an IAM mirror. Immutable append-only: a re-decision is a new node.

### 2.5 Standards — the governance-of-knowledge graph (versioned + change-impact)

- **`(:Standards:Standard)`** — `standard_id` (T1 PK) · `version` (T1) · `name` (T3) · `authority` (T3) · `status` (T2) · provenance (T1) *(the referenceable authority — "per policy 1234")*
- **`(:Standards:PolicyRule)`** — `policy_rule_id` (T1 PK) · `version` (T1) · `rule_name` (T3) · `domain` (T2, indexed) · `status` (T2, indexed, versioned) · `superseded_by` (T2) · `enforcement_level` (T2 — hard/soft) · `enforced_at_gate` (T2) · `statement` (T3 — natural-language requirement) · `rule_definition` (T3 — opaque declarative IF/THEN, the validator consumes it; the graph never traverses into it) · provenance (T1)
- **`(:Standards:ComplianceControl)`** — `control_id` (T1 PK) · `framework` (T2, indexed — HIPAA/SOC2/PCI as *data*) · `control_ref` (T3) · `control_name` (T3) · provenance (T1)

*Decision (option C):* the executable rule logic rides the `PolicyRule` node as opaque `rule_definition` (KG-as-policy-SoR, matching DDR-001's served-from-graph model); the constraint-validator evaluates it. A standard is broader than rules — it can `DEFINE` a `PolicyRule`, `PRESCRIBE` a `Technology`/`Pattern`/`Process`, etc. (`Process` node deferred, §8). Mandates resolve in two ways: **structurally** (validator reads the solution graph — prohibitions, "uses the vault") or **by attestation** (process performed / evidence produced — `Attestation`, §2.4).

### 2.6 Extension mechanism + cost plane (the R23 exemplar — first Extension registration)

**Mechanism:**
- **`(:Extension:PlaneDefinition)`** — `plane_id` (T1 PK) · `plane_name` (T3) · `version` (T1) · `status` (T2, indexed) · `attaches_to` (T2 — list of core labels the plane may enrich) · `property_schema` (T3 — opaque schema-on-write definition for the plane's node types) · provenance (T1)

The registry is self-describing (query `PlaneDefinition` nodes to enumerate registered planes). `attaches_to` and `property_schema` are **declarations** (properties), not edges-to-labels — a simplification of the POC's edge-modeled `DEFINES`/`ATTACHES_TO`. Schema-on-write validates extension nodes against their `PlaneDefinition`; instance-edges are bounded to the `attaches_to` labels. Extension nodes carry the plane's secondary label (the hybrid, §1).

**Cost plane — first registration:** `PlaneDefinition{plane_id: "cost", attaches_to: [Capability, Technology]}`.
- **`(:Cost:RateCard)`** — `rate_card_id` (T1 PK) · `version` (T1) · `effective_from`/`effective_to` (T2) · `status` (T2, indexed) · `rates` (T3, unit→cost payload) · provenance (T1). *Never-deleted; superseded only.*
- **`(:Cost:CostFactor)`** — `cost_factor_id` (T1 PK) · `factor_scope` (T2, indexed — technology/capability) · `factor_type` (T2, indexed) · `amount`/`unit` (T3) · `version` (T1) · `status` (T2) · provenance (T1). *Reference input.*
- **`(:Cost:CapabilityCostEstimate)`** — `estimate_id` (T1 PK) · `aggregate_cost` (T2 — **derived, never hand-set**) · `capability_version_ref` (T2 — staleness pin) · `confidence` (T2) · `computed_at` (T2) · provenance (T1). *Derived output, refreshable.*

*Collapses from DDR-040's six types:* `CostPlaneDefinition` → the generic `PlaneDefinition`; `CapabilityCostFactor` + `TechnologyCostFactor` → one `CostFactor` (`factor_scope`); derived line-items → `HAS_COST_FACTOR` edges (not duplicated nodes); `CostFactorDefinition` → the `factor_type` enum. Cost is the first temporally-mixed plane: `RateCard`/`CostFactor` versioned reference, `CapabilityCostEstimate` refreshable derivation. Tier-1/2 traversal + the `Tier1CostEstimateResult` DTO → RBT-25.

---

## 3. KG relationships — edge grammar + catalog

**Edge grammar:**
- **Direction & naming** — `SCREAMING_SNAKE` verb phrases in the natural semantic direction; Neo4j traverses both ways, so direction is for readability, not access. One edge per relationship — no redundant inverses.
- **Edge properties** — attributes belonging to the *relationship*, not either node.
- **Edge provenance** — asserted-fact edges (ingested, e.g. `APPROVED_OPTION_FOR`) carry `source_class`; structural edges do not.
- **Cardinality** — not constrainable in Neo4j schema → documented invariant + conformance check.
- **Temporal edges** — relationships whose *validity* is time-bound carry `effective_from`/`effective_to` + `status`; structural edges do not.
- **Confidence** — KG-internal edges are authoritative by default (no confidence); environment/operational-derived edges *may* carry `confidence`; reasoning-time confidence lives on the RG `Evidence` edge (§5), not on KG edges.

**Edge catalog (six sub-graphs):**

*Selection (Catalog):* `(Pattern)-[:REQUIRES_CAPABILITY {required, tier_conditional, tier_threshold}]->(Capability)` · `(Technology)-[:APPROVED_OPTION_FOR {conditional, justification}]->(Capability)` *(temporal)* · `(Pattern)-[:PREFERRED_OVER]->(Pattern)` · `(Technology)-[:REPLACED_BY]->(Technology)` *(temporal)* · `(IacTemplate)-[:IMPLEMENTS]->(Pattern)`

*As-running (Environment, confidence-bearing):* `(DeployedService)-[:RUNS {confidence}]->(Technology)` · `(DeployedService)-[:DEPLOYED_IN {confidence}]->(DeploymentEnvironment)` · `(DeployedService)-[:REALIZES {confidence}]->(Capability)` · `(ConfigurationItem)-[:PART_OF {confidence}]->(DeployedService)`

*Track-record (Operational):* `(ObservedPattern)-[:OBSERVED_IN {confidence}]->(Technology | Pattern | Capability | DeploymentEnvironment)`

*Governance-of-knowledge (Standards):* `(Standard)-[:DEFINES]->(PolicyRule)` · `(Standard)-[:PRESCRIBES]->(Technology | Pattern | Process)` · `(PolicyRule)-[:MAPS_TO]->(ComplianceControl)` · `(PolicyRule)-[:MANDATES]->(Technology)` · `(Pattern | Technology | Capability)-[:GOVERNED_BY]->(PolicyRule)` *(static associations only — solution-time governance is computed by matching the rule condition against the solution, not a stored edge)*

*Decision/audit (Governance):* `(Actor)-[:HAS_ROLE]->(Role)` *(temporal)* · `(Actor)-[:APPROVED {role, approved_at}]->(GateDecision)` · `(GateDecision)-[:REVIEWED {hash}]->(Artifact)` · `(Attestation)-[:SATISFIES]->(PolicyRule)` · `(Attestation)-[:BY]->(Actor)` · `(Attestation)-[:EVIDENCED_BY]->(Artifact)` · `(Attestation)-[:FOR_PROCESS]->(Process)`

*Cost (Extension):* `(CapabilityCostEstimate)-[:FOR_CAPABILITY]->(Capability)` *(cardinality 1)* · `(CapabilityCostEstimate)-[:HAS_COST_FACTOR]->(CostFactor)` · `(CostFactor)-[:FOR_TECHNOLOGY]->(Technology)` · `(CapabilityCostEstimate)-[:PRICED_BY]->(RateCard)`

*Solution-centric edges are deferred to the keystone (§5).*

**Obligation↔satisfaction model.** Standards hold the *obligation*; Governance holds the *attestation*; the solution sits in the middle. Validation traverses from a solution to its obligations and checks each has a matching satisfaction. Two closing mechanisms: validator-structural (prohibitions, structural requirements) and attestation-evidenced (process performed / evidence produced). A missing satisfaction surfaces as a compliance gap (an RG risk inference), not silence.

---

## 4. The Reasoning Graph — node schemas

**Label reconciliation** (align to ADR-002 §2.6 / ADR-001 §2.2 vocabulary, retiring POC names): `Inference` → `ReasoningProgress`; `Hypothesis` → `RejectedAlternative`; `Evidence` and `ReasoningSession` kept. Per **ADR-002 §2.6**, the rich `ReasoningProgress` *fields* are SDD-level; DDR-002 owns only the schema contract.

- **`(:Reasoning:ReasoningSession)`** — `session_id` (T1 PK) · `solution_ref` (T1, 1:1 with the produced solution) · `lifecycle_state` (T2 — AOE-owned) · `created_at` (T2) · provenance (T1)
- **`(:Reasoning:ReasoningProgress)`** — `progress_id` (T1 PK) · `conclusion_type` (T2, indexed — PatternMatch / TechnologySelection / GapConclusion / OverrideFlag / RiskSignal / ComplianceEvaluation) · `confidence` (T2) · `overridden_by_human` (T2) · `created_at` (T2) · provenance (T1). *= the typed conclusion (lean reading: no separate container). Rich conclusion/rationale → SDD.*
- **`(:Reasoning:Evidence)`** — `evidence_id` (T1 PK) · `fact_summary` (T2 — denormalized snapshot) · `confidence` (T2, inherited) · `weight` (T2) · `source_node_version` (T2 — version pin) · `observed_at` (T2)
- **`(:Reasoning:RejectedAlternative)`** — `rejected_id` (T1 PK) · `candidate_type` (T2, indexed) · `rejection_reason` (T3) · `score_delta` (T2) · `human_accepted` (T2) · `human_accepted_at` (T2)

*Write authority (**ADR-002 §2.6** invariant):* ASA authors `ReasoningProgress`; AOE owns `ReasoningSession` lifecycle only; writes route via knowledge-service. Mechanization → RBT-33.
*RG-internal edges:* `(ReasoningSession)-[:CONTAINS]->(ReasoningProgress)` · `(ReasoningProgress)-[:SUPPORTED_BY]->(Evidence)` · `(ReasoningProgress)-[:REJECTED]->(RejectedAlternative)` · `(ReasoningProgress)-[:LED_TO]->(ReasoningProgress)`.
*Point-in-time fidelity:* `fact_summary` + `source_node_version` make the audit trail immune to later KG drift.

**RG provenance posture (M-5 resolution — flagged for confirmation).** Provenance is present across the RG, but expressed by node kind:
- `ReasoningSession` and `ReasoningProgress` are *authored reasoning state* → they carry the provenance group (provenance = the authoring session/agent, ASA per §2.6).
- `Evidence` and `RejectedAlternative` are *derived* and deliberately omit the group; their provenance is **structural**: `Evidence` pins `source_node_version` + `observed_at` and links `SOURCED_FROM` the authoritative KG node it snapshots (§5); `RejectedAlternative` is reached only via its parent `ReasoningProgress` (`REJECTED`) and `WOULD_HAVE_USED` the KG node it points at, inheriting the parent's provenance.

So the provenance *existence constraint* (§7) scopes to **KG nodes + the two authored RG types**; the two derived RG types are covered by the structural surrogate, not a group. *(This is the one Pass-1 finding whose resolution is a design call — confirm before authoring.)*

---

## 5. Cross-graph linkage + the feedback loop

**Ownership line (R8 / R22) — what DDR-002 owns vs. cites in this section.** DDR-002 **owns** the *schema contract*: the `(:Artifact:Solution)` and `CandidatePromotion` node shapes, the cross-graph and promotion edge grammar, and the *structural* invariants (exclusion-by-label, append-only terminal status, provenance-chain traceability). DDR-002 **cites, and does not re-author:** the promotion *mechanics / data-path* → DDR-001; the *diagnosis policy / EA approval criteria / thresholds / cadence* → DDR-003 (RBT-14); the *workflow* → SDD. The Refine/Request-new/Correct-scope framing and the "EA-gate is a diagnosis" characterization below are stated for schema motivation only — their governance is DDR-003's, their data-path is DDR-001's.

**Evidence edges (RG → KG):** `(Evidence)-[:SOURCED_FROM]->(KG node)` *(confidence inherits here — authoritative Catalog scores above aging Environment)* · `(RejectedAlternative)-[:WOULD_HAVE_USED]->(KG node)`. *(`DREW_FROM`/`TRAVERSED` deferred — the considered-set is reconstructable from Evidence + RejectedAlternative.)*

**The Solution keystone:**
- **`(:Artifact:Solution)`** — `artifact_id` (T1 PK) · `artifact_type` (T2 — `solution`) · `version` (T1) · `lifecycle_state` (T2, indexed — FSM: proposed→architected→gated→approved→operational) · `content_hash` (T2 — tamper-detection) · `snapshot_ref` (T2 — dual-home pointer) · `target_environment` (T2 — design-time intent) · `created_at` (T2) · provenance (T1). `(:Artifact)` is the general produced-deliverable family (solutions, BCDR plans, build sheets).

*Bridge edges:* `(ReasoningSession)-[:PRODUCED]->(Solution)` *(1:1)* · `(Solution)-[:USES]->(Technology)` · `(Solution)-[:FOLLOWS]->(Pattern)` · `(GateDecision)-[:DECIDED_ON]->(Solution)` · `(Solution)-[:HAS_ARTIFACT]->(Artifact)`. `target_environment` is a property (design intent), not an edge; the realized environment arrives later via `DeployedService`. Dual-home mechanics → §6.

**CandidatePromotion + feedback loop (R22)** — *schema contract owned here; mechanics cited to DDR-001 per the ownership line above:*
- **`(:Reasoning:CandidatePromotion)`** — `candidate_id` (T1 PK) · `promotion_type` (T2, indexed) · `proposed_change` (T3 — opaque) · `requested_item` (T3) + `requested_item_kind` (T2 — technology/pattern/capability/integration) + `target_ref` (T3) *(for request-new gaps)* · `basis_strength` (T2) · `confidence` (T2) · `status` (T2, indexed — proposed / under_review / approved / rejected / promoted) · `created_at` (T2) · provenance (T1). **Append-only**; terminal `status` (`promoted` / `rejected {reason}`) is the durable evaluation outcome — declines are explainable and gaps don't re-surface.

*Promotion edges:* `(CandidatePromotion)-[:PROPOSED_FROM]->(ReasoningProgress | Evidence | ObservedPattern)` · `(GateDecision)-[:DECIDED_ON]->(CandidatePromotion)` *(EA-gate reuses `GateDecision{gate: ea_promotion}`)* · `(CandidatePromotion)-[:PROMOTES_TO_KNOWLEDGE]->(KG node)`.

*Structural invariants (DDR-002-owned):* **exclusion-by-label** — `CandidatePromotion` carries no KG plane label, so ground-truth traversals (plane-scoped) skip it structurally; a proposal cannot masquerade as fact. **Provenance chain** — a promoted node traces back through `PROMOTES_TO_KNOWLEDGE` → `CandidatePromotion` → `PROPOSED_FROM` → `ReasoningProgress`/`Evidence` → `SOURCED_FROM` → original facts.

**Generalized correction mechanism** *(schema motivation; governance → DDR-003).* Every `conclusion_type` is a human-correction surface (technology, pattern, capability, integration, risk, compliance, cost), in three flavors: **Refine** (override to an existing option → context-scoped, evidence-backed preference signal on the selection edge, no pairwise cycles), **Request-new** (gap → human evaluation/onboarding; never auto-created), **Correct-scope** (false risk / mis-scoped rule → adjust existing ground truth). The capture machinery (`overridden_by_human`, `human_accepted`, `GapConclusion`, `RejectedAlternative`, `CandidatePromotion`, EA-gate, `PROMOTES_TO_KNOWLEDGE`) is general across surfaces. The "override is a signal the EA *diagnoses*" framing is governance characterization owned by DDR-003, not authored here.

---

## 6. Versioning & temporal model

**Per-posture spectrum** (each plane fit to its nature): Catalog/Standards/RateCard **version** (supersession), Environment **ages** (`observed_at`), Operational **distills** (status-managed), Governance **accretes** (immutable append-only), RG **pins** (point-in-time), Solutions **dual-home**.

**Supersession — Option A (scoped to versioned-ground-truth types: Catalog, Standards, RateCard, CostFactor, PlaneDefinition).** A node carries `version` + `effective_from`/`effective_to` + `status` + `superseded_by`; superseding creates a new retained node and marks the old superseded. Structural edges track *current* (gateway re-points on supersession); audit/evidence edges pin to a *specific* version node. Never-delete via retained versions; as-of via effective-dating. Chosen over an identity+version-node pattern to keep the selection-graph hot path hop-free (versioning is rare; traversal is constant).

**Version-pinning.** `Evidence.source_node_version` + `CapabilityCostEstimate.capability_version_ref` reference specific retained version nodes; with `Evidence.fact_summary` that yields point-in-time fidelity.

**Dual-home (Artifact/Solution).** The graph node holds metadata, edges, `content_hash`, `snapshot_ref`; immutable content lives in the external snapshot store (Firestore per R9, routed to DDR-001); the hash is tamper-detection (snapshot hash must match `content_hash`). A new version is a new node + new snapshot; the old pair is retained.

**Uniqueness under versioning.** PKs unique on `(business_key, version)`; "exactly one active version per business_key" is a documented invariant + conformance check.

---

## 7. Constraints, indexes & conformance

**DB-enforced (Neo4j Enterprise) — generating rules:**
- **Uniqueness** on every PK; `(business_key, version)` for the versioned-ground-truth types.
- **Existence constraints** on the provenance group (`source_class`, `ingested_at`) on every **KG** node and the two authored RG types (`ReasoningSession`, `ReasoningProgress`) — see §4 for the RG-provenance posture — plus each node's T1 required props. (The Enterprise *edition* committed in ADR-002 — edition per **R3** — buys existence-constraint capability.)
- **Indexes** on the flagged T2 traversal/filter properties only (lean — no speculative indexing); plane secondary-labels are inherently indexed.

**Conformance-checked invariant set (Neo4j cannot express → documented + CI; mechanization → RBT-33):** no vector properties (R6); relationship cardinality; one active version per business_key; aggregate-derivation (`CapabilityCostEstimate.aggregate_cost` never hand-set); schema-on-write (extension nodes vs. `PlaneDefinition`; edges bounded to `attaches_to`); **ADR-002 §2.6** write-authority; never-delete (versioned types supersede); exclusion-by-label (`CandidatePromotion`); tamper-detection (`Artifact.content_hash`); no-PHI (classification, gateway-enforced).

---

## 8. Boundary routing & doc frame

**Boundary Routing Map** (named here, owned elsewhere):
- **→ DDR-001** (one-way, R8): plane-model architecture, Extension *architecture*, gateway pattern, three-store persistence (R9), feedback-loop *architecture* (data-path / promotion mechanics). Cited, never re-opened.
- **→ DDR-003 (RBT-14):** feedback-loop *governance* — EA authority, diagnosis policy, what-gets-promoted criteria, thresholds, cadence, retention/audit policy.
- **→ RBT-25 (cost-estimation SDD):** Tier-1/2 traversal, cost DTOs.
- **→ RBT-15 (knowledge-service SDD):** gateway write endpoints; enforcement of the invariants (derivation, never-delete, schema-on-write, classification, supersession edge re-pointing).
- **→ constraint-validator SDD:** `rule_definition` evaluation.
- **→ detection/promotion SDD:** `ObservedPattern` detection, `CandidatePromotion` aggregation, the generalized correction mechanism.
- **→ reasoning/ASA SDD:** full `ReasoningProgress` fields (**ADR-002 §2.6**).
- **→ RBT-33:** mechanization of the conformance invariant set.

**DDR-002-native conformance checks** (design-time enforced, mechanization at RBT-33): every KG node carries a plane label + provenance; no vector properties; `CandidatePromotion` carries no KG plane label; extension nodes validate against a `PlaneDefinition`; exactly one active version per business_key; RG write-authority honored (ADR-002 §2.6).

**Conscious exclusions / deferred scope** (boundary chosen, not missed):
- Attestation time-decay / re-attestation cadence
- Waiver / risk-acceptance closure of mandates
- Aggregate / portfolio-level mandates
- Inherited / platform-level compliance
- Full bitemporal *relationship*-history (node as-of + evidence pinning are preserved)
- The `Process` node type (Standards will want it)
- `DREW_FROM` / `TRAVERSED` reasoning-trail edges

**Forward dependencies:** RBT-12/DDR-001 (landed, upstream — Done @ `15ff20f`, PR #12), RBT-14/DDR-003 (governance), RBT-15 + RBT-25 (SDDs this gates), RBT-33 (conformance mechanization). *New items to file post-merge (with DIRECTIVE-025 dedup at filing):* a `Process` node-type ticket; the detection/correction SDD; the selection-edge preference-landing.

**Doc frame:** references DDR-001, ADR-001, ADR-002, and rulings R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25; single original-authoring Change Log row per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED); identity string *Executive Architect, Haffey Enterprises LLC*; lands at `docs/ddr/DDR-002-graph-schema.md`.

---

## Appendix — ratification trace

Ratified section by section in the RBT-13 claude.ai design session (2026-06-19), one ratification per turn: schema grammar & hybrid plane membership → Catalog → Environment (`DeploymentEnvironment` naming) → Operational (re-centered to dual-nature `ObservedPattern`, R24) → Governance (`GateDecision` as reference, `Actor` generalization) → Standards (`Standard` un-deferred, option-C `rule_definition`, obligation↔satisfaction / `Attestation`) → Extension mechanism → cost plane (R23) → edge grammar + catalog → RG nodes (label reconciliation) → cross-graph + Solution keystone → CandidatePromotion + feedback loop + generalized correction mechanism → versioning (Option A) → constraints/indexes/invariants → boundary routing + conscious exclusions. Ledger rulings written: R23 (prior), R24, R25.

**v0.2 fold (Pass-1 three-hat, 2026-06-19):** M-1 five-core-+-Extension framing (§0, §2); M-2 §9→§8 (§0, §2.5); M-3 ADR-002 §2.6 disambiguation (§4, §7, §8); M-4 §5 owns/cites delimiter; M-5 provenance-scope reconciliation + RG-provenance posture (§1, §4, §7) — *flagged for confirmation*; M-6 R9 added to §0; C-1 R10 no-PHI label; C-2 existence-constraint edition cited to R3. Forward-pointers held for ratification: FP-1 (RBT-13 ticket Ledger-line edit), FP-3 (post-merge filings).
