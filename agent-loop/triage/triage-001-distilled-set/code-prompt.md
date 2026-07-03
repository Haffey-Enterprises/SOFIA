# Triage-001 Doc-Fix Batch — Claude Code Execution Prompt

**Status: RATIFIED by Tad 2026-07-02 — ready to hand to Claude Code.**

| Field | Value |
|---|---|
| **Mission** | Execute the ratified triage-001 amendment batch across the four-document design corpus. Documentation-only PR. |
| **Ruling authority** | `agent-loop/triage/triage-001-distilled-set/record.md` — read it FIRST, in full. Every edit below cites its ruling (§T-NN). Where this prompt and the record conflict, the record wins; stop and flag rather than guess. |
| **Targets** | `docs/adr/ADR-001-reasoning-architecture.md` · `docs/adr/ADR-002-graph-system-of-record.md` · `docs/ddr/DDR-001-data-architecture.md` · `docs/ddr/DDR-002-graph-schema.md` — fresh-fetch each at current HEAD before editing (base: `b857a0e`) |
| **Skills** | `author-decision-record` (templates, change-log discipline, version rules) governs all edits |
| **Out of scope** | `conformance/` (a separate Linear ticket chases this PR — do NOT touch constants, assertions, or contracts); any service code; Notion; the triage record itself |

## Version bumps

| Document | From | To | Basis |
|---|---|---|---|
| ADR-001 | v1.0.0 | **v1.1.0** | Material clarifications (T-11 reframe, T-19 fence, T-24 clause, T-14 cross-ref). *Flag: minor-bump is Claude's call, ratify-on-review — rows below are honest that no decision changes.* |
| ADR-002 | v1.0.0 | **v1.1.0** | Ratified at T-09 (new write-authority principle — a real decision addition) + T-04, T-07, T-25 |
| DDR-001 | v1.2.0 | **v1.3.0** | Ratified (T-01, T-02, T-04, T-05, T-07, T-09, T-12, T-25) |
| DDR-002 | v1.1.0 | **v1.2.0** | Ratified (the batch centerpiece — see below) |

## Discipline (binding)

1. **No story-telling** (record §D.1): normative docs carry contracts; history goes in change-log rows only. No deliberation prose, no trial narratives, no "we decided because of session X."
2. **Honest change-log rows, one per ruling or coherent ruling-group**, citing the record §T-NN. "No decision change" appears ONLY where true (T-07, T-10, T-11, T-12, T-14, T-16, T-18, T-24, T-25 legs). Decision-bearing rows (T-01, T-02, T-04, T-05, T-06, T-08, T-09, T-13, T-17, T-19–T-22, T-26–T-28) say what was decided, tersely.
3. **Design-first, one branch, one PR.** Tad reviews and merges; you do not merge.
4. **Self-review before PR:** re-read the record's spec sections against your diff; run the `code-review` skill's solo self-review pass on the diff (doc conformance: template structure, Decision-block discipline, cross-reference integrity, no orphaned §-references after edits).
5. Check renumbering is FORBIDDEN — existing #1–#21 keep their numbers; new checks append as #22–#25 exactly as assigned below.

---

## ADR-001 edits (→ v1.1.0)

1. **§2.2 reframe (T-11, ratified fix-now + absorptions):** retire the "illustrative" hedge — the vocabulary deferral was discharged by DDR-002 §4. The ADR commits the *categories* of captured reasoning (conclusion, evidence, rejected alternative); canonical labels are DDR-002 §4's, now ratified, cited not hedged. Add the altitude parenthetical, extended per **T-24**: structural containers (`ReasoningSession`), retention-mechanism nodes (`ProvenanceSummary`), and the produced-deliverable Artifact family take their authority from the data architecture (DDR-001) and its schema realization (DDR-002 §4–§5), not from this capture contract.
2. **§6 checks 2 and 6 (T-11):** bind category-first, verified against canonical vocabulary per DDR-002 §4 (rename-safe phrasing).
3. **§6 Propagation / §7 Cross-References (T-14):** add Cross-References entry — *Directives-Context-Envelope Bridge — runtime directive-propagation mechanism (forthcoming, unauthored); §6 neither requires nor pre-empts it.* §6 sentence unchanged.
4. **T-24 clause** is folded into edit 1 (same parenthetical). No separate edit.
5. **Three-hat fencing clause (T-19):** one clause — the §6 three-hat design review is platform-development governance, not a graph-captured gate. Home: ADR-001 §6 or DDR-002 §2.4 posture note — pick whichever reads cleaner in context; note the choice in the PR body.
6. **Change-log:** one v1.1.0 row covering 1–5 with record cites; "clarification/reconciliation — no decision change" (true here).

## ADR-002 edits (→ v1.1.0)

1. **General write-authority principle (T-09, the decision):** new subsection (natural home: extend §2.6 region) — every authoritative graph write has a named, component-scoped author; the gateway (§2.5) is the sole *executor* and enforcement boundary of all writes and is never itself the authoring authority; for EA-gated materializations, authority rests with the approving decision. Reframe existing §2.6 as the synthesis-time *instance* (ASA/AOE assignment unchanged). Add companion compliance check: *designs introducing an authoritative write name its component-scoped author; the gateway is never the author.*
2. **§2.2/§4.1 re-grounding (T-04, reduced form):** Enterprise requirement stated on present grounds — the DB-enforced existence-constraint set (DDR-002 §7) is Enterprise-only per vendor documentation (verified 2026-07-02) and in active schema use; secondary option-value note: deferred topology may adopt Enterprise clustering (§5.3 alignment). Community-trial narrative and "empirically established and ratified" REMOVED entirely. §4.1 Alternative A rewritten on the testable deficiency (no property-existence constraints). **T-23 rider:** the §2.2 substitution sentence cites the bar by named home — "the Substitution-Contract Capability Bar (DDR-001)."
3. **Decision-statement completeness (T-07):** Decision statement/§2 surfaces the GKE runtime exception as a sub-decision; ASA and AOE get a one-line introduction at §2.6 first use.
4. **§2.4 Firestore row (T-25):** label → *immutable produced-solution snapshots (per-version; dual-home model → DDR-001)*. Do NOT widen to artifact-family.
5. **§6 tracking pointer (tail: f4738b7b):** the aspirational-compliance line gains its tracking reference — the conformance harness (`conformance/`, RBT-33 Increment 1) + **RBT-48** (conformance harness catch-up).
6. **Change-log:** v1.1.0 rows — T-09 row is decision-bearing (principle added); T-04 row: "trial specifics never captured; recollection unreliable; requirement re-grounded on the vendor-verifiable existence-constraint dependency"; T-07/T-25 rows: no decision change.

## DDR-001 edits (→ v1.3.0)

1. **T-01:** session-root bullet drops "carries aggregate confidence"; add routing clause — confidence is per-conclusion (`ReasoningProgress` rollup, DDR-002 §4); any session-level aggregate is a read-time traversal affordance (`CONTAINS`→`ReasoningProgress`), consuming-SDD-owned, never a stored property. Row: decision re-homed (per-Solution comparison intent; DDR-002's 0..\* model controls).
2. **T-02 interim:** Decision.5 second clause + conformance check 4 scoped to ADR-001 §2.5's actual object (SOFIA's own reasoning entering encoded knowledge, EA-gated); broader entry-checkpoint principle routed by name to the forthcoming KG-entry-governance ADR.
3. **T-04:** Spike Findings section RETIRED entirely; Substitution-Contract Capability Bar gains item 6 — *DB-enforced property-existence-constraint capability at the schema layer*; single-database non-contradiction guard removed with the narrative. Row carries the history (same wording as ADR-002's T-04 row).
4. **T-05 Leg 2:** Cross-References DDR-003 entry gains status marker (forthcoming, unauthored).
5. **T-07:** Decision list gains the feedback-loop write-authority component, **citing amended ADR-002** (T-09 resolved on the cite-upstream branch).
6. **T-09 recast:** feedback-loop section rewritten in author/authorizer/executor terms — loop-job authors the proposal; the approving `PromotionDecision` is the authority for the materialization (provenance snapshot included, same transaction); the gateway executes, as it executes all writes. Conformance check 7 updated to match. **Artifact-authority homing (ratified sub-ruling):** ASA authors Solution artifacts (creation), gateway-routed; lifecycle-transition authority routed to SDDs under the ADR-002 principle.
7. **T-12:** footnote ² gains — *governance-participating identities only, not an IAM mirror; per-action disposition events excluded (transient → orchestration/observability SoR)*.
8. **T-25:** Firestore row's "concretized here as" preamble simplifies to a plain citation.
9. **Change-log:** v1.3.0 rows per above; T-01/T-02/T-09 decision-bearing, T-07/T-12/T-25 no-decision-change, T-04 the re-grounding row, T-05 marker-only.

## DDR-002 edits (→ v1.2.0) — the centerpiece

**§1:**
1. (T-22) Matrix note: SOFIA-recorded human decisions are the `authored → primary` case.
2. (tail: 958411d3) Unify `source_record_ref` applicability vocabulary with §7 #17: required on `ingested` and on `derived` with `derivation_class: distilled`; permitted-not-required on `aggregated`. One clause; align phrasing, change no rule.

**§2.3:**
3. (T-02 interim) Strike the staging-tier substantiation AND the "non-EA-gated" characterization; the distillation write's checkpoint posture is explicitly un-decided, routed to the forthcoming KG-entry-governance ADR (Named Gaps species). Pollution controls stand untouched.
4. (T-28) `CandidatePromotion` gains **`proposal_kind`** — T2, indexed, enum `{promotion, retraction}`; gloss: the FSM tracks proposal execution — `promoted` = the proposal's effect materialized, both kinds.

**§2.4:**
5. (T-06) GateDecision keeps only the grounded contract (`origin_mechanism: ingested`, external-captured, `source_record_ref`); authored-reserved clause and intermediate-case aside come out.
6. (T-19) Gloss GateDecision as the **enterprise SDLC gate on produced Solutions** (external authority decides; SOFIA mirrors as captured reference); decided-in-SOFIA mechanics routed by name to the approval + governance-state-manager SDDs.
7. (T-21) Clarifying clause: `approved_conditional` on GateDecision is a faithful mirror of a real enterprise outcome; it does not constitute §5 selection; gate conditions are NOT the promotion `Condition` machinery (external record holds them, reachable via `source_record_ref`).
8. (T-22) PromotionDecision gains explicit `origin_mechanism: authored` (approving Actor = human EA); "no source_record_ref" re-grounded on the §1 matrix. Condition: `authored`. Attestation: `authored`. Entry-path rule stated for Governance-plane types (mirrored → `ingested` + ref; SOFIA-issued/registered → `authored`, no ref); Actor/Role sourcing routed to governance-state-manager SDD.
9. (T-27) Verdict-precedence gains: ties are structurally excluded — the gateway enforces per-candidate strict `decided_at` monotonicity on `DECIDED_ON` writes.
10. (tail: 2fd87588) GateDecision entry cross-links §7 #17 at the `origin_mechanism` line.

**§3:**
11. (T-16) Decision/audit sub-catalog gains pointer entry: *GateDecision verdict edge `DECIDED_ON {outcome}` → Solution: defined at the Solution keystone (§5).* No duplication.

**§4:**
12. (T-17, decisions 1–3+5) `ReasoningProgress` gains: **`reasoner_category`** (T2, indexed; enum `encoded_reasoning | specialized_agent | llm_advisory | human_override` — ADR-001 §2.2's four categories); **`reasoner_ref`** (T2; required when `reasoner_category = specialized_agent`; permitted otherwise — SDDs may tighten); **`authoritative`** (T2, indexed boolean; fixed mapping — `llm_advisory` → false, all others → true; the §5.2-of-ADR-001 filter surface). State the **LLM-advisory invariant**: LLM-rendered content rides authored artifacts as non-authoritative content properties, never as authored nodes; the artifact's category/flag governs reads (rich payload stays T3/T4, SDD-shaped).
13. (T-17 Evidence reconciliation) One sentence in the RG-provenance posture: `Evidence`'s attribution is structural — `SOURCED_FROM` + version pin recover its source by traversal; authoritativeness is inherited-confidence-weighted; this satisfies ADR-001 §2.2's intent for this type.
14. (T-26) Rollup sentence gains the comparator pin: ceiling = max of supporting `Evidence.confidence`; `weight` affects aggregation below the ceiling, never the ceiling; zero-evidence case → SDD with the rollup function. (Coordinate with edit 12 — same §4 region as T-01's DDR-001-side removal.)
15. (T-10) Rewrite the §4 mapping paragraph to the true structure: four direct correspondences (technology/pattern/risk/compliance); capability → GapConclusion per DDR-001's gap definition (cite it); integration/cost as stated absorbed variants; OverrideFlag is flavor-carrying (Refine), orthogonal to the surface axis. *(contested)* flag stays.

**§5:**
16. (T-20) Provenance-survival guarantee gains the span definition: originating-Evidence set = closure over `PROPOSED_FROM` targets — Evidence → itself; ReasoningProgress → its `SUPPORTED_BY` Evidence set; ObservedPattern → nothing to freeze; RejectedAlternative → no Evidence. Two named Evidence-reaching edges; gateway computes the closure in the materialization transaction.
17. (T-13) §5 integrity-expectation prose cites new check #22; #19's "blocking safety control" claim stands substantiated.
18. (T-21) §5 selection sentence: `approved` is the sole selection-constituting outcome (coordinates with edit 7).

**§7:**
19. (T-13) **New check #22** — *conditional-scope carry-forward on supersession*: every supersession of an `applicability_state: conditional` node yields a successor that either carries `conditional` (condition preserved or EA-re-scoped) or was explicitly re-scoped `unconditional` by an EA `PromotionDecision`. Predecessor-keyed. **Safety-critical tier; gateway-behavioral.**
20. (T-17 decision 4) **New check #23** — *flag↔category consistency*: `authoritative` matches the fixed category mapping on every `ReasoningProgress`. **Safety-critical tier.**
21. (T-26) **New check #24** — *rollup upper bound*: `ReasoningProgress.confidence ≤ max(SUPPORTED_BY Evidence.confidence)`, scoped to conclusions with supporting evidence. **Follow tier; graph-state.** Comparator bound to §4's canon (amends with the SDD's rollup function if it redefines path strength).
22. (T-28) **New check #25** — *proposal_kind ↔ RETRACTS-edge consistency*. **Follow tier.**
23. (T-27) **#15 gains the well-definedness clause** (no new number): the governing edge is total under per-candidate strict `decided_at` monotonicity, gateway-enforced. Inherits #15's safety-critical tier.
24. (T-20) **#20 gains the completeness clause**: existence AND completeness against the §5-defined span at materialization. Tier unchanged.
25. (T-15) Authority-split paragraph re-drawn: the safety-critical *classification* stays bound (schema-contract metadata); "binds the precede-gateway rule" becomes the conformance requirement — *the gateway must not operate against an unenforced safety-critical tier* — with realization sequencing routed to build planning. Exposure-window text updates to marker-level current state: safety tier = Increment 1 mechanized (1a enforced; 1b contracts specified, required-flip at the gateway build); follow tier = Increment 2, later BUILD leg. Cross-References →conformance-mechanization entry gains the marker.
26. (T-18) #13's entry + exposure-window paragraph gain the layer reconciliation: runtime mechanism = gateway-enforced per §1/DDR-001; conformance contract = gateway-behavioral, 1b-specified, required-flip at gateway build; plus the structural sentence — classification enforcement and the sole write path are co-located in the gateway, so no PHI-bearing exposure interval precedes enforcement at graph entry.
27. (T-05 Leg 4 / T-02) Retraction's upstream-authority citations route to the forthcoming KG-entry-governance ADR (entry AND un-promotion scope), replacing the ADR-001 §2.5 stretch.

**Decision block (T-07):**
28. Numbered components added (terse, testable): the retraction shape (EA-gated reversing `CandidatePromotion` + `RETRACTS`); the provenance-survival guarantee (`ProvenanceSummary`, at-promotion materialization, §5 span); the `applicability_state` conditional-consumption model; the Option A supersession/temporal commitment.

**Named Gaps (consolidations):**
29. (T-01) New entry — *Solution-level aggregate confidence*: single-criterion candidate comparison at the pre-gate pick; ASA-computed at synthesis; requires per-candidate reasoning-attribution linkage + rollup scope + write-authority disposition; precedent: `aggregate_cost` (derived-at-creation-frozen, check #5 species); additive on first real instance (solutioning SDD).
30. (T-06 + T-19, consolidated) One *gate-decision origin evolution* entry: current = `ingested` (external SoR, mirrored) → future-1 = approval-in-SOFIA (`authored`, human Actor; live §1 value, #17-exempt; preconditions: RBT-21/22 SDD designs) → future-2 = SOFIA-issued approval (preconditions verbatim from T-06: upstream Position-4 gate-authority ruling; write-authority home; ADR-001 taxonomy category).
31. (T-21) New entry — *conditionally-approved-Solution semantics* (lifecycle advancement policy; whether a gate-condition structure is warranted) → governance-state-manager + solutioning SDDs, additive on first real mirrored instance.

**Cross-References / §2.6 / misc:**
32. (T-05 Leg 2) DDR-003 status marker (forthcoming, unauthored).
33. (T-08) §2.6 separates its two justifications: the Extension-validation exemplar purpose stands as authored; the cost-*capability* purpose is explicitly routed to the forthcoming cost-capability decision record.
34. (tail: e8cdf1c0) De-number "twelve SDDs" → "the downstream service SDDs" (both occurrences).
35. **Change-log:** v1.2.0 rows grouped per ruling; decision-bearing rows for T-02/T-06/T-08/T-13/T-17/T-19–T-22/T-26–T-28; no-decision-change rows for T-10/T-12(n/a here)/T-16/T-18/T-24-side effects; the tail rides the nearest ruling's row or one "resolvable-tail conformance fixes" row.

## Tail note (22b3ac4a / baseline N8)

The version bumps in this batch restore version-discipline going forward (each new content state carries a distinct version). Do not rewrite historical rows.

## PR

- Branch: `triage-001-doc-fix`. Title: `docs: triage-001 amendment batch (ADR-001 v1.1.0, ADR-002 v1.1.0, DDR-001 v1.3.0, DDR-002 v1.2.0)`.
- Body: link the record path; per-document bullet of rulings executed; the two flagged judgment calls (ADR-001 bump level; T-19 fencing-clause home); confirmation that `conformance/` was untouched and the catch-up ticket chases the merge.
- Self-review evidence: one paragraph confirming the record-vs-diff pass ran and what it caught.
