# File: docs/adr/ADR-004-graph-fresh-schema-file-driven-ingestion.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-22
# Description: ADR-004 — Graph as Fresh Schema / file-driven ingestion. Commits that the SOFIA graph is instantiated greenfield from declared source artifacts, orchestrated by a driver-less loader utility that leverages knowledge-service — which remains the sole holder of the graph driver for schema provisioning and data alike — with no migration, no destructive-reset, and the Reasoning Graph preserved by construction.

# ADR-004: Graph as Fresh Schema / File-Driven Ingestion

| Field | Value |
|---|---|
| **Document ID** | ADR-004 |
| **Status** | PROPOSED |
| **Version** | 0.1.0 |
| **Date** | 2026-07-22 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — establishes new platform principle. |

---

## 1. Context

ADR-001 committed the reasoning-capture invariant and ADR-002 committed the graph as the system of record for all SOFIA architecture and reasoning state — the Knowledge Graph (KG) and Reasoning Graph (RG) as logical subgraphs in one instance, accessed through a single sole-owner gateway (knowledge-service, the sole holder of the graph driver). Neither settled how the graph is first *populated*: how an empty instance becomes the enterprise's ground-truth context, and how that first population relates to every subsequent update.

That question is now forcing. A development graph instance exists; the schema's data-definition half — the uniqueness, property-existence, and index constraints — has not yet been applied to it, and no ground truth has been loaded. The graph is empty: no ingestion and no promotion has occurred. Downstream, the ingestion port and the forthcoming architecture-ingestion design both need an authoritative answer to "how is the graph instantiated, and what is the relationship between first-load and steady-state update?" before they can be built or authored against a stable principle. Absent an explicit commitment, instantiation drifts toward the path of least resistance: a privileged load that bypasses the gateway at exactly the moment the graph's ground truth is established, a second component holding its own graph driver to apply schema out of band, or an implicit assumption that re-running a loader is a safe way to "reset" a live graph.

This ADR ends that ambiguity. It commits that the graph is instantiated fresh — greenfield, with no migration from any prior corpus or graph — and that instantiation, both schema provisioning and data load, is orchestrated by a driver-less loader that leverages knowledge-service, so the sole-owner-of-the-driver line established by ADR-002 holds for the very first write as it does for every later one.

---

## 2. Decision

The SOFIA graph is instantiated **greenfield from declared source artifacts**, and instantiation — schema provisioning and data load alike — is orchestrated by a **driver-less loader utility that leverages knowledge-service's ports**. knowledge-service remains the **sole holder of the graph driver** for data-definition and data writes both; no other component holds a graph driver. There is **no migration**: the graph is authored fresh, prior-corpus material is reference-only and never a starting point, and the instantiation path has **no destructive-reset mode**. Instantiation writes the Knowledge Graph only and preserves the Reasoning Graph by construction.

### 2.1 Instantiation is file-driven ingestion through the gateway

Populating the graph is an act of *ingestion*, not a privileged bypass. All graph state entering the graph at instantiation — every node and edge of ground truth — flows through the knowledge-service ingestion port and is subject to its enforcement (schema-on-write against the target plane definition — a plane being one of the KG's schema-defined partitions — data classification, and provenance stamping), exactly as steady-state updates are. There is no direct-driver path and no direct graph-query-language (Cypher) path for instantiation data. The graph is populated the same way it will forever be updated; the first load exercises the same contract as the thousandth. The loader utility that drives instantiation calls this port; it holds no graph driver of its own.

### 2.2 Schema provisioning holds the sole-driver line

The schema's data-definition half — the constraints and indexes the gateway validates writes against, expressed in the graph's data-definition language (DDL) — is provisioned **through knowledge-service**, which is committed here to expose a schema-provisioning capability — an addition its service design does not yet enumerate, gained as a named obligation of this decision — exercised over the graph driver it already holds. Provisioning is a distinct administrative operation, not the schema-on-write data path, so there is no circularity in knowledge-service laying down the constraints its later data writes validate against, and it is ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards. The driver-less loader utility invokes this capability to bring an instance to schema-ready before it loads data; the service process can start and connect to an empty instance, so provisioning runs before readiness reports green (which checks that the schema is present). **No component other than knowledge-service holds a graph driver — for data-definition or for data.** This keeps the sole-owner-of-the-driver principle intact for instantiation rather than carving an exception into it. Ownership of constraint *versioning* over the platform's life — how the provisioning capability evolves a live instance's constraints — is a forward question, governed by construction (it is a knowledge-service operation, not an out-of-band path) but with its policy not settled here — tracked as a forward item against the schema-provisioning capability's design.

### 2.3 Fresh, not migrated

The graph is instantiated as a fresh product. There is no migration path: no prior graph is carried forward, and prior-corpus material — including archived predecessor designs and the legacy corpus — is **reference-only, never a structural starting point**. "Fresh schema / no migration" binds the *origin* of the graph and forbids recreating legacy structure; it is not a license to reset or rebuild a populated instance (§2.4).

### 2.4 Additive by supersession, never destructive

File-driven ingestion is **additive by supersession**, never a destructive wipe-and-reload. It is one operation whose behavior is selected per node by the graph's current state, not by a loader mode: against an empty instance every business key is new and is created; against a populated instance a changed versioned-ground-truth node supersedes its predecessor under the schema's supersession discipline (planes that age or distill follow their own per-plane discipline), an unchanged business key introduces no new version, and a genuinely new business key is created. Changing the authoritative content of a versioned ground-truth node therefore requires an explicit **version increment in the source artifact**, which supersedes the predecessor and retains it; there is no in-place overwrite of ground truth. True re-instantiation — an empty instance becoming populated — is a per-instance event (a new environment, or disaster recovery), never a means of resetting a live graph, because the never-delete and supersession disciplines make the live path additive. The instantiation path exposes **no destructive-reset operation**.

### 2.5 KG-scoped; the Reasoning Graph preserved by construction

Instantiation from source artifacts writes the **Knowledge Graph only**. The Reasoning Graph is emergent institutional memory with no source-of-record artifact; it is written solely by the reasoning-capture path and is **neither written, reconstructed, nor discarded by instantiation**. In steady state, re-ingestion supersedes KG versions while the RG is untouched, and captured evidence continues to pin the specific KG versions it read — point-in-time fidelity is preserved, not staled. On a true re-instantiation of an empty instance, only the KG is restored from source; **the RG is not source-recoverable and must not be presumed so** — its durability across instance loss rests on instance-level backup and restore. In the current development runtime that responsibility sits with the managed graph provider; the production runtime, and therefore its backup posture, is deferred (see §5.3). The instantiation path having no destructive-reset mode (§2.4) is the structural guarantee that the reasoning-capture invariant suffers no silent RG loss: nothing in the instantiation path can discard reasoning state.

### 2.6 The source-artifact contract — principle, not format

Instantiation is driven from source artifacts satisfying four properties, whichever concrete format realizes them:

- **Declared, human-reviewable artifacts.** The unit of instantiation is a declared artifact a human can read and verify — not hand-run statements and not code. The bytes a human reviews for fidelity are the bytes that load.
- **Self-describing authority.** Each artifact declares the plane it populates and pins the schema authority (version) it conforms to, so load-time validation runs against a declared, verifiable contract rather than an assumption.
- **Deterministic and order-declared.** Instantiation is deterministic, and load order is declared so that cross-referencing planes resolve in a defined sequence.
- **One artifact, both surfaces.** A single artifact is simultaneously the human-review surface and the machine-load source; a divergence between the two is a defect, not a degree of freedom.

The concrete source-artifact format, its adapters, and their decomposition are the forthcoming architecture-ingestion design's; the enforcing port is the knowledge-service design's. This ADR fixes the properties any such format must satisfy, and does not restate a format. The ingestion port is adapter-agnostic, so file-based instantiation is the committed first realization, and additional source adapters are an additive design concern, not an amendment to this ADR.

### 2.7 Authoritative-source fidelity control

Instantiation of authoritative-source ground truth (the selection-catalog and standards planes) is subject to the fidelity control the ground-truth-mutation governance record commits: a **provisional-versus-official distinction**, where captured representations enter provisionally and **official, consumable entry is gated behind a human fidelity verification** that the captured representation faithfully reflects its authoritative source. That control's existence, its provisional-to-official shape, and its scope (the authoritative-source class, per-write) are the governance record's; this ADR **realizes that control for instantiation** and is the record the governance record names as the home of the ingestion-mechanics *authority* — the decision that authority is routed to, distinct from the port-level mechanics that realize it. Two commitments follow here: the gate is scoped to the authoritative-source class — it is not applied to the ungated Environment observation stream or to externally-decided mirrored records (the Operational distillation class carries its own review control and is out of scope here); and **read-exclusion of provisional ground truth is committed as a schema-level invariant** — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered. That invariant is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries, mirrored by the port's behavioral contract. The port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's.

### 2.8 Write authorship of instantiation

Every authoritative graph write at instantiation has a **named author**, per the platform's write-authority principle; authorship is never diffuse. The **author is the accountable authority declared by the source artifact** — a human curator, and for the authoritative-source class the human fidelity verifier of §2.7 — and the write **executes through the gateway, which is the sole executor and never the author.** The loader utility that orchestrates instantiation is neither author nor executor; it is the relay between the declared source artifact and the gateway.

---

## 3. Rationale

Making instantiation an act of ingestion is what keeps the graph's enforcement boundary intact from the first node. Provenance, classification, and schema-on-write validation matter most precisely at the moment ground truth is established; routing the first load through the same gateway as every later write means the seed is not a trusted special case but a verified one, and that the path real updates take is exercised on day one rather than first tested in production.

Holding schema provisioning inside knowledge-service — rather than granting a second component its own graph driver to apply constraints out of band — keeps that same single boundary whole for the data-definition half. The service already holds the driver; a distinct provisioning operation over it is not the data path and raises no circularity, so there is no forcing function for a second driver. A driver-less loader that leverages the service to provision and then to load preserves the one-write-boundary property the system-of-record decision rests on, and it makes constraint evolution over a live instance a governed operation of the sole owner rather than a standing out-of-band path. The cost is honest and bounded: the service gains a provisioning capability, and constraint application is located in that capability rather than left to an out-of-band deploy-time script — fixing where it belongs before any such script hardens into practice (the schema's data-definition half is, as §1 notes, not yet applied).

Committing "fresh, not migrated" and "additive, never destructive" together preserves the durability the platform exists for. Because the schema retains superseded versions rather than deleting them, and because instantiation supersedes rather than overwrites, re-running the loader accretes history instead of resetting it — and the reasoning record, which has no source artifact to rebuild from, is never placed at risk by a data-load operation. Scoping instantiation to the KG and forbidding a reset mode turns "no silent loss of reasoning" from an aspiration into a structural property of the instantiation path.

Finally, driving instantiation from declared, reviewable artifacts is what makes the authoritative-source fidelity gate coherent: a human can verify an artifact and then load exactly what was verified, and that same human is the write's accountable author. The deterministic, order-declared, authority-pinned artifact is the object that fidelity review, authorship, and machine load can share.

---

## 4. Alternatives Considered

### 4.1 Alternative A — Privileged bulk load bypassing the gateway for the first load

*Description:* Load the initial ground truth with direct-driver bulk statements, bypassing the ingestion port for instantiation and reserving the gateway for steady-state writes only.

*Rejection rationale:* This bypasses schema-on-write, classification, and provenance enforcement at exactly the moment the graph's ground truth is established — the highest-stakes write there is. It makes the seed a special case that never exercises the path real updates take, so the first genuine test of the ingestion contract is deferred to a later load. And it re-introduces a second write boundary the system-of-record decision already rejected as a diffuse-access hazard: a load path with its own driver is a place a graph-write invariant can be violated. The first load is the strongest reason to route through the gateway, not an exception to it.

### 4.2 Alternative B — A separate schema-provisioning tool holding its own graph driver

*Description:* Provision the schema constraints from a pre-gateway utility (or deploy-time script) that holds its own graph driver, sanctioned as a narrow, content-bounded exception to the sole-driver rule.

*Rejection rationale:* This was considered and rejected: any second holder of the graph driver is precisely the diffuse-driver hazard the system-of-record decision forecloses, and bounding the exception by content rather than by time licenses a standing pre-gateway path that could evolve a live instance's constraints out of band. It is also runtime-specific. Because the service already holds the driver and a provisioning operation over it raises no circularity, the exception buys nothing: concentrating schema provisioning in the sole owner, invoked by a driver-less loader, is both more consistent with the sole-owner principle and strictly less machinery than sanctioning and then having to reconcile an exception.

### 4.3 Alternative C — Destructive re-instantiation (wipe-and-reload from source)

*Description:* Treat each instantiation run as a rebuild — clear the graph and reload it from the current source artifacts — reading "no migration" as license to reset.

*Rejection rationale:* This violates the never-delete and supersession disciplines the schema commits, and it structurally endangers the Reasoning Graph, which has no source artifact to rebuild from — a wipe-and-reload would silently discard reasoning state that no source can restore. "No migration" binds the graph's origin (greenfield, no predecessor carried forward), not the behavior of a loader against a populated instance. The additive-by-supersession path delivers the same "graph reflects current source" outcome without destroying history or risking the reasoning record.

### 4.4 Alternative D — Ratify the concrete source-file format into this ADR

*Description:* Fix the file's structure — frontmatter fields, the payload block, serialization rules, load-order convention — as normative content of this ADR.

*Rejection rationale:* The concrete format is the province of the forthcoming architecture-ingestion design and the enforcing port, not a platform principle. Restating a format here creates a standing drift surface: two documents that must be kept in sync, one of which is the wrong altitude to own it. Fixing the *properties* any format must satisfy, and pointing to the owning design for the format itself, keeps this ADR at principle altitude and lets the format evolve without amending a platform record.

---

## 5. Consequences

### 5.1 Positive Consequences

- The graph's enforcement boundary is intact from the first node — provenance, classification, and schema-on-write apply to instantiation exactly as to steady-state writes.
- The sole-owner-of-the-driver line holds for schema provisioning and data alike — no second component holds a graph driver, and no exception to the principle is carved.
- Instantiation exercises the same path real updates take, so the ingestion contract is proven by first use rather than tested late; the seed rehearses steady state.
- Instantiation is deterministic and auditable — order-declared, authority-pinned source artifacts produce a repeatable graph.
- The authoritative-source fidelity gate is coherent and its authorship is accountable — a human verifies an artifact, is the write's named author, and loads exactly what was verified.
- The Reasoning Graph is safe *from instantiation-caused loss* by construction — no data-load operation can write, reconstruct, or discard it; durability against instance loss is a separate matter, resting on backup/restore (§2.5, §5.3).

### 5.2 Constraints Imposed

- No component other than knowledge-service holds a graph driver — for data-definition or data; the loader utility holds none and leverages knowledge-service's ports.
- No direct-driver and no direct-query-language data path exists for instantiation; all graph state enters through the ingestion port.
- Changing versioned ground truth requires a version increment in the source artifact — supersession, never in-place overwrite.
- Authoritative-source ground truth enters provisionally and reaches official, consumable state only through a human fidelity verification; provisional nodes are read-excluded from synthesis until then; the ungated Environment observation stream and mirrored externally-decided records are not gated.
- The instantiation path exposes no destructive-reset operation; dropping or recreating an instance is a separately-governed explicit act, never triggerable by ingestion.
- Every instantiation write names its accountable author; the gateway is the sole executor and never the author.

### 5.3 Risks

- **Instantiation is unproven until the first real load.** This record fixes the form of the instantiation path; that an instantiate-from-empty run works end-to-end against the live graph is demonstrated at the ingestion-port build, not asserted here. *Mitigation:* the first load is an explicit build-time acceptance step, not a background assumption.
- **The Reasoning Graph is not source-recoverable.** Because the RG has no source artifact, its durability across an instance-loss event depends on instance-level backup and restore. In the development runtime this is the managed provider's responsibility; the production runtime and its backup posture are deferred. *Mitigation:* the ADR names re-instantiation as KG-only so backup/restore is understood as the RG's only recovery path; the backup discipline itself is an operational concern the deferred production-runtime decision carries.
- **Constraint-versioning ownership over the platform's life is deferred.** Provisioning is governed by construction (a knowledge-service operation), but how it evolves a live instance's constraints over time is not settled here. *Mitigation:* the operation's location in the sole owner keeps any future evolution on the governed path; the versioning policy is a named forward question, not a silent gap.
- **The fidelity-gate mechanism is downstream.** The enforcement *locus* is fixed (a forthcoming schema read-discipline invariant, mirrored by the port contract), but the port mechanics — provisional-state representation and the official-entry transition — land with the ingestion-port build. *Mitigation:* the locus being committed makes the compliance check falsifiable; the mechanism is a named build obligation, and until it lands the gate's guarantee is stated conditionally on that enforcement.

---

## 6. Compliance

Conformance is verified at the platform's three-hat architecture review (its lead-application, solution, and enterprise-architecture stances) for every design that instantiates or ingests graph state, and at the schema-conformance harness where a check is mechanizable:

1. **Data-through-gateway.** No design introduces a direct-driver or direct-query-language data path for instantiation; instantiation state flows through the ingestion port, and the loader holds no graph driver.
2. **Sole-driver-for-schema-too.** Schema provisioning runs through knowledge-service's driver; no component other than knowledge-service holds a graph driver, data-definition included.
3. **Additive-not-destructive.** Instantiation and re-ingestion supersede versioned ground truth (on a version increment) or add no version (on unchanged content), with age/distill planes following their own per-plane discipline; no design introduces a destructive-reset or wipe operation in the instantiation path.
4. **KG-scoped / RG-preserving.** No instantiation operation writes, reconstructs, or discards Reasoning-Graph state.
5. **Source-artifact conformance.** Instantiation sources are declared, human-reviewable artifacts that pin the schema authority they conform to and declare their load order.
6. **Fidelity gate.** Authoritative-source ground truth reaches official, consumable state only through a human fidelity verification, and provisional nodes are read-excluded from synthesis until then; the ungated Environment observation stream and mirrored externally-decided records are not gated.
7. **Write-authorship.** Every instantiation write names its accountable author (the source artifact's declared curator or fidelity verifier); the gateway is named as sole executor, never as the author.
8. **Reference-not-migration.** No instantiation source carries forward predecessor-corpus structure as a starting point; prior corpora inform, they do not seed.

Checks 1–4 and 8 are largely mechanizable and map onto the schema-conformance harness's write-path and read-discipline invariants as that coverage extends; checks 5–7 are review-judgment until the fidelity-gate and write-authorship mechanics land, at which point check 6 gains a mechanized read-discipline mirror.

---

## 7. Cross-References

- **ADR-001 (Reasoning Architecture)** — the reasoning-capture invariant this ADR protects on instantiation (ADR-001 §2.2); the durability of the RG that "no destructive-reset" makes structural.
- **ADR-002 (Graph as System of Record)** — the graph as system of record for KG/RG state (ADR-002 §2.1), the sole-holder-of-the-driver principle instantiation preserves for schema and data (ADR-002 §2.5), the author/executor write-authority principle §2.8 discharges (ADR-002 §2.6), and the managed-runtime backup/restore responsibility on which RG recovery rests (ADR-002 §5.2).
- **ADR-008 (Ground-Truth Mutation Governance)** — the authoritative-source fidelity control this ADR realizes for instantiation (ADR-008 §2.2, §5.2); this record is the "forthcoming file-driven ingestion decision record" that governance record names as the home of ingestion-mechanics authority.
- **DDR-001 (Data Architecture)** — the graph-gateway pattern instantiation uses and whose sole-driver prohibition it preserves; the bounded RG-retention posture.
- **DDR-002 (Graph Schema)** — the supersession discipline instantiation is additive under (DDR-002 §6), the never-delete and read-discipline invariants (DDR-002 §7), to which the fidelity-gate read-exclusion invariant is a forthcoming addition, and the plane-definition and declaration model source artifacts validate against (DDR-002 §2.6).
- **DDR-004 (Inherited Confidence Derivation)** — the confidence semantics captured evidence inherits from the versions instantiation supersedes.
- **SDD-001 (knowledge-service)** — the readiness posture under which the schema is checked present (SDD-001 §3.1) and the ingestion port instantiation flows through, which is to gain the schema-provisioning operation and carry the forthcoming fidelity-checkpoint amendment (SDD-001 §3.6).
- **The forthcoming architecture-ingestion design** — owns the concrete source-artifact format, the loader utility, and the adapters realizing the §2.6 properties.
- **Reboot Decision Ledger** — R2 (author-clean / fresh-product, no migration), R12 (fresh-set inventory ratified).

---

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-22 | RBT-10 | Original authoring; PROPOSED. Greenfield graph instantiation as file-driven ingestion through the sole-owner gateway, with schema provisioning held inside knowledge-service (sole graph-driver holder for data-definition and data alike) and orchestrated by a driver-less loader utility; no migration (prior corpora reference-only); additive-by-supersession with no destructive-reset; KG-scoped with the RG preserved by construction; the four source-artifact principle-properties; the authoritative-source provisional-to-official fidelity control with read-exclusion homed as a schema read-discipline invariant (discharging the ground-truth-mutation governance record's forward-reference); and named write-authorship for instantiation. |
