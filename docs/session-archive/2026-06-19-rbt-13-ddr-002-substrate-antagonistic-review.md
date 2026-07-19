# File: docs/reviews/2026-06-19-rbt-13-ddr-002-substrate-antagonistic-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: Antagonistic review (DIRECTIVE-032) of the DDR-002 Graph Schema ratified design substrate (v0.2). Pressure-tests every assumption and design decision for gaps, loopholes, and authoring-blocking defects before the substrate is used to author DDR-002.

# Antagonistic Review — DDR-002 Graph Schema Design Substrate (v0.2) — 2026-06-19

| Field | Value |
|---|---|
| **Review Date** | 2026-06-19 |
| **Reviewer** | claude.ai antagonistic reviewer (LAA / SA / EA hats), under DIRECTIVE-032 — verification-only; corrective authoring returns to the primary session (§32.3) |
| **Scope** | The ratified design substrate `DDR-002-graph-schema-design-substrate-v0.2.md` (RBT-13), evaluated as the authoring source for `docs/ddr/DDR-002-graph-schema.md` |
| **Authority** | Operator invocation of an antagonistic pass (DIRECTIVE-032 §32.1, major-deliverable boundary); fresh-fetched canon: RBT-13/RBT-12 (Linear), Reboot Decision Ledger (Notion), ADR-001, ADR-002, governance corpus |
| **Outcome** | **PASS WITH FINDINGS (BLOCKING present) — do not author until B-1…B-3 are dispositioned.** 3 BLOCKING, 17 MATERIAL, 6 COSMETIC, against a substantial POSITIVE no-drift set. Convergence not reached this pass. |

---

## §0 Reviewer stance and scope boundary

This is a deliberately adversarial pass. Its job is to find what breaks if Claude Code authors DDR-002 from this substrate — internal inconsistency, dangling references, unassigned authority, under-defined contract surfaces, conformance holes, and loopholes a downstream SDD or implementer could drive through.

**What this review does not do.** It does not relitigate closed rulings. R3 (Neo4j Enterprise edition), R5 (logical planes), R6 (vector-out), R8 (architecture/schema split), R9 (three-store), R10 (no-PHI/no-CMEK), R23/R24/R25, and the closed Option sets are ratified institutional memory and are treated as fixed. Every finding below challenges the **substrate's application** of those rulings, or the **completeness of the schema contract** — not the rulings themselves. Where a finding touches a ruling, it argues the substrate under-realizes or mis-applies the ruling, never that the ruling is wrong.

**Known reviewer blind spots (DIRECTIVE-032 §32.4.1).** (1) Cross-block internal consistency was checked manually, not mechanically — propagation drift between blocks may remain. (2) This is design-time review of authored content; runtime behavior (Neo4j constraint expressivity at the exact versions, gateway transactional semantics, CI mechanization) is deferred to runtime verification. (3) **A material source was unavailable:** DDR-001's accepted body is neither in project knowledge nor fetchable (private-repo `get_file_contents` 404). DDR-002's vocabulary alignment with DDR-001's RG/feedback-loop architecture is therefore asserted by the substrate and unverified here (see M-14).

---

## §1 Scope

### 1.1 In-scope
- `DDR-002-graph-schema-design-substrate-v0.2.md` §0–§8 + Appendix — every node schema, edge, constraint, invariant, posture, and routing claim.
- Conformance of the substrate against its governing rulings (R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25), ADR-001 (esp. §2.2 capture invariant + label-ownership delegation), and ADR-002 (esp. §2.5 gateway authority, §2.6 write authority, §6 conformance checks).
- Fitness of the substrate as DIRECTIVE-034 deliberation substrate and as a fill-source for the DDR template's mandatory sections.

### 1.2 Out of scope (deliberately)
- The ratified rulings' correctness (closed; see §0).
- DDR-001 / DDR-003 / the SDD bodies — referenced only as boundary counterparties.
- The eventual three-hat review **of record** for DDR-002. This antagonistic pass is upstream of, and does not substitute for, that gate (DIRECTIVE-007 / DIRECTIVE-032 §32.3).
- ADR-002's own header identity straggler (`Enterprise Architect, Haffey Enterprises`) — that is RBT-36's sweep, not this DDR's.

---

## §2 Findings

### 2.1 BLOCKING — must resolve before the DDR-002 authoring gate proceeds

#### Finding B-1: The capture invariant's audit-critical RG nodes lose their only DB-enforceable provenance — and the substrate itself leaves this an open design call

**Location:** §1 Provenance; §4 RG-provenance posture (M-5 "flagged for confirmation"); §7 existence constraints.

**Description:** `Evidence` and `RejectedAlternative` deliberately omit the provenance group; their provenance is asserted to be "structural" — `Evidence` via `SOURCED_FROM` + `source_node_version`, `RejectedAlternative` via its parent `REJECTED` edge. The provenance **existence constraint** is then scoped to "KG nodes + the two authored RG types," explicitly excluding the two derived RG types. The substrate flags this as "the one Pass-1 finding whose resolution is a design call — confirm before authoring."

Two problems compound. (a) It is an **unresolved design call** on the auditability of exactly the nodes ADR-001 §2.2 makes first-class (the evidence, and the rejected alternatives). A document cannot be promoted to ACCEPTED with an open ruling on its keystone invariant. (b) The structural surrogate is **not DB-enforceable**: Neo4j cannot constrain "every `Evidence` MUST have a `SOURCED_FROM` edge" (the substrate concedes in §3 that cardinality is not constrainable). So the derived RG nodes' provenance rests entirely on a *conformance check* — which ADR-002 §6 itself describes as aspirational and not-yet-mechanized (RBT-33). Net effect: the "why" of every captured decision is protected, for these nodes, only by an unbuilt check.

**Why blocking:** This is the reasoning-capture invariant — SOFIA's reason to exist (CLAUDE.md anti-simplification clause). Authoring a DDR that ships the capture invariant's audit trail on an honor-system check, while a core design question is still open, fails the ADR-001 §2.2 / ADR-002 §6 conformance bar at three-hat.

**Risk if not addressed:** Evidence or RejectedAlternative nodes created without their structural-provenance edges are undetectable until RBT-33 lands; the audit chain (`promoted node → … → Evidence → SOURCED_FROM → original facts`, §5) silently breaks; "explainable and auditable" degrades to "auditable when the writer remembered to wire the edge." This is precisely the drift-to-logging-convention failure ADR-002 §2.1 was written to prevent.

**Disposition (returns to primary session):** Resolve the design call before authoring. Preferred direction: make structural provenance *enforceable* — promote `SOURCED_FROM` (and `RejectedAlternative`'s parent linkage) to a generating-rule with a startup/CI assertion in the **DB-enforceable-where-possible** tier, not the aspirational tier; or carry the lightweight group on all four RG types and accept the redundancy. If the team accepts the surrogate-only posture, it must be an explicit, ratified risk acceptance with the exposure named, not a "flagged for confirmation."

#### Finding B-2: The proposal→fact write path (`CandidatePromotion` → `PROMOTES_TO_KNOWLEDGE`) has no assigned write authority at the system-of-record level

**Location:** §5 CandidatePromotion + promotion edges; §4 write authority; §7 write-authority invariant; §8 routing ("CandidatePromotion aggregation → detection/promotion SDD").

**Description:** ADR-002 §2.6 fixes reasoning-state **authorship** as a system-of-record decision ("*which component is authorized to author that state* is a system-of-record decision, fixed here"). It assigns exactly two: ASA authors `ReasoningProgress`; AOE owns `ReasoningSession` lifecycle. The substrate introduces `CandidatePromotion` in the `Reasoning:` namespace and the `PROMOTES_TO_KNOWLEDGE` edge that **writes KG ground truth** — and defers its writer to "the detection/promotion SDD." So the single most sensitive write in the platform (the one that turns a proposal into authoritative fact) has no authority fixed at the layer ADR-002 says must fix it.

**Why blocking:** ADR-002 §6 check #5 (write-authority) is a mandatory three-hat check. A reviewer applying it will find that authorship of a reasoning-namespace node that mutates the KG is unspecified. Either `CandidatePromotion` is reasoning state (then its authorship is a SoR decision ADR-002 §2.6 did not make, and DDR-002 cannot silently delegate it to an SDD) or it is not reasoning state (then its `Reasoning:` label and RG placement are wrong). Both branches block.

**Risk if not addressed:** The promotion path becomes the platform's widest write loophole — any service the SDD layer happens to wire can author a `CandidatePromotion` and execute `PROMOTES_TO_KNOWLEDGE`, injecting un-gated nodes into ground truth. The EA-gate (§5) is only as strong as the rule that *nothing else* writes promoted nodes, and that rule is currently unwritten.

**Disposition:** Escalate the authorship question. Decide at DDR/ADR level which component authors `CandidatePromotion` and which executes the `PROMOTES_TO_KNOWLEDGE` write (and confirm both route through knowledge-service per §2.5). If this is judged an ADR-002 §2.6 gap, that is an ADR-002 amendment trigger, not a DDR-002 silent fill.

#### Finding B-3: The edge catalog references a `Process` node type the schema does not define

**Location:** §2.5 (`PRESCRIBES → … | Process`); §3 Standards edges (`PRESCRIBES`) and Governance edges (`(Attestation)-[:FOR_PROCESS]->(Process)`); §8 conscious exclusions ("The `Process` node type … deferred").

**Description:** Two edges in the binding edge catalog target `Process`, while §8 lists `Process` as a *conscious exclusion / deferred*. The DDL/contract the DDR emits would therefore bind relationships to an undefined label. The schema is internally inconsistent: it both defers the node and ships edges to it.

**Why blocking:** A binding node/relationship/constraint contract that references an undefined node type fails its own conformance. Code authoring DDL-style content from §3 will either emit edges to a phantom label or be forced to improvise — a fabrication surface DIRECTIVE-034 §34.2 forbids.

**Risk if not addressed:** Either a malformed schema contract, or an ad-hoc `Process` node invented at authoring time outside the ratified design — re-introducing the "author from a thin prompt" failure mode.

**Disposition (small fix, but real):** Choose one — (a) include a minimal T1 `Process` node now (identity + plane label only, T3 payload deferred), or (b) defer `PRESCRIBES→Process` and `FOR_PROCESS→Process` alongside the node, with an explicit "edges land when `Process` lands" note. Do not leave the asymmetry.

### 2.2 MATERIAL — should be fixed in scope of authoring; not gate-blocking individually

#### Finding M-1: The provenance group is ingestion-shaped but must cover four origin classes
**Location:** §1 Provenance (`source_class` + `ingested_at`); applies to §2.3 ObservedPattern, §2.6 CapabilityCostEstimate, §5 promoted nodes.
**Description:** The group's `ingested_at` assumes external ingestion. But several KG nodes are not ingested: `ObservedPattern` is *distilled*, `CapabilityCostEstimate` is *computed/derived*, and any node arriving via `PROMOTES_TO_KNOWLEDGE` is *promoted from reasoning*. `ingested_at` is semantically wrong for all three, and `source_class` has no declared value for "distilled" / "computed" / "promoted."
**Risk:** Either the timestamp lies (a computed node claims an ingestion time) or writers leave it null and the existence constraint (§7) fails. Provenance becomes inconsistent across origin classes — corroding the very auditability it exists to provide.
**Disposition:** Generalize the group: `source_class` enumerates {ingested, distilled, computed, promoted, authored}; rename/parameterize the timestamp to an origin-neutral `recorded_at` (or add origin-specific timestamps). Define each plane node's expected `source_class`.

#### Finding M-2: The Environment plane is an unbounded ingestion surface — a latent CMDB mirror, in tension with R24
**Location:** §2.2 Environment (`DeployedService`, `ConfigurationItem`, `DeploymentEnvironment`); R24.
**Description:** R24 rules the KG holds durable distillation/reference, never a mirror of a transient external SoR, and names "full IAM directories" as out. The substrate honors this for Operational (ObservedPattern, not telemetry) and Governance (references, "not an IAM mirror"). But Environment ingests `DeployedService` + `ConfigurationItem` with no stated bound — which is the shape of a full CMDB mirror, the same anti-pattern class. The substrate's only defense is "ages via freshness," which bounds *staleness*, not *scope*.
**Risk:** Environment grows into a ServiceNow/CMDB replica — the bloat-and-coupling failure R24 exists to prevent — with no ruling to point to when an ingestion SDD asks "why not just mirror the CMDB?"
**Disposition:** State the Environment scope bound explicitly (which subset, why reasoning needs it as graph nodes rather than reference), and reconcile it against R24 the way Operational and Governance were. If Environment is genuinely a curated subset, name the curation rule; if it is a reference plane, model it as references like Governance.

#### Finding M-3: `GateDecision` reuse for the EA-promotion gate breaks its own enum and posture
**Location:** §2.4 (`gate` enum = gate_0/1/2; "external entity is **always** the SoR"); §5 ("EA-gate reuses `GateDecision{gate: ea_promotion}`").
**Description:** `ea_promotion` is not a member of the declared `gate` domain (gate_0/1/2). And the EA-promotion gate is a SOFIA-*internal* governance act, which contradicts `GateDecision`'s ratified posture that the external entity is *always* the system of record (no `external_record_ref` exists for an internal promotion).
**Risk:** Either the enum silently expands at authoring (undocumented contract drift) or the internal gate is forced into an external-SoR shape it does not fit, weakening the clean "captured reference, not our record" model.
**Disposition:** Either expand the `gate` domain to include `ea_promotion` and carve an explicit `origin: self_issued, external_record_ref: null` sub-case for internal gates, or give knowledge promotions their own decision node. Reconcile with the "always external SoR" posture either way.

#### Finding M-4: `confidence` is overloaded across node and edge types with no canonical scale or inheritance contract
**Location:** §2.2/§3 environment edges; §2.3 ObservedPattern; §3 confidence rule; §4 Evidence (`confidence (T2, inherited)`), ReasoningProgress, CandidatePromotion; §5 ("confidence inherits here").
**Description:** `confidence` appears on at least six node/edge surfaces with different meanings (ingestion confidence, observation confidence, evidence weight, promotion confidence) and an unspecified scale. "inherited" is asserted for `Evidence.confidence` and on `SOURCED_FROM` without a defined inheritance computation. This is a T2 (traversal/filter-bearing) property — it *drives behavior* — yet has no canonical definition.
**Risk:** Implementers diverge on scale and on how confidence combines across the `SOURCED_FROM` inheritance and the RG `Evidence`→`ReasoningProgress` rollup; "authoritative Catalog above aging Environment" becomes uncomparable across surfaces. Reasoning that weighs evidence by confidence (ADR-001 §2.2) produces non-reproducible results.
**Disposition:** Define `confidence` once (scale, semantics), state per-surface which flavor applies, and specify the inheritance/rollup rule (or rename per-surface variants to stop the overload).

#### Finding M-5: `ReasoningSession.lifecycle_state` has no enumerated domain
**Location:** §4 (`lifecycle_state (T2 — AOE-owned)`).
**Description:** A T2 status property with no value set. "AOE-owned" names the writer, not the domain. Contrast `Solution.lifecycle_state` (explicit FSM) and `CandidatePromotion.status` (explicit enum).
**Risk:** The SDD invents the state set, risking drift from any AOE/orchestration expectation set elsewhere; the lifecycle the RG hangs on is undefined at the schema layer that claims to own node contracts.
**Disposition:** Enumerate the session lifecycle states (even if AOE owns transitions), or explicitly route the enum to the AOE SDD with a named placeholder — but say which.

#### Finding M-6: `conclusion_type` enum and the correction-surface taxonomy do not reconcile
**Location:** §4 (`conclusion_type` = PatternMatch / TechnologySelection / GapConclusion / OverrideFlag / RiskSignal / ComplianceEvaluation); §5 generalized correction ("every `conclusion_type` is a human-correction surface (technology, pattern, capability, integration, risk, compliance, cost)").
**Description:** The claim "every `conclusion_type` is a correction surface" maps a 6-value enum onto a 7-item surface list with non-matching names. `capability`, `integration`, and `cost` are correction surfaces with no `conclusion_type`; `GapConclusion`/`OverrideFlag` are enum values with no obvious surface.
**Risk:** The correction mechanism's generality claim is unverifiable as written; a surface (e.g., cost correction) may have no capture path, or an enum value may have no correction semantics. Downstream SDDs build against an inconsistent taxonomy.
**Disposition:** Reconcile the two lists into one mapping (conclusion_type ↔ correction surface ↔ promotion_type), or state explicitly that they are orthogonal and how they relate.

#### Finding M-7: The `Artifact`/`Solution` keystone family is under-specified (plane membership, generic-Artifact PK, HAS_ARTIFACT semantics)
**Location:** §5 (`(:Artifact:Solution)`, "`(:Artifact)` is the general produced-deliverable family", `(Solution)-[:HAS_ARTIFACT]->(Artifact)`); §1 plane-label invariant; §7 provenance scope.
**Description:** Three gaps. (a) `:Artifact:Solution` carries no plane secondary label, yet §1 says every KG node carries one and §7 scopes the provenance constraint to "KG nodes" — Solution carries `provenance (T1)` but is neither clearly KG-plane nor RG. (b) Generic non-Solution `:Artifact` nodes (BCDR plans, build sheets) have no defined PK or constraints. (c) `HAS_ARTIFACT` from a `:Artifact:Solution` to `:Artifact` is ambiguous (self/family match), since Solution *is* an Artifact.
**Risk:** The keystone that joins RG↔KG sits outside the plane/provenance contract that governs everything else; exclusion-by-label behavior for Solution is unspecified (is a Solution skipped by ground-truth traversals like CandidatePromotion, or not?); generic Artifacts are uniqueness-unconstrained.
**Disposition:** Decide and state Artifact/Solution's graph membership (a distinct "artifact" family that is neither KG-plane nor RG, with its own provenance + uniqueness rules), and clarify `HAS_ARTIFACT` target scope.

#### Finding M-8: Supersession edge re-pointing lacks an atomicity statement and a machine-readable structural-vs-pinned classification
**Location:** §6 ("Structural edges track *current* (gateway re-points on supersession); audit/evidence edges pin to a *specific* version node").
**Description:** On supersession the gateway must re-point all *structural* edges to the new version while *audit/evidence* edges stay pinned. The substrate (a) gives no atomicity guarantee for the (potentially large) re-point write set, and (b) provides the structural-vs-pinned distinction only narratively ("asserted-fact vs structural") — the gateway needs a machine-readable per-edge-type classification to know which to re-point.
**Risk:** A partial re-point splits structural edges across old/new versions (split-brain ground truth); without a classification carried in the schema, the gateway's re-point logic is guesswork or hard-coded out-of-band.
**Disposition:** State that supersession re-pointing is a single atomic transaction, and add a per-edge-type `rebind: current|pinned` (or equivalent) classification to the edge grammar so the gateway can drive it from the contract.

#### Finding M-9: `exclusion-by-label` is weaker than stated — it is query-discipline-dependent, not structural
**Location:** §5 structural invariants; §1 plane membership; §2.5 gateway (ADR-002 §2.5, sole reader/writer).
**Description:** "A proposal cannot masquerade as fact" holds only because plane-scoped traversals skip non-plane-labelled nodes. But an un-scoped query (`MATCH (n) WHERE n.status='promoted'`) or one that matches `:Reasoning:CandidatePromotion` directly bypasses the protection entirely. The invariant is a *query convention*, not a graph constraint.
**Risk:** Any consumer that reads ground truth without plane-scoping can read unpromoted proposals (and other non-plane nodes) as fact — the exact masquerade the invariant claims to prevent.
**Disposition:** Either (a) make knowledge-service's gateway enforce plane-scoping on all ground-truth reads (and say so), recasting the invariant as gateway-enforced rather than structural; or (b) state honestly that exclusion-by-label is a read-discipline invariant and name its enforcement point.

#### Finding M-10: R6's positive half — graph-native semantic retrieval — is unrealized in the schema
**Location:** §1/§7 (no-vector enforced); R6 ("semantic retrieval becomes graph-traversal-native").
**Description:** The substrate enforces the *prohibition* (no embeddings) but ships no *affordance* for the substitute R6 promises (graph-native precedent/pattern retrieval). The `l1/l2/l3_taxonomy` on Capability is the likely substrate but is tagged T2 with no statement that it is the retrieval mechanism.
**Risk:** The first solutioning SDD that needs "find similar precedents" finds no schema support and pushes back toward a vector index — re-opening R6 under pressure, exactly when the prohibition is hardest to defend.
**Disposition:** Either name the graph-native retrieval structure the schema provides (shared-taxonomy traversal, pattern-similarity edges, etc.) and tag it as the R6 substitute, or explicitly route retrieval-affordance design to the solutioning SDD with R6's prohibition restated as a constraint on it.

#### Finding M-11: ~11 integrity invariants are CI-only and depend on RBT-33, which ADR-002 §6 calls not-built — the exposure window is unquantified
**Location:** §7 conformance-checked invariant set; §8 ("mechanization → RBT-33"); ADR-002 §6 ("Compliance is currently aspirational").
**Description:** No-vector, edge cardinality, one-active-version, aggregate-derivation, schema-on-write + `attaches_to` bounding, write-authority, never-delete, exclusion-by-label, tamper-detection, no-PHI — and (per B-1) derived-RG provenance — are all relegated to documented-+-CI checks, none DB-enforced, all pending RBT-33. ADR-002 §6 itself states this mechanization is not yet built. So from DDR acceptance until RBT-33 lands, the graph's integrity is design-time review plus honor system. The substrate does not quantify this exposure or sequence RBT-33 against the SDDs (RBT-15, RBT-25) that will begin *writing*.
**Risk:** The window in which SDDs start writing the graph but no invariant is mechanically enforced is the highest-aggregate-risk period in the build. Silent violations accrue and are expensive to detect retroactively.
**Disposition:** (a) Separate the DB-enforceable-now invariants (uniqueness, existence — already done) from the mechanization-pending set, and foreground the latter as a named risk in the DDR's Consequences/Risks. (b) Sequence RBT-33 relative to the first writing SDD, or state the accepted exposure. (c) Re-examine which "CI-only" invariants are actually DB-promotable (never-delete via permissions; some exclusion via label constraints).

#### Finding M-12: `rule_definition` opacity undermines the Standards plane's "change-impact" promise
**Location:** §2.5 (opaque `rule_definition`, "the graph never traverses into it"; plane titled "versioned + change-impact"); §3 (`GOVERNED_BY`, `MANDATES`).
**Description:** Executable rule logic rides `PolicyRule` as an opaque blob the validator consumes and the graph never reads. Dependencies the rule actually has on technologies/patterns are only visible to change-impact analysis if they are *also* expressed as traversable edges (`GOVERNED_BY`/`MANDATES`). Nothing keeps the opaque logic and the traversable edge surface in sync, and the node `version` does not bump on opaque-logic edits the graph can't see.
**Risk:** A rule whose dependency is encoded inside `rule_definition` but not mirrored as an edge is invisible to change-impact traversal — so the plane's headline capability silently misses it. The KG-as-policy-SoR model becomes a store of un-analyzable blobs.
**Disposition:** State the invariant that every traversal-relevant dependency in `rule_definition` MUST also be expressed as a `GOVERNED_BY`/`MANDATES` edge (and add it to the conformance set), or constrain `rule_definition` to a form the change-impact tooling can parse.

#### Finding M-13: `CandidatePromotion.status: approved` creates an approved-but-unwritten window with no enforced completion
**Location:** §5 (`status` enum proposed/under_review/approved/rejected/promoted; "terminal status (promoted / rejected)").
**Description:** `approved` is a declared status but `promoted`/`rejected` are the stated terminal states — so `approved` is the transient state between EA-approval and the `PROMOTES_TO_KNOWLEDGE` write. Nothing enforces `approved → promoted` completion. If the write fails, an `approved` CandidatePromotion persists with no `PROMOTES_TO_KNOWLEDGE` edge.
**Risk:** Approved-but-unwritten promotions are a silent integrity gap in the most sensitive path: the proposal was blessed but the fact never landed (or landed without the edge), and append-only immutability means the stuck node persists. Reconciliation has no signal to key on.
**Disposition:** Define `approved` as transient with a required completion (or fold approval into the write so `approved`+`PROMOTES_TO_KNOWLEDGE` are atomic), and add a conformance check for "no `approved` CandidatePromotion without a terminal transition."

#### Finding M-14: DDR-001 vocabulary alignment is asserted, not verified — and is unverifiable from the review surface
**Location:** §0/§5/§8 (R8/R22 ownership line; "Cited, never re-opened"); reviewer blind spot §0(3).
**Description:** Per R22, DDR-001 (architecture) owns the feedback-loop data-path and names the promotion mechanics; DDR-002 (schema) owns the node/edge contract for the *same vocabulary* (`CandidatePromotion`, `PROMOTES_TO_KNOWLEDGE`, signal/action classes, the five-plane + Extension model, the gateway). The substrate asserts alignment, but DDR-001's accepted text is not in project knowledge and is not fetchable (private-repo 404). The single place where R8's clean one-way separation is thinnest is exactly this shared feedback-loop vocabulary — and it is the one place the alignment can't be checked here.
**Risk:** If DDR-002's labels/edges or the signal/action classes diverge from DDR-001's accepted architecture vocabulary, the schema half silently contradicts the architecture half, and R8's "architecture not re-opened" is violated in substance even though DDR-001's file is untouched.
**Disposition:** Before authoring, fresh-fetch DDR-001's accepted body (operator-side, since the MCP route 404s — e.g., via the local `$SOFIA_REBOOT_ROOT` working tree or the Filesystem connector) and diff DDR-002's node/edge/class vocabulary against it. Treat any mismatch as a blocker.

#### Finding M-15: Honest empirical floor — the schema's evidentiary base is a single thin POC, and several T2 "invariant-bearing" classifications are asserted, not evidenced
**Location:** §1 tiering; R25 ("Anchored against the thin POC-spreadsheet origin … over-specifying from a thin empirical base is guessing"); DDR template ("DDRs with empirical spike findings get an additional review pass on whether the ruling generalizes beyond the spike's context").
**Description:** R25 is sound, and the tiering is applied. But the empirical base under the tiering is a single POC spreadsheet of unknown coverage. Several properties are placed in T2 (invariant/traversal-bearing → "complete now, index") on assertion — e.g., the specific `conclusion_type` value set, `polarity`'s `neutral` option, the `gate_0/1/2` enumeration, `basis_strength`. The DDR template prescribes an extra generalization-review pass for spike-grounded DDRs; here the "spike" is a POC, so that pass is *more* needed, not less.
**Risk:** T2/T1 classifications that are POC artifacts get baked into the expensive-to-reverse surface — the exact over-specification R25 warns against, now load-bearing for 12 SDDs.
**Disposition:** For each contested T2 classification, state whether it is invariant-grounded or POC-asserted, and where POC-asserted, either justify the generalization or drop to T3 (gap-named). Add the template's spike-generalization pass to the DDR's review plan.

#### Finding M-16: Pre-acceptance conditions are not framed — the DDR likely lands PROPOSED or ACCEPTED-WITH-CONDITIONS, not ACCEPTED
**Location:** §8 forward dependencies; DDR template (Pre-Acceptance/Pre-Migration Conditions; "DDRs frequently land at ACCEPTED-WITH-CONDITIONS").
**Description:** The substrate carries at least one open design call (B-1 / the §4 M-5 confirmation) and hard upstream/downstream couplings, but frames them as "forward dependencies," not as *pre-acceptance conditions*. The DDR template treats acceptance-conditions as a load-bearing, tracked section.
**Risk:** A DDR promoted straight to ACCEPTED while a keystone design call is open mis-states its own maturity — the lock-vs-closure conflation DIRECTIVE-007 §7.5 names. Conditions left as prose forward-pointers are "wishes" (template language), untracked.
**Disposition:** Enumerate pre-acceptance conditions (at minimum: resolve B-1; verify M-14; disposition B-2/B-3), map each to a tracked item, and set the landing status accordingly (PROPOSED until B-1…B-3 clear, or ACCEPTED-WITH-CONDITIONS if the team accepts a conditional landing).

#### Finding M-17: R18 leakage risk — the substrate's own v0.2 / Pass-1-fold history must not enter the DDR
**Location:** Substrate header ("v0.2"), "Revision (v0.2, 2026-06-19)" line, "v0.2 fold" appendix; R18 ("in-session review iterations are session process … not document versions"; single original-authoring Change Log row).
**Description:** The substrate is correctly versioned as *session process* (v0.2), but Code authoring from it must not carry the v0.2 marker, the "Revision (v0.2)" line, or the Pass-1-fold appendix into the DDR's Change Log or version — R18 forbids a drafting-iteration trail. This is a live authoring trap precisely because the source document looks versioned.
**Risk:** DDR-002 ships with a 0.1.0→0.2 drafting trail in its Change Log, violating R18 and re-introducing the DELTA-trail R2 sheds.
**Disposition:** Add an explicit authoring instruction: DDR-002 carries Version 0.1.0 (PROPOSED) → 1.0.0 (ACCEPTED) with a single original-authoring Change Log row; the substrate's v0.2/fold history stays in the substrate and the review/ruling-rationale artifacts, never in the DDR.

### 2.3 COSMETIC — noted, no-action (or trivial)

- **C-1:** `DECIDED_ON` is overloaded to both `Solution` and `CandidatePromotion` (§5). Legal in Neo4j; note for traversal-callers that "what did this gate decide on" returns mixed labels.
- **C-2:** The substrate's §0 Frame is prose; the DDR template §1 Decision wants numbered, testable ruling-components. Authoring nudge, not a defect.
- **C-3:** The DDR should carry the template's Layer-of-abstraction note (data-substrate layer) and Substrate-stability note — DDR-002 gates all 12 SDDs (RBT-15…RBT-26); that blast radius deserves an explicit line.
- **C-4:** `Solution.target_environment` (design intent, a property) cannot be traversed to the realized `DeploymentEnvironment` (intent-vs-realized cross-check is string-match, not edge). Likely intended (different lifecycle phases); note it.
- **C-5:** Index choices are made pre-SDD ("indexed where it drives traversal") without the query patterns the SDDs will define. Online index-add is cheap in Neo4j, so low-risk — but mark the index set provisional/revisitable post-SDD.
- **C-6:** Provenance "source-record ref where applicable" (§1) conceptually overlaps `GateDecision.external_record_ref` (§2.4). Clarify whether these are the same concept at different scopes.

### 2.4 No-drift confirmations (POSITIVE — required, DIRECTIVE-007 §7.2)

- **R23 cost-via-Extension — conformant and elegant.** Cost registers as the first `PlaneDefinition`, not a sixth core plane; DDR-040's six types collapse cleanly (`CostPlaneDefinition`→generic `PlaneDefinition`; two cost-factor types→one `CostFactor` with `factor_scope`); DDR-001 is not re-opened. The "first Extension registration as a worked exemplar" benefit is preserved.
- **R24 — correctly applied on both surfaces it was ratified against.** Operational holds distilled dual-polarity `ObservedPattern`, not telemetry; Governance holds `GateDecision` *references* + participating `Actor`s, explicitly excludes the disposition-event stream, and is "not an IAM mirror." (The one place R24 is *under*-applied is Environment — see M-2.)
- **R25 tiering — a genuinely strong completeness discipline,** applied per node/edge by reversibility (T1–T4), with gaps named rather than padded.
- **ADR-001 §2.2 label-ownership delegation — correctly executed.** DDR-002 takes ownership of the canonical RG labels ADR-001 left illustrative (`Inference`→`ReasoningProgress`, `Hypothesis`→`RejectedAlternative`; `Evidence`/`ReasoningSession` kept), which is exactly the delegation ADR-001 §2.2 makes.
- **ADR-002 §2.6 write authority — carried into the RG node model and the conformance set** (ASA authors ReasoningProgress; AOE owns ReasoningSession lifecycle; writes route via knowledge-service). (The gap is the *un*-assigned CandidatePromotion authorship — B-2 — not the assigned ones.)
- **R6 prohibition — enforced** (no vector/embedding properties; documented invariant + check). (Positive half unrealized — M-10.)
- **R18 single-artifact posture — correctly stated** (0.1.0 PROPOSED → 1.0.0 ACCEPTED, single Change Log row). (Leakage risk flagged — M-17.)
- **Identity string — corrected** to *Executive Architect, Haffey Enterprises LLC* per RBT-36.
- **Filename/placement — conformant** (`docs/ddr/DDR-002-graph-schema.md`, DMS naming).
- **Boundary routing (§8) and conscious-exclusions discipline — exemplary.** The owns-vs-cites delimiter (§5), the routing map, and the "boundary chosen, not missed" exclusions list are the substrate's strongest feature and materially reduce SDD-layer ambiguity.
- **Structural invariants (exclusion-by-label, provenance-chain traceability) — thoughtful** even where they need hardening (M-9): the *intent* to make masquerade structurally impossible and promotion traceable end-to-end is the right design instinct.

---

## §3 Forward-pointer triage

Candidate work items surfaced by this review (file with DIRECTIVE-025 dedup at filing; do not file from this review — these return to the primary session for ratification).

| Proposed ID | Summary | Source | Proposed disposition |
|---|---|---|---|
| RBT-NNN | `Process` node type — define + land its deferred edges (`PRESCRIBES→Process`, `FOR_PROCESS→Process`) | B-3, §8 | File (substrate already anticipates a post-merge `Process` ticket); resolve the B-3 asymmetry *in* DDR-002 first |
| RBT-NNN | Detection / promotion / correction SDD — `ObservedPattern` detection, `CandidatePromotion` aggregation + writer authority, generalized correction mechanism | B-2, M-13, §8 | File; carries the B-2 authorship resolution into service realization |
| RBT-NNN | Selection-edge preference-landing (Refine signal on selection edges) | §5, §8 | File (substrate names it) |
| RBT-NNN | Graph-native semantic-retrieval affordance — design the R6 substitute | M-10 | Investigation note → likely solutioning SDD scope |
| RBT-NNN | DDR-001 ↔ DDR-002 vocabulary-alignment verification (one-time, pre-authoring) | M-14 | Operator-side fresh-fetch of DDR-001 body + diff; gating, not deferrable |
| RBT-33 (exists) | Conformance mechanization — sequence against first writing SDD; re-examine DB-promotable invariants | M-11, B-1 | Broaden/sequence existing ticket |

---

## §4 Audit outcome

> **PASS WITH FINDINGS — BLOCKING present; authoring gate NOT satisfied this pass.** 3 BLOCKING (B-1 derived-RG provenance / open design call; B-2 promotion-path write authority; B-3 `Process` dangling edges), 17 MATERIAL, 6 COSMETIC, against a substantial POSITIVE no-drift set confirming correct application of R23/R24/R25, ADR-001 §2.2, ADR-002 §2.6, R6, R18, and the identity/placement postures.

The substrate is **strong, disciplined work** — the tiering, boundary routing, and conscious-exclusions are above the bar, and the rulings it was built to apply are mostly applied faithfully. It is not yet authoring-ready. The three BLOCKING findings are the gate: an open design call on the capture invariant's audit trail (B-1), an unassigned authority on the proposal→fact write path (B-2), and an internal-consistency defect in the edge catalog (B-3). The MATERIAL set clusters around four themes worth holding as the corrective agenda: **provenance coverage** (M-1, B-1), **write-authority/integrity on the promotion path** (B-2, M-13, M-9), **enforcement that is aspirational until RBT-33** (M-11), and **alignment that is asserted but unverified** (M-14, M-15).

Per DIRECTIVE-032 §32.3, the corrective authoring returns to the primary session; this reviewer does not author the fixes. Convergence (zero new + zero unresolved prior findings, §32.4) requires at least one further pass after the BLOCKING set and the MATERIAL agenda are dispositioned. Per §32.4.1, zero-findings convergence will not equal zero-defects: the DDR-001 vocabulary diff (M-14) and the RBT-33 mechanization window (M-11) are deferred-to-runtime-verification items the next pass should explicitly carry as residual risk rather than close.

---

## §5 Cross-references

- **Authority:** DIRECTIVE-032 (antagonistic review), DIRECTIVE-007 (finding-severity vocabulary), DIRECTIVE-034 (pre-authoring substrate requirement).
- **Reviewed:** `DDR-002-graph-schema-design-substrate-v0.2.md` (RBT-13).
- **Canon fresh-fetched for the pass:** RBT-13 + RBT-12 (Linear); Reboot Decision Ledger R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25 (Notion `374caeea-1325-818d-8f9f-f5f56898b133`); ADR-001, ADR-002 (project knowledge).
- **Unavailable (declared limitation):** DDR-001 accepted body (`develop`@`15ff20f`) — not in project knowledge; private-repo MCP fetch 404. Drives M-14.
- **Next:** corrective pass in the primary session; DDR-002 three-hat review of record remains a separate downstream gate.
