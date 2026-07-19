# File: docs/reviews/2026-06-20-rbt-13-ddr-002-substrate-v0_3-antagonistic-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-20
# Description: Brutal antagonistic review (DIRECTIVE-032) of the DDR-002 Graph Schema design substrate v0.3 — attacks the design decisions on their merits, including assumptions DDR-002 inherits from DDR-001 (now in project knowledge) and the soundness of prior-pass dispositions, to find every gap, loophole, and issue before the substrate is used to author a DDR.

# BRUTAL Antagonistic Review — DDR-002 Graph Schema Substrate (v0.3) — 2026-06-20

| Field | Value |
|---|---|
| **Review Date** | 2026-06-20 |
| **Reviewer** | claude.ai antagonistic reviewer (architecture leadership team — adversarial stance), DIRECTIVE-032 |
| **Subject** | `DDR-002-graph-schema-design-substrate-v0.3.md` (RBT-13) |
| **Mandate** | Pressure-test the substrate for every gap, loophole, and issue **if used to author a DDR**. Challenge every assumption and design decision. This is a destructive pass, not a confirmation pass. |
| **New leverage** | DDR-001 v1.0.0 is now in project knowledge — used here to attack the *parent's* assumptions where they silently propagate into DDR-002. |
| **Outcome** | **DO NOT AUTHOR — 3 BLOCKING, 14 MATERIAL, 3 COSMETIC.** The v0.3 fold mechanics are clean (verified last pass), but the *design underneath* carries unexamined soundness problems — three of them cross-document contradictions with DDR-001's own ratified text that the convergence pass did not surface. |

---

## §0 Stance — and why this differs from the three-hat pass

The prior three-hat pass verified that v0.3 *folded* the earlier findings and that its captures were truthful. It did its job — but it was a convergence pass: it largely accepted the design decisions and checked whether the folds landed. **This pass assumes the design is wrong until proven otherwise** and attacks the decisions themselves.

Three consequences of that stance worth stating up front:

1. **I attack my own prior praise.** Last pass I called the M-4 confidence definition and the M-8 atomicity "resolved." Under adversarial load both crack (A-13, A-11). Praise earned in a confirmation pass is not a finding's acquittal in an antagonistic one.
2. **I attack DDR-001's inheritance.** The substrate cites DDR-001 as settled foundation and builds on it. But DDR-001 carries assumptions — *non-blocking capture*, *evidence expiry*, *deterministic-not-LLM-judged* — that quietly contradict DDR-002's own invariants. Three of the BLOCKING findings live in that seam, and they were invisible until DDR-001 was placed beside the schema.
3. **I do not relitigate closed rulings.** R3 (Enterprise), R6 (vector-out), the closed Option sets — fixed. Every finding challenges the substrate's *design and application*, never a ratified ruling's existence. Where a finding cites R24/R26/R27, it argues the substrate under-realizes or over-corrects the ruling, not that the ruling is wrong.

---

## §1 BLOCKING — the design is unsound or self-contradictory as written

### A-1 — The structural-provenance surrogate is unsound under DDR-001's own *non-blocking capture* model

**Location:** DDR-002 §1/§4/§7 #1 (RG-provenance surrogate: "every `Evidence` carries a mandatory `SOURCED_FROM` edge"); **DDR-001 §RG invariants** — *"Capture is non-blocking enrichment, not a synthesis gate"*; *"All RG writes are gateway-mediated"* and gateway "writes non-blocking."

**The attack.** The entire B-1 resolution rests on a structural surrogate: `Evidence` and `RejectedAlternative` carry no provenance group because their provenance is *recovered structurally* — every `Evidence` is guaranteed to have a `SOURCED_FROM` edge. But DDR-001 mandates that RG capture is **non-blocking** and asynchronous ("not a synthesis gate"). Non-blocking capture means the `Evidence` node and its `SOURCED_FROM` edge are not necessarily written in one synchronous transaction — and the substrate never asserts they are atomic. So there is an observable window in which an `Evidence` node exists **without** its `SOURCED_FROM` edge. During that window the surrogate is false: an `Evidence` node with no provenance group *and* no source edge has **no provenance at all**. And the enforcement that would catch it (§7 #1) is CI-only (not transactional) and doesn't exist until RBT-33.

**Why blocking.** The surrogate is the sole provenance mechanism for the two audit-critical derived RG types, and it is the linchpin of the B-1 disposition that let DDR-002 proceed. If it is not sound under the parent's mandated async-write model, the B-1 disposition is built on sand — the schema's auditability guarantee for the "why" of every decision has a structural hole, not just a mechanization gap.

**Risk if not addressed.** Provenance-less `Evidence` is observable in normal operation (not just failure), and feeds the promotion chain (A-14). "Auditable reasoning" — SOFIA's reason to exist — degrades to "auditable once the async edge-write completes, if it completes."

**Reconcile.** Require that an `Evidence` node and its `SOURCED_FROM` edge are written in a **single gateway transaction** (atomic capture unit), and state it as a schema invariant — even if the *broader* capture pipeline is non-blocking, the node+edge unit must be atomic. Or carry the provenance group on all four RG types (the B-1 option that was declined). The current posture — surrogate + async + CI-only — is the worst of the three.

### A-2 — Evidence expiry (DDR-001 retention) severs DDR-002's provenance chain; the schema has no summary mechanism to preserve it

**Location:** DDR-002 §5 (provenance chain: "a promoted node traces back through `PROMOTES_TO_KNOWLEDGE` → `CandidatePromotion` → `PROPOSED_FROM` → `ReasoningProgress`/`Evidence` → `SOURCED_FROM` → original facts"); **DDR-001 Versioning** — *"RG retention posture | bounded + non-uniform; summary-on-evidence-expiry preserves explainability."*

**The attack.** DDR-002 asserts a structural invariant it *owns*: end-to-end provenance-chain traceability from a promoted ground-truth node back to original facts, threaded through `Evidence`. But DDR-001 explicitly says RG `Evidence` is **retained non-uniformly and expires**, with explainability preserved by a **summary-on-evidence-expiry**. When the `Evidence` in a promotion's provenance chain expires, the chain's `Evidence` link is gone — and DDR-002 models **no summary node or property** to stand in for the expired evidence. DDR-001 promises the summary preserves explainability; DDR-002, the schema owner, never schematizes the summary. So the chain DDR-002 claims is unbreakable is, in fact, broken by the parent's own retention model, with nothing in the schema to catch the pieces.

**Why blocking.** This is a DDR-002-**owned** structural invariant (§5 explicitly lists "provenance-chain traceability" among the invariants DDR-002 owns) that is **false** under DDR-001's ratified retention posture. An owned invariant that the parent's design contradicts cannot pass authoring.

**Risk if not addressed.** A promoted node — now permanent KG ground truth — becomes un-traceable to its originating facts the moment its supporting `Evidence` is summarized away. The audit trail for the highest-stakes writes (proposal→fact) has a built-in expiry.

**Reconcile.** DDR-002 must either (a) schematize the "summary-on-evidence-expiry" structure DDR-001 relies on (a `ProvenanceSummary` node or denormalized chain-summary on the promoted node / `CandidatePromotion`), or (b) declare that `Evidence` participating in a promotion provenance chain is **exempt from expiry** (pinned for the life of the promoted node). Retention *policy* is DDR-003's; the retention-surviving *schema* is DDR-002's, and it's missing.

### A-3 — The obligation-closure model contradicts itself: "traverse to obligations" vs. "governance is computed, not stored"

**Location:** DDR-002 §3 obligation↔satisfaction ("Validation **traverses** from a solution to its obligations and checks each has a matching satisfaction") vs. §2.5 / §3 `GOVERNED_BY` ("solution-time governance is **computed** by matching the rule condition against the solution, **not a stored edge**").

**The attack.** These two statements specify incompatible mechanisms for the same operation. If which `PolicyRule`s apply to a solution is **computed** at validation time by evaluating opaque `rule_definition`s against the solution graph (§2.5), then the obligation set is **not traversable** — you cannot "traverse from a solution to its obligations" (§3) because the obligations don't exist as edges; they're the output of running rules. The compliance model's core claim — "each obligation has a matching satisfaction, checked by traversal" — is therefore incoherent: the obligations are computed, the satisfactions (`Attestation`) are stored, and you cannot traverse between a computed set and a stored set.

**Why blocking.** Compliance closure is a load-bearing capability (the whole Standards/Governance/Attestation apparatus exists for it), and the schema describes its mechanism two contradictory ways. Authoring a DDR from this produces a compliance model an implementer cannot build to — they'd have to pick one reading and the other section would be wrong.

**Risk if not addressed.** Either the validator computes obligations (and the "traverse to obligations + check satisfaction" framing in §3 is fiction), or obligations are stored edges (and §2.5's "computed, not stored" is wrong). Shipping both guarantees a contradiction the SDDs inherit.

**Reconcile.** Decide and state the mechanism precisely: obligations are **computed** by the validator (rule evaluation), and the "closure check" is *validator logic*, not graph traversal — the graph stores `Attestation`s and `GOVERNED_BY` *associations*, and the validator joins computed-obligations to stored-attestations. Then rewrite §3's "traverses to its obligations" to match, and clarify exactly what `GOVERNED_BY` contributes if it isn't the obligation set (this is also A-12).

---

## §2 MATERIAL — design weaknesses that need resolution in scope

### A-4 — `CapabilityCostEstimate` is a refreshable cache masquerading as KG ground truth — the R24 anti-pattern, again
**Location:** §2.6 (`CapabilityCostEstimate`: `aggregate_cost` "derived, never hand-set", `computed_at`, "refreshable", `source_class: computed`); R24; cost DTO already routed to RBT-25.
**The attack.** R24 was the ruling that the KG holds *durable knowledge, not transient derived data* — the exact logic that produced B-4 on the Operational plane. Yet `CapabilityCostEstimate` is a **refreshable, recomputable cache** of a traversal over `RateCard` + `CostFactor`, persisted as a ground-truth KG node. That is transient derived data wearing a ground-truth label — the same anti-pattern R24 exists to kill, sitting un-caught in the cost plane because the B-4 analysis only looked at Operational and Governance. And it has **no staleness signal**: when a `RateCard` supersedes, every estimate `PRICED_BY` it is silently stale, but remains queryable as ground truth; detecting staleness requires the consumer to compare the pinned `RateCard`/`capability_version_ref` against current. The Tier-1/2 traversal + DTO is *already* routed to RBT-25 — so the live computation exists. Why persist the cache at all?
**Risk.** Stale cost estimates served as authoritative fact; a cache-invalidation problem (rate-card supersession fan-out) the schema doesn't model; a self-inconsistency with the very ruling that drove B-4.
**Reconcile.** Either compute cost on read (the RBT-25 traversal/DTO) and drop `CapabilityCostEstimate` from the KG, or justify persistence explicitly and add a `stale`/recompute-trigger signal. Apply the R24 test to the cost plane the way B-4 applied it to Operational.

### A-5 — The B-4 fix traded a contradiction for an unbounded-growth commitment on the Operational plane
**Location:** §2.3 ("**No in-graph TTL**"; never-delete via status); R26; DDR-001 retention → DDR-003.
**The attack.** B-4 (my finding) was resolved by removing TTL from Operational and making `ObservedPattern` durable (R26). But "durable + no-TTL + never-delete + retention-deferred-to-DDR-003" is a latent **unbounded-growth** commitment on a plane fed by *continuous distillation*. Superseded/resolved `ObservedPattern`s accumulate forever; the schema bakes in never-delete and defers any retention path. The original DDR-001 TTL existed to bound exactly this. The fix removed the bound without replacing it.
**Risk.** Operational grows without limit; the "trends, not raw signal" framing assumes a bounded set of distinct lessons, but version/status churn accumulates regardless. Query performance on the track-record subgraph degrades over time.
**Reconcile.** Even though retention *policy* is DDR-003's, the schema should name the expectation that `resolved`/`superseded` `ObservedPattern`s have a retention/archival path, and not foreclose it with an unqualified never-delete. The B-4 resolution should carry this consequence explicitly rather than leave it as an emergent surprise.

### A-6 — Deterministic-KG vs. LLM-judged-RG boundary is implicit, and promotion *launders* model opinion into graph fact
**Location:** §4 (RG confidence/conclusions, ASA-authored); §5 (`PROMOTES_TO_KNOWLEDGE`); **DDR-001 KG invariants** — *"deterministic, not LLM-judged … graph facts, not model opinions."*
**The attack.** DDR-001 insists KG ground truth is **deterministic, not LLM-judged** ("graph facts, not model opinions"). But the RG captures **ASA (an LLM agent)** reasoning — `conclusion_type`, `confidence`, `RejectedAlternative` rationale — which are, definitionally, model judgments. The feedback loop then **promotes** RG-derived proposals into KG ground truth via `PROMOTES_TO_KNOWLEDGE`. So a model opinion (RG) can become a graph fact (KG) through promotion. The EA gate is the intended laundering-control (a human converts opinion to fact), but the schema never makes the deterministic-KG / judged-RG boundary explicit, and never marks promoted-from-judgment nodes distinctly from deterministically-ingested ones beyond the coarse `source_class: promoted`.
**Risk.** The KG's "deterministic, not model opinions" guarantee (DDR-001) erodes silently as promoted, judgment-derived nodes accumulate as indistinguishable ground truth. The moat (auditable, deterministic reasoning) depends on this boundary, and it's unschematized.
**Reconcile.** Make the boundary explicit: state that RG content is *captured judgment* (not held to KG determinism), that the EA gate is the determinism-restoring control, and that promoted nodes retain a traceable link to their judgment origin (the chain — which A-1/A-2 already threaten). Confirm `source_class: promoted` is sufficient to honor DDR-001's invariant, or strengthen it.

### A-7 — `source_class` conflates two orthogonal axes and is lossy for compound provenance
**Location:** §1 (`source_class` ∈ {ingested, distilled, computed, promoted, authored}).
**The attack.** The enum mixes **entry-mechanism** (ingested / promoted / authored) with **derivation-nature** (distilled / computed) on a single property. A node that is computed-then-promoted, or ingested-then-human-corrected, has only one `source_class` and cannot express both axes. DDR-001 check #6 (promoted≠ingested) is satisfied, but the enum loses information precisely for the compound-origin nodes the feedback loop and correction mechanism create.
**Risk.** Provenance queries ("show me all human-corrected ground truth," "all computed-then-promoted nodes") are unanswerable; the lossy enum forces a choice that hides one axis.
**Reconcile.** Split into two properties (`origin_mechanism` × `derivation_class`) or explicitly accept and document the lossiness with a stated precedence rule.

### A-8 — The promotion ratchet has no reverse gear: erroneously-promoted nodes are permanent ground truth
**Location:** §5 (`PROMOTES_TO_KNOWLEDGE` materializes real KG nodes); §6 (never-delete, supersede-only); §5 "Correct-scope" (asserted to handle false ground truth).
**The attack.** Promotion creates ground truth; never-delete means it can only be *superseded*, never removed. There is **no schema-level retraction/rollback** for a promotion the EA later realizes was wrong. "Correct-scope" is hand-waved as the remedy, but supersession requires authoring a *new version* — you cannot supersede a node out of existence — so a bad promotion persists permanently in version history, excluded from the hot path only by a `status` flag. The EA gate is the **only** safety valve, and it's a single human checkpoint with no structural undo behind it.
**Risk.** One bad EA approval permanently pollutes ground truth; the only mitigation is status-flagging, which depends on every consumer filtering by status correctly (the same read-discipline fragility as M-9).
**Reconcile.** Define a retraction/quarantine path in the schema (a `retracted` status distinct from `superseded`, with explicit exclusion semantics) and state how a wrongly-promoted node's downstream edges are handled. Don't leave "Correct-scope" as the unspecified answer.

### A-9 — `ReasoningSession`↔`Solution` 1:1 forecloses the no-solution and multi-option cases — for a system whose value is exploring alternatives
**Location:** §4 (`ReasoningSession.solution_ref` T1, "1:1 with the produced solution"; `PRODUCED` 1:1).
**The attack.** The schema hard-codes one solution per reasoning session. But a reasoning system's value is exploring alternatives: a session may produce **multiple** candidate solutions for comparison, or **none** (fully-rejected / exploratory). `solution_ref` as a required T1 property forecloses both — a session *must* have exactly one solution. Is the architect really never comparing two solutions in one session, or recording a session that reached "no viable solution"?
**Risk.** The RG can't represent multi-option deliberation or dead-end sessions — precisely the reasoning the moat is supposed to capture. SDDs hit this wall and either bend the schema or lose the data.
**Reconcile.** Relax to 1:many (`PRODUCED` with cardinality ≥0) and make `solution_ref` optional, or justify 1:1 against a concrete claim that sessions never compare or fail.

### A-10 — The Extension mechanism is untested-by-construction; the cost plane doesn't actually exercise it
**Location:** §2.6 (`PlaneDefinition.property_schema` opaque; `attaches_to` a label list; schema-on-write validation); R23 ("worked exemplar"); §7 #6 (CI-only).
**The attack.** The Extension safety story — "bounded, schema-on-write validated, zero impact" — rests entirely on opaque/CI machinery: `property_schema` is an **opaque blob** (like `rule_definition`, A-12) that an external validator interprets, and `attaches_to` is an **unvalidated label list** (nothing checks the labels exist). The cost plane is sold as the "worked exemplar" that validates the Extension mechanism end-to-end — but it is **hand-authored**, so it never exercises the schema-on-write *validation path*. The mechanism that's supposed to make Extension safe is therefore untested until a *second*, non-hand-authored extension runs through it — which is exactly when a flaw would bite, in production.
**Risk.** The "zero impact on existing traversals" guarantee (R23/DDR-001) is asserted, not demonstrated; the first real (non-exemplar) Extension registration is the actual test, with no prior validation of the validator.
**Reconcile.** Specify the `property_schema` format precisely enough to validate (or route it to RBT-15 with a stated contract), add an `attaches_to`-labels-exist invariant to §7, and note that the cost plane is an *authoring* exemplar, not a *validation* exemplar — the validation path needs its own test before a second extension lands.

### A-11 — Supersession's atomic re-point is O(degree) write amplification — expensive exactly for the most important nodes
**Location:** §6 ("supersession is a **single atomic transaction** — … re-point all `rebind:current` structural edges to the new node"); §6 rationale ("versioning is rare; traversal is constant").
**The attack.** Atomically re-pointing **all** `rebind:current` inbound edges on supersession is O(node degree) work in one locking transaction. A high-degree Catalog node — a widely-referenced `Capability` cited by hundreds of `Pattern`s/`Technology`s/`Solution`s — costs hundreds of edge re-points in a single lock-heavy, memory-heavy transaction. The Option-A rationale ("versioning is rare, traversal is constant") quietly assumes supersession is *cheap*; it's actually most expensive for the most-referenced (most-important) nodes, and it must be atomic (no batching/async escape).
**Risk.** Revising a core `Capability` stalls the write path and contends with hot-path readers; the "rare" event has unbounded cost tied to centrality.
**Reconcile.** Either bound the re-point cost (e.g., an indirection/version-pointer pattern for high-degree nodes — the identity+version-node pattern §6 explicitly rejected), or state the degree assumption and confirm Neo4j transaction limits hold for the highest-degree core nodes. The §6 rationale needs the write-amplification cost on the other side of the ledger.

### A-12 — `GOVERNED_BY` "static associations" vs. "computed, not stored" makes M-12's sync invariant unenforceable
**Location:** §3 (`GOVERNED_BY` "static associations only … computed by matching the rule condition, not a stored edge"); §2.5 / §7 #10 (M-12: `rule_definition` traversal-dependencies must also exist as `GOVERNED_BY`/`MANDATES` edges).
**The attack.** M-12's invariant presumes `GOVERNED_BY` edges *capture* a rule's real dependencies, so it can check the opaque `rule_definition` against them. But §3 calls `GOVERNED_BY` "**static associations only**" while the real governance is "**computed, not a stored edge**." If the genuine dependency is computed (inside the opaque blob) and `GOVERNED_BY` is merely a coarse static association, then M-12 is checking a computed thing against a static thing — two different objects — and is **unenforceable**. The relationship between the static edge and the computed evaluation is never defined.
**Risk.** M-12 (the fix to the original `rule_definition`-opacity finding) is illusory: it can't actually catch a dependency hidden in `rule_definition`, because "the dependency" (computed) and "the edge" (static association) aren't the same thing.
**Reconcile.** Define precisely what `GOVERNED_BY` represents and what the validator computes, and restate M-12 in terms a checker can evaluate (e.g., "every label referenced in `rule_definition` appears as a `GOVERNED_BY`/`MANDATES` target") — or concede M-12 is advisory, not enforceable.

### A-13 — Confidence's node-vs-edge split in Environment is unreconciled — the M-4 "canonical definition" papered over it
**Location:** §3 (Environment edges carry `{confidence}`); §4 (M-4: `Evidence.confidence` "inherits from the `SOURCED_FROM` KG node's **authority class** at snapshot time"; "on a confidence-bearing KG edge it is observation certainty").
**The attack.** In the Environment plane, confidence lives on **edges** (`RUNS {confidence}`, `DEPLOYED_IN {confidence}`) — observation certainty. But `Evidence` inheritance is defined off the source **node's** authority class × freshness. When `Evidence` is `SOURCED_FROM` an Environment **node** (e.g., a `DeployedService`), the node carries *no* confidence — only its edges do — so what does `Evidence` inherit, and do the edge confidences factor in at all? M-4 reconciled the *surfaces* nominally but left two distinct confidence notions in Environment (edge observation-certainty vs. node-derived authority) unjoined.
**Risk.** Reasoning that weighs Environment evidence by confidence gets a node-authority number that ignores the edge-level observation certainty the schema actually stores — non-reproducible, and arguably wrong (a low-certainty `RUNS` edge produces high-authority Evidence because the node is "fresh").
**Reconcile.** State how Evidence sourced from an Environment node combines node-freshness with the relevant edge's observation-certainty, or move Environment confidence to a consistent location.

### A-14 — The feedback loop's *primary input* (`RejectedAlternative`) has the *weakest* provenance
**Location:** §4 (`RejectedAlternative` — no provenance group, "reached only via parent", CI-only enforcement); **DDR-001 §RG** ("Rejected alternative … the **primary feedback-loop input**"); §5 (`PROPOSED_FROM` from `RejectedAlternative`).
**The attack.** DDR-001 names `RejectedAlternative` the *primary* feedback-loop input (override-recurrence drives promotions). Yet in DDR-002 it is the node with the **least** provenance protection: no provenance group, provenance "inherited" from a parent it's reached-only-through, and enforcement that is CI-only and doesn't exist until RBT-33. So the single most important signal feeding ground-truth promotion rides the least-protected, least-enforceable provenance — and when it feeds `PROPOSED_FROM`, the promotion's provenance chain inherits that weakness (compounding A-1/A-2).
**Risk.** The highest-leverage feedback signal is the least auditable; a promotion driven by recurring rejected alternatives may be un-traceable to *why* those alternatives were rejected.
**Reconcile.** Given its feedback-criticality, treat `RejectedAlternative` provenance with the same weight as authored RG types (carry the group, or pin its rejection rationale durably), rather than the lightest structural surrogate.

### A-15 — `PromotionDecision`↔`CandidatePromotion` 1:1 forecloses batch/policy promotion governance that DDR-003 owns
**Location:** §2.4/§5 (`PromotionDecision` `DECIDED_ON` → `CandidatePromotion`, modeled 1:1); R22 (governance → DDR-003).
**The attack.** The schema fixes one `PromotionDecision` per `CandidatePromotion`. But promotion *governance* — batching, policy-based auto-approval thresholds, bulk EA dispositions — is explicitly **DDR-003's** to decide (R22). By hard-wiring 1:1, the schema **pre-constrains** a governance space it deferred: a DDR-003 model where one EA decision dispositions a batch of candidates has no schema home.
**Risk.** DDR-003 authoring discovers the schema forbids the governance model it wants; either DDR-003 is constrained by a schema decision it should drive, or DDR-002 gets re-opened.
**Reconcile.** Allow `PromotionDecision` `DECIDED_ON` to target one-or-many `CandidatePromotion`s (or state that 1:1 is a deliberate, ratified constraint on DDR-003 and confirm DDR-003's authors accept it).

### A-16 — The `Decision` multi-label model permits malformed nodes the schema can't reject
**Location:** §2.4 (`Decision` supertype "never instantiated bare"; `GateDecision`/`PromotionDecision` subtypes; shared `decision` enum).
**The attack.** Multi-label elegance buys two new un-enforceable failure modes (Neo4j can't constrain label combinations): (a) a node carrying **both** `GateDecision` and `PromotionDecision` (contradictory `origin`: `external_captured` *and* `self_issued`); (b) a **bare** `Decision` with no subtype. Neither is in §7's CI-only set. Separately, the shared `decision` enum includes `approved_conditional`, but `CandidatePromotion.status` has no conditional value — so a `PromotionDecision: approved_conditional` has no representable candidate state.
**Risk.** Malformed governance nodes pass the schema; the conditional-promotion case is unrepresentable, forcing an SDD workaround.
**Reconcile.** Add to §7: exactly-one-subtype per `Decision`. Decide whether `PromotionDecision` may be `approved_conditional` and, if so, give `CandidatePromotion.status` the matching state.

### A-17 — The provenance group's "source-record ref where applicable" is an undefined property
**Location:** §1 (provenance = `source_class` + `recorded_at` "and a source-record ref where applicable"); §2.3 (distilled `ObservedPattern` "a source-record ref to the external telemetry").
**The attack.** The provenance group names a third element — a "source-record ref" — but never gives it a property name, shape, or applicability rule. §2.3 relies on it ("a source-record ref to the external telemetry") and `GateDecision.external_record_ref` looks like a specific instance of it, but the general property is a hand-wave. "Where applicable" is itself an undefined trigger.
**Risk.** Distilled/ingested nodes that should carry a back-reference to their external SoR record have no defined field; the link from KG knowledge to its external origin is unschematized exactly where R24's "reference, not mirror" posture depends on it.
**Reconcile.** Name the property (`source_record_ref`), define its shape, and state the applicability rule per `source_class` (required for ingested/distilled; n/a for authored/computed; `external_record_ref` is the Governance specialization).

---

## §3 COSMETIC

- **A-18 (LAA):** `Solution.target_environment` is an *unvalidated string* matched against `DeploymentEnvironment.name` (also a free T3 string) — drift-prone ("prod"/"production"). A controlled vocabulary (the `environment_class` enum already on `DeploymentEnvironment`) would remove the ambiguity without an FK-edge.
- **A-19 (EA):** §0 cites identity "per RBT-36/**RBT-37**"; RBT-37 is a **Duplicate** of RBT-36 (ledger build-leg). Cite RBT-36 only.
- **A-20 (SA):** Lean indexing is chosen pre-SDD (accepted as C-5), but sanity-check the reverse cross-graph lookups (e.g., "all `Evidence` `SOURCED_FROM` node X") have a traversal/index story before authoring, since they're inherent to explainability reads, not SDD-specific query patterns.

---

## §4 What's *not* wrong (kept honest)

The adversarial stance isn't license to manufacture. These hold up under load: the M-1 origin-class enum (modulo A-7's lossiness) genuinely carries DDR-001 check #6; the M-3 de-conflation cleanly separates SDLC and promotion gates (modulo A-16's malformed-node gap); the M-7 Artifact-third-family resolves the plane-membership ambiguity; the R23 cost-collapse from DDR-040's six types is sound modeling; the boundary-routing/conscious-exclusions discipline remains exemplary; and the capture layer is verifiably truthful (confirmed last pass). The design is *good* — which is why the remaining problems are deep ones, not surface ones.

---

## §5 Outcome

> **DO NOT AUTHOR — 3 BLOCKING · 14 MATERIAL · 3 COSMETIC.** The fold mechanics are clean; the design beneath them is not yet sound. The three blockers are cross-cutting: two are **contradictions with DDR-001's own ratified text** (async capture vs. the provenance surrogate, A-1; evidence-expiry vs. the provenance chain, A-2) that the convergence pass could not see because it wasn't reading the parent adversarially, and one is an **internal contradiction** in the compliance model (traverse-vs-compute obligations, A-3).

**The through-line.** Three of the BLOCKING/MATERIAL findings (A-1, A-2, A-14) and one MATERIAL (A-6) converge on a single soft spot: **the provenance and audit guarantees of the feedback loop are weaker than the substrate claims** — async-undermined, expiry-severed, weakest exactly at the primary feedback input, and laundering model-judgment into deterministic ground truth. The B-1 disposition (structural surrogate + named exposure) addressed *mechanization timing*; it did not address whether the surrogate is *sound* under DDR-001's async/expiry model. It is not, as written. **That is the finding to take most seriously.**

A second cluster (A-4, A-5) shows the **R24 test was applied unevenly** — rigorously to Operational (producing B-4), not at all to the cost plane (A-4, a cache-as-ground-truth) or to the *consequence* of the B-4 fix itself (A-5, unbounded growth). Re-run R24 across the whole schema, not just the plane that triggered it.

**Disposition (returns to the primary session).** None of this is folded here — antagonistic review surfaces; the primary session deliberates and ratifies. Recommend: resolve A-1/A-2/A-3 before any authoring; treat the provenance-soundness cluster (A-1/A-2/A-6/A-14) as a single re-deliberation rather than four separate folds; and re-apply R24 to the cost plane (A-4) and the B-4 consequence (A-5). The serialize gate (RBT-39) and the RBT-33 sequencing are unaffected — these are schema-design findings, upstream of both.

---

## §6 Cross-references
- **Subject:** `DDR-002-graph-schema-design-substrate-v0.3.md` (RBT-13).
- **Adversarial leverage:** DDR-001 v1.0.0 (project knowledge) — §RG invariants ("non-blocking … capture"; "deterministic, not LLM-judged"), Versioning ("summary-on-evidence-expiry"). Drives A-1, A-2, A-6.
- **Prior passes:** antagonistic Pass-1 (v0.2), Pass-2 (DDR-001 cross-check), three-hat Pass-3 (v0.3 convergence). This pass attacks the design those passes accepted.
- **Rulings re-tested (not relitigated):** R24 (uneven application — A-4/A-5), R26 (B-4 consequence — A-5), R27 (B-1 soundness — A-1/A-2/A-14), R23 (Extension exemplar — A-10).
