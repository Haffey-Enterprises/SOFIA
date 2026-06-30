# File: docs/adr/ADR-002-graph-system-of-record.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises
# Created: 2026-06-15
# Description: ADR-002 — Graph as System of Record. Establishes the Neo4j Enterprise graph as the authoritative store for all SOFIA architecture and reasoning state, with the KG and RG realized as logical subgraphs in a single instance and state-class authority divided across a three-store persistence backbone.

# ADR-002: Graph as System of Record

| Field | Value |
|---|---|
| **Document ID** | ADR-002 |
| **Status** | ACCEPTED |
| **Version** | 1.0.0 |
| **Date** | 2026-06-15 |
| **Authors** | Thaddeus Haffey (LAA / SA / EA) |
| **Reviewers** | Three-hat (LAA/SA/EA) review of record: converged at Cycle 2 / Pass 2 (PASS), 2026-06-16. See §7. |
| **Supersedes** | None — establishes new platform principle. |
| **Amendment Process** | Changes require LAA + SA + EA approval. Material changes increment minor version; breaking changes increment major version. |

---

## 1. Context

SOFIA is at initial design. ADR-001 established the reasoning-architecture commitment — SOFIA is the reasoning-capture layer for the enterprise SDLC, operating at Position 5 on a trajectory toward Position 4, with the Knowledge Graph (KG) as the enterprise's unified ground-truth context and the Reasoning Graph (RG) as the platform's persistent institutional memory. ADR-001 committed the *capture invariant* — whoever reasons, SOFIA captures it in the RG with evidence linkage to the KG — but it deliberately deferred the structural questions on which that invariant depends: what store holds the graph, how the KG and RG are realized, and how authority over architecture and reasoning state is divided across the platform's stores.

No service is yet deployed and no per-phase design is yet accepted. The forcing function is the data and service architecture about to be committed: the Data Architecture design (DDR-001) and every service design that reads or writes architecture state need an authoritative answer to "where does state live, and what is the system of record?" before they can be authored — DDR-001 is blocked on this decision. Absent an explicit system-of-record commitment, the architecture drifts by default: services hold authoritative state in local stores, the KG/RG split degrades into an application-layer join rather than a first-class graph traversal, and the reasoning-capture invariant ADR-001 committed loses the durable, queryable home that distinguishes it from a logging convention.

This ADR ends that ambiguity. It commits the graph as the system of record for all SOFIA architecture and reasoning state, names the store and its persistence backbone, and fixes the division of authority on which the data and service architecture depend.

---

## 2. Decision

The Neo4j Enterprise graph is the system of record for all SOFIA architecture and reasoning state — the Knowledge Graph and Reasoning Graph realized as logical subgraphs in a single instance — with state-class authority divided across a three-store persistence backbone (Neo4j, PostgreSQL, Firestore).

### 2.1 Graph as system of record

The graph is the authoritative store for all SOFIA architecture and reasoning state — both the Knowledge Graph (enterprise ground-truth context) and the Reasoning Graph (captured inferences, evidence, and rejected alternatives per ADR-001 §2.2). Every authoritative state change to architecture or reasoning state flows through the graph. Services do not hold authoritative architecture or reasoning state in their local stores; a service's local store holds operational, cache, or staging state only, and reads authoritative state from the graph.

This is the structural commitment that makes ADR-001's reasoning-capture invariant durable: the RG is the system of record, queryable by traversal alongside the KG it links to, not a side-channel log that can drift from the decisions it records.

### 2.2 Graph platform — Neo4j Enterprise, self-managed on GKE

The system of record is a native graph database, realized by **Neo4j Enterprise**.

Enterprise is the committed edition because the five-plane KG — the planes plus the multiple edge types their traversals require — is a graph Community edition could not support: **Community was trialed for it and failed** (R3). The rejection is empirically established and ratified, not a preference. The trial itself predates the Reboot's formal capture, so its outcome is carried forward as ratified institutional memory; its durable home as a spike finding is **DDR-001's spike-findings section** — which records the outcome (and the specific Enterprise capability the plane model depends on) so the rejection stands without re-running the trial. A specific Neo4j minor-version pin is deferred to the data and operational designs (consistent with the topology deferral, §5.2); the edition (Enterprise) is the commitment fixed here.

**Deployment runtime.** The graph runs **self-managed on GKE** (R20) — the orchestrated-container exception to the platform's Cloud Run default, per the platform's stateful-workload deployment criterion: a stateful, clustered graph database cannot run on serverless-container Cloud Run, and there is no managed Neo4j option on GCP, so SOFIA accepts operational responsibility for self-managed Neo4j Enterprise on GKE. This ADR is the home for that runtime exception. Runtime placement (GKE) and production topology (cluster count / HA, deferred per §5.2) are distinct axes — only the latter is deferred.

**Substitution contract.** A replacement for Neo4j Enterprise must satisfy the plane-model graph at the complexity §2.3 commits (five planes plus Extension and the RG, with first-class cross-plane and cross-graph traversal); the precise capability bar is the one DDR-001 establishes. Substituting a graph platform that cannot meet it — or moving the runtime off self-managed GKE — is an amendment to this ADR, not an implementation detail.

### 2.3 Logical plane realization

The KG's planes (five planes plus an Extension plane) and the RG are **logical subgraphs within one Neo4j instance**, not physically separate databases. Cross-graph KG↔RG traversal — and cross-plane traversal within the KG — is therefore a first-class single-database graph operation, not an application-layer join across stores.

This ADR commits the logical-not-physical realization and the first-class-traversal property it preserves. The enumeration and definition of the planes, the KG/RG structure, and the traversal patterns are the Data Architecture design's (DDR-001), which this ADR precedes; this section references the plane model only as the forcing function for §2.2 and the realization commitment stated here.

### 2.4 Persistence backbone — three stores, no vector store

SOFIA's persistence backbone is **three stores**, with authority divided by state class:

- **Neo4j** — system of record for the KG and RG (architecture and reasoning state), per §2.1.
- **PostgreSQL** — workflow, audit, and staging state.
- **Firestore** — immutable workflow snapshots.

There is **no vector store**. Semantic retrieval — of precedents, patterns, directives, and standards — is graph-traversal-native, not delegated to a separate vector index. This both follows from the graph-as-system-of-record commitment and fits the deterministic Position 4–5 ethos (ADR-001 §2.3): graph-native retrieval over the enterprise context is deterministic and auditable where probabilistic vector similarity is neither.

The persistence *patterns* across these stores — the graph-gateway pattern, read/write paths, snapshot mechanics — are the Data Architecture design's (DDR-001). This section commits the store set and the division of authority.

### 2.5 Graph access authority

The graph system of record is accessed through a single sole-owner gateway. **knowledge-service is the sole holder of the Neo4j driver and the single graph-access boundary**: every other service and agent reads and writes graph state through knowledge-service's API rather than holding a direct Neo4j client. Concentrating graph access in one component — the KG/RG gateway — gives write-boundary enforcement (provenance, validation, data classification), driver lifecycle, and the single-source-of-truth guarantee exactly one place to live.

This ADR commits the access-authority *principle*. The gateway's API shape — its operations, contracts, and the read/write paths through it — is the Data Architecture design's graph-gateway pattern (DDR-001), not this ADR's.

### 2.6 Reasoning-state write authority

Write authority for reasoning state into the RG is component-scoped, not diffuse, and is exercised through the sole-owner gateway (§2.5). The **Architecture Solutioning Agent (ASA) is the authorized author of ReasoningProgress** — the reasoning-producing component authors its own progress into the Reasoning Graph — and the write **executes via knowledge-service's graph-write API**; ASA holds no direct Neo4j driver. The **Agent Orchestration Engine (AOE) owns the ReasoningSession lifecycle only** and does not author ReasoningProgress.

This is the system-of-record consequence of ADR-001's capture invariant: because the graph is authoritative for reasoning state (§2.1) and accessed through a single sole-owner gateway (§2.5), *which component is authorized to author that state* is a system-of-record decision, fixed here. The service-level realization — the ReasoningProgress artifact's fields and the write path through the gateway — is the relevant service design's (SDD), not this ADR's; this section fixes the authorship assignment and its routing through the gateway.

### 2.7 Data-protection posture — no CMEK, no PHI by design

The initial build uses **no customer-managed encryption keys (CMEK)**. This is sound because the platform carries **no PHI by design**: data classification at intake and ingestion is an enforced constraint that keeps PHI out of the system, with compensating controls as the backstop should any leak in. A future change that brings PHI into scope is its own ADR, which would re-evaluate CMEK; this ADR commits the no-CMEK / no-PHI-by-design posture for the initial build only.

---

## 3. Rationale

Once the graph is the system of record, the reasoning-capture invariant ADR-001 committed has a durable home: the *why* behind every architectural decision — the inference, the evidence it drew on, the alternatives it rejected — lives in the RG as authoritative, traversable state linked to the KG, not as a log that can drift from the decisions it records. Auditability and explainability become structural properties answerable by traversal, because the authoritative record *is* the graph rather than a derivative of it.

Fixing the store and its realization is also what makes the data and service architecture buildable without re-litigation. A single system of record with a defined division of authority means services share one authoritative state model rather than reconciling local copies; logical planes in one instance keep KG↔RG traversal first-class rather than degrading it into cross-store joins; and graph-native retrieval keeps semantic lookup deterministic and auditable rather than introducing a probabilistic index the Position 5 burden of proof (ADR-001 §2.3) would have to justify. The three-store backbone draws the authority lines — graph for architecture and reasoning state, relational for workflow and audit, immutable store for snapshots — so each downstream design inherits a clear answer to "where does this state live and who owns it."

---

## 4. Alternatives Considered

### 4.1 Alternative A — Neo4j Community (single instance)

*Description:* The same single-instance graph realization on the Community edition, avoiding Enterprise licensing.

*Rejection rationale:* Community was trialed for the five-plane KG — the planes plus the multiple edge types their traversals require — and could not support it; Enterprise is the empirically-established requirement (R3), not a preference. The plane model is not negotiable down to fit the edition; it is the structure the KG commits to. The spike result is carried as ratified institutional memory; its durable home — the outcome and the specific Enterprise capability the plane model depends on — is DDR-001's spike-findings section, so the rejection stands without re-running the trial each cycle.

### 4.2 Alternative B — Separate physical databases per plane / graph

*Description:* Realize the KG planes and the RG as physically separate databases rather than logical subgraphs in one instance.

*Rejection rationale:* Physical separation breaks first-class cross-graph traversal: KG↔RG and cross-plane queries become application-layer joins across stores rather than single-database graph operations. Because there are recurring reasons to traverse the KG and RG together — capture linkage, evidence retrieval, provenance queries — degrading that traversal to a cross-store join is a structural cost paid on every such query. Logical subgraphs in one instance keep the traversal native.

### 4.3 Alternative C — Retain a vector store for semantic retrieval

*Description:* Keep a dedicated vector index (e.g., a managed vector-search service) for semantic retrieval of precedents, patterns, directives, and standards, alongside the graph.

*Rejection rationale:* The vector store was an early pre-graph retrieval attempt, not a requirement of the KG/RG target. With the graph as system of record, semantic retrieval is graph-traversal-native — deterministic and auditable where vector similarity is probabilistic — a better fit for the Position 4–5 ethos and one that avoids a second retrieval substrate to keep consistent with the graph. A genuine future need for vector retrieval is its own ADR; carrying it speculatively now adds an unjustified store. (The three-store backbone in §2.4 is the direct consequence of this rejection: three stores, not four.)

### 4.4 Alternative D — CMEK on the graph store now

*Description:* Apply customer-managed encryption keys to the Neo4j volumes from the initial build.

*Rejection rationale:* CMEK is unjustified without PHI in the system. The platform is no-PHI-by-design with classification enforced at intake/ingestion, so the data CMEK would protect is, by design, absent. Adding CMEK now is operational cost and key-management surface with no corresponding data-sensitivity driver. A future PHI scope-change is the event that justifies revisiting CMEK, and it gets its own ADR.

### 4.5 Alternative E — Diffuse graph access (no sole-owner gateway)

*Description:* Each service holds its own Neo4j driver and reads and writes the graph directly, rather than routing through a single gateway service.

*Rejection rationale:* Diffuse direct-driver access multiplies the graph-write boundary across every service, so provenance, validation, and data-classification enforcement have no single place to live and must be re-implemented — and kept consistent — per service. It also widens the driver-dependency surface: every service becomes a place a graph-write invariant can be violated. A single sole-owner gateway (§2.5) concentrates enforcement and the driver lifecycle in one component, at the cost of that component sitting on the path of every graph access — a cost addressed by treating it as a scalable gateway, not a store.

### 4.6 Alternative F — Cloud Run / managed runtime for the graph

*Description:* Run the graph on the platform's serverless-container default (Cloud Run), or adopt a GCP-managed graph service, rather than self-managing Neo4j Enterprise on GKE.

*Rejection rationale:* This alternative is thin, by the honest standard — there is no managed Neo4j offering on GCP, and a stateful, clustered graph database cannot run on serverless-container Cloud Run. Self-managed Neo4j Enterprise on GKE is therefore the forced runtime, taken as the documented exception to the Cloud Run default (§2.2). The cost — operational responsibility for the self-managed cluster — is accepted and recorded as a constraint (§5.2).

---

## 5. Consequences

### 5.1 Positive Consequences

- Reasoning capture is durable and authoritative — ADR-001's RG invariant lives in the system of record, traversable alongside the KG, not in a drift-prone side log.
- Architecture and reasoning state have one authoritative model — services share the graph rather than reconciling local authoritative copies, removing split-brain between service stores.
- KG↔RG and cross-plane traversal is first-class — logical subgraphs in one instance keep capture-linkage, evidence retrieval, and provenance queries as native graph operations.
- Semantic retrieval is deterministic and auditable — graph-native retrieval over the enterprise context replaces a probabilistic vector index, consistent with the Position 5 burden of proof.
- The persistence authority lines are explicit — each downstream design inherits a clear "where does this state live and who owns it" across the three stores.
- Graph-access enforcement has a single home — the sole-owner gateway concentrates write-boundary validation, provenance, and classification in one component instead of spreading them across every service.

### 5.2 Constraints Imposed

- Services may not hold authoritative architecture or reasoning state locally — all such state flows through the graph; local stores are operational/cache/staging only.
- The platform is committed to Neo4j Enterprise's licensing and operational footprint for the system of record; a graph platform that cannot meet the plane-model complexity §2.2/§2.3 commit is not a drop-in substitute (§2.2 substitution contract).
- SOFIA accepts operational responsibility for the self-managed Neo4j Enterprise cluster on GKE (§2.2) — backup/restore, upgrade lifecycle, and cluster-health monitoring are platform burdens carried by the operational design, the accepted cost of the §25.1 self-managed exception over a managed runtime.
- No service other than knowledge-service may hold a direct Neo4j driver; all graph access routes through knowledge-service's gateway (§2.5).
- **Production topology is intentionally unspecified.** Cluster count and HA configuration are not committed by this ADR; they are determined after dev implement-and-test, sized to real workload rather than asserted as a premature minimum. Locking a specific cluster topology now (e.g., a three-node causal cluster) is rejected as a premature production commitment. Topology is independent of the CMEK posture (§2.7) and does not gate this ADR's acceptance.
- No vector store is available as a retrieval substrate; designs needing semantic retrieval use graph-native traversal, and a genuine vector need is a new ADR, not a local addition.
- No CMEK in the initial build; the no-PHI-by-design constraint must be enforced (classification at intake/ingestion) for the no-CMEK posture to remain sound.

### 5.3 Risks

- **PHI leaks in despite the by-design constraint.** If classification at intake/ingestion fails and PHI enters the graph, the no-CMEK posture (§2.7) is no longer sound. *Mitigation:* classification is an enforced constraint with compensating controls as backstop; a PHI scope-change triggers a new ADR that re-evaluates CMEK. The enforcement mechanism is a downstream design and compliance concern (see §6).
- **Single-instance scale or availability pressure.** Logical subgraphs in one instance concentrate the KG and RG in a single graph store; at scale or under availability requirements this could strain the single-instance realization. *Mitigation:* topology is deliberately deferred (§5.2) precisely so it is sized to real workload; the logical-plane commitment is about traversal locality, not a bar on Enterprise clustering, which the deferred topology decision can adopt.
- **Graph-native retrieval underperforms a vector index for some semantic workload.** Rejecting the vector store (§2.4) bets that graph-native retrieval suffices. *Mitigation:* a demonstrated retrieval need that graph traversal cannot meet is an explicit ADR trigger (§4.3), not a silent re-introduction; the bet is reversible by amendment with evidence.
- **The graph-access gateway is a chokepoint.** knowledge-service sits on the path of every graph read and write (§2.5); its availability gates all graph access. *Mitigation:* the gateway is an access layer over the graph, which holds the authoritative state, so it scales horizontally independent of the single-instance graph; gateway capacity and the graph's deferred topology (§5.2) are sized together at dev implement-and-test.

---

## 6. Compliance

Conformance with this ADR is verified at architecture review. The following are checked for every new SDD and DDR, and at each design pass that touches architecture or reasoning state:

1. **System-of-record check.** The design reads authoritative architecture/reasoning state from the graph and holds no authoritative state of those classes in a local store.
2. **Graph-access-authority check.** No service other than knowledge-service holds a direct Neo4j driver; the design accesses graph state through knowledge-service's gateway (§2.5), not a direct client.
3. **Store-authority check.** State the design persists is placed in the correct store per the §2.4 division of authority (graph / PostgreSQL / Firestore); no vector store is introduced.
4. **Traversal-locality check.** Designs touching KG/RG or cross-plane access use first-class graph traversal, not application-layer joins across stores.
5. **Write-authority check.** Designs that write reasoning state honor the §2.6 assignment (ASA authors ReasoningProgress, routed via knowledge-service; AOE owns ReasoningSession lifecycle only).
6. **Data-protection check.** Designs handling ingested data enforce the no-PHI-by-design classification (§2.7); any design that would bring PHI into scope is flagged as an ADR trigger, not absorbed.

**Enforcement.** These checks are enforced at three-hat (LAA/SA/EA) review — the gate every SDD and DDR passes through — at design time. Mechanized enforcement (CI / schema validators for the store-authority and write-authority checks, which are more mechanizable than judgment-based review) is not built yet. Compliance is currently aspirational; enforcement-mechanization is tracked at RBT-33. Until that lands, conformance is reviewed at SDD/DDR-authoring time and at three-hat architectural reviews.

---

## 7. Review and Approval

### Review Cycle 1

| Reviewer Role | Name | Date | Outcome | Findings |
|---|---|---|---|---|
| LAA | Thaddeus Haffey | 2026-06-15 | FINDINGS RAISED | M-2 — RBT-8 ledger-citation incomplete (R7/R12 absent). |
| SA | Thaddeus Haffey | 2026-06-15 | FINDINGS RAISED | B-1 (BLOCKING) — §6 unfilled enforcement-tracking placeholder; M-1 (shared) — GKE runtime unhomed; M-3 — Community-rejection capability unspecified. |
| EA | Thaddeus Haffey | 2026-06-15 | FINDINGS RAISED | M-1 (shared) — §25.1 GKE-runtime decision unhomed in this ADR. |

Cycle 1 → 1 BLOCKING + 3 MATERIAL + 2 COSMETIC (no-action), against a large set of POSITIVE no-drift confirmations. Review of record: `docs/reviews/2026-06-15-adr-002-three-hat-review.md`. SA at `pause` (B-1); gate not satisfied this cycle.

### Review Cycle 2

| Reviewer Role | Name | Date | Outcome | Findings |
|---|---|---|---|---|
| LAA | Thaddeus Haffey | 2026-06-16 | APPROVED | M-2 resolved (RBT-8 citation completed); no open findings. |
| SA | Thaddeus Haffey | 2026-06-16 | APPROVED | B-1 resolved (RBT-33); M-1 resolved (R20, §2.2 runtime); M-3 resolved (R3 clarification + DDR-001 routing); no open findings. |
| EA | Thaddeus Haffey | 2026-06-16 | APPROVED | M-1 resolved; new material (runtime, Alternative F, operational constraint) sound; no open findings. |

Cycle 2 → PASS (converged); all three hats `proceed`. Review of record: `docs/reviews/2026-06-16-adr-002-three-hat-review-cycle-2.md`. Forward dependency D-1 → RBT-12 (DDR-001 spike-findings must record the Community-trial outcome + named Enterprise capability).

### Final Approval

The three-hat LAA → SA → EA cycle converged at Cycle 2 / Pass 2 with all BLOCKING and MATERIAL findings resolved — anchored by Decision Ledger R3 (Community-rejection clarification), R7, R12, and R20; B-1 → RBT-33; M-2 → RBT-8 citation. ACCEPTED 2026-06-16.

---

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.0.0 | 2026-06-15 | RBT-8 | Original authoring. |

---

*End of ADR-002.*
