# File: docs/ddr/DDR-001-data-architecture.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: DDR-001 — Data Architecture. Realizes the Knowledge Graph and Reasoning Graph as co-resident logical subgraphs in a single Neo4j Enterprise instance, with a five-plane-plus-Extension KG, a three-store persistence backbone, a sole-owner graph gateway, and an EA-gated feedback loop — implementing ADR-002's graph-as-system-of-record commitment at the data-architecture layer.

# DDR-001 — Data Architecture: Knowledge Graph and Reasoning Graph

| Field | Value |
|---|---|
| **Document ID** | DDR-001 |
| **Version** | 1.3.0 |
| **Status** | ACCEPTED |
| **Date** | 2026-07-03 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None |
| **References** | ADR-001 v1.1.0; ADR-002 v1.1.0 |

---

## Decision

The Knowledge Graph (KG) and Reasoning Graph (RG) are realized as co-resident logical subgraphs in one Neo4j Enterprise instance, with a typed-plane KG, a three-store persistence backbone, a sole-owner gateway, and an EA-gated feedback loop — decomposed into testable sub-decisions:

- **Decision.1** — The Knowledge Graph and Reasoning Graph are **co-resident logical subgraphs in a single Neo4j Enterprise instance**.
- **Decision.2** — The KG is partitioned into **five typed planes** (Catalog, Environment, Operational, Governance, Standards) **plus an Extension layer**.
- **Decision.3** — Persistence is a **three-store backbone** — Neo4j (system of record), PostgreSQL (workflow/audit/staging), Firestore (immutable snapshots) — **with no vector store**.
- **Decision.4** — All graph access flows through a **single sole-owner gateway** (knowledge-service), the only holder of the Neo4j driver.
- **Decision.5** — A **scheduled, EA-gated feedback loop** promotes recurring RG findings into the KG; **SOFIA does not self-modify its EA-gated encoded knowledge** (scoped to ADR-001 §2.5's object — SOFIA's own reasoning entering encoded knowledge). The broader human-accountable checkpoint governing *all* KG entry is routed to the forthcoming **KG-entry-governance ADR**, not asserted here.
- **Decision.6** — This DDR owns **plane definitions and data-architecture patterns** (the architecture half of the architecture-vs-schema split); the node/relationship/constraint contract is **DDR-002's**.
- **Decision.7** — Write authority for the three feedback-loop graph writes is **component-scoped and gateway-routed** under **ADR-002 §2.6's general write-authority principle** (as amended): the `CandidatePromotion` proposal is authored by the scheduled feedback-loop job; the at-promotion provenance snapshot and the EA-gated KG materialization execute via the gateway, the materialization's authoring authority resting with the approving `PromotionDecision`.

---

## Rationale

This ruling is **deliberation-grounded** — the output of the scoping session whose design substrate this DDR realizes — and additionally rests on a present, vendor-verifiable dependency: the schema's DB-enforced property-existence constraints require Neo4j Enterprise (ADR-002 §2.2/§4.1; the Substitution-Contract Capability Bar, below). This satisfies the DDR-route substrate gate (deliberation grounding before authoring).

---

## Two-Graph Model

### Knowledge Graph — five typed planes + Extension

Enterprise ground truth ("what do we know?"). Consumers query the graph, never a plane directly (uniform access behind a common ingestion-port role). **Source systems are named by *class*, not vendor product.**

| Plane | Role | Source-class | Cadence | Illustrative node types |
|---|---|---|---|---|
| Catalog | approved-technology portfolio | enterprise architecture / portfolio catalog | batch | capabilities, technologies, patterns, IaC templates, solution documents |
| Environment | deployed reality | CMDB / service registry | daily + deploy-event | deployed services, environments, configuration items |
| Operational¹ | distilled operational knowledge | observability / AIOps telemetry (external SoR) | periodic distillation; durable (no in-graph TTL) | derived `ObservedPattern`s (weakness / strength trends) |
| Governance² | actors and decisions | IAM + SOFIA workflow events | event-driven | users, roles, approval decisions |
| Standards | normative corpus | EA standards repository | on-publish / versioned | enterprise standards, policy directives, compliance controls |
| Extension | open future sources | any registered source | per-plane adapter | extension nodes, plane definitions |

¹ *Operational holds durable distilled `ObservedPattern`s — derived weakness / strength trends — not raw telemetry. The observability / AIOps telemetry is an external system of record (TTL-bounded there) from which `ObservedPattern`s are distilled; it is not itself a KG plane. Distillation mechanics → DDR-002; retention / archival policy → DDR-003.*

² *Disambiguated at first use: the Governance **plane** (actor/decision ground truth) is distinct from feedback-loop **governance** (DDR-003) and three-hat **governance**. The plane holds **governance-participating identities only, not an IAM mirror**; per-action disposition events are excluded (transient → orchestration/observability SoR).*

**Cross-cutting KG invariants (label-free):** provenance on every node; **deterministic, not LLM-judged** (gap = required capability with no resolving technology; override = unsanctioned preference — graph facts, not model opinions); Operational holds **durable distilled `ObservedPattern`s** (no in-graph TTL; raw telemetry TTL-bounded in its external SoR); environment edges carry **confidence**; Extension is **bounded, not dynamic** (`PlaneDefinition` registration + schema-on-write; zero migration, zero impact on existing traversals).

### Reasoning Graph — four structural roles (bridged to ADR-002 §2.6 vocabulary)

SOFIA's persistent reasoning record ("how did we decide?"). **Two write authorities per ADR-002 §2.6: ASA authors reasoning *content* (`ReasoningProgress`); AOE owns the `ReasoningSession` lifecycle.** Four roles:

- **Session root — corresponds to `ReasoningSession`** — one per synthesis run; the traversable root aggregating a run's reasoning. Confidence is **per-conclusion** (the `ReasoningProgress` rollup, DDR-002 §4); any session-level aggregate is a **read-time traversal affordance** (`CONTAINS` → `ReasoningProgress`), consuming-SDD-owned, **never a stored property** on the session root. **Lifecycle owned by AOE.**
- **Typed conclusion** — a single reasoning conclusion of a known kind (illustratively: pattern selection, technology resolution, gap, override, risk, compliance evaluation). The `ReasoningProgress` node (**ASA-authored**).
- **Evidence** — a KG-linked supporting fact, confidence **inherited from its source plane**; the traversable link from reasoning to ground truth. Linked to `ReasoningProgress` (**ASA-authored**).
- **Rejected alternative** — a considered-and-discarded conclusion and why; the primary feedback-loop input. Linked to `ReasoningProgress` (**ASA-authored**).

*(Session root corresponds to `ReasoningSession`; the typed conclusion is `ReasoningProgress`, with `Evidence` and `RejectedAlternative` linked to it by edges. Formal labels/properties → DDR-002.)*

**RG invariants:** ASA is the **sole author of reasoning content** (`ReasoningProgress`); the **`ReasoningSession` lifecycle is owned by AOE** (ADR-002 §2.6). **All RG writes are gateway-mediated and driver-less** (ADR-002 §2.5). Capture is **non-blocking enrichment, not a synthesis gate**. **No PHI in reasoning state.** Retention/TTL and read-access scoping are deferred (DDR-003 / SDD) — see the versioning model.

### Cross-graph edges — the same-store keystone

KG and RG are co-resident logical subgraphs (ADR-002 §2.3), joined by two cross-graph edge **roles**: **evidence linkage** (illustratively `SOURCED_FROM` / `DREW_FROM`) — RG → cited KG facts, making explainability a single-DB traversal; **promotion** (illustratively `PROMOTES_TO_KNOWLEDGE`) — the EA-gated feedback path. **Keystone:** first-class cross-plane and cross-graph traversal as single-store operations — never application-layer joins. This is the load-bearing reason the two graphs share one instance (ADR-002 §2.3).

---

## Versioning & Temporal Model

Carried as a named treatment so coverage is visible; explicit and complete, not retrofit. **Posture (ratified):** **version-pinned evidence + per-plane retention** — RG Evidence pins the cited KG version; versioned planes retain superseded versions (never delete); explainability resolves point-in-time by traversal to the pinned version (keystone preserved). **Prior-intent lineage:** the versioning mechanism (effective-dating / never-delete / version-at-generation) is an established pattern, re-grounded here on ADR-001's auditable-reasoning thesis rather than a compliance/HIPAA framing.

**Two objects, versioned two ways:** (1) **KG ground truth** version-retained in Neo4j; (2) the produced **solution** dual-homed — graph node in Neo4j (relationships, for feedback traversal) + immutable per-version snapshot in Firestore (body, for revert/audit).

| Axis | Mechanism | Store | Owner |
|---|---|---|---|
| KG ground-truth versioning | effective-dating / supersession / never-delete | Neo4j | DDR-001 posture · DDR-002 schema |
| Evidence version-pinning | pins cited KG version | Neo4j | DDR-001 contract · DDR-002 field |
| Solution (ASD — Architecture Solution Document) versioning | dual-home: graph node + immutable per-version snapshot | Neo4j + Firestore | DDR-001 shape · SDD workflow |
| Operational distillation retention | durable `ObservedPattern`s; no in-graph TTL (raw telemetry expires in external SoR) | Neo4j | DDR-001 invariant · DDR-003 archival policy |
| RG retention posture | bounded + non-uniform; summary-on-evidence-expiry preserves explainability | Neo4j | DDR-001 posture · DDR-003 policy |
| Core schema evolution | additive via Extension; core-contract lifecycle | — | DDR-002 (named here via Extension) |
| Governance-decision immutability | append-only immutable facts | Neo4j | DDR-001 (closed here) |
| Feedback-promotion provenance | `PROMOTES_TO_KNOWLEDGE` + lineage; promoted ≠ ingested; auditable | Neo4j | DDR-001 architecture · DDR-003 audit policy |

---

## Hybrid Persistence Model

Three stores, authority by state class (ADR-002 §2.4):

- **Neo4j** — KG + RG (system of record) + in-graph per-plane version history.
- **PostgreSQL** — workflow / audit / staging.
- **Firestore** — immutable per-version snapshots of produced solutions (ASD bodies) for revert/audit; append-only, point-in-time (ADR-002 §2.4).
- **No vector store** — semantic retrieval is graph-traversal-native.

**Two distinct temporal mechanisms, never conflated:** in-graph version retention (Neo4j, cited ground truth) vs. immutable produced-solution snapshots (Firestore, solution bodies).

**Boundary:** store responsibilities + temporal contract + no-vector-store are settled here. Access mechanics → the gateway pattern (cross-referenced below). Snapshot triggers/types + the snapshot-service → SDD.

---

## Graph-Gateway Pattern

**Sole-owner boundary** — knowledge-service holds the only Neo4j driver and is the single graph-access boundary (ADR-002 §2.5).

| Role | Purpose | Posture |
|---|---|---|
| **KG read** | synthesis-context retrieval | read-only traversal; results carry source-plane + confidence + version-pin attribution |
| **RG write + read** | reasoning capture; explainability + feedback reads | **two writers, both gateway-mediated & driver-less: ASA writes reasoning content (`ReasoningProgress`), AOE writes session lifecycle (`ReasoningSession`); writes non-blocking** |
| **Ingestion** | per-plane load | schema-on-write validation against `PlaneDefinition`; Extension registration |

**Boundary enforces:** provenance; schema-on-write validation; classification (single no-PHI enforcement point, ADR-002 §2.7); version-pin resolution; driver lifecycle + single-source-of-truth.

**Prohibited:** any other direct driver; authoritative KG/RG state in local stores (local = cache/operational/staging only, ADR-002 §5.2); querying a plane directly.

**Port-substitutability:** roles are exposed as ports — the seam that makes the ADR-002 §2.2 substitution contract enforceable and an alternate adapter a port-swap.

**Boundary:** the *pattern* is owned here (DDR-001); the *API method contract* → knowledge-service SDD; the *schema* enforced → DDR-002; ingestion-adapter decomposition → SDD.

---

## Feedback-Loop Architecture (data-path; governance → DDR-003)

**Out-of-band by design** — a scheduled job over accumulated RG, not inline with synthesis. **Path:** detect (cross-graph traversal over RG + KG + Operational) → propose (`CandidatePromotion`) → **mandatory, non-bypassable EA gate** (the loop proposes, a human materializes) → materialize (real KG node + `PROMOTES_TO_KNOWLEDGE` edge, provenance-stamped). **Proposal-visibility invariant:** a `CandidatePromotion` is a distinct proposal class **excluded from synthesis ground-truth traversal**, materialized only on EA approval. **Signal/action classes (illustrative):** override-recurrence, gap-recurrence, evidence-quality; at least one action class — knowledge *promotion* (EA-gated) and *source-quality feedback* (feeds ingestion scoring, no promotion).

**Write authority — the three feedback-loop writes (ADR-002 §2.6 general principle; ADR-002 §2.5 gateway-routed; graph-home-agnostic).** ADR-002 §2.6 (as amended) states the general rule: every authoritative graph write has a **named, component-scoped author**; the sole-owner gateway (ADR-002 §2.5) is the **sole executor** and never the author; for an EA-gated materialization the **authoring authority is the approving decision**. Its synthesis-time *instance* assigns ASA as author of `ReasoningProgress` and AOE as owner of the `ReasoningSession` lifecycle (the two write authorities named for the Reasoning Graph above). The feedback loop's three writes are the instance of the same general rule at the promotion boundary:

- **`CandidatePromotion` proposal** — **authored** by the **scheduled feedback-loop job** (the detection-promotion mechanism), pre-approval; gateway-executed. A component-scoped author beyond the synthesis-time ASA/AOE instance, under the same general principle.
- **At-promotion provenance snapshot** — **executed** by the **gateway** in the same materialization transaction as the KG write (below), preserving lineage ahead of the cited `Evidence`'s retention (§Versioning & Temporal Model's summary-on-evidence-expiry). Its node/edge *schema* is DDR-002's; its authoring authority is the approving `PromotionDecision`, as for the materialization it accompanies.
- **Materialized KG node + `PROMOTES_TO_KNOWLEDGE` edge** — the **authoring authority is the approving `PromotionDecision`** (the human EA's gate); the **gateway executes** it, as it executes all graph writes. This is an authoritative KG ground-truth write. The loop proposes, the EA (via the `PromotionDecision`) authorizes, the gateway executes — **SOFIA does not self-modify its EA-gated encoded knowledge** (Decision.5).

This assigns write **authority** only and is **graph-home-agnostic** — where `CandidatePromotion` resides is deferred; nothing here depends on it. The ADR-002 §2.6 synthesis-time assignment for `ReasoningProgress` / `ReasoningSession` is unchanged.

**Artifact write authority (ADR-002 §2.6 general principle).** The **ASA authors `(:Artifact:Solution)` artifacts** on creation — the producing-component pattern — gateway-routed and driver-less, as with its `ReasoningProgress` authorship. Authority over **Solution lifecycle transitions** (the FSM advancement `proposed → architected → gated → approved → operational`, DDR-002 §5) is **routed to the relevant SDDs** under the same ADR-002 §2.6 principle — each transition's authoring authority named there — not fixed here.

**Boundary:** thresholds, signal definitions, EA criteria, cadence, and retention → DDR-003; `CandidatePromotion` schema → DDR-002; the scheduled job + EA-review portal → SDD.

---

## Substitution-Contract Capability Bar (ADR-002 §2.2 routes here)

A replacement graph platform — or moving the runtime off self-managed GKE — is an ADR-002 amendment, not an implementation detail. A substitute must support:

1. the five typed planes + Extension + RG as co-resident logical subgraphs in one instance;
2. the multiple relationship/edge types the plane traversals require;
3. first-class cross-plane and cross-graph (KG↔RG) traversal as single-store operations;
4. in-graph version retention + point-in-time (as-of) resolution per the temporal model;
5. gateway-enforceable provenance, schema-on-write validation, and classification at the write boundary;
6. **DB-enforced property-existence-constraint capability at the schema layer** — the present, vendor-verifiable dependency the Neo4j Enterprise edition commitment rests on (Enterprise-only per the current Cypher Manual; the DDR-002 §7 provenance-group existence constraints depend on it; ADR-002 §2.2/§4.1).

---

## Conformance Checks (aspirational; mechanization deferred)

Downstream SDDs verify against:

1. All graph access routes through the sole-owner gateway; no other component holds a Neo4j driver.
2. No authoritative KG/RG state in local stores (local = cache/operational/staging only).
3. RG content is authored only by ASA (`ReasoningProgress`); `ReasoningSession` lifecycle only by AOE; both gateway-mediated.
4. `CandidatePromotion` proposals are excluded from synthesis ground-truth traversal until EA-approved; SOFIA does not self-modify its EA-gated encoded knowledge (ADR-001 §2.5). The broader entry-checkpoint principle governing all KG entry → forthcoming KG-entry-governance ADR.
5. RG Evidence resolves to its pinned KG version (point-in-time explainability).
6. Every KG node carries provenance; promoted knowledge is distinguishable from ingested.
7. Feedback-loop graph writes honor ADR-002 §2.6's author/executor/authorizer separation: the `CandidatePromotion` proposal is authored by the scheduled feedback-loop job; the at-promotion provenance snapshot and the materialized KG node are executed by the gateway, their authoring authority resting with the approving `PromotionDecision`. The KG materialization occurs **only on EA approval** — SOFIA does not self-modify its EA-gated encoded knowledge (cf. check 4).

*Aspirational checkpoints — mechanized enforcement is deferred, not CI-enforced at authoring.*

---

## Pre-Acceptance Conditions / Migration Path

**No pre-acceptance conditions. Ruling stands as authored.** **No Migration Path** (greenfield). Forward items (DDR-002 schema, DDR-003 governance, RG-retention policy, the SDDs) are forward *dependencies*, not acceptance conditions.

---

## Cross-References

- **Upstream implemented:** ADR-001 v1.1.0 (spine), ADR-002 v1.1.0 (system of record).
- **Sibling (forward):** DDR-003 — feedback-loop governance (**forthcoming, unauthored**); the architecture/governance split is settled (this DDR owns the data-path, DDR-003 owns governance).
- **Downstream consumers:** DDR-002 — graph schema; SDDs — knowledge-service, snapshot-service. *(One-way dependency: DDR-002 depends on this DDR; DDR-001 routes schema concerns forward to DDR-002 but does not depend on it.)*
- **Standards:** house conventions — self-managed-GKE exception (ADR-002 §2.2); data-classification tiers.

---

## Layer-of-Abstraction Note

This DDR operates at the data-substrate / platform-data-model layer; it constrains store choice, the plane model, persistence, and access, and is consumed by DDR-002 (schema) and the SDDs (service).

---

## Substrate-Stability Tracking

DDR-001 is substrate for DDR-002 (schema), DDR-003's scope boundary, and the SDDs. Amendments to the plane model, gateway pattern, or temporal model carry blast radius into those; the one-way dependency direction (DDR-002 depends on DDR-001, not the reverse) is explicit.

---

## Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.3.0 | 2026-07-03 | — | Triage-001 amendment batch (record: `agent-loop/triage/triage-001-distilled-set/record.md`). **Aggregate-confidence re-homed (T-01):** the session-root bullet drops "carries aggregate confidence"; confidence is per-conclusion (`ReasoningProgress` rollup, DDR-002 §4), any session-level aggregate a read-time traversal affordance, never a stored property — the per-Solution comparison intent moves to DDR-002's Named Gaps. **KG-entry checkpoint scoped (T-02):** Decision.5 second clause and conformance check 4 scoped to ADR-001 §2.5's object (SOFIA's own reasoning entering encoded knowledge); the broader all-KG-entry checkpoint routed by name to the forthcoming KG-entry-governance ADR. **Feedback-loop write authority recast (T-09):** the three-writes treatment and check 7 rewritten in author/executor/authorizer terms citing amended ADR-002 §2.6; Artifact write authority homed here (ASA authors `Solution` on creation; lifecycle-transition authority routed to SDDs). Decision.7 added. |
| 1.3.0 | 2026-07-03 | — | **Enterprise-edition requirement re-grounded (T-04):** the Spike Findings section is retired entirely (trial specifics never captured; recollection unreliable; single-database non-contradiction guard removed with the narrative); its durable content re-homes as Substitution-Contract Capability Bar item 6 — DB-enforced property-existence-constraint capability, the vendor-verifiable dependency the edition rests on (verified 2026-07-02). Rationale re-grounded on that present dependency. |
| 1.3.0 | 2026-07-03 | — | **Record-completeness / honesty (no decision change):** Decision list gains the feedback-loop write-authority component (Decision.7) citing amended ADR-002 (T-07); footnote ² adds the governance-participating-identities-only / no-IAM-mirror clause and per-action disposition-event exclusion (T-12); Firestore row's "concretized here as" preamble simplifies to a plain ADR-002 §2.4 citation (T-25); DDR-003 Cross-References entry gains the forthcoming/unauthored status marker (T-05 Leg 2); upstream references bumped to ADR-001 v1.1.0 / ADR-002 v1.1.0. |
| 1.2.0 | 2026-07-01 | — | Distilled to standalone contract form; ledger coupling, prior-corpus intent-source lineage, and revision-diary residue removed; cross-references qualified to source doc; documentation-purity pass folded in (session cardinality tightened, RG roles aligned to the DDR-002 edge model, one-way reference corrected to dependency, footnotes reordered, ASD expanded, Date normalized); no decision change. |
| 1.2.0 | 2026-06-23 | RBT-45 | Additive MINOR amendment. Homes write authority for the three feedback-loop writes to named, gateway-routed components (`CandidatePromotion` proposal → scheduled feedback-loop job, pre-approval; at-promotion provenance snapshot + materialized KG node → gateway, the latter on EA approval), reconciled against ADR-002 §2.6's component-scoped principle; adds conformance check 7. Write-authority only; `CandidatePromotion` graph-home deferred. |
| 1.1.0 | 2026-06-21 | RBT-39 | Operational plane redefined to durable distilled `ObservedPattern`s (no in-graph TTL); raw telemetry is an external system of record. |
| 1.0.0 | 2026-06-19 | RBT-12 | Initial authoring; ACCEPTED. |

---

## Appendix — Boundary Routing Map (DDR-001 vs the rest)

| Concern | Owner |
|---|---|
| Plane definitions, RG roles, gateway pattern, persistence patterns, feedback data-path, temporal posture, substitution bar, conformance checks | **DDR-001** (this) |
| Node/relationship/constraint contract; version/supersession/pinned-reference schema; `CandidatePromotion` schema | **DDR-002** |
| Feedback signal policies, thresholds, EA criteria, cadence, RG retention policy, promotion audit policy | **DDR-003** |
| Gateway API method contract; ingestion-adapter decomposition; snapshot triggers/types; revision-loop workflow; async realization; conformance-check mechanization | **SDDs** |
