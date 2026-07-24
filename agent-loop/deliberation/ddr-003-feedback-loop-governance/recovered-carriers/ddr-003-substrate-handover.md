# DDR-003 — Feedback Loop Governance · Code authoring handover (ratified substrate)

**Ticket:** RBT-14 (In Progress) · **Branch:** `feature/rbt-14-d3-author-ddr-003-feedback-loop-governance`
**Role split (DIRECTIVE-026):** this is the ratified design substrate; Code authors the DDR-003 artifact from it. claude.ai did all deliberation, ledger, and ticket captures; Code does git only, pause-point mode.

---

## 0. Sequencing — this is a coordinated two-PR leg (amendment first)

DDR-003 consumes DDR-002 schema (R8 one-way). Three named-gap realizations must land in DDR-002 **before** DDR-003 cites them, so the leg runs as two PRs in one session:

- **PR-A — DDR-002 → v1.1.0 amendment (RBT-43).** Three additive changes (see §7). Authored by **claude.ai** as a complete-replacement staging file + apply-prompt against fresh-fetched DDR-002 state (DIRECTIVE-026.5) and handed over separately — **not** in this file. Code executes the apply-prompt (RBT-39 pattern: pause-point, pre-execution three-hat, two commits). Lands first; `develop` advances to DDR-002 v1.1.0.
- **PR-B — DDR-003 (RBT-14).** Authored by Code from the substrate below, **against the landed DDR-002 v1.1.0** (so every schema citation resolves to real, landed schema). This handover is PR-B's input.

**Git-leg conventions (both PRs):** `feature/*` branch → squash-merge to `develop`; **no `Co-Authored-By` trailer** (standing convention); PR body references its ticket (RBT-43 / RBT-14). Tad holds all merge gates (DIRECTIVE-018).

---

## 1. Live pointers (fresh-fetch at authoring time — do not reason from this file's summaries)

- **Linear:** RBT-14 (this) · RBT-43 (the DDR-002 amendment) · related RBT-13, RBT-15, RBT-22, RBT-25, RBT-27, RBT-33.
- **Notion Reboot Decision Ledger:** page `374caeea-1325-818d-8f9f-f5f56898b133`. Anchoring rulings: **R22** (architecture/governance split), **R24/R26** (durable distillation), **R25** (empirical-warrant completeness), **R27** (CI-only enforcement posture + retraction shape), and this session's **R29 / R30 / R31**.
- **Upstream authorities (cite at ACCEPTED state):** ADR-001 v1.0.0 (reasoning architecture; §2.5 is the spine for this DDR), ADR-002 v1.0.0 (system of record), DDR-001 v1.1.0 (data architecture; owns the feedback-loop *architecture* / data-path), **DDR-002 v1.1.0** (graph schema; owns the *schema contract* — available after PR-A lands).
- **Intent source (non-authoritative, R2):** prior-SOFIA DDR-038. Mine for shape only; the live corpus + this substrate are the substrate-of-truth.

---

## 2. Framing (state once, up front)

DDR-003 governs the **policy layer** around DDR-001's EA-gated promotion *architecture* — the engine by which recurring reasoning consolidates into encoded knowledge (**ADR-001 §2.5**, the Position-5 → Position-4 trajectory). It governs a loop that **has never run** (no deployed services, no telemetry, no promotion cycles), so the whole document holds one cut line, ratified as the session frame:

- **Rule now** — governance-architecture that is reversibility-expensive or already anchored upstream.
- **Structure now, parameterize at operational onboarding** — calibration-dependent values with no empirical floor (R4 / R25 discipline).
- **Name as gap, with a reversal path** — mechanisms with no driving instance, or owned by a downstream consumer.

---

## 3. Ratified substrate — the EA gate (the spine)

**3.1 Authority & accountability.** Every materialized promotion must trace to an approving `PromotionDecision` (the accountability contract). Pin **one** concrete enforceable authority — **Enterprise-Architect promotion-approval** — the single authorization the gate cannot function without (grounded in ADR-001's "EA-gated"). DDR-002 check #15's role-authorization tightens onto this. The broader non-EA role/permission surface (who is SA/LAA, view/defer/queue-access) is a **routed RBAC gap**, not authored here.

**3.2 Diagnosis policy.** The EA diagnoses each candidate to separate **genuine knowledge** from **data-defect / transient workaround / spurious artifact**. Dispositions map to DDR-002's outcomes (`approved` / `approved_conditional` / `rejected`) plus the three correction flavors (Refine / Request-new / Correct-scope). Enumerate **five diagnosis dimensions** a decision must weigh — recurrence strength · evidence quality / source authority · genuine-pattern-vs-data-defect · target deprecation/staleness state · conditional-vs-unconditional applicability. **Weights and decision rules are EA judgment + operational calibration — not authored.**

**3.3 Action-class routing.** Two action paths, with a **no-leak invariant** between them:
- **Path 1 — EA-gated knowledge promotion:** gap-recurrence + override-recurrence → `CandidatePromotion` → EA gate → possible KG materialization.
- **Path 2 — source-quality feedback:** evidence-quality → ingestion-scoring / data-quality signal; **no EA gate, no KG mutation.**
A source-quality signal **never crosses into promotion** except by independently re-entering as a promotion-eligible signal. Both paths' mechanisms → SDD. A novel action class registers additively into one of the two paths.

**3.4 Batch eligibility.** Batching is permitted (DDR-002's `PromotionDecision -[:DECIDED_ON]->` is 1:many). But every candidate in a batch retains its **own diagnosis** (the five dimensions) and its **own per-candidate verdict** (on the `DECIDED_ON` edge). Batching bundles the *recording act*, never the *diagnosis*. Volume-driven guardrails (auto-batching, size caps, queue-flood guards) are a **calibration gap**.

**3.5 Authorship & gate completion.** The `CandidatePromotion` is **system-authored** by the out-of-band feedback process as a **proposal-class node**, excluded from ground-truth traversal until approved (confirms DDR-001's proposal-visibility / check #4), and **carries the diagnosis substrate** the EA needs (supporting signal instances, recurrence count, the five-dimension inputs). **Gate completion** = recording a `PromotionDecision` with a per-candidate outcome; approval precedes materialization (the loop proposes, a human materializes); a **rejected verdict is terminal and durably explained** so the same gap doesn't re-surface and re-burn EA attention; the promotion must be auditable (policy → §5). Scheduled-job lifecycle, review queue/portal, and the dual-store write sequence → SDD.

---

## 4. Ratified substrate — signals & detection

**4.1 Signal taxonomy** (organized by `PROPOSED_FROM` source + action path; closed-but-additively-extensible; detection mechanics → SDD):
- **RG reasoning-recurrence → promotion path:** gap-recurrence (recurring `GapConclusion`) and override-recurrence (recurring human override: `ReasoningProgress{overridden_by_human}` → `REJECTED` → `RejectedAlternative{human_accepted}` → `WOULD_HAVE_USED` — the primary feedback input per DDR-001).
- **Operational track-record → promotion path:** `ObservedPattern` strength/weakness trends. *(This source is the reboot's advance over DDR-038's RG-only model — do not drop it.)*
- **RG evidence-quality → source-quality path (not promotion):** low-confidence `Evidence` under overridden conclusions.
- **KG participates as ground-truth-checked-against** (de-dup: don't re-propose already-promoted knowledge; the target-node references) — mechanics → SDD.

**4.2 Calibration-parameter mechanism** (one mechanism, named parameter set, values deferred): the loop's tunable parameters are **data-configured (not code), EA-owned** (only the §3.1 EA may change them), **audit-logged on every change** (→ §5), and **read fresh per run** (a change takes effect next run, no redeploy). Parameter set: **detection threshold** (min qualifying instances to surface a candidate), **lookback window** (rolling period instances are counted over), **run cadence** (how often detection runs). **Values are operational-onboarding calibration gaps — assert none.** Config store: PostgreSQL (DDR-001's existing workflow/staging assignment).

**4.3 Distillation governance — the derive/promote authority seam.** Distillation *deriving* an `ObservedPattern` into Operational is a permitted **non-EA-gated `derived` write** (distilled track-record, `derivation_class: distilled`, never authoritative selection knowledge); *promoting* it into authoritative selection knowledge (Catalog / Standards) stays **EA-gated** via the loop. Operational is the **staging tier**; the EA gate sits between it and the **authoritative tier** — which is why a non-EA-gated KG write does **not** breach ADR-001's SOFIA-never-self-modifies invariant (state this explicitly; it closes an apparent contradiction). Distillation cadence + generalization sensitivity reuse §4.2's mechanism; the **generalization algorithm and job ownership → SDD**.

---

## 5. Ratified substrate — retention, audit, provenance-survival

**5.1 Retention-class framework** (non-uniform, two cross-cutting invariants):
- **Durable / never-expire:** terminal-`promoted` `CandidatePromotion`, cost as-of records, the promotion audit trail, and terminal `CandidatePromotion`s (rejected included) as governance audit trail.
- **Bounded / non-uniform:** RG reasoning state — by structural role: `Evidence` shortest-lived (point-in-time snapshot; its **expiry is the trigger** for the preservation step in §5.3 — build-before-expiry); `RejectedAlternative` longest-lived (primary feedback input, authored — must outlive the detection windows that might promote it); `ReasoningProgress` / `ReasoningSession` between. Relative ordering is ruled; **absolute windows are §4.2 parameters, deferred.**
- **Archivable-on-terminal:** Operational `ObservedPattern`s in `resolved` / `superseded` — trigger keyed to terminal state + a **dwell** parameter (§4.2, deferred); archival is **retention-tier demotion, never deletion** (archived pattern stays traceable; reversible if a dormant pattern recurs). *(Requires DDR-002 amendment §7.1.)*
- **Two invariants binding all classes:** **never silently delete**; **explainability survives expiry** (when bounded retention removes an `Evidence`, any promotion sourced from it has its traceability preserved **before** the `Evidence` is removed).
- **Cost-record volume management** (partitioning / indexing / cold-tiering — *not* deletion) is shared-ownership with **RBT-25**; named, not authored.

**5.2 Audit policy** (two-record model):
- **Accountable decision:** the append-only `PromotionDecision` in the Neo4j Governance plane (authoritative who-approved-what; DDR-002-settled).
- **Operational audit trail:** the workflow event stream (candidate surfaced → decided → materialized / failed) + §4.2 config changes, append-only in **PostgreSQL** (DDR-001 audit assignment).
- **Audit-first invariant:** no KG promotion materializes without its audit record committed first; a successful KG mutation with no audit record is the unaudited-mutation failure mode — prohibited.
- **Recoverability requirement:** for any promoted fact, the audit answers who approved it, when, on what diagnosis basis, and the full provenance chain to source.
- The write sequence + event-type taxonomy → SDD. *(R24 note to state explicitly: the PostgreSQL trail is durable governance audit — not in the graph, not the transient per-action disposition stream R24 excludes. No tension with R24.)*

**5.3 Provenance-survival snapshot:** a dedicated frozen **`(:ProvenanceSummary)`** node (not a subgraph snapshot, not a blob — R25/R27-blessed as traversable), `origin_mechanism: derived`, carrying the frozen lineage a post-expiry audit needs (the `Evidence` summary, source-version pins, the chain to the governing `PromotionDecision`). **Materialize at promotion** (not at expiry) so build-before-expiry holds **by construction** — the ordering is an invariant of the promotion act, not a sweep that races retention. The reverse-lookup index/affordance, query patterns, and CI-invariant-or-not → **RBT-15**. *(Requires DDR-002 amendment §7.2.)*

---

## 6. Ratified substrate — conditional governance & retraction

**6.1 Conditional → promoted transition.** `approved_conditional` is a first-class EA diagnosis outcome (the §3.2 fifth dimension) — chosen when a pattern is genuine but **scope-bounded**. Authoring the `Condition` is part of the approval act. **Scope-setting is an EA accountability:** the predicate defines where the knowledge is safe to reuse — too broad over-admits (the safety failure check #19 prevents), too narrow strands genuine knowledge — so it is EA-authored and **audit-recorded as diagnosis basis** (§5.2). **Carry-forward governance requirement:** on supersession, a conditional scope is preserved unless an explicit EA `PromotionDecision` re-scopes it (silent default-to-`unconditional` is prohibited); the *mechanism* + CI-invariant-or-not → RBT-15 / RBT-33. Predicate **vocabulary/grammar → RBT-22** (constraint-validator). *(No DDR-002 amendment — conditional schema already locked.)*

**6.2 Multi-condition — named gap + safe interim posture.** The multi-`HAS_CONDITION` **consumption combinator** (disjunctive vs. otherwise), the **condition-set lifecycle** (activation/retirement/`status`), and any `Condition.status` field **stay the DDR-002 named gap**, resolved on first real instance. Rule **only** the safe interim posture: a second conditional promotion of an already-conditional fact **surfaces to the EA as a scope-conflict** requiring explicit diagnosis (widen / replace / add a disjunctive branch?) — **never silently auto-composed**. This preserves check #19's never-consumed-out-of-scope guarantee through the unresolved case. *(No DDR-002 amendment — rides existing machinery.)*

**6.3 Retraction governance.** Remedy boundary: **supersession** (the default) when promoted knowledge is *wrong-but-replaceable* (DDR-002 §6 versioning already supports it); **retraction** (the exception) when it *should never have been promoted* and has no correct replacement (a data-defect promotion, a spurious pattern). Retraction is itself an **EA-gated** decision (a reversing `CandidatePromotion` the EA approves), with the same accountability + audit as a forward promotion. **Record discipline:** a retraction requires **durable rationale** (why this should never have been knowledge) — captured on the audit trail + decision rationale, **not** a separate per-retraction DDR. *(Requires DDR-002 amendment §7.3 — the R27-pre-designed shape.)*

---

## 7. DDR-002 v1.1.0 amendment set (lands in PR-A, before DDR-003 cites it)

All three are **additive** (MINOR, 1.0.0 → 1.1.0; DDR-002's first `# Revised:` per R18). DDR-003 cites them as landed schema:

1. **`ObservedPattern.status` → add `archived`** (additive T2 value) — realizes §5.1's terminal-state archival path.
2. **`(:ProvenanceSummary)` node + `MATERIALIZES_PROVENANCE_OF` edge + the at-promotion materialization invariant** (to §7 CI-only set) — realizes §5.3.
3. **reversing `CandidatePromotion` + `RETRACTS` edge + the retraction-is-EA-gated invariant** (to §7 CI-only set) — realizes §6.3 (the R27-refinement shape).

The two new §7 invariants (at-promotion materialization; retraction-gated) extend **RBT-33**'s conformance set — CI tiering tracked there.

---

## 8. Named gaps & routed forward dependencies (carry these explicitly; do not silently drop)

- **multi-condition consumption + condition-set lifecycle** → DDR-002 amendment on first instance (§6.2).
- **provenance-survival index/affordance + CI-invariant-or-not** → RBT-15 (§5.3).
- **conditional carry-forward mechanism + CI-invariant-or-not** → RBT-15 / RBT-33 (§6.1).
- **Condition predicate vocabulary** → RBT-22 (§6.1).
- **cost-record volume management** → RBT-25 (§5.1).
- **judgment-consolidation health / weighting (promoted-vs-ingested)** → RBT-27 (parked) — a forward dependency DDR-003 *names*, does not author.
