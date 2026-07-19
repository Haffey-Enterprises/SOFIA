# DDR-002 Graph Schema — Ratified Design Substrate (v0.3)

**Status:** Ratified design substrate (pre-authoring). Not the DDR itself.
**Carrier:** RBT-13 (DDR-002 Graph Schema) — the R8 schema half.
**Authoring route:** Claude Code authors `docs/ddr/DDR-002-graph-schema.md` from this substrate via the `author-decision-record` skill (DIRECTIVE-026); claude.ai designs/authors, Code executes git.
**Source:** claude.ai RBT-13 pre-authoring design session, 2026-06-19 / 2026-06-20 — ratified section by section, one ratification per turn.
**Authoring postures:** single-artifact per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED, single original-authoring Change Log row); reference flows architecture → schema only (R8), DDR-001 not re-opened. Author DDR-002 with the current identity string *Executive Architect, Haffey Enterprises LLC* (per RBT-36/RBT-37).

> **Substrate version vs. DDR version (R18 / M-17).** "v0.3" is the *substrate session-process* version — the design-cycle revision of this pre-authoring artifact. It is **not** the DDR version. The authored DDR-002 carries the single-artifact lifecycle `0.1.0` PROPOSED → `1.0.0` ACCEPTED with **one** original-authoring Change Log row. The v0.x history and the fold-log below live in the substrate **only** and never appear in the DDR.

**Revision (v0.2, 2026-06-19):** Pass-1 three-hat findings folded — M-1 (five-core-+-Extension framing), M-2 (§9→§8 cross-refs), M-3 (ADR-002 §2.6 disambiguation), M-4 (§5 owns/cites delimiter), M-5 (provenance-scope reconciliation + RG-provenance posture), M-6 (R9 added to §0), C-1/C-2 (citation precision).

**Revision (v0.3, 2026-06-20):** Pass-2 three-hat (PASS, converging) + antagonistic Pass-1 + DDR-001 cross-check addendum dispositioned and folded. **Blockers:** B-4 (Operational↔DDR-001 contradiction → Model A, *serialize* behind DDR-001 v1.1.0 / RBT-39 / ledger R26); B-1 (RG-provenance enforceability → structural surrogate stands, exposure named, mechanized at RBT-33 / ledger R27); B-3 (Process dangling edges → pulled, deferred to RBT-40). **Structural forks (substrate-folds):** M-7 (Artifact = distinct third family), M-9 (exclusion-by-label dissolved → DDR-001 proposal-visibility invariant, gateway-enforced read-discipline), M-3 (Decision supertype + GateDecision/PromotionDecision subtypes; resolves C-1; gate-enum reconcile → RBT-41), M-10 (R6 positive half → name existing retrieval substrate, affordance → SDD). **Fold batch:** M-1, M-4, M-5ᴬ, M-6, M-8, M-12, M-15, M-16, M-17, C-2…C-6, C2-1, M2-1. Full disposition table in the fold-log appendix. The v0.2 M-5 RG-provenance posture, *flagged for confirmation*, is **confirmed** under B-1 (c). Ledger this cycle: **R26, R27**. Linear this cycle: **RBT-39** (DDR-001 amendment, blocks RBT-13), **RBT-40** (Process node + deferred edges), **RBT-41** (gate-enum reconcile), **RBT-33** broadened (DDR-002 CI-only set; raised to High; sequenced ahead of RBT-15).

---

## 0. Frame

DDR-002 fixes the **node / relationship / constraint / index contract** for the SOFIA graph system-of-record. It owns the schema; it does **not** own architecture (DDR-001), feedback-loop governance (DDR-003), or service realization (the SDDs). Where a concern is named here but owned elsewhere, it is routed in §8.

Two graphs in one Neo4j Enterprise instance (R3, R5): the **Knowledge Graph** (enterprise ground truth — **five core planes plus the Extension plane**) and the **Reasoning Graph** (captured reasoning), with first-class cross-graph traversal. Cost is realized as the *first Extension registration*, not a sixth core plane (R23). Two further citizen-families sit outside the KG-plane model: the **Reasoning Graph** node set (§4) and the **Artifact family** (produced deliverables, §5) — both deliberately exempt from KG-plane labelling (M-7).

**Frame components (testable — map to DDR template §1):**
1. Node/relationship/constraint/index contract for KG + RG + Artifact families.
2. KG = five core planes (DDR-001-fixed) + Extension plane (R23 cost exemplar).
3. RG = captured reasoning, cross-graph-linked, not a KG plane.
4. Artifact family = produced deliverables, not a KG plane and not RG.
5. Schema only — architecture (DDR-001), feedback governance (DDR-003), service realization (SDDs) routed in §8.

**Governing rulings:** **R3** (Neo4j Enterprise edition), **R5** (five logical planes + Extension), **R6** (no vector store), **R8** (architecture/schema split), **R9** (three-store), **R10** (no-PHI-by-design enforced constraint), **R18** (single-artifact authoring), **R20** (Enterprise self-managed on GKE), **R22** (feedback architecture/governance split), **R23** (cost via Extension), **R24** (durable knowledge, not transient telemetry), **R25** (completeness posture), **R26** (DDR-001 Operational plane amended to durable distillation — B-4), **R27** (enforcement posture for CI-only integrity invariants — B-1).

**Upstream dependency (B-4 / R26 / serialize).** DDR-002's Operational plane (§2.3) depends on DDR-001's Operational-plane *definition*. DDR-001 v1.0.0 defined it as raw telemetry; ledger R24/R26 corrected the platform posture to **durable distilled `ObservedPattern`s**. DDR-001 is being amended to v1.1.0 to catch up (RBT-39). Per the B-4 *serialize* decision, **DDR-002 Code-authoring waits until DDR-001 v1.1.0 lands on `develop`** — so the parent and child agree before the schema is authored.

**Layer-of-abstraction & substrate-stability (C-3).** DDR-002 is a *foundational substrate* doc: it gates twelve downstream SDDs (RBT-15…RBT-26) and is cited by DDR-003. Schema churn is expensive downstream, so the completeness posture (R25) is deliberately reversibility-scoped — T1/T2 are locked now; T3/T4 stay schema-on-write and SDD-level. DDR-001 models this same layering (architecture stable, schema/service deferred).

---

## 1. Schema grammar & global conventions

**Naming.** Node labels `PascalCase`; relationship types `SCREAMING_SNAKE`; properties `snake_case`; primary keys `<entity>_id`.

**Provenance (M-1 — origin-neutral group).** Every **KG** node carries a provenance group — minimally `source_class` + `recorded_at` (and a source-record ref where applicable); DB-existence-constrained (§7). `source_class` is an **origin-class enum**: `ingested` (external ground truth), `distilled` (derived from external telemetry/SoR — e.g. `ObservedPattern`), `computed` (derived in-graph — e.g. `CapabilityCostEstimate`), `promoted` (materialized through the feedback-loop EA gate), `authored` (human/SOFIA-authored governance state). `recorded_at` is the origin-neutral timestamp (replacing the ingestion-specific `ingested_at`, which presumed a single origin). The `promoted` vs. `ingested` distinction is a **DDR-001 conformance-check #6 obligation** (promoted knowledge must be distinguishable from ingested) — the origin-class enum is the structural carrier of that obligation. RG and Artifact provenance differ (below; §4; §5).

**Provenance scope (M-7).** The provenance *existence constraint* (§7) scopes to three citizen-families: **KG nodes**, the **two authored RG types** (`ReasoningSession`, `ReasoningProgress`), and the **Artifact family** (§5). The two *derived* RG types (`Evidence`, `RejectedAlternative`) are covered by a structural surrogate, not a carried group (§4, confirmed under B-1).

**No vectors (R6) — both halves.** *Negative half:* no node or edge carries vector/embedding properties (documented invariant + conformance check). *Positive half (M-10):* the graph-native retrieval substrate that *replaces* vector similarity is the existing structure — the `l1/l2/l3` capability/pattern taxonomy (§2.1), the selection-edge web (§3), and the track-record subgraph (§2.3). DDR-002 **names** these as the R6 substitute and restates the no-vector prohibition as binding; the concrete **retrieval affordance** (graph-traversal query patterns; whether a `SIMILAR_TO` edge is warranted and how it would be populated without embeddings) is **routed to the knowledge-service / solutioning SDDs** (RBT-15, RBT-17), not designed here.

**Classification / no-PHI (R10).** Data classification is gateway-enforced at ingestion; SOFIA stores no PHI *data*. Note the distinction: PHI/PCI *policies* are legitimate Standards knowledge (rules about architectures that handle such data); R10 strips the data, not the rules.

**Plane membership — hybrid (KG-scoped, M-7).** Every **KG** node carries a **secondary plane label** (enables cheap label-scoped traversal) **and** the plane is declared in a `PlaneDefinition` registry node (§2.6). Core planes are fixed by DDR-001; the registry is the Extension surface. **RG nodes and Artifact-family nodes carry no KG plane label** — they are not plane citizens; they are reached by cross-graph traversal (§5). This exemption is what lets plane-scoped ground-truth traversals skip reasoning state and produced artifacts structurally.

**Completeness posture (R25) — the tiering that governs every node/edge.** Scope by *reversibility*, not a uniform dial:
- **T1** — identity / structural keys, constraints, edge-binding properties. *Expensive to reverse → complete now.*
- **T2** — invariant- or traversal-bearing properties (filters, discriminators, version pins, status). *Drives behavior → complete now, indexed where it drives traversal.*
- **T3** — descriptive payload. *Cheap to add (schema-on-write) → minimal now, gaps named not padded.*
- **T4** — rich application payload. *SDD-level, not schema.*

**Contested-T2 annotation (M-15).** Where a T2 value-set is **POC-asserted** rather than invariant-grounded, it is flagged inline so a spike-generalization review pass can revisit it. Current contested T2s: `conclusion_type` enum (§4), `GateDecision.gate` enum (§2.4, → RBT-41), `polarity` neutral option (§2.3), `basis_strength` (§5). Invariant-grounded T2s (plane labels, version pins, status discriminators) are not flagged.

Cross-plane concerns stay in their owning plane, reached by traversal — never duplicated onto a node.

---

## 2. The planes — node schemas (five core planes §2.1–§2.5 + the Extension plane §2.6)

Property tier in parentheses. `provenance (T1)` denotes the provenance group. §2.1–§2.5 are the five core planes fixed by DDR-001; §2.6 is the Extension surface, where cost registers first per R23.

### 2.1 Catalog — the selection graph (versioned ground truth)

- **`(:Catalog:Pattern)`** — `pattern_id` (T1 PK) · `version` (T1) · `pattern_type` (T2, indexed) · `status` (T2, indexed, versioned) · `effective_from`/`superseded_by` (T2) · `name` (T3) · provenance (T1)
- **`(:Catalog:Capability)`** — `capability_id` (T1 PK) · `version` (T1) · `name` (T3) · `l1_taxonomy`/`l2_taxonomy`/`l3_taxonomy` (T2) · `status` (T2) · `description` (T3) · provenance (T1)
- **`(:Catalog:Technology)`** — `technology_id` (T1 PK) · `version` (T1) · `name` (T3) · `vendor` (T3) · `platform` (T3) · `approval_status` (T2, indexed) · `version_constraint`/`min`/`max` (T2) · `deprecation_date` (T2) · `tier_applicability[]` (T2) · `approved_data_classifications[]` (T2) · provenance (T1)
- **`(:Catalog:IacTemplate)`** — `iac_template_id` (T1 PK) · `template_type` (T2) · `name` (T3) · `version` (T1) · `status` (T2) · provenance (T1)

The `l1/l2/l3` taxonomy + the selection edges are the **graph-native retrieval substrate** (R6 positive half, §1) — affordance design → RBT-15/RBT-17.

*Redistributed out (POC conflation resolved):* `cost_tier` → cost plane; `required_capabilities`/`options`/`preferred_over`/`replacement` → edges; `policy_rules`/`gate_requirements` → Standards/Governance; embedding block → retired (R6). Org/vendor specifics genericized (name-by-class, R2).

*Reference vs. produced (M-7).* "Solution documents" as *reference* Catalog content (template/exemplar solutions, library knowledge) are distinct from the **produced** `(:Artifact:Solution)` keystone (§5). A reference solution is Catalog ground truth; a produced solution is an Artifact. They are not the same node, and Catalog never holds the produced ASD.

### 2.2 Environment — the as-running graph (POC-absent; ages via freshness)

- **`(:Environment:DeployedService)`** — `deployed_service_id` (T1 PK) · `service_type` (T3) · `lifecycle_state` (T2, indexed) · `observed_at` (T2) · provenance (T1, `source_class` = `ingested`, runtime/CMDB class)
- **`(:Environment:DeploymentEnvironment)`** — `environment_id` (T1 PK) · `name` (T3) · `environment_class` (T2, indexed — production/staging/dev) · provenance (T1)
- **`(:Environment:ConfigurationItem)`** — `ci_id` (T1 PK) · `ci_type` (T2, indexed) · `name` (T3) · `observed_at` (T2) · provenance (T1)

*Plane signature:* freshness (`observed_at`) — runtime facts are less authoritative than catalog ground truth; this lets the RG weight environment evidence lower. *Lifecycle distinction:* `DeploymentEnvironment` is the **realized** runtime environment, distinct from a solution's design-time `target_environment` (§5, C-4). Environment is DDR-001-sanctioned CMDB-sourced ground truth (cross-check: not a contradiction — M-2 closed).

### 2.3 Operational — the track-record graph (POC-absent; durable distillation, not telemetry)

- **`(:Operational:ObservedPattern)`** — `observed_pattern_id` (T1 PK) · `polarity` (T2, indexed — `strength` / `weakness` / optional `neutral` *(M-15 contested)*) · `pattern_type` (T2, indexed) · `description` (T3) · `observation_window` (T3) · `confidence` (T2 — see §4 canonical def) · `first_observed_at`/`last_observed_at` (T2) · `status` (T2, indexed — active/superseded/resolved) · provenance (T1, `source_class` = `distilled`)

*Per R24 / R26 (B-4 — durable distillation, serialize).* The KG does **not** mirror transient SoR telemetry (ServiceNow/Datadog). It holds the durable distilled lesson — a recurring operational pattern, of **dual polarity** (a clean track record is as informative as a weakness). **No in-graph TTL.** Raw telemetry stays TTL-bounded in the **external** observability/AIOps SoR; it is not a KG plane and is not mirrored. The distillation step (reading the SoR, generalizing patterns) writes `ObservedPattern` with `source_class: distilled` and a source-record ref to the external telemetry (C-6); the process itself (cadence, generalization criteria, ownership) → **DDR-003 / detection-promotion SDD** (RBT-14). Weakness/strength entry into the KG is **EA-gated** via the feedback loop (§5), not auto-ingested. *DDR-001 v1.1.0 (RBT-39) aligns the parent definition to this; DDR-002 authoring is serialized behind that landing (§0).*

### 2.4 Governance — the decision/audit graph (immutable append-only; references, not records)

**Decision supertype + subtypes (M-3 (iii)).** A single shared decision *shape* with two subtype labels, so SDLC gates and the feedback-loop promotion gate share structure without being conflated:

- **`(:Governance:Decision)`** *(supertype shape — never instantiated bare; every decision node also carries a subtype label)* — `decision_id` (T1 PK) · `decision` (T2, indexed — approved/approved_conditional/rejected) · `decided_at` (T2) · `approval_token_id` (T3) · provenance (T1). Decided-by via `(Actor)-[:APPROVED]->(Decision)`.
- **`(:Governance:Decision:GateDecision)`** *(SDLC gates — external-captured)* — adds `gate` (T2, indexed — SDLC gate discriminator; **placeholder `gate_0`/`gate_1`/`gate_2`, M-15 contested → reconcile to enterprise gate taxonomy, RBT-41**) · `origin` (T2 — `external_captured`/`self_issued`) · `source_class` (T2 — per-gate SoR, e.g. EAMS for design, ITSM for change/release) · `external_record_ref` (T3 — pointer to the authoritative external record) · `all_hard_constraints_passed` (T2) · `rejection_reason` (T3, conditional). `DECIDED_ON` → **Solution** (§5).
- **`(:Governance:Decision:PromotionDecision)`** *(feedback-loop EA approval — SOFIA-issued)* — `origin` fixed `self_issued`; **no `external_record_ref`** (SOFIA is the issuer, not a capturer). `DECIDED_ON` → **CandidatePromotion** (§5).

- **`(:Governance:Actor)`** — `actor_id` (T1 PK) · `actor_type` (T2, indexed — `human` / `system`) · `name` (T3) · provenance (T1)
- **`(:Governance:Role)`** — `role_id` (T1 PK) · `name` (T3) · provenance (T1)
- **`(:Governance:Attestation)`** — `attestation_id` (T1 PK) · `result` (T2, indexed — pass/fail) · `attested_at` (T2) · provenance (T1) *(closes obligation↔satisfaction, §3)*

*Key postures:* for `GateDecision`, the external entity is **always** the system of record; the node is a **captured/issued reference**, not SOFIA's authoritative record (`origin` + `external_record_ref` carry inbound-capture vs. self-issue-then-transmit). For `PromotionDecision`, SOFIA *is* the issuing authority over the feedback loop, so there is no external record to point at — the de-conflation (M-3) keeps the SDLC-gate semantics from leaking onto the promotion gate and vice-versa. `Actor` generalizes the POC's "User" so any decider — human, SOFIA, or another external system — has a structural home. The per-action **disposition-event stream is excluded** (transient → orchestration/observability SoR, per R24). `Actor`/`Role` are governance-participating identities, **not** an IAM mirror. Immutable append-only: a re-decision is a new node.

### 2.5 Standards — the governance-of-knowledge graph (versioned + change-impact)

- **`(:Standards:Standard)`** — `standard_id` (T1 PK) · `version` (T1) · `name` (T3) · `authority` (T3) · `status` (T2) · provenance (T1) *(the referenceable authority — "per policy 1234")*
- **`(:Standards:PolicyRule)`** — `policy_rule_id` (T1 PK) · `version` (T1) · `rule_name` (T3) · `domain` (T2, indexed) · `status` (T2, indexed, versioned) · `superseded_by` (T2) · `enforcement_level` (T2 — hard/soft) · `enforced_at_gate` (T2) · `statement` (T3 — natural-language requirement) · `rule_definition` (T3 — opaque declarative IF/THEN, the validator consumes it; the graph never traverses into it) · provenance (T1)
- **`(:Standards:ComplianceControl)`** — `control_id` (T1 PK) · `framework` (T2, indexed — HIPAA/SOC2/PCI as *data*) · `control_ref` (T3) · `control_name` (T3) · provenance (T1)

*Decision (option C):* the executable rule logic rides the `PolicyRule` node as opaque `rule_definition` (KG-as-policy-SoR, matching DDR-001's served-from-graph model); the constraint-validator evaluates it. **`rule_definition`↔edge sync invariant (M-12):** any KG entity a `rule_definition` depends on for *traversal-relevant* evaluation MUST also be reachable as an explicit `GOVERNED_BY` / `MANDATES` edge — the opaque blob may not hide a dependency the graph can't see. Documented invariant + conformance check (§7). A standard is broader than rules — it can `DEFINE` a `PolicyRule`, `PRESCRIBE` a `Technology`/`Pattern`, etc. **The `Process` node type and its edges are deferred (B-3 → RBT-40)**; `PRESCRIBES` keeps its non-Process targets and loses the Process target until Process lands. Mandates resolve in two ways: **structurally** (validator reads the solution graph — prohibitions, "uses the vault") or **by attestation** (process performed / evidence produced — `Attestation`, §2.4).

### 2.6 Extension mechanism + cost plane (the R23 exemplar — first Extension registration)

**Mechanism:**
- **`(:Extension:PlaneDefinition)`** — `plane_id` (T1 PK) · `plane_name` (T3) · `version` (T1) · `status` (T2, indexed) · `attaches_to` (T2 — list of core labels the plane may enrich) · `property_schema` (T3 — opaque schema-on-write definition for the plane's node types) · provenance (T1)

The registry is self-describing (query `PlaneDefinition` nodes to enumerate registered planes). `attaches_to` and `property_schema` are **declarations** (properties), not edges-to-labels — a simplification of the POC's edge-modeled `DEFINES`/`ATTACHES_TO`. Schema-on-write validates extension nodes against their `PlaneDefinition`; instance-edges are bounded to the `attaches_to` labels. Extension nodes carry the plane's secondary label (the hybrid, §1).

**Cost plane — first registration:** `PlaneDefinition{plane_id: "cost", attaches_to: [Capability, Technology]}`.
- **`(:Cost:RateCard)`** — `rate_card_id` (T1 PK) · `version` (T1) · `effective_from`/`effective_to` (T2) · `status` (T2, indexed) · `rates` (T3, unit→cost payload) · provenance (T1). *Never-deleted; superseded only.*
- **`(:Cost:CostFactor)`** — `cost_factor_id` (T1 PK) · `factor_scope` (T2, indexed — technology/capability) · `factor_type` (T2, indexed) · `amount`/`unit` (T3) · `version` (T1) · `status` (T2) · provenance (T1). *Reference input.*
- **`(:Cost:CapabilityCostEstimate)`** — `estimate_id` (T1 PK) · `aggregate_cost` (T2 — **derived, never hand-set**) · `capability_version_ref` (T2 — staleness pin) · `confidence` (T2) · `computed_at` (T2) · provenance (T1, `source_class` = `computed`). *Derived output, refreshable.*

*Collapses from DDR-040's six types:* `CostPlaneDefinition` → the generic `PlaneDefinition`; `CapabilityCostFactor` + `TechnologyCostFactor` → one `CostFactor` (`factor_scope`); derived line-items → `HAS_COST_FACTOR` edges (not duplicated nodes); `CostFactorDefinition` → the `factor_type` enum. Cost is the first temporally-mixed plane: `RateCard`/`CostFactor` versioned reference, `CapabilityCostEstimate` refreshable derivation. Tier-1/2 traversal + the `Tier1CostEstimateResult` DTO → RBT-25.

---

## 3. KG relationships — edge grammar + catalog

**Edge grammar:**
- **Direction & naming** — `SCREAMING_SNAKE` verb phrases in the natural semantic direction; Neo4j traverses both ways, so direction is for readability, not access. One edge per relationship — no redundant inverses.
- **Edge properties** — attributes belonging to the *relationship*, not either node.
- **Edge provenance** — asserted-fact edges (ingested, e.g. `APPROVED_OPTION_FOR`) carry `source_class`; structural edges do not.
- **Re-bind discipline (M-8)** — each edge *type* declares a supersession behavior: **`rebind:current`** (structural / selection edges re-point to the new version node on supersession — the hot path stays on current) or **`rebind:pinned`** (audit/evidence edges pin to the specific version node and never re-point). Declared per edge type in the catalog below.
- **Cardinality** — not constrainable in Neo4j schema → documented invariant + conformance check.
- **Temporal edges** — relationships whose *validity* is time-bound carry `effective_from`/`effective_to` + `status`; structural edges do not.
- **Confidence (M-4)** — KG-internal edges are authoritative by default (no confidence); environment/operational-derived edges *may* carry `confidence`; reasoning-time confidence lives on the RG `Evidence` edge (§5), not on KG edges. Confidence semantics are canonically defined in §4.

**Edge catalog (five core-plane sub-graphs + Cost/Extension):**

*Selection (Catalog) — `rebind:current`:* `(Pattern)-[:REQUIRES_CAPABILITY {required, tier_conditional, tier_threshold}]->(Capability)` · `(Technology)-[:APPROVED_OPTION_FOR {conditional, justification}]->(Capability)` *(temporal)* · `(Pattern)-[:PREFERRED_OVER]->(Pattern)` · `(Technology)-[:REPLACED_BY]->(Technology)` *(temporal)* · `(IacTemplate)-[:IMPLEMENTS]->(Pattern)`

*As-running (Environment, confidence-bearing):* `(DeployedService)-[:RUNS {confidence}]->(Technology)` · `(DeployedService)-[:DEPLOYED_IN {confidence}]->(DeploymentEnvironment)` · `(DeployedService)-[:REALIZES {confidence}]->(Capability)` · `(ConfigurationItem)-[:PART_OF {confidence}]->(DeployedService)`

*Track-record (Operational):* `(ObservedPattern)-[:OBSERVED_IN {confidence}]->(Technology | Pattern | Capability | DeploymentEnvironment)`

*Governance-of-knowledge (Standards):* `(Standard)-[:DEFINES]->(PolicyRule)` · `(Standard)-[:PRESCRIBES]->(Technology | Pattern)` *(Process target deferred → RBT-40)* · `(PolicyRule)-[:MAPS_TO]->(ComplianceControl)` · `(PolicyRule)-[:MANDATES]->(Technology)` · `(Pattern | Technology | Capability)-[:GOVERNED_BY]->(PolicyRule)` *(static associations only — solution-time governance is computed by matching the rule condition against the solution, not a stored edge)*

*Decision/audit (Governance):* `(Actor)-[:HAS_ROLE]->(Role)` *(temporal)* · `(Actor)-[:APPROVED {role, approved_at}]->(Decision)` *(targets either subtype via the supertype, M-3)* · `(GateDecision)-[:REVIEWED {hash}]->(Artifact)` · `(Attestation)-[:SATISFIES]->(PolicyRule)` · `(Attestation)-[:BY]->(Actor)` · `(Attestation)-[:EVIDENCED_BY]->(Artifact)`. *(`(Attestation)-[:FOR_PROCESS]->(Process)` deferred entirely → RBT-40.)*

*Cost (Extension):* `(CapabilityCostEstimate)-[:FOR_CAPABILITY]->(Capability)` *(cardinality 1)* · `(CapabilityCostEstimate)-[:HAS_COST_FACTOR]->(CostFactor)` · `(CostFactor)-[:FOR_TECHNOLOGY]->(Technology)` · `(CapabilityCostEstimate)-[:PRICED_BY]->(RateCard)` *(`rebind:pinned`)*

*Solution-centric and promotion edges are deferred to the keystone (§5).*

**Obligation↔satisfaction model.** Standards hold the *obligation*; Governance holds the *attestation*; the solution sits in the middle. Validation traverses from a solution to its obligations and checks each has a matching satisfaction. Two closing mechanisms: validator-structural (prohibitions, structural requirements) and attestation-evidenced (process performed / evidence produced). A missing satisfaction surfaces as a compliance gap (an RG risk inference), not silence.

---

## 4. The Reasoning Graph — node schemas

**Label reconciliation** (align to ADR-002 §2.6 / ADR-001 §2.2 vocabulary, retiring POC names): `Inference` → `ReasoningProgress`; `Hypothesis` → `RejectedAlternative`; `Evidence` and `ReasoningSession` kept. Per **ADR-002 §2.6**, the rich `ReasoningProgress` *fields* are SDD-level; DDR-002 owns only the schema contract. RG nodes carry **no KG plane label** (M-7, §1).

- **`(:Reasoning:ReasoningSession)`** — `session_id` (T1 PK) · `solution_ref` (T1, 1:1 with the produced solution) · `lifecycle_state` (T2 — **AOE-owned; value-set deferred to the AOE SDD, RBT-16, with a named placeholder; DDR-001 likewise leaves it unspecified — M-5ᴬ**) · `created_at` (T2) · provenance (T1)
- **`(:Reasoning:ReasoningProgress)`** — `progress_id` (T1 PK) · `conclusion_type` (T2, indexed — PatternMatch / TechnologySelection / GapConclusion / OverrideFlag / RiskSignal / ComplianceEvaluation; **M-15 contested; M-6 reconciliation below**) · `confidence` (T2) · `overridden_by_human` (T2) · `created_at` (T2) · provenance (T1). *= the typed conclusion (lean reading: no separate container). Rich conclusion/rationale → SDD.*
- **`(:Reasoning:Evidence)`** — `evidence_id` (T1 PK) · `fact_summary` (T2 — denormalized snapshot) · `confidence` (T2, inherited) · `weight` (T2) · `source_node_version` (T2 — version pin) · `observed_at` (T2)
- **`(:Reasoning:RejectedAlternative)`** — `rejected_id` (T1 PK) · `candidate_type` (T2, indexed) · `rejection_reason` (T3) · `score_delta` (T2) · `human_accepted` (T2) · `human_accepted_at` (T2)

**Confidence — canonical definition (M-4).** Confidence is a `[0.0, 1.0]` scalar with **per-surface semantics**: on `Evidence` it is *source authority × freshness* (authoritative Catalog scores above aging Environment, decayed by `observed_at`); on a confidence-bearing **KG edge** (Environment/Operational) it is *observation certainty*; on `ReasoningProgress` it is the *rolled-up conclusion confidence*. **Inheritance/rollup rule:** `Evidence.confidence` inherits from the `SOURCED_FROM` KG node's authority class at snapshot time; `ReasoningProgress.confidence` is a (SDD-defined) rollup over its `SUPPORTED_BY` Evidence — DDR-002 fixes that the rollup exists and is monotone (a conclusion is no more confident than its strongest evidence path), the function itself → SDD.

**conclusion_type ↔ correction-surface ↔ DDR-001 reconciliation (M-6).** The six `conclusion_type` values are the *typed-conclusion* enum. They map onto the seven correction-surfaces of §5 (technology, pattern, capability, integration, risk, compliance, cost) — `integration` and `cost` surface as `TechnologySelection`/`GapConclusion` variants rather than distinct conclusion types — and align with DDR-001's signal/action classes (no contradiction: DDR-001's classes are coarser). The enum is confirmed aligned; the mapping table is authored into the DDR so the three vocabularies are reconciled in one place.

*Write authority (**ADR-002 §2.6** invariant):* ASA authors `ReasoningProgress`; AOE owns `ReasoningSession` lifecycle only; writes route via knowledge-service. Mechanization → RBT-33.
*RG-internal edges:* `(ReasoningSession)-[:CONTAINS]->(ReasoningProgress)` · `(ReasoningProgress)-[:SUPPORTED_BY]->(Evidence)` · `(ReasoningProgress)-[:REJECTED]->(RejectedAlternative)` · `(ReasoningProgress)-[:LED_TO]->(ReasoningProgress)`.
*Point-in-time fidelity:* `fact_summary` + `source_node_version` make the audit trail immune to later KG drift.

**RG provenance posture (M-5 — confirmed under B-1 (c)).** Provenance is present across the RG, but expressed by node kind:
- `ReasoningSession` and `ReasoningProgress` are *authored reasoning state* → they carry the provenance group (provenance = the authoring session/agent, ASA per §2.6).
- `Evidence` and `RejectedAlternative` are *derived* and deliberately omit the group; their provenance is **structural**: `Evidence` pins `source_node_version` + `observed_at` and links `SOURCED_FROM` the authoritative KG node it snapshots (§5); `RejectedAlternative` is reached only via its parent `ReasoningProgress` (`REJECTED`) and `WOULD_HAVE_USED` the KG node it points at, inheriting the parent's provenance.

So the provenance *existence constraint* (§7) scopes to **KG nodes + the two authored RG types + the Artifact family** (M-7); the two derived RG types are covered by the structural surrogate. **The surrogate's enforceability gap is named, not hidden (B-1 / R27):** the cardinality invariants that *make* the surrogate sound are CI-only (§7) — Neo4j cannot express them as constraints — so they are documented and mechanized at RBT-33, which is sequenced ahead of RBT-15 so the gateway is built against an enforced contract. *(v0.2 flagged this posture for confirmation; ratified under B-1 (c) — the structural surrogate stands, the exposure is named.)*

---

## 5. Cross-graph linkage + the feedback loop

**Ownership line (R8 / R22) — what DDR-002 owns vs. cites in this section.** DDR-002 **owns** the *schema contract*: the `(:Artifact:Solution)` and `CandidatePromotion` node shapes, the cross-graph and promotion edge grammar, and the *structural* invariants (append-only terminal status, provenance-chain traceability). DDR-002 **cites, and does not re-author:** the promotion *mechanics / data-path* → DDR-001; the *diagnosis policy / EA approval criteria / thresholds / cadence* → DDR-003 (RBT-14); the *workflow* → SDD. The Refine/Request-new/Correct-scope framing and the "EA-gate is a diagnosis" characterization below are stated for schema motivation only — their governance is DDR-003's, their data-path is DDR-001's.

**The Artifact family (M-7 — a distinct third citizen-class).** `(:Artifact …)` is **neither a KG plane nor RG** — it is the produced-deliverable family (solutions, BCDR plans, build sheets). It carries its own PK, its own provenance group (`source_class: authored`/`computed`), and its own uniqueness, and it carries **no KG plane label** (so plane-scoped ground-truth traversals skip produced artifacts). It joins KG and RG only by edges. This resolves the v0.2 ambiguity about whether `Solution` was a Catalog node or an RG node: it is **neither** — it is an Artifact.

**Evidence edges (RG → KG):** `(Evidence)-[:SOURCED_FROM]->(KG node)` *(`rebind:pinned`; confidence inherits here — authoritative Catalog scores above aging Environment)* · `(RejectedAlternative)-[:WOULD_HAVE_USED]->(KG node)`. *(`DREW_FROM`/`TRAVERSED` deferred — the considered-set is reconstructable from Evidence + RejectedAlternative.)*

**The Solution keystone:**
- **`(:Artifact:Solution)`** — `artifact_id` (T1 PK) · `artifact_type` (T2 — `solution`) · `version` (T1) · `lifecycle_state` (T2, indexed — FSM: proposed→architected→gated→approved→operational) · `content_hash` (T2 — tamper-detection) · `snapshot_ref` (T2 — dual-home pointer) · `target_environment` (T2 — design-time intent) · `created_at` (T2) · provenance (T1). `(:Artifact)` is the general produced-deliverable family (solutions, BCDR plans, build sheets).

*Bridge edges:* `(ReasoningSession)-[:PRODUCED]->(Solution)` *(1:1)* · `(Solution)-[:USES]->(Technology)` · `(Solution)-[:FOLLOWS]->(Pattern)` · `(GateDecision)-[:DECIDED_ON]->(Solution)` · `(Solution)-[:HAS_ARTIFACT]->(Artifact)` *(Solution → component sub-artifacts, M-7)*. `target_environment` is a **string-valued property** (design intent) resolved by string-match, **not** an FK-edge to `DeploymentEnvironment` (C-4); the realized environment arrives later via `DeployedService`. Dual-home mechanics → §6.

**CandidatePromotion + feedback loop (R22)** — *schema contract owned here; mechanics cited to DDR-001 per the ownership line above:*
- **`(:Reasoning:CandidatePromotion)`** — `candidate_id` (T1 PK) · `promotion_type` (T2, indexed) · `proposed_change` (T3 — opaque) · `requested_item` (T3) + `requested_item_kind` (T2 — technology/pattern/capability/integration) + `target_ref` (T3) *(for request-new gaps)* · `basis_strength` (T2 — *M-15 contested*) · `confidence` (T2) · `status` (T2, indexed — proposed / under_review / approved / rejected / promoted) · `created_at` (T2) · provenance (T1). **Append-only**; terminal `status` (`promoted` / `rejected {reason}`) is the durable evaluation outcome — declines are explainable and gaps don't re-surface.

*Promotion edges:* `(CandidatePromotion)-[:PROPOSED_FROM]->(ReasoningProgress | Evidence | ObservedPattern)` · `(PromotionDecision)-[:DECIDED_ON]->(CandidatePromotion)` *(the feedback-loop EA gate — distinct subtype, M-3; no longer `GateDecision{gate: ea_promotion}`)* · `(CandidatePromotion)-[:PROMOTES_TO_KNOWLEDGE]->(KG node)` *(materialized node stamped `source_class: promoted`)*.

*Structural & read-discipline invariants:*
- **Proposal-visibility (M-9 — dissolved to DDR-001 + gateway).** `CandidatePromotion` must not appear in ground-truth synthesis traversals until EA-approved. This is **owned by DDR-001** as the proposal-visibility invariant + conformance check #4 (`SOFIA never self-modifies the KG`; promotions excluded from ground-truth traversal until approved). DDR-002 supplies the *structural aid* — `CandidatePromotion` carries no KG plane label, so plane-scoped traversals skip it — but names honestly that full enforcement is **gateway-enforced read-discipline** (the sole-owner knowledge-service scopes ground-truth reads), **not** a pure structural guarantee. Lands in the R27 CI-only set (§7); cites DDR-001 check #4, no DDR-001 amendment needed.
- **Provenance chain.** A promoted node traces back through `PROMOTES_TO_KNOWLEDGE` → `CandidatePromotion` → `PROPOSED_FROM` → `ReasoningProgress`/`Evidence` → `SOURCED_FROM` → original facts; `source_class: promoted` makes it distinguishable from `ingested` (DDR-001 check #6, M-1).

**Generalized correction mechanism** *(schema motivation; governance → DDR-003).* Every `conclusion_type` is a human-correction surface (technology, pattern, capability, integration, risk, compliance, cost — reconciled to the conclusion_type enum in §4, M-6), in three flavors: **Refine** (override to an existing option → context-scoped, evidence-backed preference signal on the selection edge, no pairwise cycles; the *runtime preference-landing* → solutioning SDD, RBT-17), **Request-new** (gap → human evaluation/onboarding; never auto-created), **Correct-scope** (false risk / mis-scoped rule → adjust existing ground truth). The capture machinery (`overridden_by_human`, `human_accepted`, `GapConclusion`, `RejectedAlternative`, `CandidatePromotion`, EA-gate, `PROMOTES_TO_KNOWLEDGE`) is general across surfaces. The "override is a signal the EA *diagnoses*" framing is governance characterization owned by DDR-003, not authored here.

---

## 6. Versioning & temporal model

**Per-posture spectrum** (each plane fit to its nature): Catalog/Standards/RateCard **version** (supersession), Environment **ages** (`observed_at`), Operational **distills** (status-managed), Governance **accretes** (immutable append-only), RG **pins** (point-in-time), Solutions/Artifacts **dual-home**.

**Supersession — Option A (scoped to versioned-ground-truth types: Catalog, Standards, RateCard, CostFactor, PlaneDefinition).** A node carries `version` + `effective_from`/`effective_to` + `status` + `superseded_by`; superseding creates a new retained node and marks the old superseded. **Atomicity (M-8):** supersession is a **single atomic transaction** — create new version node, mark old `superseded`, and re-point all `rebind:current` structural edges to the new node — so a traversal never observes a half-superseded state with two active versions. `rebind:pinned` audit/evidence edges are untouched (they pin to their specific version node). The edge re-pointing is the **gateway's** responsibility (knowledge-service, sole writer — consistent with DDR-001's gateway pattern, R8 boundary; cited, not re-authored). Never-delete via retained versions; as-of via effective-dating. Chosen over an identity+version-node pattern to keep the selection-graph hot path hop-free (versioning is rare; traversal is constant).

**Version-pinning.** `Evidence.source_node_version` + `CapabilityCostEstimate.capability_version_ref` reference specific retained version nodes (`rebind:pinned`); with `Evidence.fact_summary` that yields point-in-time fidelity.

**Dual-home (Artifact/Solution).** The graph node holds metadata, edges, `content_hash`, `snapshot_ref`; immutable content lives in the external snapshot store (Firestore per R9, routed to DDR-001); the hash is tamper-detection (snapshot hash must match `content_hash`). A new version is a new node + new snapshot; the old pair is retained.

**Uniqueness under versioning.** PKs unique on `(business_key, version)`; "exactly one active version per business_key" is a documented invariant + conformance check.

---

## 7. Constraints, indexes & conformance

**DB-enforced (Neo4j Enterprise) — generating rules:**
- **Uniqueness** on every PK; `(business_key, version)` for the versioned-ground-truth types.
- **Existence constraints** on the provenance group (`source_class`, `recorded_at`) on every **KG** node, the **two authored RG types** (`ReasoningSession`, `ReasoningProgress`), and the **Artifact family** (M-7) — see §4 for the RG-provenance posture — plus each node's T1 required props. (The Enterprise *edition* committed in ADR-002 — edition per **R3** — buys existence-constraint capability.)
- **Indexes** on the flagged T2 traversal/filter properties only (lean — no speculative indexing); plane secondary-labels are inherently indexed. *The index set is **provisional**, revisitable once the SDDs surface real query patterns (C-5).*

**Conformance-checked invariant set — CI-only (Neo4j cannot express → documented + CI; mechanization → RBT-33; enforcement posture per R27).** Neo4j existence/uniqueness constraints cannot express these; they are honestly named as CI-only with a stated exposure window (below), uniform under the R27 posture:

1. **RG-provenance edge invariants (B-1 / R27 — highest-priority RBT-33 member, sequenced ahead of RBT-15):** every `(:Reasoning:Evidence)` carries a **mandatory** `SOURCED_FROM` edge to a provenance-bearing KG node; every `(:Reasoning:RejectedAlternative)` is reached via **exactly one** parent `REJECTED` edge; `Evidence` **not** sourced from a provenance-bearing KG node is **prohibited** (or carries its own declared treatment). These cardinality invariants are what make the §4 structural provenance-surrogate sound (M2-1).
2. **no vector properties** (R6).
3. **relationship cardinality** (e.g. `FOR_CAPABILITY` cardinality 1).
4. **one active version per business_key.**
5. **aggregate-derivation** (`CapabilityCostEstimate.aggregate_cost` never hand-set).
6. **schema-on-write** (extension nodes validate vs. `PlaneDefinition`; edges bounded to `attaches_to`).
7. **ADR-002 §2.6 write-authority** (ASA authors `ReasoningProgress`; AOE session-lifecycle only).
8. **never-delete** (versioned types supersede, atomic re-bind — M-8).
9. **proposal-visibility / read-discipline (M-9):** `CandidatePromotion` excluded from ground-truth synthesis traversal until EA-approved — gateway-enforced read-discipline + structural label-skip aid; defers to DDR-001 check #4.
10. **rule_definition↔edge sync (M-12):** traversal-relevant `rule_definition` dependencies also exist as `GOVERNED_BY`/`MANDATES` edges.
11. **provenance distinguishability (DDR-001 check #6, M-1):** `promoted` distinguishable from `ingested` via `source_class`.
12. **tamper-detection** (`Artifact.content_hash` matches snapshot hash).
13. **no-PHI** (classification, gateway-enforced, R10).

**Named exposure window (R27).** Until RBT-33 mechanizes them, this CI-only set is review-enforced (three-hat / DDR-SDD-authoring time), not CI-enforced — an honest gap, tracked, not hidden. RG-provenance (#1) is the highest-priority member and is implemented **before** RBT-15 knowledge-service authoring begins, so the gateway is built against an enforced provenance contract.

---

## 8. Boundary routing & doc frame

**Boundary Routing Map** (named here, owned elsewhere):
- **→ DDR-001** (one-way, R8): plane-model architecture, Extension *architecture*, gateway pattern, three-store persistence (R9), feedback-loop *architecture* (data-path / promotion mechanics), proposal-visibility invariant + check #4 (M-9), provenance-distinguishability check #6 (M-1). **DDR-001 v1.1.0 (RBT-39, R26)** aligns the Operational-plane definition to durable distillation; **DDR-002 authoring serializes behind it** (B-4). Cited, never re-opened.
- **→ DDR-003 (RBT-14):** feedback-loop *governance* — EA authority, diagnosis policy, what-gets-promoted criteria, thresholds, cadence, retention/audit policy; **telemetry→`ObservedPattern` distillation process** (B-4); **CandidatePromotion authorship + EA-gate completion** (B-2/M-13). *(RBT-14 annotated with these incoming forward-deps.)*
- **→ RBT-15 (knowledge-service SDD):** gateway write endpoints; enforcement of the invariants (derivation, never-delete + atomic re-bind, schema-on-write, classification, supersession edge re-pointing); **graph-native retrieval affordance** (R6 positive half / M-10 — query patterns, similarity-edge question). *Built against the enforced RG-provenance contract — RBT-33 sequenced ahead. (RBT-15 annotated.)*
- **→ RBT-16 (AOE SDD):** `ReasoningSession.lifecycle_state` value-set (M-5ᴬ).
- **→ RBT-17 (solutioning-agent SDD):** selection-edge **preference-landing** runtime (Refine → `PREFERRED_OVER` re-weight/re-point, `rebind` behavior); retrieval consumption (M-10). *(RBT-17 annotated.)*
- **→ RBT-25 (cost-estimation SDD):** Tier-1/2 traversal, cost DTOs.
- **→ RBT-33:** mechanization of the CI-only conformance set (broadened to include DDR-002-native checks; RG-provenance highest-priority, sequenced ahead of RBT-15).
- **→ RBT-40 (Process node):** the `Process` node type + its deferred edges (`PRESCRIBES`→Process, `FOR_PROCESS`→Process) land when the Process use case is designed (B-3).
- **→ RBT-41 (gate-enum reconcile):** `GateDecision.gate` placeholder → enterprise SDLC gate taxonomy (M-3 carry / M-15).
- **→ reasoning/ASA SDD (RBT-17):** full `ReasoningProgress` fields (**ADR-002 §2.6**).

**DDR-002-native conformance checks** (design-time enforced, mechanization at RBT-33): the CI-only set enumerated in §7.

**Conscious exclusions / deferred scope** (boundary chosen, not missed):
- Attestation time-decay / re-attestation cadence
- Waiver / risk-acceptance closure of mandates
- Aggregate / portfolio-level mandates
- Inherited / platform-level compliance
- Full bitemporal *relationship*-history (node as-of + evidence pinning are preserved)
- The `Process` node type + its edges (→ RBT-40)
- `DREW_FROM` / `TRAVERSED` reasoning-trail edges

**Risks / Pre-Acceptance Conditions (M-16 — landing posture).** The blocker dispositions resolve as follows, and govern how DDR-002 lands:
- **B-4 (Operational↔DDR-001):** *serialized* — DDR-002 Code-authoring is **gated on RBT-39 landing** DDR-001 v1.1.0 on `develop`. By authoring time this is cleared (the parent already agrees).
- **B-1 (RG-provenance enforceability):** *folded with named exposure* — structural surrogate stands (§4); the cardinality invariants are CI-only (§7 #1), documented + mechanized at RBT-33 (R27). This is an **accepted, named risk**, not a blocker.
- **B-3 (Process dangling edges):** *folded* — Process node + edges pulled, deferred to RBT-40 (§2.5, §3).
- **M-14 (DDR-001 vocab alignment):** *verified* — cross-check discharged.

**Landing posture:** with B-4 cleared by serialize before authoring and B-1/B-3 folded, DDR-002 authors as a single artifact (R18) `0.1.0` PROPOSED → `1.0.0` ACCEPTED, carrying the §7 #1 RG-provenance CI-exposure as a **named accepted risk** (R27) with RBT-33 tracked. The next review cycle (Pass-3 three-hat + antagonistic re-review on this v0.3) is the gate before authoring is unblocked.

**Forward dependencies (filed / tracked):** RBT-12/DDR-001 (landed upstream — Done @ `15ff20f`, PR #12) → **RBT-39** (v1.1.0 amendment, **blocks RBT-13**); RBT-14/DDR-003 (governance + distillation + promotion-authorship — annotated); RBT-15/RBT-16/RBT-17/RBT-25 (SDDs this gates — RBT-15/17 annotated); **RBT-33** (CI-only mechanization, broadened + sequenced ahead of RBT-15); **RBT-40** (Process node + deferred edges); **RBT-41** (gate-enum reconcile). *(All forward-pointers from this cycle are filed or annotated — no "to-file-later" tail.)*

**Doc frame:** references DDR-001 (v1.1.0), ADR-001, ADR-002, and rulings R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25/R26/R27; single original-authoring Change Log row per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED); identity string *Executive Architect, Haffey Enterprises LLC*; lands at `docs/ddr/DDR-002-graph-schema.md`.

---

## Appendix A — ratification trace

Ratified section by section in the RBT-13 claude.ai design session (2026-06-19 / 2026-06-20), one ratification per turn: schema grammar & hybrid plane membership → Catalog → Environment (`DeploymentEnvironment` naming) → Operational (re-centered to dual-nature `ObservedPattern`, R24) → Governance (`GateDecision` as reference, `Actor` generalization) → Standards (`Standard` un-deferred, option-C `rule_definition`, obligation↔satisfaction / `Attestation`) → Extension mechanism → cost plane (R23) → edge grammar + catalog → RG nodes (label reconciliation) → cross-graph + Solution keystone → CandidatePromotion + feedback loop + generalized correction mechanism → versioning (Option A) → constraints/indexes/invariants → boundary routing + conscious exclusions. Ledger rulings written across the cycle: R23 (prior), R24, R25, **R26**, **R27**.

---

## Appendix B — v0.3 fold-log (disposition of Pass-2 three-hat + antagonistic Pass-1 + DDR-001 cross-check)

> *Substrate-only per R18 / M-17 — never enters the DDR.* Every review finding and its ratified disposition. Forks marked **(fold)** are substrate-design decisions; their elevation to ledger rulings is **deferred to v0.3 acceptance** (post-review), per threshold discipline — they are not auto-promoted while still under review.

**Pass-2 three-hat (LAA/SA/EA): PASS, converging.**
- **M2-1** (RG-provenance mandatory-edge cardinality into §7) — **subsumed into B-1**; written as §7 #1.
- **C2-1** ("six sub-graphs" → "five core-plane + Cost/Extension") — applied, §3.

**Antagonistic Pass-1 + DDR-001 cross-check addendum — blockers:**
- **B-4** (Operational↔DDR-001 contradiction) — **Model A + serialize.** KG Operational = durable distilled `ObservedPattern` (no in-graph TTL); raw telemetry = external observability/AIOps SoR (TTL'd there), not a KG plane. DDR-002 authoring serialized behind DDR-001 v1.1.0 (RBT-39). Ledger **R26**. §0, §2.3, §8.
- **B-1** (RG-provenance enforceability) — **(c) structural surrogate stands**, M2-1 cardinality invariants into §7 #1, mechanized at RBT-33 (highest-priority, ahead of RBT-15), exposure named in Risks. Ledger **R27**. §4, §7, §8.
- **B-3** (Process dangling edges) — **(b) pull.** `PRESCRIBES` loses Process target; `FOR_PROCESS` deferred entirely; Process node + edges → RBT-40. §2.5, §3, §8.
- **B-2** (approved-but-unwritten completion) — **corrected DOWN to MATERIAL** by cross-check (DDR-001 supplies the EA-gate architecture; CandidatePromotion is a proposal, not ASA content). Routed to DDR-003 / detection-promotion (RBT-14, annotated). §5, §8.

**Antagonistic Pass-1 — structural forks (fold; ledger-elevation deferred to acceptance):**
- **M-7** (Artifact/Solution membership) — **(i) Artifact = distinct third family** (own PK/provenance/uniqueness; no KG plane label; joined by edges). §0, §1, §4, §5, §7. Resolves M-7(a/b/c/d).
- **M-9** (exclusion-by-label) — **dissolved.** DDR-001 owns proposal-visibility invariant + check #4; DDR-002 cites it + sole-owner gateway, names it as gateway-enforced read-discipline (structural label-skip is an aid, not the guarantee). §5, §7 #9. No DDR-001 amendment.
- **M-3** (gate conflation) — **(iii) Decision supertype + GateDecision/PromotionDecision subtypes** (multi-label). Resolves C-1 (DECIDED_ON overload). Gate-enum reconcile → RBT-41. §2.4, §3, §5.
- **M-10** (R6 positive half) — **(b) name existing substrate** (taxonomy + selection edges + track-record) as R6 retrieval substitute, restate prohibition, route affordance → RBT-15/17. §1, §2.1, §8.

**Antagonistic Pass-1 — material (fold batch, applied in v0.3):**
- **M-1** provenance origin-classes — `source_class` enum {ingested/distilled/computed/promoted/authored}, `ingested_at`→`recorded_at`; DDR-001 check-#6 obligation. §1, §2.x, §7 #11.
- **M-4** confidence canonical def — `[0,1]`, per-surface semantics, monotone rollup. §3, §4.
- **M-5ᴬ** `ReasoningSession.lifecycle_state` — routed to AOE SDD (RBT-16) with named placeholder; DDR-001 also unspecified. §4, §8.
- **M-6** conclusion_type ↔ correction-surface ↔ DDR-001 reconciliation — one mapping table; enum confirmed aligned. §4, §5.
- **M-8** supersession atomicity — single atomic transaction + per-edge `rebind:current|pinned`; re-point is gateway's job (DDR-001 pattern). §3, §6.
- **M-11** (CI-only invariant set) — templated as the uniform §7 set under R27.
- **M-12** `rule_definition`↔edge sync invariant. §2.5, §7 #10.
- **M-13** (approved-but-unwritten) — with B-2 → RBT-14.
- **M-14** (DDR-001 vocab alignment) — verified / discharged by cross-check.
- **M-15** contested-T2 annotation — conclusion_type, gate enum, polarity-neutral, basis_strength flagged; spike-generalization review pass added to plan. §1, §2.3, §2.4, §4, §5.
- **M-16** pre-acceptance conditions + landing posture — enumerated; B-4 serialized, B-1/B-3 folded; lands PROPOSED→ACCEPTED with named R27 exposure. §8 Risks.
- **M-17** authoring instruction — single Change-Log row (R18); v0.x/fold history substrate-only. Header + §8.
- **M-2** (Environment contradiction) — **→ COSMETIC** by cross-check (DDR-001-sanctioned CMDB-sourced). §2.2.

**Antagonistic Pass-1 — cosmetic:**
- **C-1** — resolved by M-3 (DECIDED_ON disambiguated by subtype).
- **C-2** — §0 Frame → numbered testable components (DDR template §1). §0.
- **C-3** — Layer-of-abstraction + substrate-stability note (gates 12 SDDs). §0.
- **C-4** — `Solution.target_environment` = string-match, not FK-edge to `DeploymentEnvironment`. §2.2, §5.
- **C-5** — index set marked provisional/revisitable post-SDD. §7.
- **C-6** — distilled-node provenance source-record ref = external telemetry ref (M-1 origin-class). §2.3.

**Ledger this cycle:** R26 (B-4), R27 (B-1). **Linear this cycle:** RBT-39 (filed, blocks RBT-13), RBT-40 (filed), RBT-41 (filed), RBT-33 (broadened + High + sequenced ahead of RBT-15); RBT-14/RBT-15/RBT-17 annotated with incoming forward-deps.
