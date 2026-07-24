# File: docs/ddr/DDR-001-data-architecture.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: DDR-001 — Data Architecture. Realizes the Knowledge Graph and Reasoning Graph as co-resident logical subgraphs in a single Neo4j Enterprise instance, with a five-plane-plus-Extension KG, a three-store persistence backbone, a sole-owner graph gateway, and an EA-gated feedback loop — implementing ADR-002's graph-as-system-of-record commitment at the data-architecture layer.
# Revised: 2026-06-21 (RBT-39 — Operational plane → durable distillation, B-4)

# DDR-001 — Data Architecture: Knowledge Graph and Reasoning Graph

| Field | Value |
|---|---|
| **Document ID** | DDR-001 |
| **Version** | 1.1.0 |
| **Status** | ACCEPTED |
| **Date** | 2026-06-19 |
| **Authors** | Thaddeus Haffey (LAA / SA / EA) |
| **Supersedes** | None |
| **References** | ADR-001 v1.0.0; ADR-002 v1.0.0; ENG-STD-001 §25.1 (self-managed-GKE documented exception), §18.1 (data-classification tiers); Reboot Decision Ledger R3 / R5 / R6 / R7 / R8 / R9 / R10 / R20 / R22 / R24 / R26. *(Not DDR-002 — R8 one-way reference rule.)* |

---

## Decision

The Knowledge Graph (KG) and Reasoning Graph (RG) are realized as co-resident logical subgraphs in one Neo4j Enterprise instance, with a typed-plane KG, a three-store persistence backbone, a sole-owner gateway, and an EA-gated feedback loop — decomposed into testable sub-decisions:

- **Decision.1** — The Knowledge Graph and Reasoning Graph are **co-resident logical subgraphs in a single Neo4j Enterprise instance**.
- **Decision.2** — The KG is partitioned into **five typed planes** (Catalog, Environment, Operational, Governance, Standards) **plus an Extension layer**.
- **Decision.3** — Persistence is a **three-store backbone** — Neo4j (system of record), PostgreSQL (workflow/audit/staging), Firestore (immutable snapshots) — **with no vector store**.
- **Decision.4** — All graph access flows through a **single sole-owner gateway** (knowledge-service), the only holder of the Neo4j driver.
- **Decision.5** — A **scheduled, EA-gated feedback loop** promotes recurring RG findings into the KG; **SOFIA never self-modifies** the KG.
- **Decision.6** — This DDR owns **plane definitions and data-architecture patterns** (the architecture half of the R8 split); the node/relationship/constraint contract is **DDR-002's**.

---

## Rationale

This ruling is both empirical-grounded (the Community-edition rejection — see Spike Findings) **and** deliberation-grounded (the RBT-12 scoping session — the design substrate this DDR realizes). Together they over-satisfy the DIRECTIVE-034 §34.1 DDR-route substrate gate.

---

## Two-Graph Model

### Knowledge Graph — five typed planes + Extension

Enterprise ground truth ("what do we know?"). Consumers query the graph, never a plane directly (uniform access behind a common ingestion-port role). **Source systems are named by *class*, not vendor product.**

| Plane | Role | Source-class | Cadence | Illustrative node types |
|---|---|---|---|---|
| Catalog | approved-technology portfolio | enterprise architecture / portfolio catalog | batch | capabilities, technologies, patterns, IaC templates, solution documents |
| Environment | deployed reality | CMDB / service registry | daily + deploy-event | deployed services, environments, configuration items |
| Operational² | distilled operational knowledge | observability / AIOps telemetry (external SoR) | periodic distillation; durable (no in-graph TTL) | derived `ObservedPattern`s (weakness / strength trends) |
| Governance¹ | actors and decisions | IAM + SOFIA workflow events | event-driven | users, roles, approval decisions |
| Standards | normative corpus | EA standards repository | on-publish / versioned | enterprise standards, policy directives, compliance controls |
| Extension | open future sources | any registered source | per-plane adapter | extension nodes, plane definitions |

¹ *Disambiguated at first use: the Governance **plane** (actor/decision ground truth) is distinct from feedback-loop **governance** (DDR-003) and three-hat **governance**.*

² *Operational holds durable distilled `ObservedPattern`s — derived weakness / strength trends — not raw telemetry. The observability / AIOps telemetry is an external system of record (TTL-bounded there) from which `ObservedPattern`s are distilled; it is not itself a KG plane. Distillation mechanics → DDR-002; retention / archival policy → DDR-003. (R24 / R26.)*

**Cross-cutting KG invariants (label-free):** provenance on every node; **deterministic, not LLM-judged** (gap = required capability with no resolving technology; override = unsanctioned preference — graph facts, not model opinions); Operational holds **durable distilled `ObservedPattern`s** (no in-graph TTL; raw telemetry TTL-bounded in its external SoR); environment edges carry **confidence**; Extension is **bounded, not dynamic** (`PlaneDefinition` registration + schema-on-write; zero migration, zero impact on existing traversals).

### Reasoning Graph — four structural roles (bridged to ADR-002 §2.6 vocabulary)

SOFIA's persistent reasoning record ("how did we decide?"). **Two write authorities per ADR-002 §2.6 / R7: ASA authors reasoning *content* (`ReasoningProgress`); AOE owns the `ReasoningSession` lifecycle.** Four roles:

- **Session root — corresponds to `ReasoningSession`** — one per synthesis run / solution; the traversable root aggregating a run's reasoning; carries aggregate confidence. **Lifecycle owned by AOE.**
- **Typed conclusion** — a single reasoning conclusion of a known kind (illustratively: pattern selection, technology resolution, gap, override, risk, compliance evaluation). Part of `ReasoningProgress` (**ASA-authored**).
- **Evidence** — a KG-linked supporting fact, confidence **inherited from its source plane**; the traversable link from reasoning to ground truth. Part of `ReasoningProgress` (**ASA-authored**).
- **Rejected alternative** — a considered-and-discarded conclusion and why; the primary feedback-loop input. Part of `ReasoningProgress` (**ASA-authored**).

*(Session root corresponds to `ReasoningSession`; the other three compose `ReasoningProgress`. Formal labels/properties → DDR-002.)*

**RG invariants:** ASA is the **sole author of reasoning content** (`ReasoningProgress`); the **`ReasoningSession` lifecycle is owned by AOE** (§2.6 / R7). **All RG writes are gateway-mediated and driver-less** (§2.5). Capture is **non-blocking enrichment, not a synthesis gate**. **No PHI in reasoning state** (R10). Retention/TTL and read-access scoping are deferred (DDR-003 / SDD) — see the versioning model.

### Cross-graph edges — the same-store keystone

KG and RG are co-resident logical subgraphs (ADR-002 §2.3), joined by two cross-graph edge **roles**: **evidence linkage** (illustratively `SOURCED_FROM` / `DREW_FROM`) — RG → cited KG facts, making explainability a single-DB traversal; **promotion** (illustratively `PROMOTES_TO_KNOWLEDGE`) — the EA-gated feedback path. **Keystone:** first-class cross-plane and cross-graph traversal as single-store operations — never application-layer joins. This is the load-bearing reason the two graphs share one instance (ADR-002 §2.3 / R5).

---

## Versioning & Temporal Model

Carried as a named treatment so coverage is visible; explicit and complete, not retrofit. **Posture (ratified):** **version-pinned evidence + per-plane retention** — RG Evidence pins the cited KG version; versioned planes retain superseded versions (never delete); explainability resolves point-in-time by traversal to the pinned version (keystone preserved). **Prior-intent lineage:** prior-SOFIA DDR-021 (intent source, not a live Reboot reference; CLAUDE.md §3.4) — effective-dating / never-delete / version-at-generation; the mechanism is inherited, but the rationale is re-grounded on ADR-001's auditable-reasoning thesis, **not** the prior corpus's HIPAA framing.

**Two objects, versioned two ways:** (1) **KG ground truth** version-retained in Neo4j; (2) the produced **solution** dual-homed — graph node in Neo4j (relationships, for feedback traversal) + immutable per-version snapshot in Firestore (body, for revert/audit).

| Axis | Mechanism | Store | Owner |
|---|---|---|---|
| KG ground-truth versioning | effective-dating / supersession / never-delete | Neo4j | DDR-001 posture · DDR-002 schema |
| Evidence version-pinning | pins cited KG version | Neo4j | DDR-001 contract · DDR-002 field |
| Solution (ASD) versioning | dual-home: graph node + immutable per-version snapshot | Neo4j + Firestore | DDR-001 shape · SDD workflow |
| Operational distillation retention | durable `ObservedPattern`s; no in-graph TTL (raw telemetry expires in external SoR) | Neo4j | DDR-001 invariant · DDR-003 archival policy |
| RG retention posture | bounded + non-uniform; summary-on-evidence-expiry preserves explainability | Neo4j | DDR-001 posture · DDR-003 policy |
| Core schema evolution | additive via Extension; core-contract lifecycle | — | DDR-002 (named here via Extension) |
| Governance-decision immutability | append-only immutable facts | Neo4j | DDR-001 (closed here) |
| Feedback-promotion provenance | `PROMOTES_TO_KNOWLEDGE` + lineage; promoted ≠ ingested; auditable | Neo4j | DDR-001 architecture · DDR-003 audit policy |

---

## Hybrid Persistence Model

Three stores, authority by state class (R9 / ADR-002 §2.4):

- **Neo4j** — KG + RG (system of record) + in-graph per-plane version history.
- **PostgreSQL** — workflow / audit / staging.
- **Firestore** — ADR-002 §2.4's **immutable workflow snapshots**, **concretized here as immutable per-version snapshots of produced solutions (ASD bodies)** for revert/audit; append-only, point-in-time.
- **No vector store** (R6) — semantic retrieval is graph-traversal-native.

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

**Boundary enforces:** provenance; schema-on-write validation; classification (single no-PHI enforcement point, R10 / §2.7); version-pin resolution; driver lifecycle + single-source-of-truth.

**Prohibited:** any other direct driver; authoritative KG/RG state in local stores (local = cache/operational/staging only, §5.2); querying a plane directly.

**Port-substitutability:** roles are exposed as ports — the seam that makes the §2.2 substitution contract enforceable and an alternate adapter a port-swap.

**Boundary:** the *pattern* is owned here (DDR-001); the *API method contract* → knowledge-service SDD; the *schema* enforced → DDR-002; ingestion-adapter decomposition → SDD.

---

## Feedback-Loop Architecture (data-path; governance → DDR-003, per R22)

**Out-of-band by design** — a scheduled job over accumulated RG, not inline with synthesis. **Path:** detect (cross-graph traversal over RG + KG + Operational) → propose (`CandidatePromotion`) → **mandatory, non-bypassable EA gate** (the loop proposes, a human materializes) → materialize (real KG node + `PROMOTES_TO_KNOWLEDGE` edge, provenance-stamped). **Proposal-visibility invariant:** a `CandidatePromotion` is a distinct proposal class **excluded from synthesis ground-truth traversal**, materialized only on EA approval. **Signal/action classes (illustrative):** override-recurrence, gap-recurrence, evidence-quality; at least one action class — knowledge *promotion* (EA-gated) and *source-quality feedback* (feeds ingestion scoring, no promotion).

**Boundary (R22):** thresholds, signal definitions, EA criteria, cadence, and retention → DDR-003; `CandidatePromotion` schema → DDR-002; the scheduled job + EA-review portal → SDD.

---

## Spike Findings — Community → Enterprise

Recorded as ratified institutional memory (R3, closed / not re-derived). **Tested:** Neo4j Community against the five-plane / multi-edge model. **Result:** could not support it — Enterprise is the established requirement (empirical, not preference). **Learned:** the plane-model complexity §2.3 commits exceeds Community. **Capability requirement (structural, as the authority states it):** the five typed planes + Extension + RG as co-resident logical subgraphs in one instance, with the multiple edge types and the cross-plane / cross-graph traversal complexity their realization requires. **Recovery-boundary note:** the specific edition-feature blocker from the original trial is not in the captured record and is **not reconstructed here** (per R3). *(Deliberately avoids attributing the rejection to Community's single-database limit, which would contradict §2.3's logical-not-physical realization.)*

---

## Substitution-Contract Capability Bar (ADR-002 §2.2 routes here)

A replacement graph platform — or moving the runtime off self-managed GKE — is an ADR-002 amendment, not an implementation detail. A substitute must support:

1. the five typed planes + Extension + RG as co-resident logical subgraphs in one instance;
2. the multiple relationship/edge types the plane traversals require;
3. first-class cross-plane and cross-graph (KG↔RG) traversal as single-store operations;
4. in-graph version retention + point-in-time (as-of) resolution per the temporal model;
5. gateway-enforceable provenance, schema-on-write validation, and classification at the write boundary.

---

## Conformance Checks (aspirational; DIRECTIVE-024 §24.1, mechanization home RBT-33)

Downstream SDDs verify against:

1. All graph access routes through the sole-owner gateway; no other component holds a Neo4j driver.
2. No authoritative KG/RG state in local stores (local = cache/operational/staging only).
3. RG content is authored only by ASA (`ReasoningProgress`); `ReasoningSession` lifecycle only by AOE; both gateway-mediated.
4. `CandidatePromotion` proposals are excluded from synthesis ground-truth traversal until EA-approved; SOFIA never self-modifies the KG.
5. RG Evidence resolves to its pinned KG version (point-in-time explainability).
6. Every KG node carries provenance; promoted knowledge is distinguishable from ingested.

*Aspirational checkpoints — enforcement-mechanization is tracked at RBT-33 (broadened to "ADR-002 §6 + DDR-001 conformance checks": checks 1–3 are ADR-002 §6 surfaces, 4–6 are DDR-001-native), not CI-enforced at authoring.*

---

## Pre-Acceptance Conditions / Migration Path

**No pre-acceptance conditions. Ruling stands as authored.** **No Migration Path** (greenfield). Forward items (DDR-002 schema, DDR-003 governance, RG-retention policy, the SDDs) are forward *dependencies*, not acceptance conditions.

---

## Cross-References

- **Upstream implemented:** ADR-001 v1.0.0 (spine), ADR-002 v1.0.0 (system of record).
- **Sibling (forward):** DDR-003 (RBT-14) — feedback-loop governance; the architecture/governance split is **ledger ruling R22** (RBT-14 "or fold" branch **resolved to no-fold**).
- **Downstream consumers:** DDR-002 (RBT-13) — graph schema; SDDs — knowledge-service (RBT-15), snapshot-service. *(One-way: DDR-002 references this DDR, not the reverse — R8.)*
- **Standards:** ENG-STD-001 §25.1 (self-managed-GKE exception), §18.1 (data-classification tiers).
- **Intent sources:** prior-SOFIA DDR-037 / DDR-021 / `sofia-graph-build-context` (intent sources, not live Reboot references; CLAUDE.md §3.4).
- **Backlog:** RBT-12 (this), RBT-13 / RBT-14 / RBT-15, RBT-33 (conformance mechanization).

---

## Layer-of-Abstraction Note

This DDR operates at the data-substrate / platform-data-model layer; it constrains store choice, the plane model, persistence, and access, and is consumed by DDR-002 (schema) and the SDDs (service).

---

## Substrate-Stability Tracking

DDR-001 is substrate for DDR-002 (schema), DDR-003's scope boundary, and the SDDs. Amendments to the plane model, gateway pattern, or temporal model carry blast radius into those; the one-way reference direction is explicit.

---

## Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.1.0 | 2026-06-21 | RBT-39 | Operational plane → durable distilled `ObservedPattern`s (no in-graph TTL); telemetry = external SoR. Aligns plane definition to R24; clears B-4. (R26.) |
| 1.0.0 | 2026-06-19 | RBT-12 | Initial authoring — accepted on three-hat PASS-CONVERGED review of record (2026-06-19). |

---

## Appendix — Boundary Routing Map (DDR-001 vs the rest)

| Concern | Owner |
|---|---|
| Plane definitions, RG roles, gateway pattern, persistence patterns, feedback data-path, temporal posture, spike finding, substitution bar, conformance checks | **DDR-001** (this) |
| Node/relationship/constraint contract; version/supersession/pinned-reference schema; `CandidatePromotion` schema | **DDR-002** (RBT-13) |
| Feedback signal policies, thresholds, EA criteria, cadence, RG retention policy, promotion audit policy | **DDR-003** (RBT-14, per R22) |
| Gateway API method contract; ingestion-adapter decomposition; snapshot triggers/types; revision-loop workflow; async realization; conformance-check mechanization (RBT-33) | **SDDs** |
