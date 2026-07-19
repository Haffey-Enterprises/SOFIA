# DDR-002 Graph Schema — Ratified Design Substrate (v0.4)

**Status:** Ratified design substrate (pre-authoring). Not the DDR itself.
**Carrier:** RBT-13 (DDR-002 Graph Schema) — the R8 schema half.
**Authoring route:** Claude Code authors `docs/ddr/DDR-002-graph-schema.md` from this substrate via the `author-decision-record` skill (DIRECTIVE-026); claude.ai designs/authors, Code executes git.
**Source:** claude.ai RBT-13 pre-authoring design session, 2026-06-19 / 2026-06-20 — ratified section by section, one ratification per turn.
**Authoring postures:** single-artifact per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED, single original-authoring Change Log row); reference flows architecture → schema only (R8), DDR-001 not re-opened. Author DDR-002 with the current identity string *Executive Architect, Haffey Enterprises LLC* (per RBT-36).

> **Substrate version vs. DDR version (R18 / M-17).** "v0.3" is the *substrate session-process* version — the design-cycle revision of this pre-authoring artifact. It is **not** the DDR version. The authored DDR-002 carries the single-artifact lifecycle `0.1.0` PROPOSED → `1.0.0` ACCEPTED with **one** original-authoring Change Log row. The v0.x history and the fold-log below live in the substrate **only** and never appear in the DDR.

**Revision (v0.2, 2026-06-19):** Pass-1 three-hat findings folded — M-1 (five-core-+-Extension framing), M-2 (§9→§8 cross-refs), M-3 (ADR-002 §2.6 disambiguation), M-4 (§5 owns/cites delimiter), M-5 (provenance-scope reconciliation + RG-provenance posture), M-6 (R9 added to §0), C-1/C-2 (citation precision).

**Revision (v0.3, 2026-06-20):** Pass-2 three-hat (PASS, converging) + antagonistic Pass-1 + DDR-001 cross-check addendum dispositioned and folded. **Blockers:** B-4 (Operational↔DDR-001 contradiction → Model A, *serialize* behind DDR-001 v1.1.0 / RBT-39 / ledger R26); B-1 (RG-provenance enforceability → structural surrogate stands, exposure named, mechanized at RBT-33 / ledger R27); B-3 (Process dangling edges → pulled, deferred to RBT-40). **Structural forks (substrate-folds):** M-7 (Artifact = distinct third family), M-9 (exclusion-by-label dissolved → DDR-001 proposal-visibility invariant, gateway-enforced read-discipline), M-3 (Decision supertype + GateDecision/PromotionDecision subtypes; resolves C-1; gate-enum reconcile → RBT-41), M-10 (R6 positive half → name existing retrieval substrate, affordance → SDD). **Fold batch:** M-1, M-4, M-5ᴬ, M-6, M-8, M-12, M-15, M-16, M-17, C-2…C-6, C2-1, M2-1. Full disposition table in the fold-log appendix. The v0.2 M-5 RG-provenance posture, *flagged for confirmation*, is **confirmed** under B-1 (c). Ledger this cycle: **R26, R27**. Linear this cycle: **RBT-39** (DDR-001 amendment, blocks RBT-13), **RBT-40** (Process node + deferred edges), **RBT-41** (gate-enum reconcile), **RBT-33** broadened (DDR-002 CI-only set; raised to High; sequenced ahead of RBT-15).

**Revision (v0.4, 2026-06-20):** Pass-3 three-hat (PASS, 1 material) + heavyweight antagonistic Pass-1 (3 blocking / 14 material / 3 cosmetic) dispositioned via a guided cluster re-deliberation. **Clusters:** **A** (provenance & audit soundness — `Evidence` surrogate scoped to `Evidence`-only, `RejectedAlternative` re-typed authored, determinism boundary made explicit, atomic capture-unit, `provenance_summary` on durable `CandidatePromotion`); **B** (compliance-model coherence — hybrid obligation closure: entity-triggered traversal ∪ condition-triggered compute, validator-logic closure, `rule_definition` dependency manifest making M-12 enforceable); **C** (R24 uniformity — cost estimates as immutable basis-pinned as-of records + compute-on-read, bounded update-in-place distillation + terminal-state archival path); **D** (promotion/Decision model — retraction path, 1:many batch `DECIDED_ON`, `approved_conditional` conditional-scoped knowledge with reusable `Condition`, exactly-one-subtype invariant); **E** (provenance precision — `source_class` → `origin_mechanism` × `derivation_class`, structured `source_record_ref`, `recorded_at` vs domain-time). **Standalones:** A-9 (`ReasoningSession`→`Solution` 0..*), A-10 (Extension `property_schema` + `attaches_to`-exists), A-11 (M-8 re-point bounded by the point-in-time rebind assignment), A-13 (M-4 confidence node/edge governing rule), M3-1 (Artifact = node-family within the two-graph store + R8 cite). **Cosmetics:** C3-2 / C3-3 / A-18 / A-19 / A-20 folded. **Ledger:** **R27** amended (Cluster A), **R23** + **R26** clarified (Cluster C). **Forward-pointers routed:** RBT-22 (constraint-validator), RBT-25 (cost-actuals/variance), RBT-15/RBT-17 (condition-evaluation), RBT-14 (DDR-003 policy hand-offs). Full disposition in the v0.4 fold-log appendix.

---

## 0. Frame

DDR-002 fixes the **node / relationship / constraint / index contract** for the SOFIA graph system-of-record. It owns the schema; it does **not** own architecture (DDR-001), feedback-loop governance (DDR-003), or service realization (the SDDs). Where a concern is named here but owned elsewhere, it is routed in §8.

Two graphs in one Neo4j Enterprise instance (R3, R5): the **Knowledge Graph** (enterprise ground truth — **five core planes plus the Extension plane**) and the **Reasoning Graph** (captured reasoning), with first-class cross-graph traversal. Cost is realized as the *first Extension registration*, not a sixth core plane (R23). Beyond the KG planes, the **Reasoning Graph** is the second graph (§4); the **Artifact family** (produced deliverables, §5) is a node-family *within* the two-graph store — **neither a KG plane nor a third graph** (M-7, narrowed under M3-1; §5). Both are deliberately exempt from KG-plane labelling.

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

**Provenance (M-1 — origin-neutral group; E/A-7 two-axis).** Every **KG** node carries a provenance group — minimally `origin_mechanism` + `recorded_at` (and `source_record_ref` where applicable); DB-existence-constrained (§7). Provenance is split into **two orthogonal axes** (A-7): **`origin_mechanism`** (how the node entered — `ingested` external ground truth · `authored` human/SOFIA-authored · `promoted` materialized through the feedback-loop EA gate · `derived` produced by an internal process), always present and invariant-bearing; and **`derivation_class`** (the nature of the content — `primary` · `distilled` · `aggregated`), present where it carries information (`derived` nodes; `primary` on raw `ingested`/`authored`). This de-tangles the v0.3 conflation where `distilled` (`ObservedPattern`) and `computed` (`CapabilityCostEstimate`) each named a *process* **and** a *derived nature*: they become (`origin_mechanism: derived`, `derivation_class: distilled`) and (`origin_mechanism: derived`, `derivation_class: aggregated`), and both axes become independently queryable. **`source_record_ref` (A-17)** is the structured, durable reference to the originating external SoR — `{source_system_class, record_id}` (system named by *class* per DDR-001 line 43, not a vendor product), honoring R24 (the graph holds the reference, not the record): **required on `ingested`**, applicable as a source/stream ref on `derived`-from-external (e.g. a distilled `ObservedPattern` references its telemetry source), **N/A on `authored`/`promoted`** (provenance is internal lineage). **`recorded_at` (C3-1)** is the uniform system/record time (when the graph captured the node); domain timestamps (`decided_at`, `first_observed_at`/`last_observed_at`, `computed_at`, `generated_at`) are node-type-specific and never conflated with it. The `promoted` vs. `ingested` distinction — a **DDR-001 conformance-check #6 obligation** (promoted knowledge must be distinguishable from ingested) — is carried by `origin_mechanism`. RG and Artifact provenance differ (below; §4; §5).

**Provenance scope (M-7; Cluster A / A-α).** The provenance *existence constraint* (§7) scopes to: **KG nodes**, the **three authored RG types** (`ReasoningSession`, `ReasoningProgress`, and — re-typed under A-α — `RejectedAlternative`, carrying `origin_mechanism: authored`), and the **Artifact family** (§5). `RejectedAlternative` is re-typed as authored content because DDR-001 line 65 frames it as ASA-authored and the *primary feedback-loop input* — v0.3's provenance-less modeling left the highest-leverage promotion signal with the weakest provenance. **`Evidence` is the sole surrogate-only RG type:** its provenance is recovered structurally via `SOURCED_FROM` (the atomic capture-unit, §7), not a carried group (§4; R27 amendment 2026-06-20).

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

- **`(:Environment:DeployedService)`** — `deployed_service_id` (T1 PK) · `service_type` (T3) · `lifecycle_state` (T2, indexed) · `observed_at` (T2) · provenance (T1, `origin_mechanism: ingested` · `derivation_class: primary`, runtime/CMDB source class)
- **`(:Environment:DeploymentEnvironment)`** — `environment_id` (T1 PK) · `name` (T3) · `environment_class` (T2, indexed — production/staging/dev) · provenance (T1)
- **`(:Environment:ConfigurationItem)`** — `ci_id` (T1 PK) · `ci_type` (T2, indexed) · `name` (T3) · `observed_at` (T2) · provenance (T1)

*Plane signature:* freshness (`observed_at`) — runtime facts are less authoritative than catalog ground truth; this lets the RG weight environment evidence lower. *Lifecycle distinction:* `DeploymentEnvironment` is the **realized** runtime environment, distinct from a solution's design-time `target_environment` (§5, C-4). Environment is DDR-001-sanctioned CMDB-sourced ground truth (cross-check: not a contradiction — M-2 closed).

### 2.3 Operational — the track-record graph (POC-absent; durable distillation, not telemetry)

- **`(:Operational:ObservedPattern)`** — `observed_pattern_id` (T1 PK) · `polarity` (T2, indexed — `strength` / `weakness` / optional `neutral` *(M-15 contested)*) · `pattern_type` (T2, indexed) · `description` (T3) · `observation_window` (T3) · `confidence` (T2 — **lesson reliability**; see §4 canonical def; per-target observation certainty rides the `OBSERVED_IN` edge, §3) · `first_observed_at`/`last_observed_at` (T2) · `status` (T2, indexed — active/superseded/resolved) · provenance (T1, `origin_mechanism: derived` · `derivation_class: distilled`)

*Per R24 / R26 (B-4 — durable distillation, serialize).* The KG does **not** mirror transient SoR telemetry (ServiceNow/Datadog). It holds the durable distilled lesson — a recurring operational pattern, of **dual polarity** (a clean track record is as informative as a weakness). **No in-graph TTL.** Raw telemetry stays TTL-bounded in the **external** observability/AIOps SoR; it is not a KG plane and is not mirrored. **Bounded by distinctness (C-β / A-5).** Distillation is **update-in-place** — the *active* `ObservedPattern` set is bounded by the number of distinct durable lessons (each updated as evidence accrues via `first_observed_at`/`last_observed_at`/`confidence`), **not** a node-per-observation; the never-delete posture is qualified to *never silently delete*, with terminal-state (`resolved`/`superseded`) patterns archivable per **DDR-003** policy (R26 clarification 2026-06-20) — DDR-002 commits no concrete `archived` status, naming the archival path as a DDR-003 dependency. The distillation step (reading the SoR, generalizing patterns) writes `ObservedPattern` with `origin_mechanism: derived` / `derivation_class: distilled` and a `source_record_ref` to the external telemetry source (C-6 / A-17); the process itself (cadence, generalization criteria, ownership) → **DDR-003 / detection-promotion SDD** (RBT-14). Weakness/strength entry into the KG is **EA-gated** via the feedback loop (§5), not auto-ingested. *DDR-001 v1.1.0 (RBT-39) aligns the parent definition to this; DDR-002 authoring is serialized behind that landing (§0).*

### 2.4 Governance — the decision/audit graph (immutable append-only; references, not records)

**Decision supertype + subtypes (M-3 (iii); Cluster D).** A single shared decision *shape* with two subtype labels, so SDLC gates and the feedback-loop promotion gate share structure without being conflated. **Subtype integrity (A-16):** every `Decision` carries **exactly one** subtype label — never bare, never both — enforced as a CI-only invariant (§7; Neo4j cannot enforce label cardinality natively). The **approving-state set** (referenced by the promoted-origin invariant, §7) is `{approved, approved_conditional}`:

- **`(:Governance:Decision)`** *(supertype shape — never instantiated bare; every decision node also carries a subtype label)* — `decision_id` (T1 PK) · `decision` (T2, indexed — approved/approved_conditional/rejected) · `decided_at` (T2) · `approval_token_id` (T3) · provenance (T1). Decided-by via `(Actor)-[:APPROVED]->(Decision)`.
- **`(:Governance:Decision:GateDecision)`** *(SDLC gates — external-captured)* — adds `gate` (T2, indexed — SDLC gate discriminator; **placeholder `gate_0`/`gate_1`/`gate_2`, M-15 contested → reconcile to enterprise gate taxonomy, RBT-41**) · `origin` (T2 — `external_captured`/`self_issued`) · `source_class` (T2 — per-gate SoR, e.g. EAMS for design, ITSM for change/release) · `external_record_ref` (T3 — pointer to the authoritative external record) · `all_hard_constraints_passed` (T2) · `rejection_reason` (T3, conditional). `DECIDED_ON` → **Solution** (§5).
- **`(:Governance:Decision:PromotionDecision)`** *(feedback-loop EA approval — SOFIA-issued)* — `origin` fixed `self_issued`; **no `external_record_ref`** (SOFIA is the issuer, not a capturer). `DECIDED_ON` → **CandidatePromotion** (§5), **1:many** (a single batch decision may decide multiple candidates — D-2; the per-candidate outcome lives on `CandidatePromotion.status`, so one decision can approve some, reject others, and conditionally-approve others — the node records the decision *act*, not a monolithic outcome). Batch-eligibility *policy* → DDR-003. **Retraction (D-1):** un-promoting a previously-promoted node is itself a `PromotionDecision` (a reversing decision) transitioning the node to `retracted` — excluded-by-label from active traversal, never hard-deleted, distinct from `superseded`; a retracted node traces to **both** its original approving decision and its retracting decision (§5/§6).

- **`(:Governance:Actor)`** — `actor_id` (T1 PK) · `actor_type` (T2, indexed — `human` / `system`) · `name` (T3) · provenance (T1)
- **`(:Governance:Role)`** — `role_id` (T1 PK) · `name` (T3) · provenance (T1)
- **`(:Governance:Attestation)`** — `attestation_id` (T1 PK) · `result` (T2, indexed — pass/fail) · `attested_at` (T2) · provenance (T1) *(closes obligation↔satisfaction, §3)*
- **`(:Governance:Condition)`** *(D-3 — applicability predicate for `approved_conditional` promotions)* — `condition_id` (T1 PK) · `predicate` (T2 — structured, evaluable predicate over solution/Catalog properties; pattern-aligned with `rule_definition`, carrying a declared dependency manifest) · `created_at` (T2) · provenance (T1). Linked from its `PromotionDecision` (`HAS_CONDITION`) and governs the conditionally-promoted node's applicability **by traversal** (R25 — not duplicated onto the node). The knowledge is promoted *with* this condition (not held pre-promotion); the **consumption-time invariant** — conditionally-promoted knowledge is usable only by a context that satisfies the predicate — is evaluated at retrieval (§7; RBT-15/17), which is what lets the same knowledge be reused across any qualifying solution. Condition vocabulary + lifecycle *policy* → DDR-003.

*Key postures:* for `GateDecision`, the external entity is **always** the system of record; the node is a **captured/issued reference**, not SOFIA's authoritative record (`origin` + `external_record_ref` carry inbound-capture vs. self-issue-then-transmit). For `PromotionDecision`, SOFIA *is* the issuing authority over the feedback loop, so there is no external record to point at — the de-conflation (M-3) keeps the SDLC-gate semantics from leaking onto the promotion gate and vice-versa. `Actor` generalizes the POC's "User" so any decider — human, SOFIA, or another external system — has a structural home. The per-action **disposition-event stream is excluded** (transient → orchestration/observability SoR, per R24). `Actor`/`Role` are governance-participating identities, **not** an IAM mirror. Immutable append-only: a re-decision is a new node.

### 2.5 Standards — the governance-of-knowledge graph (versioned + change-impact)

- **`(:Standards:Standard)`** — `standard_id` (T1 PK) · `version` (T1) · `name` (T3) · `authority` (T3) · `status` (T2) · provenance (T1) *(the referenceable authority — "per policy 1234")*
- **`(:Standards:PolicyRule)`** — `policy_rule_id` (T1 PK) · `version` (T1) · `rule_name` (T3) · `domain` (T2, indexed) · `status` (T2, indexed, versioned) · `superseded_by` (T2) · `enforcement_level` (T2 — hard/soft) · `enforced_at_gate` (T2) · `statement` (T3 — natural-language requirement) · `rule_definition` (T3 — opaque declarative IF/THEN evaluation logic, the validator consumes it; the graph never traverses into it) · `dependency_manifest` (T2 — declared, introspectable list of the Catalog entity-types/labels the rule reads; the evaluation logic stays opaque, the manifest does not — B-β) · provenance (T1)
- **`(:Standards:ComplianceControl)`** — `control_id` (T1 PK) · `framework` (T2, indexed — HIPAA/SOC2/PCI as *data*) · `control_ref` (T3) · `control_name` (T3) · provenance (T1)

*Decision (option C):* the executable rule logic rides the `PolicyRule` node as opaque `rule_definition` (KG-as-policy-SoR, matching DDR-001's served-from-graph model); the constraint-validator evaluates it. **`rule_definition`↔edge sync invariant (M-12, made enforceable under B-β):** every Catalog entity-type in a rule's declared `dependency_manifest` MUST appear as a `GOVERNED_BY` / `MANDATES` target for that rule — the opaque evaluation logic may not hide a dependency the graph can't see, and because the manifest is introspectable the invariant is now mechanically checkable (no longer advisory). Documented invariant + conformance check (§7). **`GOVERNED_BY`'s role (B-α):** the stored, traversable record of *entity-triggered* applicability (a standing Catalog fact — any solution using this entity inherits this rule), keeping governance graph-queryable; the obligation-closure mechanism (entity-triggered traversal ∪ condition-triggered compute, with validator-logic closure) lives in §3. A standard is broader than rules — it can `DEFINE` a `PolicyRule`, `PRESCRIBE` a `Technology`/`Pattern`, etc. **The `Process` node type and its edges are deferred (B-3 → RBT-40)**; `PRESCRIBES` keeps its non-Process targets and loses the Process target until Process lands. Mandates resolve in two ways: **structurally** (validator reads the solution graph — prohibitions, "uses the vault") or **by attestation** (process performed / evidence produced — `Attestation`, §2.4).

### 2.6 Extension mechanism + cost plane (the R23 exemplar — first Extension registration)

**Mechanism:**
- **`(:Extension:PlaneDefinition)`** — `plane_id` (T1 PK) · `plane_name` (T3) · `version` (T1) · `status` (T2, indexed) · `attaches_to` (T2 — list of core labels the plane may enrich) · `property_schema` (T2 — **structured, validator-consumable** schema descriptor: node-label → property → type/constraints, which schema-on-write enforces — A-10, no longer opaque) · provenance (T1)

The registry is self-describing (query `PlaneDefinition` nodes to enumerate registered planes). `attaches_to` and `property_schema` are **declarations** (properties), not edges-to-labels — a simplification of the POC's edge-modeled `DEFINES`/`ATTACHES_TO`. Schema-on-write validates extension nodes against their `PlaneDefinition`; instance-edges are bounded to the `attaches_to` labels. Extension nodes carry the plane's secondary label (the hybrid, §1). **`attaches_to`-exists invariant (A-10):** every label in a `PlaneDefinition.attaches_to` must reference an existing core label (CI-only, §7). The cost plane below is the **worked validation exemplar** — standing it up exercises the registration path end-to-end, so the Extension mechanism is *tested by construction*, not merely asserted (the R23 first-registration benefit).

**Cost plane — first registration:** `PlaneDefinition{plane_id: "cost", attaches_to: [Capability, Technology]}`.
- **`(:Cost:RateCard)`** — `rate_card_id` (T1 PK) · `version` (T1) · `effective_from`/`effective_to` (T2) · `status` (T2, indexed) · `rates` (T3, unit→cost payload) · provenance (T1). *Never-deleted; superseded only.*
- **`(:Cost:CostFactor)`** — `cost_factor_id` (T1 PK) · `factor_scope` (T2, indexed — technology/capability) · `factor_type` (T2, indexed) · `amount`/`unit` (T3) · `version` (T1) · `status` (T2) · provenance (T1). *Reference input.*
- **`(:Cost:CapabilityCostEstimate)`** *(A-4.3 — immutable, basis-pinned, as-of-decision record; NOT a refreshable cache)* — `estimate_id` (T1 PK) · `aggregate_cost` (T2 — **derived at creation, then frozen**, never hand-set) · `rate_card_version_ref` / `cost_factor_version_ref` / `capability_version_ref` (T2 — the pinned as-of basis) · `confidence` (T2) · `computed_at` (T2 — the as-of timestamp) · `decision_ref` (T2 — the option/decision this estimate informed) · provenance (T1, `origin_mechanism: derived` · `derivation_class: aggregated`). **Append-only and immutable; never claims currency** — current/hypothetical cost is **compute-on-read** (Tier-1/2 traversal + DTO, RBT-25). Persisted for decision-traceability (which option's cost drove a choice, immutably as-of) and estimate-vs-actual variance (the actuals side is external/Environment — RBT-25). R23 clarification 2026-06-20.

*Collapses from DDR-040's six types:* `CostPlaneDefinition` → the generic `PlaneDefinition`; `CapabilityCostFactor` + `TechnologyCostFactor` → one `CostFactor` (`factor_scope`); derived line-items → `HAS_COST_FACTOR` edges (not duplicated nodes); `CostFactorDefinition` → the `factor_type` enum. Cost is the first temporally-mixed plane: `RateCard`/`CostFactor` versioned reference, `CapabilityCostEstimate` an **immutable as-of-decision record** (A-4.3 — not refreshable; current cost compute-on-read). Tier-1/2 traversal + the `Tier1CostEstimateResult` DTO → RBT-25.

---

## 3. KG relationships — edge grammar + catalog

**Edge grammar:**
- **Direction & naming** — `SCREAMING_SNAKE` verb phrases in the natural semantic direction; Neo4j traverses both ways, so direction is for readability, not access. One edge per relationship — no redundant inverses.
- **Edge properties** — attributes belonging to the *relationship*, not either node.
- **Edge provenance** — asserted-fact edges (ingested, e.g. `APPROVED_OPTION_FOR`) carry provenance (`origin_mechanism`, §1); structural edges do not.
- **Re-bind discipline (M-8; bounded under A-11)** — each edge *type* declares a supersession behavior, **governed by the point-in-time principle**: edges that record a *point-in-time fact* (a solution's use of a version, evidence citations, decision references) are **`rebind:pinned`** — they never re-point, because re-pointing would falsify the historical record; edges expressing a standing *current* pointer (current-recommended, selection-preference) are **`rebind:current`** — they re-point to the new version on supersession so the hot path stays current. Because every potentially-unbounded edge is pinned by correctness necessity, the `rebind:current` re-point set is **bounded-degree by construction** (A-11); the residual — any `rebind:current` type that proved unbounded — would fall back to identity-indirection for that type (not adopted now). Declared per edge type in the catalog below.
- **Cardinality** — not constrainable in Neo4j schema → documented invariant + conformance check.
- **Temporal edges** — relationships whose *validity* is time-bound carry `effective_from`/`effective_to` + `status`; structural edges do not.
- **Confidence (M-4; governing rule under A-13)** — confidence lives **on the surface whose certainty it describes**: *edge* confidence = certainty of an observed relationship (Environment as-running edges; the Operational `OBSERVED_IN` per-target certainty); *node* confidence = reliability of a derived/reasoned thing (`ObservedPattern` lesson reliability, `CapabilityCostEstimate`, `ReasoningProgress`, `Evidence`). KG *structural* edges are authoritative by default (no confidence). Canonical definition + per-surface composition rule in §4.

**Edge catalog (five core-plane sub-graphs + Cost/Extension):**

*Selection (Catalog) — `rebind:current`:* `(Pattern)-[:REQUIRES_CAPABILITY {required, tier_conditional, tier_threshold}]->(Capability)` · `(Technology)-[:APPROVED_OPTION_FOR {conditional, justification}]->(Capability)` *(temporal)* · `(Pattern)-[:PREFERRED_OVER]->(Pattern)` · `(Technology)-[:REPLACED_BY]->(Technology)` *(temporal)* · `(IacTemplate)-[:IMPLEMENTS]->(Pattern)`

*As-running (Environment, confidence-bearing):* `(DeployedService)-[:RUNS {confidence}]->(Technology)` · `(DeployedService)-[:DEPLOYED_IN {confidence}]->(DeploymentEnvironment)` · `(DeployedService)-[:REALIZES {confidence}]->(Capability)` · `(ConfigurationItem)-[:PART_OF {confidence}]->(DeployedService)`

*Track-record (Operational):* `(ObservedPattern)-[:OBSERVED_IN {confidence}]->(Technology | Pattern | Capability | DeploymentEnvironment)` *(edge `confidence` = per-target observation certainty, distinct from the node's lesson-reliability `confidence` — composed at rollup, A-13)*

*Governance-of-knowledge (Standards):* `(Standard)-[:DEFINES]->(PolicyRule)` · `(Standard)-[:PRESCRIBES]->(Technology | Pattern)` *(Process target deferred → RBT-40)* · `(PolicyRule)-[:MAPS_TO]->(ComplianceControl)` · `(PolicyRule)-[:MANDATES]->(Technology)` · `(Pattern | Technology | Capability)-[:GOVERNED_BY]->(PolicyRule)` *(the stored, traversable record of **entity-triggered** applicability — any solution using this entity inherits this rule; B-α. Condition-triggered applicability is computed from `rule_definition`; the two combine in the obligation-closure model below.)*

*Decision/audit (Governance):* `(Actor)-[:HAS_ROLE]->(Role)` *(temporal)* · `(Actor)-[:APPROVED {role, approved_at}]->(Decision)` *(targets either subtype via the supertype, M-3)* · `(GateDecision)-[:REVIEWED {hash}]->(Artifact)` · `(Attestation)-[:SATISFIES]->(PolicyRule)` · `(Attestation)-[:BY]->(Actor)` · `(Attestation)-[:EVIDENCED_BY]->(Artifact)`. *(`(Attestation)-[:FOR_PROCESS]->(Process)` deferred entirely → RBT-40.)*

*Cost (Extension):* `(CapabilityCostEstimate)-[:FOR_CAPABILITY]->(Capability)` *(cardinality 1)* · `(CapabilityCostEstimate)-[:HAS_COST_FACTOR]->(CostFactor)` · `(CostFactor)-[:FOR_TECHNOLOGY]->(Technology)` · `(CapabilityCostEstimate)-[:PRICED_BY]->(RateCard)` *(`rebind:pinned`)*

*Solution-centric and promotion edges are deferred to the keystone (§5).*

**Obligation↔satisfaction model (B-α hybrid).** Standards hold the *obligation*; Governance holds the *attestation*; the solution sits in the middle. The **validator computes the obligation set** — *entity-triggered* obligations reached by traversing `GOVERNED_BY`/`MANDATES` from the solution's `USES`/`FOLLOWS` entities, **plus** *condition-triggered* obligations from evaluating `rule_definition` conditions against the solution — then joins each obligation to its satisfaction: validator-structural (prohibitions, structural requirements) or attestation-evidenced (`Attestation`). The **closure is validator logic, not a single graph traversal** (the graph stores the associations, the rule logic, and the attestations). A missing satisfaction surfaces as a compliance gap (an RG risk inference), not silence. Closure logic + manifest consumption → constraint-validator (RBT-22).

---

## 4. The Reasoning Graph — node schemas

**Label reconciliation** (align to ADR-002 §2.6 / ADR-001 §2.2 vocabulary, retiring POC names): `Inference` → `ReasoningProgress`; `Hypothesis` → `RejectedAlternative`; `Evidence` and `ReasoningSession` kept. Per **ADR-002 §2.6**, the rich `ReasoningProgress` *fields* are SDD-level; DDR-002 owns only the schema contract. RG nodes carry **no KG plane label** (M-7, §1).

- **`(:Reasoning:ReasoningSession)`** — `session_id` (T1 PK) · `lifecycle_state` (T2 — **AOE-owned; value-set deferred to the AOE SDD, RBT-16, with a named placeholder; DDR-001 likewise leaves it unspecified — M-5ᴬ**) · `created_at` (T2) · provenance (T1). *(No 1:1 `solution_ref` — the session→solution link is the `PRODUCED` edge (§5), now **0..\***: a session may explore multiple candidate solutions or conclude none — A-9. Consistent with DDR-001 line 62, which pins one session per run, not one solution per session.)*
- **`(:Reasoning:ReasoningProgress)`** — `progress_id` (T1 PK) · `conclusion_type` (T2, indexed — PatternMatch / TechnologySelection / GapConclusion / OverrideFlag / RiskSignal / ComplianceEvaluation; **M-15 contested; M-6 reconciliation below**) · `confidence` (T2) · `overridden_by_human` (T2) · `created_at` (T2) · provenance (T1). *= the typed conclusion (lean reading: no separate container). Rich conclusion/rationale → SDD.*
- **`(:Reasoning:Evidence)`** — `evidence_id` (T1 PK) · `fact_summary` (T2 — denormalized snapshot) · `confidence` (T2, inherited) · `weight` (T2) · `source_node_version` (T2 — version pin) · `observed_at` (T2)
- **`(:Reasoning:RejectedAlternative)`** — `rejected_id` (T1 PK) · `candidate_type` (T2, indexed) · `rejection_reason` (T3) · `score_delta` (T2) · `human_accepted` (T2) · `human_accepted_at` (T2) · provenance (T1, `origin_mechanism: authored` — re-typed under A-α; §1)

**Confidence — canonical definition (M-4; governing rule under A-13).** Confidence is a `[0.0, 1.0]` scalar living **on the surface whose certainty it describes**: **node** confidence = reliability of a derived/reasoned thing — on `Evidence` *source authority × freshness* (authoritative Catalog above aging Environment, decayed by `observed_at`), on `ObservedPattern` the *lesson reliability*, on `CapabilityCostEstimate` the estimate reliability, on `ReasoningProgress` the *rolled-up conclusion*; **edge** confidence = certainty of an observed relationship — Environment as-running edges, and `OBSERVED_IN` *per-target observation certainty*. The v0.3 def mis-lumped "Environment/Operational KG edge confidence" — corrected here: **Environment = edge-only; Operational = node (lesson reliability) + edge (per-target certainty)**, the two composed at rollup. **Inheritance/rollup rule:** `Evidence.confidence` inherits from the `SOURCED_FROM` KG node's authority class at snapshot time; `ReasoningProgress.confidence` is a (SDD-defined) rollup over its `SUPPORTED_BY` Evidence — DDR-002 fixes that the rollup exists and is monotone (a conclusion is no more confident than its strongest evidence path), the function itself → SDD.

**conclusion_type ↔ correction-surface ↔ DDR-001 reconciliation (M-6).** The six `conclusion_type` values are the *typed-conclusion* enum. They map onto the seven correction-surfaces of §5 (technology, pattern, capability, integration, risk, compliance, cost) — `integration` and `cost` surface as `TechnologySelection`/`GapConclusion` variants rather than distinct conclusion types — and align with DDR-001's signal/action classes (no contradiction: DDR-001's classes are coarser). The enum is confirmed aligned; the mapping table is authored into the DDR so the three vocabularies are reconciled in one place. *(C3-3: this is the documented 7-correction-surface → 6-conclusion-type mapping; the enum itself remains M-15-contested pending the spike-generalization pass.)*

*Write authority (**ADR-002 §2.6** invariant):* ASA authors `ReasoningProgress`; AOE owns `ReasoningSession` lifecycle only; writes route via knowledge-service. Mechanization → RBT-33.
*RG-internal edges:* `(ReasoningSession)-[:CONTAINS]->(ReasoningProgress)` · `(ReasoningProgress)-[:SUPPORTED_BY]->(Evidence)` · `(ReasoningProgress)-[:REJECTED]->(RejectedAlternative)` · `(ReasoningProgress)-[:LED_TO]->(ReasoningProgress)`.
*Point-in-time fidelity:* `fact_summary` + `source_node_version` make the audit trail immune to later KG drift.

**RG provenance posture (M-5 — confirmed under B-1 (c)).** Provenance is present across the RG, but expressed by node kind:
- `ReasoningSession` and `ReasoningProgress` are *authored reasoning state* → they carry the provenance group (provenance = the authoring session/agent, ASA per §2.6).
- `RejectedAlternative` is **re-typed as authored content (A-α)** → it now carries the provenance group (`origin_mechanism: authored`), because DDR-001 line 65 frames it as ASA-authored and the *primary feedback-loop input*; v0.3's provenance-less modeling left the highest-leverage promotion signal with the weakest provenance.
- `Evidence` is the **sole** *derived* RG type that omits the group; its provenance is **structural** — it pins `source_node_version` + `observed_at` and links `SOURCED_FROM` the authoritative KG node it snapshots (§5), written as an **atomic capture-unit** (`Evidence` + `SOURCED_FROM` in one gateway transaction, §7) so the surrogate is sound by construction.

So the provenance *existence constraint* (§7) scopes to **KG nodes + the three authored RG types (`ReasoningSession`, `ReasoningProgress`, `RejectedAlternative`) + the Artifact family** (M-7; A-α); `Evidence` is the **sole** surrogate-only type. **The surrogate's enforceability gap is named, not hidden (B-1 / R27):** the cardinality invariants that *make* the `Evidence` surrogate sound — including the **atomic capture-unit** (`Evidence` + `SOURCED_FROM` written in one gateway transaction) — are CI-only (§7); Neo4j cannot express them as constraints, so they are documented and mechanized at RBT-33, sequenced ahead of RBT-15 so the gateway is built against an enforced contract. **Determinism boundary (A-6):** RG content is captured *judgment*, not held to the KG determinism invariant; the EA gate (`PromotionDecision`) is the determinism-restoring control that converts a judgment-derived proposal into a human-ratified fact — so a promoted-origin KG node must trace to an **approving** `PromotionDecision` (§7). *(v0.2 flagged this posture for confirmation; ratified under B-1 (c) and refined under Cluster A — the `Evidence` surrogate stands, the exposure is named.)*

---

## 5. Cross-graph linkage + the feedback loop

**Ownership line (R8 / R22) — what DDR-002 owns vs. cites in this section.** DDR-002 **owns** the *schema contract*: the `(:Artifact:Solution)` and `CandidatePromotion` node shapes, the cross-graph and promotion edge grammar, and the *structural* invariants (append-only terminal status, provenance-chain traceability). DDR-002 **cites, and does not re-author:** the promotion *mechanics / data-path* → DDR-001; the *diagnosis policy / EA approval criteria / thresholds / cadence* → DDR-003 (RBT-14); the *workflow* → SDD. The Refine/Request-new/Correct-scope framing and the "EA-gate is a diagnosis" characterization below are stated for schema motivation only — their governance is DDR-003's, their data-path is DDR-001's.

**The Artifact family (M-7, narrowed under M3-1 — a node-family within the two-graph store).** `(:Artifact …)` is a **distinct node-family**, *not* a third graph or third citizen-class peer to the KG and RG: the store is the two-graph model (KG + RG, R8 / DDR-001), and Artifacts are nodes *within* it that bridge produced deliverables to the reasoning that made them and the catalog they draw on. It is **neither a KG plane nor RG** — the produced-deliverable family (solutions, BCDR plans, build sheets). It carries its own PK, its own provenance group (`origin_mechanism: authored`/`derived`), and its own uniqueness, and it carries **no KG plane label** (so plane-scoped ground-truth traversals skip produced artifacts). It joins KG and RG only by edges. This resolves the v0.2 ambiguity about whether `Solution` was a Catalog node or an RG node: it is **neither** — it is an Artifact node-family member (R8 governs the produced-solution treatment; DDR-001 lines 81/87/102/105).

**Evidence edges (RG → KG):** `(Evidence)-[:SOURCED_FROM]->(KG node)` *(`rebind:pinned`; confidence inherits here — authoritative Catalog scores above aging Environment)* · `(RejectedAlternative)-[:WOULD_HAVE_USED]->(KG node)`. *(`DREW_FROM`/`TRAVERSED` deferred — the considered-set is reconstructable from Evidence + RejectedAlternative.)*

**The Solution keystone:**
- **`(:Artifact:Solution)`** — `artifact_id` (T1 PK) · `artifact_type` (T2 — `solution`) · `version` (T1) · `lifecycle_state` (T2, indexed — FSM: proposed→architected→gated→approved→operational) · `content_hash` (T2 — tamper-detection) · `snapshot_ref` (T2 — dual-home pointer) · `target_environment` (T2 — design-time intent, drawn from the `environment_class` controlled vocabulary — A-18) · `created_at` (T2) · provenance (T1, `origin_mechanism: authored`). `(:Artifact)` is the general produced-deliverable family (solutions, BCDR plans, build sheets).

*Bridge edges:* `(ReasoningSession)-[:PRODUCED]->(Solution)` *(**0..\*** — a session may produce multiple candidate options or none; A-9)* · `(Solution)-[:USES]->(Technology)` · `(Solution)-[:FOLLOWS]->(Pattern)` · `(GateDecision)-[:DECIDED_ON]->(Solution)` · `(Solution)-[:HAS_ARTIFACT]->(Artifact)` *(Solution → component sub-artifacts, M-7)*. `target_environment` is a **controlled-vocabulary string** (the `environment_class` value-set — A-18) resolved by string-match, **not** an FK-edge to `DeploymentEnvironment` (C-4); the realized environment arrives later via `DeployedService`. Dual-home mechanics → §6.

**CandidatePromotion + feedback loop (R22)** — *schema contract owned here; mechanics cited to DDR-001 per the ownership line above:*
- **`(:Reasoning:CandidatePromotion)`** — `candidate_id` (T1 PK) · `promotion_type` (T2, indexed) · `proposed_change` (T3 — opaque) · `requested_item` (T3) + `requested_item_kind` (T2 — technology/pattern/capability/integration) + `target_ref` (T3) *(for request-new gaps)* · `basis_strength` (T2 — *M-15 contested*) · `confidence` (T2) · `status` (T2, indexed — proposed / under_review / approved / **approved_conditional** / rejected / promoted / **retracted**) · `provenance_summary` (T2 — on a durable terminal-`promoted` candidate: denormalized originating-fact refs + `source_node_version` pins + `Evidence.fact_summary` snapshots + any override basis; A-2) · `created_at` (T2) · provenance (T1). **Append-only**; terminal `status` (`promoted` / `rejected {reason}` / `retracted`) is the durable evaluation outcome — declines are explainable and gaps don't re-surface. A terminal-`promoted` candidate is **durable (expiry-exempt)** so the `provenance_summary` preserves a promoted node's traceability after its `Evidence` expires (A-2; §6). A single `PromotionDecision` may decide this candidate as part of a **batch** (1:many `DECIDED_ON`, D-2); `approved_conditional` carries an applicability `Condition` (§2.4, D-3).

*Promotion edges:* `(CandidatePromotion)-[:PROPOSED_FROM]->(ReasoningProgress | Evidence | ObservedPattern | RejectedAlternative)` · `(PromotionDecision)-[:DECIDED_ON]->(CandidatePromotion)` *(the feedback-loop EA gate — distinct subtype, M-3; **1:many** for batch decisions, D-2; no longer `GateDecision{gate: ea_promotion}`)* · `(PromotionDecision)-[:HAS_CONDITION]->(Condition)` *(for `approved_conditional`, D-3)* · `(CandidatePromotion)-[:PROMOTES_TO_KNOWLEDGE]->(KG node)` *(materialized node stamped `origin_mechanism: promoted`)*.

*Structural & read-discipline invariants:*
- **Proposal-visibility (M-9 — dissolved to DDR-001 + gateway).** `CandidatePromotion` must not appear in ground-truth synthesis traversals until EA-approved. This is **owned by DDR-001** as the proposal-visibility invariant + conformance check #4 (`SOFIA never self-modifies the KG`; promotions excluded from ground-truth traversal until approved). DDR-002 supplies the *structural aid* — `CandidatePromotion` carries no KG plane label, so plane-scoped traversals skip it — but names honestly that full enforcement is **gateway-enforced read-discipline** (the sole-owner knowledge-service scopes ground-truth reads), **not** a pure structural guarantee. Lands in the R27 CI-only set (§7); cites DDR-001 check #4, no DDR-001 amendment needed.
- **Provenance chain.** A promoted node traces back through `PROMOTES_TO_KNOWLEDGE` → `CandidatePromotion` → `PROPOSED_FROM` → `ReasoningProgress`/`Evidence`/`RejectedAlternative` → `SOURCED_FROM` → original facts; `origin_mechanism: promoted` makes it distinguishable from `ingested` (DDR-001 check #6, M-1). **Expiry survival (A-2):** when the originating `Evidence` expires, the chain is preserved by the `provenance_summary` materialized on the durable terminal-`promoted` `CandidatePromotion` (schematizing DDR-001's summary-on-evidence-expiry). **Approving-decision invariant (A-6):** a promoted node must trace to an **approving** `PromotionDecision` (outcome ∈ `{approved, approved_conditional}`) via `PROMOTES_TO_KNOWLEDGE` ← `CandidatePromotion` ← `DECIDED_ON` (CI-only, §7).

**Generalized correction mechanism** *(schema motivation; governance → DDR-003).* Every `conclusion_type` is a human-correction surface (technology, pattern, capability, integration, risk, compliance, cost — reconciled to the conclusion_type enum in §4, M-6), in three flavors: **Refine** (override to an existing option → context-scoped, evidence-backed preference signal on the selection edge, no pairwise cycles; the *runtime preference-landing* → solutioning SDD, RBT-17), **Request-new** (gap → human evaluation/onboarding; never auto-created), **Correct-scope** (false risk / mis-scoped rule → adjust existing ground truth). The capture machinery (`overridden_by_human`, `human_accepted`, `GapConclusion`, `RejectedAlternative`, `CandidatePromotion`, EA-gate, `PROMOTES_TO_KNOWLEDGE`) is general across surfaces. The "override is a signal the EA *diagnoses*" framing is governance characterization owned by DDR-003, not authored here.

---

## 6. Versioning & temporal model

**Per-posture spectrum** (each plane fit to its nature): Catalog/Standards/RateCard **version** (supersession), Environment **ages** (`observed_at`), Operational **distills** (status-managed), Governance **accretes** (immutable append-only), RG **pins** (point-in-time), Solutions/Artifacts **dual-home**.

**Supersession — Option A (scoped to versioned-ground-truth types: Catalog, Standards, RateCard, CostFactor, PlaneDefinition).** A node carries `version` + `effective_from`/`effective_to` + `status` + `superseded_by`; superseding creates a new retained node and marks the old superseded. **Atomicity (M-8; bounded under A-11):** supersession is a **single atomic transaction** — create new version node, mark old `superseded`, and re-point the `rebind:current` edges to the new node — so a traversal never observes a half-superseded state with two active versions. `rebind:pinned` audit/evidence/consumption edges are untouched (they pin to their specific version node). **The re-point is O(degree) but bounded by construction (A-11):** the point-in-time principle (§3) forces every potentially-unbounded edge (solution-consumption, evidence, decision-reference) to be `rebind:pinned`, so the `rebind:current` set is limited to standing current-pointer edges (low-degree); the assumption is stated, and the residual — any `rebind:current` type that proved unbounded — falls back to identity-indirection for that type (not adopted now). The edge re-pointing is the **gateway's** responsibility (knowledge-service, sole writer — consistent with DDR-001's gateway pattern, R8 boundary; cited, not re-authored). Never-delete via retained versions; as-of via effective-dating. Chosen over a blanket identity+version-node pattern to keep the selection-graph hot path hop-free (versioning is rare; traversal is constant).

**Version-pinning.** `Evidence.source_node_version` + `CapabilityCostEstimate`'s pinned basis (`rate_card_version_ref` / `cost_factor_version_ref` / `capability_version_ref`, A-4.3) reference specific retained version nodes (`rebind:pinned`); with `Evidence.fact_summary` that yields point-in-time fidelity. The immutable as-of cost record (A-4.3) is the cost-plane instance of this point-in-time discipline.

**Durable promotion records (A-2).** A terminal-`promoted` `CandidatePromotion` is **expiry-exempt** (durable) and carries a `provenance_summary` (§5) — so when bounded RG retention expires the originating `Evidence`, a promoted node's traceability is preserved by the summary (schematizing DDR-001's summary-on-evidence-expiry, line 89). The materialization process + retention policy → DDR-003 (RBT-14).

**Dual-home (Artifact/Solution).** The graph node holds metadata, edges, `content_hash`, `snapshot_ref`; immutable content lives in the external snapshot store (Firestore per R9, routed to DDR-001); the hash is tamper-detection (snapshot hash must match `content_hash`). A new version is a new node + new snapshot; the old pair is retained.

**Uniqueness under versioning.** PKs unique on `(business_key, version)`; "exactly one active version per business_key" is a documented invariant + conformance check.

---

## 7. Constraints, indexes & conformance

**DB-enforced (Neo4j Enterprise) — generating rules:**
- **Uniqueness** on every PK; `(business_key, version)` for the versioned-ground-truth types.
- **Existence constraints** on the provenance group (`origin_mechanism`, `recorded_at`) on every **KG** node, the **three authored RG types** (`ReasoningSession`, `ReasoningProgress`, `RejectedAlternative` — A-α), and the **Artifact family** (M-7) — see §4 for the RG-provenance posture — plus each node's T1 required props. (The Enterprise *edition* committed in ADR-002 — edition per **R3** — buys existence-constraint capability.)
- **Indexes** on the flagged T2 traversal/filter properties only (lean — no speculative indexing); plane secondary-labels are inherently indexed. *The index set is **provisional**, revisitable once the SDDs surface real query patterns (C-5).* **Reverse cross-graph lookup (A-20):** `SOURCED_FROM` is stored RG→KG, so the reverse direction (KG-node → citing-`Evidence`, "what reasoning cited this fact?") needs an index/affordance — named here; the concrete index lands with the retrieval patterns in the knowledge-service SDD (RBT-15, C-5).

**Conformance-checked invariant set — CI-only (Neo4j cannot express → documented + CI; mechanization → RBT-33; enforcement posture per R27).** Neo4j existence/uniqueness constraints cannot express these; they are honestly named as CI-only with a stated exposure window (below), uniform under the R27 posture:

1. **RG-provenance edge invariants (B-1 / R27 — highest-priority RBT-33 member, sequenced ahead of RBT-15):** every `(:Reasoning:Evidence)` carries a **mandatory** `SOURCED_FROM` edge to a provenance-bearing KG node; every `(:Reasoning:RejectedAlternative)` is reached via **exactly one** parent `REJECTED` edge; `Evidence` **not** sourced from a provenance-bearing KG node is **prohibited** (or carries its own declared treatment). These cardinality invariants are what make the §4 structural provenance-surrogate sound (M2-1).
2. **no vector properties** (R6).
3. **relationship cardinality** (e.g. `FOR_CAPABILITY` cardinality 1).
4. **one active version per business_key.**
5. **aggregate-derivation** (`CapabilityCostEstimate.aggregate_cost` derived-at-creation-then-frozen, never hand-set — A-4.3).
6. **schema-on-write** (extension nodes validate vs. `PlaneDefinition`; edges bounded to `attaches_to`).
7. **ADR-002 §2.6 write-authority** (ASA authors `ReasoningProgress`; AOE session-lifecycle only).
8. **never-delete** (versioned types supersede; atomic re-bind bounded by the point-in-time rebind assignment — M-8 / A-11).
9. **proposal-visibility / read-discipline (M-9):** `CandidatePromotion` excluded from ground-truth synthesis traversal until EA-approved — gateway-enforced read-discipline + structural label-skip aid; defers to DDR-001 check #4.
10. **rule_definition↔edge sync (M-12, enforceable under B-β):** every Catalog entity-type in a rule's declared `dependency_manifest` appears as a `GOVERNED_BY`/`MANDATES` target for that rule.
11. **provenance distinguishability (DDR-001 check #6, M-1):** `promoted` distinguishable from `ingested` via `origin_mechanism` (E/A-7).
12. **tamper-detection** (`Artifact.content_hash` matches snapshot hash).
13. **no-PHI** (classification, gateway-enforced, R10).
14. **atomic capture-unit (A-1):** an `Evidence` node and its `SOURCED_FROM` edge are written in a single gateway transaction — the structural provenance surrogate is sound by construction at the sole-writer choke-point (joins #1; highest-priority RBT-33 member).
15. **promoted-origin → approving decision (A-6):** every `origin_mechanism: promoted` KG node traces, via `PROMOTES_TO_KNOWLEDGE` ← `CandidatePromotion` ← `DECIDED_ON`, to a `PromotionDecision` whose outcome ∈ `{approved, approved_conditional}`.
16. **exactly-one-subtype-per-Decision (A-16):** every `Decision` carries exactly one of `{GateDecision, PromotionDecision}` — never bare, never both.
17. **ingested ⇒ source_record_ref (A-17):** every `origin_mechanism: ingested` node carries a `source_record_ref`.
18. **attaches_to-exists (A-10):** every label in a `PlaneDefinition.attaches_to` references an existing core label.
19. **conditional-consumption (D-3):** conditionally-promoted knowledge (an `approved_conditional` node carrying a `Condition`) is admitted to a consuming context only if that context satisfies the condition predicate (retrieval-enforced; RBT-15/17).

**Named exposure window (R27).** Until RBT-33 mechanizes them, this CI-only set is review-enforced (three-hat / DDR-SDD-authoring time), not CI-enforced — an honest gap, tracked, not hidden. RG-provenance (#1) is the highest-priority member and is implemented **before** RBT-15 knowledge-service authoring begins, so the gateway is built against an enforced provenance contract.

---

## 8. Boundary routing & doc frame

**Boundary Routing Map** (named here, owned elsewhere):
- **→ DDR-001** (one-way, R8): plane-model architecture, Extension *architecture*, gateway pattern, three-store persistence (R9), feedback-loop *architecture* (data-path / promotion mechanics), proposal-visibility invariant + check #4 (M-9), provenance-distinguishability check #6 (M-1). **DDR-001 v1.1.0 (RBT-39, R26)** aligns the Operational-plane definition to durable distillation; **DDR-002 authoring serializes behind it** (B-4). Cited, never re-opened.
- **→ DDR-003 (RBT-14):** feedback-loop *governance* — EA authority, diagnosis policy, what-gets-promoted criteria, thresholds, cadence, retention/audit policy; **telemetry→`ObservedPattern` distillation process** (B-4); **CandidatePromotion authorship + EA-gate completion** (B-2/M-13); **v0.4 policy hand-offs** — `Condition` governance + the conditional→`promoted` transition (D-3), batch-promotion eligibility (D-2), terminal-state `ObservedPattern` archival (C-β/A-5, R26 clarification). *(RBT-14 annotated with these incoming forward-deps.)*
- **→ RBT-15 (knowledge-service SDD):** gateway write endpoints; enforcement of the invariants (derivation, never-delete + atomic re-bind, schema-on-write, classification, supersession edge re-pointing); **graph-native retrieval affordance** (R6 positive half / M-10 — query patterns, similarity-edge question); **conditional-knowledge retrieval-filtering** (admit `approved_conditional` nodes only where the consuming context satisfies the `Condition` — D-3); the **reverse cross-graph lookup index** (KG→citing-`Evidence` — A-20). *Built against the enforced RG-provenance contract — RBT-33 sequenced ahead. (RBT-15 annotated.)*
- **→ RBT-16 (AOE SDD):** `ReasoningSession.lifecycle_state` value-set (M-5ᴬ).
- **→ RBT-17 (solutioning-agent / ASA SDD):** selection-edge **preference-landing** runtime (Refine → `PREFERRED_OVER` re-weight/re-point, `rebind` behavior); retrieval consumption (M-10); **conditional-knowledge consumption** (respect the `Condition` when using `approved_conditional` knowledge — D-3); full `ReasoningProgress` fields (**ADR-002 §2.6**). *(RBT-17 annotated; consolidates the prior duplicate ASA-fields entry — C3-2.)*
- **→ RBT-22 (governance-state-manager SDD):** the **constraint-validator** — `rule_definition`/`dependency_manifest` evaluation, the obligation-closure logic (entity-triggered traversal ∪ condition-triggered compute, validator-logic closure — B-α), and the shared `Condition`-predicate evaluation. *Whether this warrants a dedicated constraint-validator SDD is deferred to RBT-22 authoring (DIRECTIVE-025).*
- **→ RBT-25 (cost-estimation SDD):** Tier-1/2 traversal, cost DTOs; **compute-on-read** current/hypothetical cost over the immutable as-of estimate records; **estimate-vs-actual variance** (consumes the basis-pinned records + an external/Environment actuals source — A-4.3, R23 clarification).
- **→ RBT-33:** mechanization of the CI-only conformance set (broadened to include DDR-002-native checks; RG-provenance highest-priority, sequenced ahead of RBT-15).
- **→ RBT-40 (Process node):** the `Process` node type + its deferred edges (`PRESCRIBES`→Process, `FOR_PROCESS`→Process) land when the Process use case is designed (B-3).
- **→ RBT-41 (gate-enum reconcile):** `GateDecision.gate` placeholder → enterprise SDLC gate taxonomy (M-3 carry / M-15).

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

**Landing posture:** with B-4 cleared by serialize before authoring and B-1/B-3 folded, DDR-002 authors as a single artifact (R18) `0.1.0` PROPOSED → `1.0.0` ACCEPTED, carrying the §7 #1 RG-provenance CI-exposure as a **named accepted risk** (R27) with RBT-33 tracked. The Pass-3 three-hat + antagonistic re-review (on v0.3) is **complete** — its 3 blocking / 14 material / 3 cosmetic findings are dispositioned and folded into this v0.4 (revision header; Appendix B). The remaining gate before authoring is unblocked is the **Pass-4 three-hat + re-antagonistic review on this v0.4**, alongside the RBT-39 serialize landing.

**Forward dependencies (filed / tracked):** RBT-12/DDR-001 (landed upstream — Done @ `15ff20f`, PR #12) → **RBT-39** (v1.1.0 amendment, **blocks RBT-13**); RBT-14/DDR-003 (governance + distillation + promotion-authorship — annotated); RBT-15/RBT-16/RBT-17/RBT-25 (SDDs this gates — RBT-15/17 annotated); **RBT-33** (CI-only mechanization, broadened + sequenced ahead of RBT-15); **RBT-40** (Process node + deferred edges); **RBT-41** (gate-enum reconcile). *(All forward-pointers from this cycle are filed or annotated — no "to-file-later" tail.)*

**Doc frame:** references DDR-001 (v1.1.0), ADR-001, ADR-002, and rulings R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25/R26/R27; single original-authoring Change Log row per R18 (`0.1.0` PROPOSED → `1.0.0` ACCEPTED); identity string *Executive Architect, Haffey Enterprises LLC*; lands at `docs/ddr/DDR-002-graph-schema.md`.

---

## Appendix A — ratification trace

Ratified section by section in the RBT-13 claude.ai design session (2026-06-19 / 2026-06-20), one ratification per turn: schema grammar & hybrid plane membership → Catalog → Environment (`DeploymentEnvironment` naming) → Operational (re-centered to dual-nature `ObservedPattern`, R24) → Governance (`GateDecision` as reference, `Actor` generalization) → Standards (`Standard` un-deferred, option-C `rule_definition`, obligation↔satisfaction / `Attestation`) → Extension mechanism → cost plane (R23) → edge grammar + catalog → RG nodes (label reconciliation) → cross-graph + Solution keystone → CandidatePromotion + feedback loop + generalized correction mechanism → versioning (Option A) → constraints/indexes/invariants → boundary routing + conscious exclusions. Ledger rulings written across the cycle: R23 (prior), R24, R25, **R26**, **R27**.

---

## Appendix B — fold-log (v0.3 and v0.4 design cycles)

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

---

### v0.4 fold-log (Pass-3 three-hat + antagonistic Pass-1 on v0.3 — 2026-06-20)

**Antagonistic blockers (3):**
- **A-1** structural-provenance surrogate unsound under async capture → **atomic capture-unit** (`Evidence` + `SOURCED_FROM` in one gateway transaction; CI #14, RBT-33). §1, §4, §7. *(Cluster A)*
- **A-2** evidence-expiry severs the owned provenance chain → **`provenance_summary`** on a durable (expiry-exempt) terminal-`promoted` `CandidatePromotion`, schematizing DDR-001 summary-on-evidence-expiry. §5, §6. *(Cluster A)*
- **A-3** obligation-closure self-contradiction (traverse vs computed) → **hybrid closure** (entity-triggered traversal ∪ condition-triggered compute; closure = validator logic). §2.5, §3. *(Cluster B)*

**Antagonistic material (14):**
- **A-4** cost cache served as ground truth (R24 anti-pattern) → cost estimates are **immutable, basis-pinned, as-of-decision records**; current/hypothetical = compute-on-read. §2.6, §6. R23 clarification. *(Cluster C)*
- **A-5** B-4 fix → unbounded Operational growth → **update-in-place distillation** (active set bounded by distinct lessons) + terminal-state archival path → DDR-003. §2.3. R26 clarification. *(Cluster C)*
- **A-6** promotion launders judgment into fact → **determinism boundary** stated explicitly + promoted-origin → approving-`PromotionDecision` invariant (CI #15). §4, §7. *(Cluster A)*
- **A-7** `source_class` conflates entry-mechanism × derivation-nature → split into **`origin_mechanism` × `derivation_class`**. §1, §2.x, §4. *(Cluster E)*
- **A-8** no promotion retraction path → **retraction = reversing `PromotionDecision`** → `retracted` state (excluded-by-label; distinct from `superseded`). §2.4, §5. *(Cluster D / D-1)*
- **A-9** `ReasoningSession`↔`Solution` 1:1 forecloses multi-option/no-solution → **`PRODUCED` 0..\***. §4, §5. *(standalone)*
- **A-10** Extension untested-by-construction → structured **`property_schema`** + **`attaches_to`-exists** invariant (CI #18) + cost-plane-as-worked-exemplar. §2.6, §7. *(standalone)*
- **A-11** supersession re-point O(degree) (re-opens **M-8**) → **point-in-time rebind assignment** bounds the `rebind:current` set by construction; residual → indirection fallback (not adopted). §3, §6. *(standalone)*
- **A-12** M-12 unenforceable → `rule_definition` **`dependency_manifest`** makes M-12 mechanically checkable (CI #10). §2.5, §7. *(Cluster B)*
- **A-13** Environment confidence node/edge (re-opens **M-4**) → **governing rule** (confidence on the surface whose certainty it describes); Operational = node (reliability) + edge (per-target). §3, §4. *(standalone)*
- **A-14** `RejectedAlternative` (primary feedback input) weakest provenance → **re-typed authored** (carries the group, `origin_mechanism: authored`). §1, §4. *(Cluster A)*
- **A-15** `PromotionDecision`↔`CandidatePromotion` 1:1 forecloses batch → **1:many `DECIDED_ON`**; per-candidate outcome on `CandidatePromotion.status`. §2.4, §5. *(Cluster D / D-2)*
- **A-16** Decision multi-label permits malformed nodes → **exactly-one-subtype** invariant (CI #16); `approved_conditional` representable. §2.4, §7. *(Cluster D / D-3)*
- **A-17** `source_record_ref` undefined → **structured `{source_system_class, record_id}`** + per-`origin_mechanism` applicability (CI #17). §1, §7. *(Cluster E)*

**Antagonistic cosmetic (3):**
- **A-18** `target_environment` unvalidated string → drawn from the `environment_class` controlled vocabulary (C-4 string-match preserved). §5.
- **A-19** cite RBT-36 only (RBT-37 is its Duplicate). Header.
- **A-20** reverse cross-graph lookup index named (KG→citing-`Evidence`). §7, → RBT-15.

**Pass-3 three-hat:**
- **M3-1** (material) Artifact "third citizen-family" overstates the Two-Graph Model → reframed **node-family within the two-graph store** + R8 cite; narrows **M-7**. §5.
- **C3-1** `recorded_at` vs domain timestamps → system/record-time vs node-type-specific convention. §1.
- **C3-2** RBT-17 listed twice in §8 → consolidated. §8.
- **C3-3** `conclusion_type` 7→6 mapping → documented; enum stays M-15-contested. §4.

**D-3 conditional-scoped knowledge (new capability):** `approved_conditional` promotes *with* a captured, reusable **`Condition`** (structured predicate, reached by traversal per R25); the consumption-time invariant (CI #19) admits it only to contexts satisfying the condition → reuse across qualifying solutions. §2.4, §5, §7.

**Ledger this cycle:** **R27** amended (Cluster A — surrogate narrowed to `Evidence`, `RejectedAlternative` grouped, determinism boundary, atomic-capture + approving-decision invariants); **R23** clarified (A-4 immutable as-of cost records); **R26** clarified (A-5 bounded distillation + archival). **Linear this cycle:** forward-pointers routed to **RBT-22** (constraint-validator), **RBT-25** (cost-actuals/variance), **RBT-15/RBT-17** (condition-evaluation), **RBT-14** (DDR-003 policy hand-offs) — **zero new tickets** (DIRECTIVE-025-clean). FP-1 (RBT-13 description ledger-line cite) tracked for the RBT-13 close.

**Prior forks re-evaluated (criterion-shift — all refined, not reversed):** M-8 (A-11), M-4 (A-13), M-7 (M3-1 narrows), M-12 (B-β makes enforceable).
