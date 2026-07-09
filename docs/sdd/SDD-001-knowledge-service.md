# File: docs/sdd/SDD-001-knowledge-service.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-03
# Description: SDD-001 — knowledge-service design. The sole-owner KG/RG graph gateway: the only holder of the Neo4j driver, sole executor of all graph writes as invariant-enforcing transactional operations, and sole read boundary enforcing the platform's read-discipline controls — the gateway executes everything and authors nothing.

# knowledge-service — Service Design Document

| Field | Value |
|---|---|
| **Document ID** | SDD-001 |
| **Service** | `knowledge-service` |
| **Version** | 1.0.0 |
| **Status** | ACCEPTED |
| **Date** | 2026-07-09 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — new service |
| **References** | ADR-001 v1.1.0; ADR-002 v1.1.0; DDR-001 v1.3.0; DDR-002 v1.2.0 |

---

## 1. Purpose

`knowledge-service` is the KG/RG graph gateway: the sole holder of the Neo4j driver and the single graph-access boundary (ADR-002 §2.5). Every graph read and write on the platform — Knowledge Graph, Reasoning Graph, and Artifact family — flows through its API. Its design is distinctive in one commitment: the API is **operation-shaped, not graph-shaped** — every write endpoint is one schema-defined transactional shape whose invariants are native to the operation, so the schema's safety-critical integrity properties hold by construction rather than by policing.

`knowledge-service` is the sole service authorised to:

- Hold a Neo4j driver and execute Cypher against the graph system of record.
- Execute all authoritative graph writes, as named transactional operations enforcing the DDR-002 §7 invariant set at write time.
- Serve all graph reads, with read-discipline enforcement (proposal-visibility, conditional admission, retracted-node exclusion) built into every ground-truth retrieval path. The audit/explainability operations (§3.3.7–§3.3.8) deliberately reach read-excluded nodes and are the disclosed exception (§3.2); no read path exists outside this service.
- Enforce the ingestion boundary: schema-on-write validation against `PlaneDefinition`, data-classification enforcement (no-PHI), and provenance stamping, regardless of caller.
- Execute the atomic supersession transaction (create / mark / re-point per DDR-002 §6), the promotion-materialization transaction (including the §5 provenance-closure computation), and the retraction transaction.

`knowledge-service` explicitly does **not**: author any graph state — it is the sole *executor* of every authoritative write and the *author* of none (ADR-002 §2.6); select, rank-and-recommend, or decide among retrieval candidates — it retrieves and annotates, and the selection judgment belongs to the reasoning components whose reasoning is captured (ADR-001 §2.2/§2.3); hold authoritative architecture or reasoning state in any local store (ADR-002 §5.2); hold a PostgreSQL or Firestore client; evaluate obligation closure; or write its own operational events into the graph.

## 2. Responsibilities

### 2.1 Owned

- **Write execution with native invariant enforcement** — every write operation in §3 executes as one transaction that enforces its DDR-002 §7 obligations per the §7.1 enforcement mapping: author validation, subtype integrity, classification, provenance stamping, flag↔category consistency, `decided_at` monotonicity, capture-unit atomicity, retraction gating, conditional-scope carry-forward.
- **Two-species write-authority enforcement** (ADR-002 §2.6): component-author validation on component-authored writes; governing-approving-decision verification, in-transaction, on decision-authorized materializations. No operation's authorship defaults to this service.
- **Read-discipline enforcement** — ground-truth retrieval structurally excludes un-approved `CandidatePromotion`s (DDR-002 §7 #9 / DDR-001 check 4), admits `applicability_state: conditional` nodes only where the consuming context satisfies their `Condition` (#19, fail-closed), and excludes nodes carrying an EA-approved inbound `RETRACTS` edge (DDR-002 §5).
- **In-process `Condition`-predicate evaluation** behind a predicate-evaluation port; evaluation *semantics* are the constraint-validator SDD's shared component, consumed here (see §4.2).
- **Catalog-eligibility evaluation as annotation** — tier / data-classification fit computed against the consuming context and disclosed on results; never an exclusion (see §3.2).
- **The uniform result envelope** — source-plane, provenance, confidence, version-pin, and applicability attribution on every retrieval result (DDR-001 gateway pattern).
- **Version-pin verification and inherited-confidence computation** on `Evidence` capture — the pin records the specific retained version the request cites (§3.4.3's input-to-pin contract); the confidence derivation realizing DDR-002 §4's inheritance rule is declared in §3.4.3 as an SDD-level determination and executed identically thereafter.
- **Supersession execution** — the single atomic transaction per DDR-002 §6, including the bounded `rebind:current` re-point and the #22 carry-forward gate, in both entry paths (ingestion at an existing business key; promotion at an existing business key).
- **Promotion-boundary execution** — proposal writes, decision recording under monotonicity, materialization with in-transaction provenance-closure computation and `ProvenanceSummary` construction, retraction application with immediate read-exclusion.
- **Ingestion-boundary enforcement** — schema-on-write, classification (#13), provenance stamping (#17), Extension-plane registration (#18) — enforced at this port regardless of the calling adapter.
- **Driver lifecycle and connection management** for the platform's only Neo4j client.

### 2.2 Not owned

- **Reasoning and selection** — the Architecture Solutioning Agent (ASA) authors reasoning content and makes selection judgments; this service supplies attributed candidate sets and structural facts only (→ solutioning-agent SDD).
- **`ReasoningSession` lifecycle semantics** — AOE owns the lifecycle and its `lifecycle_state` value-set (→ AOE SDD; value-set enforcement here is TODO pending that SDD — see §3.4.1).
- **`ReasoningProgress.confidence` rollup and the zero-evidence conclusion posture** — DDR-002 §4 routes the rollup function to the SDD of the component that authors conclusion confidence: the solutioning-agent SDD, not this gateway (sole executor, never author). An evidence-less `ReasoningProgress` is a legal capture state under DDR-001's non-blocking posture — permitted, ungated, and disclosed via §8's observability surface until the owning record rules (→ solutioning-agent SDD).
- **Feedback-loop detection and proposal generation** — the scheduled feedback-loop job authors `CandidatePromotion` proposals (→ detection-promotion SDD; gated by DDR-003).
- **Promotion governance** — EA approval criteria, thresholds, cadence, batch eligibility, remedy boundary (supersession vs retraction), retention windows, condition vocabulary (→ DDR-003, forthcoming).
- **KG-entry checkpoint posture and un-promotion authority** — the distillation-write checkpoint and the upstream authority for un-promotion are routed to the forthcoming KG-entry-governance ADR; this SDD cites that routing and answers neither question.
- **`Condition`-predicate evaluation semantics** — owned by the constraint-validator SDD as the shared predicate grammar/implementation; hosted in-process here (§4.2).
- **Obligation-closure logic** — validator logic per DDR-002 §3 (→ constraint-validator SDD); this service serves the graph half (obligation-context reads).
- **Solution snapshot storage and hash verification** — `content_hash` / `snapshot_ref` *presence* is enforced here at write; hash-vs-snapshot *verification* is a cross-store concern (→ snapshot-service SDD). This service holds no Firestore client.
- **Solution lifecycle-transition authority** — per-transition authors are assigned in the approval and governance-state-manager SDDs under ADR-002 §2.6 (routed by DDR-001); this service's verification contract for those transitions instantiates when they are assigned (§3.4.6).
- **`PromotionDecision` recording transport** — which component conveys the EA's approval act (→ EA-review-portal work / governance-state-manager SDD); the authoring authority is the human EA in every case.
- **`Attestation`, `Actor`, `Role` writes** — no upstream-assigned author exists; no operations are defined for them in this version. They land as additive API amendments with the governance-state-manager SDD that assigns their authorship.
- **Ingestion adapters and per-plane source authorship** — adapter decomposition and source-side authorship are the architecture-ingestion SDD's; this service owns the enforcing port, not the sources.
- **LLM access and prompt assembly** — no model client exists in this service.

## 3. API Contract

### 3.1 Health and readiness

- `GET /healthz` → `200 {status, service}` — liveness only.
- `GET /readyz` → `200` when ready; `503` otherwise. Readiness checks, ordered: (1) Neo4j connectivity and authentication — critical, fails readiness; (2) schema metadata loaded — the `PlaneDefinition` registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode: this service has exactly one backing store, and every operation requires it.

### 3.2 Contract conventions (all ports)

**Two-species write authority.** Every write operation belongs to one species, fixed per operation:

- *Species 1 — component-authored.* The request carries the authoring component's identity as a first-class field; the gateway validates it against the upstream-fixed assignment (§7's ADR-002 rows) and rejects mismatches with a typed error. Assignments enforced: ASA → reasoning content (`ReasoningProgress`, the `Evidence` capture-unit, `RejectedAlternative`) and `(:Artifact:Solution)` creation; AOE → `ReasoningSession` lifecycle only; the scheduled feedback-loop job → `CandidatePromotion` proposals. Species-1 validation is invocation authority at the request; nothing is stamped onto nodes whose schema carries no author field (`Evidence` is surrogate-only — its provenance is structural per DDR-002 §4).
- *Species 2 — decision-authorized.* The request carries a `decision_id`, never an author field; the gateway verifies **in-transaction** that the referenced `PromotionDecision`'s *governing* `DECIDED_ON` edge on the target (latest `decided_at`, per DDR-002 §2.4) carries an approving outcome, and executes only then. The calling component is transport. The request schema for Species-2 operations has no author field: authorship-by-gateway is unexpressible.

**Consuming-context payload.** Every ground-truth retrieval operation carries a consuming-context object: `environment_class` / tier and data classification of the consuming solution context, plus any fields declared by an applicable `Condition.dependency_manifest`. Required fields are determined introspectably from the manifests of conditions in scope; both applicability surfaces (§3.2, applicability block) evaluate against this one payload.

**Result envelope.** Every retrieval result carries: plane label(s) · `origin_mechanism` (+ `derivation_class` where present) · version + effective window · the version pin the result resolves to · confidence on the surface that carries it (node confidence, and edge confidences where the traversal composed them, per DDR-002 §3/§4 semantics) · an **applicability block** — Catalog-eligibility verdict with failing fields named (annotation, never exclusion) and conditional-admission status. Ground-truth responses additionally carry a **disclosure channel**: excluded-conditional entries as `{node_id, reason}` with **no content payload**, `reason ∈ {condition_unsatisfied, condition_unevaluable, multi_condition_scope_conflict}`. Un-approved proposals and retracted nodes are excluded without disclosure on ground-truth reads (they remain reachable to audit via the explainability operations, §3.3.7–§3.3.8).

**Error semantics.** Rejections are typed, one type per enforced invariant: `AUTHOR_VIOLATION`, `DECISION_NOT_APPROVING`, `MONOTONICITY_VIOLATION`, `SCOPE_DISPOSITION_MISSING`, `SCOPE_CONFLICT`, `SUBTYPE_VIOLATION`, `CLASSIFICATION_REJECTED`, `SCHEMA_VIOLATION`, `PROVENANCE_MISSING`, `SOURCE_REF_MISSING`, `FLAG_CATEGORY_MISMATCH`, `UNIQUENESS_CONFLICT`, `TARGET_NOT_FOUND`, `CONFIDENCE_UNDERIVABLE`. `SUBTYPE_VIOLATION` is retained as documented defense-in-depth — unreachable by design through the mediated write surface (§7.1). Identifier conventions follow DDR-002 §1 (`<entity>_id`, caller-supplied); uniqueness is DB-enforced, and a duplicate-key retry surfaces as `UNIQUENESS_CONFLICT` — write operations are safely retryable on transport failure.

**No raw access.** There is no Cypher passthrough, no generic node/relationship CRUD, and no plane-direct query surface in either direction. Every operation is a named contract realizing a documented traversal or transactional shape (DDR-001: uniform access; port-substitutability).

### 3.3 KG retrieval port (read-only)

All operations enforce the read-discipline trio and return the §3.2 envelope. The operation set is the **initial contract, provisional by declared design** — it is derived from the corpus's named consumers ahead of any synthesis run, and it evolves additively as consuming SDDs land; DDR-002's provisional-index-set revisit rides with it.

1. **`select-patterns`** — selection-web traversal (`REQUIRES_CAPABILITY` / `APPROVED_OPTION_FOR` / `PREFERRED_OVER` / `IMPLEMENTS`) from required capabilities; returns candidate patterns with technology options, taxonomy placement, and per-candidate applicability blocks.
2. **`resolve-technology`** — approved options for a capability under the consuming context; eligibility verdicts disclosed per option; no recommended pick is returned.
3. **`track-record-lookup`** — Operational-plane lookup for target entities; returns `ObservedPattern` lesson-reliability (node confidence) and `OBSERVED_IN` per-target certainty (edge confidence) as **uncomposed structural facts** on the envelope. DDR-002 §4 fixes that the two are composed at rollup and routes the rollup function to an SDD; the composition judgment travels with that routing (→ solutioning-agent SDD, §2.2) — composing here would author a reasoning weight this gateway holds no authority to fix.
4. **`obligation-context`** — `GOVERNED_BY` / `MANDATES` traversal from a solution's `USES` / `FOLLOWS` entity set, returning applicable `PolicyRule`s with `statement`, `rule_definition`, and `dependency_manifest` payloads. Closure is the constraint-validator's; this operation serves the graph half.
5. **`find-precedents`** — prior produced `(:Artifact:Solution)` retrieval by structural criteria (shared capability/pattern/technology linkage, `target_environment`, gate outcome), with gate-decision context. Deterministic traversal; no similarity scoring.
6. **`read-as-of`** — point-in-time resolution over versioned ground truth (effective-dating / retained versions per DDR-002 §6), including resolution of a supplied version pin.
7. **`citation-lookup`** — the reverse cross-graph affordance (KG node → citing `Evidence` → owning `ReasoningProgress` / session). Two modes: **per-version** (citations of this exact version) and **business-key-wide** (citations across the version chain). Pagination mandatory in both modes. Completeness contract, stated plainly: complete within the RG retention window; beyond it, provenance survives per-promotion via `provenance-of` (below), not per-cited-fact. No dedicated index is added: entry is by uniqueness-indexed PK and `SOURCED_FROM` is natively traversable in both directions; a filtered reverse pattern that native traversal cannot serve escalates to DDR-002's provisional-index revisit.
8. **`provenance-of`** — the provenance-survival retrieval affordance for a promoted node: traverses `PROMOTES_TO_KNOWLEDGE` to the `CandidatePromotion`, then its two parallel inbound edges per DDR-002 §5 — `MATERIALIZES_PROVENANCE_OF` (from the `ProvenanceSummary`) and `DECIDED_ON` (from the governing `PromotionDecision`). Returns the **frozen layer always** (the `ProvenanceSummary`'s ratified content — `frozen_fact_summaries` + `frozen_source_version_pins`, the guaranteed audit floor) plus the **live `Evidence` chain where it still exists**, entries marked live vs frozen-only (live/frozen correlation by version-pin match, pending the DDR-002 structuring amendment — §3.5.3 routing note). The contract is retention-agnostic by construction: it does not change under any DDR-003 retention policy. **Determination recorded (DDR-002 Named Gap, provenance-survival retrieval affordance):** the affordance warrants **no CI invariant of its own** — reachability of the frozen layer is exactly what §7 #20 already guarantees (existence, completeness, at-promotion binding), and the materialization transaction writes the whole chain atomically; a second invariant would re-verify #20 under another name. The read operation's frozen-fallback correctness is service test discipline (§6). Pruning the Named Gap's open question is a DDR-002 amendment, not performed here.
9. **`session-trace`** — explainability traversal over a `ReasoningSession`: conclusions, evidence with resolved pins, rejected alternatives, `LED_TO` chains.

### 3.4 RG capture port (write + read)

Species 1 throughout. Capture operations are individually atomic and impose no session-scoped transaction and no ordering beyond structural prerequisites (a session before its `CONTAINS`, a conclusion before its evidence) — DDR-001's non-blocking-enrichment posture realized at the contract.

1. **`open-session` / `advance-session`** — author: AOE only. Writes `ReasoningSession` and its `lifecycle_state` transitions. The gateway enforces authorship and structure; **`lifecycle_state` value-set enforcement is TODO** — the value-set is deferred to the AOE SDD by DDR-002's own routing, and enforcement lands here by additive amendment when that SDD fixes it.
2. **`capture-conclusion`** — author: ASA. One transaction: `ReasoningProgress` + `CONTAINS` from its session + optional `LED_TO` predecessors. Enforces at write: `reasoner_category` present; `reasoner_ref` present when `reasoner_category = specialized_agent`; `authoritative` matches the fixed category→flag mapping (#23 rejected at write, not merely CI-detected). Note on #24 (rollup ceiling): the ceiling is not checkable at conclusion-write time, since supporting evidence attaches in subsequent operations; #24 is harness-verified (§7.1) — a deliberate consequence of the non-blocking capture order, acceptable because #24 guards reasoning-quality integrity, not ground-truth entry (its ruled tier).
3. **`capture-evidence`** — author: ASA. One transaction: `Evidence` + `SOURCED_FROM` + `SUPPORTED_BY` to its owning conclusion. Realizes the #14 atomic capture-unit and **tightens it** (the "SDDs may tighten" species, DDR-002 §4): a `SUPPORTED_BY` parent is required at this API even though schema-legal unlinked `Evidence` exists — an evidence node supporting nothing has no capture semantics under ADR-001 §2.2. **Input-to-pin contract (declared):** the request cites a **specific retained version node** — the version reference the retrieval envelope supplied (§3.2) — and the pin records exactly that version; business-key-only citations are rejected (`SCHEMA_VIOLATION`), and citing a since-superseded version is legal by design (Evidence pins what the reasoner actually read — point-in-time fidelity per DDR-002 §6). The gateway verifies the referenced version node exists (`TARGET_NOT_FOUND` otherwise) and computes inherited confidence per the authority-class derivation below. The derivation's **authority** — function form, constants, anchor treatment, Extension-branch totality, and the calibration path — is routed to the forthcoming **inherited-confidence-derivation decision record**; DDR-002 §4 fixes the inheritance rule and the qualitative canon, not a concrete function, and this SDD does not fix one permanently. Until that record rules, the derivation below is the implemented behavior, executed identically on every capture (the `aggregate_cost` derived-at-creation species), its constants configuration-surfaced per §4.6 with the values documented here as their defaults: *(i)* where the cited node itself carries a node `confidence` (Operational `ObservedPattern`, Cost `CapabilityCostEstimate`), the inherited value **is that node confidence** — the plane's native authority measure, freshness already baked in; *(ii)* otherwise, class base × freshness — Catalog / Standards / Governance base **1.0** (versioned or append-only authoritative ground truth; staleness is handled by supersession, not decay), Environment base **0.9 × exp(−Δt/τ)** with Δt from the cited node's `observed_at` and **τ = 90 days *(contested)*** — the base and τ are POC-asserted pending calibration on real capture traffic, flagged per DDR-002 §1's contested-T2 convention; Extension-plane nodes take branch *(i)* where they carry a node `confidence`, else — where they carry `observed_at` — Environment-class treatment *(contested)*. **The derivation is total by construction: the gateway derives or rejects, never defaults a value it has no authority to invent.** A citation for which no branch yields a derivation — the known reachable case: an Extension node carrying neither a node `confidence` nor `observed_at` — is rejected, typed (`CONFIDENCE_UNDERIVABLE`), fail-closed; the Extension-branch totality rule is the forthcoming record's to fix. The caller supplies `fact_summary` and `weight` (reasoning content under ASA's Species-1 authority).
4. **`capture-rejected-alternative`** — author: ASA. One transaction: `RejectedAlternative` + exactly one `REJECTED` parent edge (#1) + optional `WOULD_HAVE_USED` targets.
5. **`create-artifact`** — author: ASA (Solution creation per DDR-001's Artifact write-authority ruling). One transaction: `(:Artifact:Solution)` + `PRODUCED` from its session. `content_hash` and `snapshot_ref` presence enforced (#12's presence half; verification → snapshot-service, §2.2). **Determination (declared):** no upstream names the writer of the structural edges these creation transactions carry (`PRODUCED` here; `CONTAINS` at §3.4.2) — this SDD declares them written under the transaction author's validated Species-1 authority, as structural riders of the authored node-creation (they carry no author of their own, DDR-002 §3); AOE's lifecycle-only grant does not reach them.
6. **`advance-artifact-lifecycle`** — writes a `lifecycle_state` transition on a Solution. Per-transition authoring authority is **routed, not assigned** (→ approval / governance-state-manager SDDs under ADR-002 §2.6); this operation's authority validation instantiates per transition as those SDDs assign it, and until a transition's author is assigned, that transition is rejected (`AUTHOR_VIOLATION`) — unassigned authority is unexecutable, not defaulted.

### 3.5 Promotion boundary port (write + read)

1. **`propose-candidate`** — Species 1; author: the scheduled feedback-loop job. Writes `CandidatePromotion` (either `proposal_kind`) + `PROPOSED_FROM` edges. For `proposal_kind: retraction`, the un-promotion target is designated in the proposal payload; **no `RETRACTS` edge is written at proposal** (see `materialize-retraction`). Proposals are structurally invisible to ground-truth reads from creation (#9).
2. **`record-promotion-decision`** — writes `PromotionDecision` (subtype integrity #16; `origin_mechanism: authored`, approving `Actor` = human EA per DDR-002 §1/§2.4) + per-candidate `DECIDED_ON {outcome}` edges (1:many batch form) + `HAS_CONDITION` for `approved_conditional` outcomes. Enforces **per-candidate strict `decided_at` monotonicity** on `DECIDED_ON` writes (#15's write contract): a new edge must carry `decided_at` strictly greater than any existing edge's on that candidate, else `MONOTONICITY_VIOLATION`. Transport component routed (§2.2); the authoring authority is the EA.
3. **`materialize-promotion`** — Species 2. In one transaction, after governing-verdict verification: materialize the KG node stamped `origin_mechanism: promoted` + `applicability_state` · write `PROMOTES_TO_KNOWLEDGE` · compute the §5 provenance-closure over `PROPOSED_FROM` targets and construct the `ProvenanceSummary` per DDR-002 §4's ratified contract (`frozen_fact_summaries` + `frozen_source_version_pins`, complete against the §5 span) · write `MATERIALIZES_PROVENANCE_OF` · advance the candidate to terminal `status: promoted`. **Routing note (DDR-002 amendment):** the snapshot's internal structuring is a DDR-002 named gap, reserved for additive amendment; this SDD's proposed structuring — per-Evidence entries keyed by `evidence_id`, each carrying fact summary + version pin + source-node reference, enabling mechanical live/frozen correlation in `provenance-of` — is recorded as proposed amendment content, not exercised ahead of the gap's closure. #20 holds by construction of this shape. The gateway's #15 contributions — the §3.5.2 monotonicity precondition and this transaction's in-transaction governing-verdict verification — hold at write time; **#15 itself** (a promoted node's *standing* traceability to the governing approving edge) is CI-detected by upstream design (DDR-002 §7 names the post-materialization verdict flip as its detection case), and no transactional shape can make a later flip unexpressible. **Existing-business-key path (supersession of promoted ground truth):** executes the §6 atomic supersession within the same transaction, under the carry-forward gate below.
4. **`materialize-retraction`** — Species 2. In one transaction, after governing-verdict verification: write `RETRACTS` from the reversing candidate to the target · advance the candidate to terminal `status: promoted` (proposal-execution semantics per DDR-002 §5). Read-exclusion of the target is effective immediately on commit (read-discipline keyed on the EA-approved edge). #21 holds by construction. *Routing note (DDR-002 amendment):* under materialization-time `RETRACTS` writing — grounded in DDR-002 §5's own execution-time gloss ('the `RETRACTS` edge written and the target read-excluded' at terminal status) — #25's biconditional as ratified is unsatisfied during a retraction proposal's pre-decision window. The scoping clause (biconditional scoped to executed/terminal proposals) is **proposed additive DDR-002 amendment content**; the harness implements from ratified text, before and after amendment. This SDD's timing stands.

**Conditional-scope carry-forward (the #22 gate — both supersession paths).** When a supersession's predecessor carries `applicability_state: conditional`:

- *Promotion path:* the `materialize-promotion` request must carry an explicit **scope disposition** — `carry_conditional` (gateway verifies a `Condition` is linked via the approving decision's `HAS_CONDITION`) or `rescope_unconditional` (gateway verifies the approving decision carries no `HAS_CONDITION`). An absent disposition is rejected (`SCOPE_DISPOSITION_MISSING`): the silent default #22 targets is unexpressible, not merely detectable. What the gateway cannot verify — that the EA *deliberated* the re-scope — is workflow, routed to the EA-review surface and DDR-003; the gateway enforces presence and structural consistency.
- *Ingestion path (cross-origin case):* an ingested successor cannot structurally satisfy #22 (it is not a promoted node; it carries no `applicability_state` and no re-scoping decision). The gateway **blocks** the supersession and surfaces it as a **scope-conflict** (`SCOPE_CONFLICT`, disclosed and logged as a governance-significant event) — never silent admission, never silent precedence of ingested reality over an EA-set scope; DDR-002's own safe-interim posture ('surface-to-EA as a scope-conflict, never silent auto-composition') applied as this case's warrant. Remediation runs through the promotion boundary (EA retracts or re-scopes the conditional fact; ingestion retries clean). Any richer cross-origin disposition is KG-entry-governance ADR / DDR-003 territory, cited as the escalation path. Empirical floor: no promotion and no ingestion run has yet occurred; blocking forfeits nothing and is fully disclosed.

### 3.6 Ingestion port

1. **`ingest`** — per-plane load. Enforced regardless of calling adapter: schema-on-write against the target `PlaneDefinition` (#6) · data-classification / no-PHI (#13 — classification and the sole write path are co-located here, the zero-exposure property) · provenance stamping (`origin_mechanism`, `recorded_at`; `source_record_ref` required on `ingested` and `distilled` per #17). **Existing-business-key path:** executes the §6 atomic supersession (create new version · mark predecessor `superseded` · re-point `rebind:current` edges, `rebind:pinned` untouched), subject to the #22 cross-origin gate above.
2. **`register-plane`** — Extension registration: writes `PlaneDefinition`, validates `attaches_to` against existing core labels (#18) and `property_schema` well-formedness; subsequent extension-node ingestion validates against it.
3. **`mirror-gate-decision`** — typed ingestion of the enterprise SDLC gate: `GateDecision` (`origin_mechanism: ingested`, `source_record_ref` required, #16/#17 enforced) + `DECIDED_ON {outcome}` → Solution. `approved` is the sole selection-constituting outcome; a mirrored `approved_conditional` is recorded faithfully and does not constitute selection (DDR-002 §2.4/§5). `decided_at` monotonicity is **not** extended to this edge — DDR-002 scopes it to `CandidatePromotion` `DECIDED_ON` writes, and widening it is an upstream question, not this SDD's.

## 4. Internal Architecture

### 4.1 Module structure

```
knowledge_service/
├── app/
│   ├── main.py                     # FastAPI app, lifespan, routes per port
│   ├── config.py                   # Settings (house application-code standard)
│   ├── models.py                   # Request/response contracts, result envelope
│   ├── ports/
│   │   ├── graph_store.py          # GraphStoragePort — the DDR-001 substitution seam
│   │   └── predicate_eval.py       # PredicateEvaluationPort — shared Condition grammar host
│   ├── adapters/
│   │   ├── neo4j_adapter.py        # The platform's only Neo4j driver
│   │   └── in_memory_graph.py      # Test double
│   ├── domain/
│   │   ├── retrieval/              # §3.3 operations; read-discipline; envelope assembly
│   │   ├── capture/                # §3.4 operations; capture-unit transactions
│   │   ├── promotion/              # §3.5 operations; closure computation; carry-forward gate
│   │   ├── ingestion/              # §3.6 operations; schema-on-write; supersession
│   │   └── shared/
│   │       ├── authority.py        # Two-species validation (Species 1 assignments; Species 2 governing-verdict verification)
│   │       ├── provenance.py       # Stamping + #17 applicability
│   │       ├── classification.py   # No-PHI enforcement (#13)
│   │       ├── supersession.py     # §6 atomic transaction incl. re-point + #22 gate
│   │       ├── envelope.py         # Attribution + applicability block + disclosure channel
│   │       └── schema_metadata.py  # PlaneDefinition registry + validation metadata cache
│   └── observability/              # Structured events + metrics per §8
└── tests/                          # Per house testing standard (§6)
```

No vector, embedding, task-queue, PostgreSQL, or Firestore module exists in this service by design.

### 4.2 Ports and adapters

- **`GraphStoragePort`** — the seam that makes ADR-002 §2.2's substitution contract enforceable (DDR-001 port-substitutability): domain code depends on the port; `Neo4jAdapter` is the sole production implementation; the in-memory double serves tests. A substitute adapter must satisfy the Substitution-Contract Capability Bar (DDR-001) — a port-swap in code, an ADR-002 amendment in governance.
- **`PredicateEvaluationPort`** — hosts `Condition`-predicate evaluation **in-process** (no service on the hot path of a safety-critical read control; enforcement keeps one home). Evaluation **semantics are single-sourced** from the constraint-validator SDD's shared predicate component — one grammar, one implementation, two hosts; a gateway-local fork of predicate semantics is prohibited. **TODO:** the concrete predicate grammar is DDR-003's condition vocabulary (forthcoming). Not blocking — on two legs, load-bearing first: the **fail-closed rule (§4.4)** bounds the exposure structurally (an unevaluable `Condition` excludes its node, always — the worst reachable state ahead of DDR-003 is over-exclusion, never over-admission); secondarily, conditional promotions arise only through the ratified EA gate (DDR-001 Decision.5), whose governing criteria are DDR-003's.

### 4.3 Transaction shapes

Each write operation is exactly one transaction. The composed shapes: the capture-unit (`Evidence` + `SOURCED_FROM` + `SUPPORTED_BY`); the supersession (create + mark + re-point + carry-forward gate); the promotion materialization (verify governing verdict + KG node + `PROMOTES_TO_KNOWLEDGE` + closure + `ProvenanceSummary` + `MATERIALIZES_PROVENANCE_OF` + candidate terminal status, with supersession folded in on the existing-key path); the retraction (verify + `RETRACTS` + candidate terminal status). Every by-construction row in §7.1 rests on one of these shapes.

### 4.4 Read-discipline evaluation

Ground-truth retrieval applies, in order: proposal exclusion (structural label-skip + status guard, #9) · retraction exclusion (EA-approved inbound `RETRACTS`) · conditional admission (#19): resolve `HAS_CONDITION` via the governing decision, determine required context fields from the `dependency_manifest`, evaluate through the predicate port. **Fail-closed:** a predicate that cannot be evaluated — missing manifest-declared context, malformed predicate, unratified vocabulary — excludes the node, always (the T-21-pinned never-auto-admit posture). **Multi-condition** (multiple `HAS_CONDITION` paths): excluded and disclosed as `multi_condition_scope_conflict` — DDR-003's stated safe interim (surface-to-EA, never silent auto-composition), realized verbatim; no composition rule is invented here. Catalog-eligibility evaluation runs alongside as annotation only — silent eligibility filtering is prohibited because it would erase the gap-vs-ineligible distinction the reasoning capture depends on (a dropped-but-existing technology must remain expressible as a `RejectedAlternative`; an absent one as a `GapConclusion`).

### 4.5 Caching posture

**No ground-truth result caching.** #19, #21, and #22 are read-time controls; a cached admitted result could serve retracted or re-scoped knowledge after the graph says otherwise. Read-discipline immediacy wins over read latency in this design. **Schema-metadata caching permitted** (`PlaneDefinition` descriptors, predicate parse artifacts): write-through invalidation is complete by construction — every write that could stale these caches flows through this same service, so no external-writer invalidation race exists.

### 4.6 Configuration and secrets

Settings per the house application-code standard: service identity, `PORT`, log level; `NEO4J_URI` / `NEO4J_DATABASE` / pool sizing; credentials via GCP Secret Manager with Workload Identity Federation per the house infrastructure standard — no key files, no credentials in Kubernetes Secrets. **Every *(contested)* runtime constant in this design is a configuration-surfaced tunable with the documented value as its default** — the §3.4.3 derivation constants (Environment base, τ) and the §8 evidence-less-conclusion dwell — so calibration is a config change, not a code change; re-ratifying a tuned value into this document remains the amendment act. The Neo4j connection scheme follows the deployed topology; production topology is deliberately deferred upstream (ADR-002 §5.2), so the URI is opaque configuration and this SDD pins no cluster scheme.

### 4.7 Gateway-local state

Per ADR-002 §5.2: operational, cache, and staging state only — driver/pool lifecycle, config, and the §4.5 metadata caches. **The gateway's operational events are not graph citizens**: rejected writes, scope-conflict blocks, exclusions, and evaluation failures emit as structured log events into the platform's monitoring/logging surfaces (§8) and are never written as graph nodes — DDR-001's Governance plane excludes per-action disposition events by name, and a gateway journaling its own enforcement into the graph would be authoring state with no assigned authority.

## 5. Data Flows

### 5.1 Reasoning capture (inbound, ASA/AOE)

AOE `open-session` → session node. ASA `capture-conclusion` (authority + #23 validated; node + `CONTAINS`) → per supporting fact, ASA `capture-evidence` (atomic unit; pin resolved, confidence inherited) → ASA `capture-rejected-alternative` as options are discarded → ASA `create-artifact` on candidate production (`PRODUCED` edge). Each operation one transaction; no cross-operation gating (non-blocking capture).

### 5.2 Promotion materialization (inbound, feedback loop → EA → gateway)

Feedback-loop job `propose-candidate` (invisible to ground truth from birth) → EA decision recorded via `record-promotion-decision` (monotonic `DECIDED_ON`; `HAS_CONDITION` if conditional) → `materialize-promotion`: governing verdict verified → KG node stamped `promoted` + `applicability_state` → closure computed over `PROPOSED_FROM` targets → `ProvenanceSummary` written and bound → candidate terminal `promoted`. On an existing business key, the supersession executes in the same transaction under the carry-forward gate (explicit scope disposition or rejection).

### 5.3 Ingestion with supersession (inbound, adapters)

Adapter `ingest` → schema-on-write vs `PlaneDefinition` → classification (#13) → provenance stamped (#17) → new business key: plain create; existing key: atomic supersession (create/mark/re-point) — unless the predecessor is `conditional`, in which case the write blocks as `SCOPE_CONFLICT` (governance-significant event; EA remediation via the promotion boundary; retry clean).

### 5.4 Conditional retrieval (outbound, ASA)

ASA retrieval call with consuming context → traversal → proposal + retraction exclusions → per `conditional` node: manifest-derived required context checked, predicate evaluated fail-closed → admitted results assembled into the envelope with eligibility annotations → excluded conditionals disclosed as `{node_id, reason}`. ASA composes the applicability facts into its selection judgment — captured back through §5.1.

## 6. Testing Requirements

House testing standard applies (platform-default coverage gate). Elevated, 100%-branch modules — each an enforcement surface where a missed branch is a safety-control hole: `shared/authority.py` (both species) · `shared/supersession.py` (carry-forward dispositions incl. cross-origin block) · `promotion/` closure computation and monotonicity enforcement · read-discipline evaluation incl. fail-closed and multi-condition paths · `shared/classification.py`. All domain tests run against the in-memory port doubles; no test depends on live Neo4j. **Relationship to the conformance harness, kept distinct:** service tests verify this design's behavior; the harness (`conformance/`) independently verifies the schema's invariant set against the real gateway — the 1b gateway-behavioral contracts are the external acceptance surface at the BUILD leg (§7.2), and this SDD's tests neither replace nor duplicate them.

## 7. Upstream Compliance Checklist

### 7.1 Check-by-check conformance

| Upstream | Requirement | This SDD's conformance |
|---|---|---|
| ADR-001 §6 check 1 | Position commitment | All gateway logic is deterministic encoded reasoning; no LLM use exists in this service. Contributes to the Position-4 trajectory by making deterministic graph-native retrieval the platform's only retrieval substrate. |
| ADR-001 §6 check 2 | Reasoning-capture invariant | This service produces no architectural decisions of its own (sole executor, never author); it realizes the capture write path — §3.4's operations — through which every reasoner's output enters the RG with category attribution, authoritative flag, evidence linkage, and rejected-alternative capture. Evidence linkage is structurally enforced at `capture-evidence` (the §3.4.3 tightening: no `Evidence` without its `SUPPORTED_BY` parent) and deliberately not conclusion-gated (DDR-001's non-blocking capture); the zero-evidence conclusion posture routes with the rollup function (§2.2), disclosed via §8. |
| ADR-001 §6 check 3 | Deterministic/probabilistic classification | Every output of this service is deterministic. Zero probabilistic outputs exist in this design. |
| ADR-001 §6 check 4 | Burden of proof on probabilistic output | No probabilistic output exists to carry the burden. |
| ADR-001 §6 check 5 | LLM-as-renderer language | No model use to describe. The design additionally enforces the boundary from the retrieval side: candidate sets and structural facts out, selection judgment never (§3.3, §4.4). |
| ADR-001 §6 check 6 | Specialized-agent integration | This SDD introduces no specialized agent. Agent-authored capture is served via §3.4 with `reasoner_category` / `reasoner_ref` enforced at write. |
| ADR-001 §6 check 7 | Lifecycle-stage scope | The gateway is lifecycle-spanning infrastructure; every decision in this service is SOFIA-encoded; no stage-specific human/LLM decision shape exists here. |
| ADR-002 §6 check 1 | System-of-record | All authoritative state read/written through the graph; local state is operational/cache only (§4.7). |
| ADR-002 §6 check 2 | Graph-access authority | This service is the sole Neo4j driver holder (§2.1) and exposes the sole access API; no other client path exists. |
| ADR-002 §6 check 3 | Store authority | Neo4j client only; no vector store, no PostgreSQL, no Firestore client in this service (§1, §2.2); no vector properties are expressible through the operation contracts (#2 by construction for mediated writes). |
| ADR-002 §6 check 4 | Traversal locality | Every cross-plane and cross-graph operation in §3 is a single-store traversal; no application-layer join exists. |
| ADR-002 §6 check 5 | Write authority (synthesis instance) | ASA-authors-`ReasoningProgress` / AOE-session-lifecycle-only enforced at write time as Species-1 validation (§3.2, #7). |
| ADR-002 §6 check 6 | Data protection | #13 enforced at the ingestion boundary, co-located with the sole write path (zero-exposure at graph entry); a PHI scope change is an ADR trigger, not absorbed here. |
| ADR-002 §6 check 7 | Write-authorship general principle | Every write operation names a component author (Species 1) or an authorizing decision (Species 2); no operation's author is or can default to this service (§3.2); unassigned authorities are unexecutable, not defaulted (§3.4.6). |
| DDR-001 check 1 | Sole gateway | Realized as this service's existence and §3's exclusive surface. |
| DDR-001 check 2 | No authoritative local state | §4.7. |
| DDR-001 check 3 | RG authorship | §3.4 Species-1 assignments. |
| DDR-001 check 4 | Proposal visibility / no self-modification | #9 structurally enforced on every ground-truth read (§4.4); KG materialization executes only on a verified governing approving decision (§3.5.3). |
| DDR-001 check 5 | Evidence pin resolution | `capture-evidence` pins the cited retained version at write under the §3.4.3 input-to-pin contract; `read-as-of` and `provenance-of` resolve pins at read (§3.3.6/§3.3.8). |
| DDR-001 check 6 | Provenance on every node; promoted distinguishable | Presence half: provenance-group stamping on every write path, backed by DDR-002 §7's DB-enforced existence constraints, plus #17's `source_record_ref` applicability. Distinguishability half: `promoted` vs `ingested` via `origin_mechanism` (#11), carried on every envelope. |
| DDR-001 check 7 | Feedback-loop author/executor/authorizer separation | §3.5 realizes it operation-by-operation: job authors proposals; EA decisions authorize; the gateway executes materializations against the verified governing verdict. |

**DDR-002 §7 — enforcement mapping.** The gateway's runtime relationship to the invariant set (the harness's mechanization bucketing is conformance-mechanization's and is not restated here):

| Mode | Checks |
|---|---|
| **By construction** (transactional shape makes violation unexpressible) | #1, #14 (capture-unit ops) · #4, #8, #22 (supersession shapes incl. the cross-origin block) · **#15's monotonicity precondition** (`record-promotion-decision`) · #20 (in-transaction closure + at-promotion binding) · #21 (`materialize-retraction`) · #2 (no vector property is expressible through any operation contract) · #16 (each `Decision`-writing operation creates its single subtype as the operation's fixed shape — `record-promotion-decision` writes `PromotionDecision`, `mirror-gate-decision` writes `GateDecision`; a bare or double-subtyped `Decision` is unexpressible through any mediated write; `SUBTYPE_VIOLATION` retained as documented defense-in-depth, §3.2) · #11 (each write path stamps its own `origin_mechanism` as part of its fixed shape; `promoted`/`ingested` distinguishability holds by the operations' own stamping) |
| **Write-time rejected** (typed rejection) | #6, #18 (schema-on-write / registration) · #7 (Species-1 authority) · #13 (classification) · #17 (`source_record_ref` applicability) · #23 (flag↔category) · provenance-group presence (DB-enforced existence constraints per DDR-002 §7; a missing field surfaces typed as `PROVENANCE_MISSING`) |
| **Read-discipline** (no bypassing read path exists) | #9 · #19 (fail-closed; multi-condition surfaced, never composed) · retracted-node exclusion (§5) |
| **Harness-verified / routed** (not gateway runtime) | #3, #5 (attach to future cost-write operations — routed, not invented) · #10 (constraint-validator SDD + CI) · #12's verification half (→ snapshot-service) · **#15 itself** (standing promoted-origin traceability — CI-detected per DDR-002 §7; the gateway contributes the monotonicity precondition and at-materialization governing-verdict verification, §3.5.2/§3.5.3) · #24 (see §3.4.2 note) · #25 (with the §3.5.4 routing note) |

### 7.2 Binding constraints (charter-mandated, stated as this SDD's own obligations)

- **Authority split honored.** DDR-002 §7's safety-critical classification is binding on this design: this SDD **downgrades no safety-critical classification and permits no safety-critical invariant to slip the gateway gate**. Every safety-critical check appears above in the by-construction, write-time, or read-discipline rows — none is deferred past gateway operation. The gateway must not operate against an unenforced safety-critical tier; this design's operations are the enforcement.
- **1b required-flip obligation (binds the BUILD leg; set-generic by design).** The knowledge-service build is complete only when the conformance harness's **full 1b gateway-behavioral contract set as derived from DDR-002 §7's ratified invariant set (including ratified additive amendments) at build time** — deliberately not a frozen enumeration, but bounded by the ratified invariant universe — runs against the built gateway un-skipped, as required status checks, all green: the gateway demonstrably implements the `GraphGateway` seam as a conforming superset. Flipping 1b contracts to required is this build's act and no earlier increment's.

## 8. Observability Contract

Wire format, propagation, and retention per the platform observability standard; this section defines the service-specific contract. Consistent with §4.7, these surfaces are the *only* home of the gateway's operational record — none of it enters the graph.

**Structured log events** (mandatory fields per platform standard; `correlation_id` propagated end-to-end):

| Event | Trigger | Severity / class |
|---|---|---|
| `write_rejected` | Any typed rejection; carries the §3.2 error type + operation | WARN; **governance-significant** for `AUTHOR_VIOLATION`, `DECISION_NOT_APPROVING`, `MONOTONICITY_VIOLATION`, `CLASSIFICATION_REJECTED`, `SCOPE_DISPOSITION_MISSING` |
| `scope_conflict_blocked` | #22 cross-origin block or multi-condition surfacing | WARN; **governance-significant** |
| `conditional_excluded` | #19 exclusion; carries reason | INFO |
| `promotion_materialized` / `retraction_applied` | Species-2 transaction commit | INFO; **governance-significant** |
| `supersession_executed` | §6 transaction commit; carries re-point count | INFO |
| `plane_registered` | Extension registration | INFO; **governance-significant** |
| `predicate_evaluation_failed` | Unevaluable predicate (fail-closed path taken) | WARN |
| `evidence_less_conclusion` | A `ReasoningProgress` past a dwell (default 24h *(contested)*) with no `SUPPORTED_BY` edge — disclosure only, never gating (§2.2 routing) | INFO |

**Metrics:** read/write latency histograms per port · rejection counters by error type · read-discipline exclusion counters by reason · scope-conflict gauge (open, awaiting EA remediation) · evidence-less conclusion gauge (count past dwell — the §2.2 zero-evidence disclosure surface) · `rebind:current` re-point degree histogram (the §6 bounded-degree assumption, observed) · pool/connection health.

## 9. Cross-References

- **Upstream implemented:** ADR-001 v1.1.0 · ADR-002 v1.1.0 · DDR-001 v1.3.0 · DDR-002 v1.2.0. Built against DDR-002's safety-critical-tier contract per §7.2.
- **Forthcoming upstream (routed, unauthored):** **DDR-003** — condition vocabulary, promotion governance, retention windows (§2.2, §4.2) · **KG-entry-governance ADR** — distillation checkpoint posture, un-promotion authority, cross-origin escalation (§2.2, §3.5) · **Inherited-confidence-derivation decision record** — the §3.4.3 derivation's authority: function form and constants, anchor treatment, Extension-branch totality, calibration path (§3.4.3).
- **Proposed DDR-002 additive amendments (named content, not opened):** ProvenanceSummary internal structuring — keyed per-Evidence entries incl. source-node reference (§3.5.3 routing note) · #25 executed-proposal scoping clause (§3.5.4 routing note).
- **Sibling SDDs (routed-to, unauthored):** AOE (`lifecycle_state` value-set) · solutioning-agent/ASA (selection judgment; applicability composition; preference landing; `ReasoningProgress.confidence` rollup function + zero-evidence conclusion posture per DDR-002 §4's routing, realized at §2.2/§3.3.3) · constraint-validator (predicate semantics single-source; obligation closure; manifest-completeness) · governance-state-manager + approval (Solution lifecycle-transition authors; `Attestation`/`Actor`/`Role` authorship; decision-recording transport) · architecture-ingestion (adapter decomposition; source authorship) · snapshot-service (hash verification) · detection-promotion (feedback-loop job) · cost-estimation (future cost operations; #3/#5 attachment).
- **Conformance:** the graph conformance harness (`conformance/`) — the 1b gateway-behavioral set is this build's acceptance surface (§7.2); the #25 timing note (§3.5.4) coordinates there.
- **Deliberation artifact:** `agent-loop/deliberation/sdd-001-knowledge-service/record.md` — the pre-authoring deliberation record (dispositions ratified per item, 2026-07-03); charter substrate: `agent-loop/triage/triage-001-distilled-set/record.md` (§T-15/T-17/T-27, Item-4 charter notes, Addendum). **v0.2.0 revision carriers:** `agent-loop/runs/run-009-sdd-001/audit.md` + `agent-loop/runs/run-008-sdd-001/audit.md` (review-union rulings ratified per item, 2026-07-04). **v0.3.0 revision carriers:** `agent-loop/runs/run-010-sdd-001/audit.md` + `agent-loop/runs/run-011-sdd-001/audit.md` + `agent-loop/runs/run-011-sdd-001/disposition.md` (union rulings and disposition ratified per item, 2026-07-05; amendment dispositions ratified per item, 2026-07-08). **v1.0.0 acceptance carrier:** `agent-loop/runs/run-012-sdd-001/audit.md` (verification-draw rulings and acceptance ratified per item, 2026-07-09).
- **Standards:** house application-code, testing, and infrastructure-code standards.

## 10. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.0.0 | 2026-07-09 | RBT-15 | First ACCEPTED — verification draw clean (run-012-sdd-001; acceptance carrier: `agent-loop/runs/run-012-sdd-001/audit.md`; rulings and acceptance ratified per item, 2026-07-09). No content change; the v0.3.0 row's carrier list corrected (typo-class). PROPOSED → ACCEPTED. |
| 0.3.0 | 2026-07-08 | RBT-15 | Amendment from the ratified run-010 ∪ run-011 review union (revision carriers: `agent-loop/runs/run-010-sdd-001/audit.md` + `agent-loop/runs/run-011-sdd-001/audit.md` + `agent-loop/runs/run-011-sdd-001/disposition.md`; union disposition ratified per item 2026-07-05; amendment dispositions ratified per item 2026-07-08). **Authority re-routed:** the §3.4.3 inherited-confidence derivation's authority routed to the forthcoming inherited-confidence-derivation decision record (elected from the union disposition, Item 1); the derivation stands as implemented behavior until that record rules, constants configuration-surfaced per §4.6 as defaults. **Fail-closed interim:** derivation total by construction — derive or reject, never default; the confidence-less, timestamp-less Extension citation rejects typed (`CONFIDENCE_UNDERIVABLE`, new §3.2 type, not governance-significant per §8); "Extension-class default" dropped from §4.6's tunables. **Re-bucketed:** #16 and #11 to §7.1's by-construction row (subtype fixed per operation shape, `SUBTYPE_VIOLATION` retained as documented defense-in-depth; `origin_mechanism` stamped per write path); stamping-presence citation corrected to DDR-002 §7's DB-enforced existence constraints; DDR-001 check-6 row split (presence half / distinguishability half). **Notation:** "§6.x" → "§6 check x" across the fourteen ADR-001/ADR-002 conformance rows. **Confirmed, no change:** §3.5.4 routing note stands as written (union disposition Item 5). PROPOSED; pending one verification draw (union disposition Item 7). |
| 0.2.0 | 2026-07-04 | RBT-15 | Revision from the ratified run-008 ∪ run-009 review union (carriers: the two run audits, rulings ratified per item). **Declared determinations:** structural-edge write authority under the transaction author (§3.4.5, covering §3.4.2's `CONTAINS`); capture-evidence input-to-pin contract — explicit version reference, verification not resolution (§3.4.3); inherited-confidence derivation with contested constants (§3.4.3). **Re-scoped:** §1 read-boundary absolute (audit ops as disclosed exception); #15 enforcement split — precondition by-construction, invariant CI-detected (§3.5.3/§7.1); track-record confidences returned uncomposed (§3.3.3); §7.2 1b set bounded to DDR-002 §7's ratified universe; §4.2 not-blocking re-grounded on fail-closed. **Routed:** `ReasoningProgress` rollup + zero-evidence posture → solutioning-agent SDD (§2.2; §8 disclosure surface added); ProvenanceSummary internal structuring + #25 scoping → named DDR-002 additive-amendment content (§3.5.3/§3.5.4 — supersedes deliberation Items 2g(iii)/2a(ii) on those two points). **Riders:** §3.2 invocation-authority clause; §3.5 safe-interim warrant; §3.3.8 traversal-notation fix. PROPOSED; pending its own review run. |
| 0.1.0 | 2026-07-03 | RBT-15 | Initial draft from the pre-authoring deliberation session; greenfield (no prior service referenced); PROPOSED. |
