# Triage-001 Record — Frontier Triage of the Distilled-Set Runs

| Field | Value |
|---|---|
| **Session** | Frontier triage, 2026-07-02 (claude.ai surface; incremental record, extended per ratification) |
| **Corpus** | ADR-001 v1.0.0 · ADR-002 v1.0.0 · DDR-001 v1.2.0 · DDR-002 v1.1.0 at repo HEAD `b857a0e` |
| **Inputs** | run-004/005/007 ledgers + ratified audits (authoritative for validity/stance/dup/false-pos); run-006 emissions (unadmitted, four named triage-eligible finds); Notion SOFIA page (fetched — **no frontier section exists**); `~/Downloads/DDR-002-graph-schema-v1.1.0-staging.md`; retired-ledger rulings R30 and R3 (supplied by Tad in-session) |
| **Rulings** | All dispositions ratified per-item by Tad; this record is the durable carrier — Notion/Linear/kickoffs point here |
| **Status** | **COMPLETE.** T-01–T-29 ratified (T-03 dissolved) · Item 4 executed (Notion) · Item 5 executed: `code-prompt.md` RATIFIED; Linear **RBT-48** (harness catch-up, after PR merge) + **HEB-49** (skill lines, HEB-48 sibling). Remaining outside this record: Tad runs Code with the prompt → reviews/merges PR → SDD-001 gate clears; R23 paste owed for Appendix E. **Update 2026-07-03:** doc-fix PR #8 merged (`c935c68`); SDD-001 gate cleared; RBT-48 unblocked. R23 paste still owed for Appendix E. |

**Excluded false positives:** d677da64, 20f73ce0, 1c827a44 (per run audits) + **cae82b89** (ruled FALSE-POS this session, §Item-2). Cumulative loop precision 88/92.

---

## Item 1 — Dup-collapsed triage list (RATIFIED, as amended)

54 decision-bearing findings (17+14+19 across runs 004/005/007) + 4 run-006 uniques + 4 memory-carried frontier items + 3 EA judgment calls, collapsed to **28 items + resolvable tail** (T-03 dissolved at Item 2). Frontier carriers were memory-sourced (the Notion frontier write never landed — confirmed by fetch); dissolutions: E-1→T-04, E-2+F-2→T-09, F-1→T-17 (widened), F-3→T-22/T-28.

| # | Item | Members (run) | Notes |
|---|---|---|---|
| T-01 | B1 — ReasoningSession aggregate confidence | baseline B1; missed 3/3 runs | BLOCKING; ruled below |
| T-02 | S1 — staging-tier carve-out | 7f610b6c (005); d677da64 was its false-credit | Ruled below |
| T-03 | cae82b89 change-log honesty | — | **DISSOLVED** into T-02 (FALSE-POS, §Item-2) |
| T-04 | Spike substantiation (D1) + E-1 | e1bb7e0c, 986612a3 (004) · 498012b8 (005) · 784d7a9e, ddefe9fb (007) · 006 echoes | 4/4 draws; ruled below |
| T-05 | DDR-003 timing family (D2) | d6053ce6, d7364887, 66a041a2, 23c28708 (004) · bfa59e82, dae71869 (005) · a4d078fe (007) + legs 2b6ac1a8/006-EA#2, 40aef0f8 | 4/4; ruled below |
| T-06 | Authored-reserved GateDecision posture (D3) | d69da3e8, 912767ff (004) · 036560d7 (005) · e7b94bac (007) · 006-SA authority-home unique | 4/4, three hats; own-record candidate |
| T-07 | Decision-statement completeness family | 0b6e871a (004) · 855eff98, 241c43f4, cb282dff (005) · 0b501571 (007) · 006-LAA GKE-in-Decision | 4/4; 241c43f4 cross-notes T-09 |
| T-08 | Cost plane without upstream need | aba94bda (007) · 006-EA#1 | 2/2 EA; own-record candidate; R23 grounding — check capture-fidelity pattern (§D) |
| T-09 | Gateway-as-author / §2.6 extension + E-2 + F-2 | 7686768d (004) · ed1fa7d2 (005) · b8be270e (007) | Rider: Artifact-family write authority unassigned upstream (from T-01) |
| T-10 | conclusion_type 6↔7 mapping | e01ddee2 (005) · 7bc0b9a2 (007) | capability + OverrideFlag both unmapped |
| T-11 | Illustrative-vs-mandatory check 2 (ADR-001) | 4271a56b (005) · d89119a3 (007) · 006-SA#3 | |
| T-12 | IAM drift, Governance plane | 7c25420a (005, resolvable) · 35bd79e1 (007) · 006-SA#6 | resolvable reading favored |
| T-13 | Supersession carry-forward vs #19 claim | 6f145a17 (004) · 006-SA#5 | |
| T-14 | Dangling Directives-Context-Envelope Bridge ref | 877ab44c (007) · 006-LAA#3 | |
| T-15 | §7 enforcement-posture family | 01b84a95 (004) · 61f33a96 (005) · f59dd120 (007) | constructed cluster (ratified); one authority ruling disposes all three |
| T-16 | DECIDED_ON edge-catalog omission | 1f683374 (004) | fix-now candidate |
| T-17 | Capture-contract blocker (F-1, widened) | f789ddb8 (004) = Evidence slice | DDR-002 §4 missing source-category / authoritative-flag / LLM-advisory-content; verified live |
| T-18 | no-PHI enforcement contradiction | c288829a (004) | §1 gateway-enforced vs §7 CI-only; ADR-002 §2.7 depends |
| T-19 | GateDecision ingested vs internal three-hat gate | 64e28d99 (005) | |
| T-20 | ProvenanceSummary frozen-set completeness | aea9a913 (005) | #20 checks existence, not completeness |
| T-21 | approved_conditional undefined for GateDecision | 5840457e (007) | |
| T-22 | PromotionDecision origin_mechanism unspecified | b94454b7 + ede8ad3e (007) | provenance-matrix gap; F-3 overlap |
| T-23 | Mutual authoring dependency, capability bar | b1863ae1 (007) | note: T-04's re-grounding may moot |
| T-24 | ProvenanceSummary/Artifact under §2.2 deferral | 64319dce (007) | |
| T-25 | Firestore state-class narrowing | df072a4b (007) | "workflow snapshots" vs solution-body snapshots |
| T-26 | Rollup upper bound has no §7 check | 006-SA unique | survives T-01's fix; separate |
| T-27 | decided_at tie-break absent | 006-SA unique | F-3 overlap |
| T-28 | Terminal-token reuse (retraction `status: promoted`) | memory-sourced (F-3), verified at HEAD | judgment call: hazard vs ruled economy |
| T-29 | E-3 — DDR-002 normative contract density | memory-sourced EA call | reject-as-non-issue is a live bucket (3 draws, no density finding) |

**Resolvable tail** (rides Item-5 Code prompt, no per-item deliberation): 2fd87588, 958411d3, e8cdf1c0 (004 over-triggered) · f4738b7b · 22b3ac4a (=N8) · da89dc21 · 5f103fc4.

---

## Item 2 — cae82b89 verification (RATIFIED: FALSE-POSITIVE)

**Evidence:** the derive/promote seam is present verbatim in the v1.1.0 staging copy (2026-06-22, pre-distillation); sole delta is the removed "R30" citation. Distillation did not introduce it; the "no decision change" label is TRUE for this surface. Attribution positively confirmed by the recovered R30 ruling (ratified 2026-06-22, RBT-14 session). T-03 dissolved into T-02.

**Corrections logged:** (1) "fabricated" retracted — DDR-002 transcribed a ratified ruling faithfully; the defect is capture fidelity at R30 itself. (2) The retired ledger is *reachable* (deliberately excluded from the cleanup, not lost) — Tad can supply rulings on request; recorded as a live evidence option.

---

## T-01 — B1: ReasoningSession aggregate confidence (RATIFIED)

**Ruling:** amend-with-decision, two documents. Intent (stated by Tad this session — single-source, now record-carried): the aggregate is a **per-Solution comparison score** — one criterion for candidate-to-candidate comparison at the ASA's pre-gate pick; ASA computes it at synthesis (deterministic encoded reasoning per ADR-001 §2.3). The session root was a stale 1:1-era carrier; DDR-002's ratified 0..\* session→solution model controls, and a session-level scalar cannot compare candidates within one session. Upstream check: ADRs are silent on confidence (no conflict there); the carry-through failure is DDR-001→DDR-002.

**Amendment spec:**
- **DDR-001 (v1.3.0 batch):** session-root bullet drops "carries aggregate confidence"; add routing clause — confidence is per-conclusion (`ReasoningProgress` rollup, DDR-002 §4); any session-level aggregate is a read-time traversal affordance (`CONTAINS`→`ReasoningProgress`), consuming-SDD-owned, never a stored property. Change-log row: decision re-homed (per-Solution comparison intent), not deleted.
- **DDR-002 (v1.2.0 batch):** Named Gaps entry — *Solution-level aggregate confidence*: single-criterion candidate comparison at the pre-gate pick and gate support; ASA-computed at synthesis; requires per-candidate reasoning-attribution linkage (current edge grammar has none: CONTAINS/SUPPORTED_BY/LED_TO are session/conclusion-scoped) + rollup scope rule + write-authority disposition (see T-09 rider); realization pattern precedent: `aggregate_cost` (derived-at-creation-frozen, check #5 species); additive amendment on first real instance (solutioning SDD).
- **T-09 rider:** Artifact-family write authority is assigned nowhere upstream (§2.6 is RG-scoped; DDR-001 gateway table and dual-home row are silent on Solution-node authorship). Rule at T-09 with E-2.

---

## T-02 — S1: staging-tier carve-out + KG-entry governance (RATIFIED, compound)

**Root cause (two layers):** DDR-001 Decision.5's unqualified "SOFIA never self-modifies the KG" cites ADR-001 §2.5 (scoped to *encoded reasoning*) for a broader claim §2.5 doesn't make — because the principle actually intended was never authored. **Stated intent (Tad, this session):** human-accountable checkpoint on anything entering the Knowledge Graph, calibrated per source class — ingestion from an authoritative source gets a human checkpoint before official KG entry; noisy operational signal (logs, incidents with unclear root cause) must not pollute the Operational plane unchecked; the plane holds distilled lessons ("component X root-caused numerous incidents"), never an ITSM/observability replica; a way to see raw signal is needed to determine plane representation. R30 (recovered) transcribed faithfully into DDR-002 §2.3 but captured the ruling as a "staging tier" — not as intended; capture-fidelity failure at the ruling, not the transcription. The Operational plane is authoritative track-record, not pre-authoritative; the checkpoint belongs on the *write*. "Staging" also collides with two assigned senses (PostgreSQL state class; service-local stores) — the third sense dies.

**Ruling:** own-decision-record + interim honesty amendments.
- **Own-decision-record:** new ADR — **KG-entry governance** (charter: Appendix A). Authored in its own session with the deliberation gate; not here.
- **DDR-002 §2.3 (interim, v1.2.0 batch):** strike the staging-tier substantiation and the "non-EA-gated" characterization; the distillation write's checkpoint posture is explicitly **un-decided**, routed to the forthcoming KG-entry-governance ADR (Named Gaps species). Pollution controls (distilled-not-raw, bounded-by-distinctness, update-in-place, `archived` demotion) stand untouched.
- **DDR-001 (interim, v1.3.0 batch):** Decision.5 second clause + conformance check 4 scoped to ADR-001 §2.5's actual object (SOFIA's own reasoning entering encoded knowledge, EA-gated); the broader entry-checkpoint principle routed to the forthcoming ADR by name, not asserted without authority.
- **T-05 rider (discharged at T-05):** ADR owns the principle; DDR-003 owns the feedback-loop instantiation, citing it.

---

## T-04 — Spike substantiation (D1) + E-1 (RATIFIED, reduced form)

**Evidence base:** R3 recovered — blocker never captured; stated rationale ("Community could not create the necessary planes") describes a failure the current logical-subgraph realization would not hit; the "empirically established and ratified" phrase originates verbatim in R3's 2026-06-16 clarification (capture-fidelity pattern, second instance). April-era record corroborates the Enterprise *choice* on different, since-reversed grounds (clustering + support SLA; topology now deferred) and contains no plane-trial trace. Tad flags possible conflation of the Community trial with the failed pre-graph vector-store attempt — the trial-as-remembered is uncertain. **Vendor verification performed 2026-07-02:** property existence constraints are Enterprise-Edition-only per the current Neo4j Cypher Manual; uniqueness is available in both editions.

**Ruling:** amend-with-decision — re-ground on the present dependency; **no story-telling** (convention, §D): the trial narrative leaves the normative documents entirely; history lives in change-log rows only.

**Amendment spec:**
- **ADR-002 §2.2/§4.1:** Enterprise requirement stated on present grounds — the DB-enforced existence-constraint set (DDR-002 §7) is Enterprise-only per vendor documentation and in active schema use; secondary option-value note: deferred topology may adopt Enterprise clustering (aligns §5.3). Community-trial narrative and "empirically established and ratified" removed. §4.1 Alternative A rewritten on the testable deficiency (no property-existence constraints).
- **DDR-001:** Spike Findings section **retired**; its durable content moves affirmatively into the Substitution-Contract Capability Bar as new item 6 — *DB-enforced property-existence-constraint capability at the schema layer*; single-database non-contradiction guard removed with the narrative.
- **Change-log rows (both docs):** "trial specifics never captured; recollection unreliable; requirement re-grounded on the vendor-verifiable existence-constraint dependency." The dated row is the re-inflation tripwire.
- **E-1 ruled:** floor NOT acceptable as written; acceptable as re-grounded. Discharged.
- **R3 closure respected:** the Enterprise decision is not relitigated; only the record's account of its justification changes. Clustering stays out of the capability bar (option-value, not present requirement).

---

## T-05 — DDR-003 timing family (D2) (RATIFIED, four legs)

Live defect: DDR-003 — the corpus's most-cited forthcoming document — appears nowhere on the fetched roadmap.

- **Leg 1 (defer-with-scope):** roadmap item *Author DDR-003 — Feedback Loop Governance*, positioned in **Next, after the KG-entry-governance ADR** (its upstream: DDR-003's promotion-gate criteria instantiate that ADR's checkpoint principle). DDR-003 gates the **detection-promotion SDD**, not SDD-001 (the gateway builds against DDR-002's safety-critical-tier contract; DDR-003-routed policies ride the named interim postures DDR-002 already models). Sequencing confirmed at Item 4.
- **Leg 2 (fix-now):** DDR-001 and DDR-002 Cross-References gain a status marker on DDR-003 (forthcoming/unauthored) — marker, not narrative. ADR-001 already carries it. Rides the Item-5 batch.
- **Leg 3 (rejected as defect, affirmed as designed):** "governance shape locked ahead of DDR-003" (2b6ac1a8, 006-EA#2) attacks the ratified reversibility-tiering posture operating as intended; no locked shape found that forecloses DDR-003's policy space (scan, not proof); concrete shape defects stay live at T-27 and T-21.
- **Leg 4 (route to new ADR):** 40aef0f8 is right — ADR-001 §2.5 authorizes promotion only; un-promotion has no upstream authority. The KG-entry-governance ADR's scope is **mutation of enterprise ground truth generally** (entry AND un-promotion); DDR-002's retraction citations route there interim (same species as the T-02 interim edits).
- **T-02 rider discharged — the boundary:** the ADR owns the principle; DDR-003 owns the feedback-loop instantiation (EA criteria, thresholds, cadence, retention windows, remedy-boundary policy) citing the ADR as authority.

---

## T-06 — Authored-reserved GateDecision posture (RATIFIED)

**Ruling:** amend-with-decision (DDR-002 v1.2.0 batch) — demote to Named Gaps; own-decision-record declined-for-now, preserved as the gap's re-instatement precondition. Basis: the reservation clause is unsubstantiated in every load-bearing word — "expressible without re-architecture" is false (no write-authority home exists; expressing it requires at minimum an ADR-002 amendment, per 006-SA); "Position 4" does not supply a system-authored *approval* category (ADR-001's reasoner taxonomy has none; whether Position-4 arrival includes SOFIA holding gate authority is an open platform question a schema aside cannot settle — e7b94bac, 036560d7); and the clause rides §2.4 un-enumerated (d69da3e8). Forward-speculation narrative in a schema contract also strips under the no-story-telling convention. Nothing real is lost: `origin_mechanism` is a §1 platform-wide axis (`authored` stays legal; check #17's exemption is general); re-instatement is genuinely additive.

**Amendment spec (DDR-002 v1.2.0 batch):**
- §2.4 GateDecision keeps only the grounded contract: `origin_mechanism: ingested`, external-captured gate, `source_record_ref`. The authored-reserved clause and the intermediate-case aside come out.
- Named Gaps gains: *SOFIA-authored authoritative GateDecision* — re-instatement preconditions: (1) an upstream decision record ruling whether/when SOFIA authors authoritative gate decisions (Position-4 gate-authority question; likely territory for the encoding-strategy / Position-4 records in Later, e.g. the ADR-006/ADR-007 slots — not a triage authoring); (2) a write-authority home (same non-enumerated-authoritative-writes question as T-09's rider); (3) an ADR-001 reasoner-taxonomy category. Note in gap: the provenance axis already supports the value; realization is additive.
- Honest change-log row: the platform is not pre-committing gate authority — a removal that decides, per the item-2 precedent.

---

## T-07 — Decision-statement completeness family (RATIFIED: fix-now)

**Ruling:** fix-now, Item-5 batch. Every un-surfaced ruling is already made, ratified, and live in the body — enumeration repairs the record's claim about itself; "no decision change" is TRUE on these rows (item-2 label discipline, working in the other direction). Two legs mooted by prior rulings: d69da3e8's enumeration complaint (content removed at T-06); §2.3 seam enumeration (removed at T-02).

**Fix spec (Item-5 batch; terse testable enumeration lines per no-story-telling):**
- **DDR-002 Decision block:** numbered components added for the retraction shape (EA-gated reversing `CandidatePromotion` + `RETRACTS`), the provenance-survival guarantee (`ProvenanceSummary`, at-promotion materialization), the `applicability_state` conditional-consumption model, and the Option A supersession/temporal commitment. Exact lines finalized in the Code prompt spec.
- **DDR-001 Decision list:** gains the feedback-loop write-authority component. **Coordination note:** wording waits on T-09's substance ruling (upstream amendment → cite it; otherwise → enumerate as the DDR's own ruling). Same batch either way.
- **ADR-002:** Decision statement/§2 surfaces the GKE runtime exception as a sub-decision; ASA/AOE get a one-line introduction at §2.6 first use.
- **Root-cause routing:** family occurred 4/4 because amendments (RBT-43, RBT-45) added rulings without revisiting Decision blocks. Skill fix: amendment-discipline line for the `author-decision-record` bedrock skill ("an amendment that adds a ruling updates the Decision enumeration") — rides the Item-5 skill ticket with the no-story-telling convention.

---

## T-08 — Cost plane without upstream need (RATIFIED: defer-with-scope + interim honesty amendment)

**Ruling:** the plane stays; the capability decision gets a scheduled home. Finding verified TRUE (no cost capability in ADR-001/ADR-002/DDR-001; R23 grounding orphaned at de-ledgering — third instance). Two framing corrections ratified with it: blast radius is one SDD (cost-estimation), not twelve — Extension registration is additively reversible by construction; and §2.6 carries a real in-corpus justification (Extension-mechanism worked validation exemplar) alongside the unauthored one (cost as platform capability, corroborated by RBT-25 in Later but never authored upstream). Declined buckets: demote-to-gap strips the exemplar value and the §5 correction-surface weave; author-now is over-engineering ahead of the cost-estimation workstream; plain reject ignores a true finding.

**Spec:**
- **Frontier item (Item-4 write):** *author the cost-capability decision record* — own record or folded into the cost-estimation SDD's pre-authoring deliberation gate (authoring session's call) — positioned with RBT-25 in Later, **gating the cost-estimation SDD**.
- **Interim amend (DDR-002 v1.2.0 batch):** §2.6 separates its two justifications — exemplar purpose stands as authored; cost-capability purpose explicitly routed to the forthcoming record.
- **R23:** mandatory charter substrate for the future record (paste from Tad when convenient; not a gate) + capture-fidelity pattern's third test when the text arrives.

---

## T-09 — Gateway-as-author / §2.6 extension family + E-2 + F-2 + Artifact-authority rider (RATIFIED)

**Key:** the corpus already owns the author/executor distinction (ADR-002 §2.6: ASA *authors*; the write *executes* via the gateway) and stopped applying it. The materialization prose wrote "authority" where its own frame ("the loop proposes, the EA authorizes, the gateway materializes") meant "execution." **E-2 ruled:** §2.6's synthesis-time scoping is deliberate and correct as an *instance*; the defect is the missing general principle at ADR altitude.

**Amendment spec:**
- **ADR-002 → v1.1.0 (F-2 discharged; MINOR, additive, honest row):** general write-authority principle — every authoritative graph write has a named, component-scoped author; the gateway (§2.5) is the sole *executor*/enforcement boundary and is never the authoring authority; EA-gated materializations' authority = the approving decision. §2.6 reframed as the synthesis-time instance (assignment unchanged). Compliance gains the companion check: designs introducing an authoritative write name its author; the gateway is never it.
- **DDR-001 (v1.3.0 batch):** feedback-loop section recast in author/authorizer/executor terms; conformance check 7 updated; Decision-list write-authority line cites amended ADR-002 (T-07 coordination note resolved on the cite-upstream branch). 7686768d resolved: DDR-001 instantiates a stated principle, not silence-as-license.
- **Artifact-authority sub-ruling (ratified):** **ASA authors Solution artifacts** (creation), gateway-routed — producing-component pattern per §2.6's own statement; homed in DDR-001's write-authority treatment. Lifecycle-transition authority (Solution FSM advancement) **routed, not decided** — SDD territory under the new principle. Floor note: ASA-authors-Solution was inference from the stated pattern, ratified by Tad.
- Retires the defect *class*: T-06's authority-home precondition and future author-class questions resolve against a stated rule.

---

## T-10 — conclusion_type 6↔7 mapping (RATIFIED: fix-now)

**Ruling:** the sentence's defect is category confusion, not an enum defect — §5's correction mechanism is a two-axis structure (seven surfaces × three flavors) and the §4 sentence flattened it into a values→surfaces arrow. True structure: technology/pattern/risk/compliance map directly; capability homes on GapConclusion **by DDR-001's gap definition** ("gap = required capability with no resolving technology" — the uncited reconciliation e01ddee2 needed); integration/cost are the stated absorbed variants; **OverrideFlag is flavor-carrying (Refine), orthogonal to the surface axis** (7bc0b9a2's residue). Fix: rewrite the §4 mapping paragraph to the true structure. No value-set changes; *(contested)* flag stays; spike-generalization pass remains the enum's revisit vehicle. Declined: enum restructuring (front-runs the scheduled pass with zero synthesis runs); defer (leaves a false correspondence claim in locked T2 contract). Rides Item-5 batch.

---

## T-11 — Illustrative-vs-mandatory tension in ADR-001 (RATIFIED: fix-now + two absorptions)

**Ruling:** root cause is staleness, not contradiction — the "illustrative" hedge was correct at authoring, then DDR-002 §4 discharged the vocabulary deferral (ratifying exactly those labels; ADR-001's own distillation row records the refresh) and the hedge never came down. Fix-now: §2.2 re-framed — the ADR commits the *categories*; canonical labels are DDR-002 §4's, now ratified, cited not hedged. §6 checks 2/6 bind category-first, verified against canonical vocabulary per DDR-002 §4 (rename-safe). No decision change — acknowledging a completed delegation.

**Absorptions (ratified):** (1) tail items da89dc21/5f103fc4 — the three-kind list enumerates captured-reasoning *content* categories; `ReasoningSession` is the structural lifecycle container, an altitude fact not drift; half-parenthetical in §2.2 stops the finding regenerating. (2) Cross-note to T-17: check 2's "source attribution and authoritative flag" mandate is exactly what T-17 rules on — Code prompt lands both coherently.

---

## T-17 — Capture-contract blocker, widened F-1 (RATIFIED: amend-with-decision — the v1.2.0 batch centerpiece)

**Defect (verified at HEAD):** ADR-001 §2.2 commits per-artifact source attribution by category + authoritative flag; §5.2 makes the flag read-discipline-bearing. DDR-002 §4 supplies none of it — `origin_mechanism: authored` is uniform across RG content and cannot discriminate reasoner categories; no authoritative flag (§5.2's bypass structurally unimplementable); no LLM-advisory content marking. The platform's defining invariant is unrealized in the schema gating twelve SDDs. Named Gaps inapplicable: the empirical instance is the upstream mandate itself.

**Five ratified decisions (DDR-002 v1.2.0 batch):**
1. `ReasoningProgress` gains reasoner-category attribution — T2, indexed; ADR-001 §2.2's four categories (encoded reasoning / specialized agent / LLM advisory / human override).
2. Specific-agent attribution — reasoner reference (T2), required when category = specialized agent; other-category applicability finalized in the Code-prompt spec.
3. Authoritative flag — **explicit, indexed T2 boolean** (the §5.2 filter surface), not derived-at-read; new §7 CI check binds flag↔category consistency (dependency_manifest species: denormalized-for-introspection, sync-checked).
4. The new check joins the **safety-critical tier** — meets the precede-gateway criterion verbatim (guards wrong-consumption of non-authoritative content as authoritative; #19's species).
5. LLM-advisory invariant stated in schema: LLM-rendered content rides authored artifacts as non-authoritative content properties, never authored nodes; artifact category/flag governs reads. Rich payload stays T3/T4 SDD-shaped.

**Evidence reconciliation (f789ddb8, ratified):** reconcile-in-place — `Evidence`'s attribution is structural (`SOURCED_FROM` + version pin, recoverable by traversal; authoritativeness inherited-confidence-weighted) and satisfies ADR-001's intent for this type; one sentence in §4's RG-provenance posture makes the argument the document never made.

**Floor note:** property naming + reasoner-ref applicability matrix finalize in the Code-prompt spec (Tad reviews at Item 5). **Convergence note:** F-1 was distillation-era knowledge; the loop independently found the Evidence corner (f789ddb8) with zero shared context.

---

## T-12 — IAM drift, Governance plane (RATIFIED: fix-now)

**Ruling:** source-class and representation-scope are different axes; DDR-001's terse row conflated them by silence. IAM is correct as source-class (where actor identity comes from); the plane's own stated role ("actors and decisions" — decision/audit graph) needs participants, never the directory — DDR-002 §2.4's narrowing is the intent made explicit (concurring with the run-005 arbiter's resolvable ruling over run-007's flip). Fix: DDR-001 footnote ² gains one clause — *governance-participating identities only, not an IAM mirror; per-action disposition events excluded (transient → orchestration/observability SoR)*. Source-class and illustrative node-types columns unchanged. Declined: softening DDR-002's side (moves away from evident intent). Rides Item-5 batch.

---

## T-13 — Supersession carry-forward vs #19's blocking-safety-control claim (RATIFIED: amend-with-decision)

**Ruling:** the document left itself an open question ("whether it warrants a CI invariant" — routed, unanswered); the finding answers it. The bypass meets the safety-critical criterion nearly verbatim (wrong-consumption of conditional knowledge as ground truth from first writes); if the front door (#19) is safety-critical, its named bypass is the same tier. The "cannot catch" objection dissolves by **keying the check on the predecessor, not the successor**.

**Amendment spec (DDR-002 v1.2.0 batch):**
- New §7 check — *conditional-scope carry-forward on supersession*: every supersession of an `applicability_state: conditional` node must yield a successor that either carries `conditional` (condition preserved or EA-re-scoped) or was explicitly re-scoped `unconditional` by an EA `PromotionDecision`. **Safety-critical tier; gateway-behavioral** mechanization (the #21 combination; supersession is one atomic gateway transaction per §6). Numbering finalized in the spec (T-17 also adds a check).
- §5 integrity-expectation prose cites the check; #19's claim stands **substantiated** rather than softened (aligns with T-02's checkpoint intent: EA-set scope survives mechanically).
- Still routed: carry-forward implementation + cross-origin case → knowledge-service SDD; multi-condition semantics remain the existing named gap.
- Declined: fix-now-by-softening — preserves a hole in a safety control to save a check.

---

## T-14 — Dangling Directives-Context-Envelope Bridge reference (RATIFIED: fix-now)

**Ruling:** the referent is not a phantom — it is the roadmap's "ADR-005 or fold — Directives Propagation Bridge (RBT-11)" (identification inferred from naming + the runtime directive-propagation context; if distinct artifacts, the fix is identical with a different gloss). T-05 Leg 2 species: real, planned, unauthored referent lacking a status marker. Fix: ADR-001 §7 Cross-References gains — *Directives-Context-Envelope Bridge — runtime directive-propagation mechanism (forthcoming, unauthored); §6 neither requires nor pre-empts it.* §6's sentence stands (it prevents design-time/runtime propagation conflation); canonical naming settles at the ADR-005-or-fold authoring. Declined: deletion (removes useful disambiguation; silently un-decides a scope ruling). Rides Item-5 batch.

---

## T-15 — §7 enforcement-posture family (RATIFIED, as revised on fetched evidence)

**Fork ruled: misunderstanding (Claude's), not over-swept retirement — the mechanization was BUILT.** `conformance/` = RBT-33 Increment 1 (2026-06-22, TDD-first, ephemeral-Neo4j): **1a** graph-state assertions (#1, #11, #15, #16, #17 + DDR-001 check 5) enforce-on-landing; **1b** gateway-behavioral contracts (#7, #9, #13, #14, #19) `xfail` against the `GraphGateway` seam, required-flip reserved to RBT-15. Increment 2 (follow tier) deliberately unbuilt.

**Findings disposed:** 61f33a96 (feasibility) — empirically closed; the built 1a/1b split IS the answer, pre-dating the finding; fired because the *document* presents mechanization as forthcoming (true-on-the-document, overtaken by repo reality). f59dd120 (authority) — stands: §7 restates precede-gateway as a **conformance requirement** (gateway must not operate against an unenforced safety tier); delivery sequencing routed to build planning. 01b84a95 (gating decision) — substantially discharged: the requirement + the built flip rule is the gating decision, operational; residual = catch-up gap, verified (constants fresh-fetched from **v1.0.0** — #20/#21 absent; tonight's v1.2.0 additions widen it).

**Spec:**
- **DDR-002 v1.2.0 batch:** §7 authority-split re-drawn (requirement form) + status-marker honesty — exposure-window text and →conformance-mechanization cross-reference reflect current state at marker level (safety tier: Increment 1 mechanized, 1a enforced, 1b specified pending gateway flip; follow tier: Increment 2, later BUILD leg). No narrative.
- **Linear ticket (Item 5), sequenced AFTER the doc-fix PR merges:** conformance harness catch-up increment — #20 + #21 plus T-13's carry-forward and T-17's flag↔category checks as 1b-style contracts; `schema_constants.py` refreshed to v1.2.0 vocabulary (`ProvenanceSummary`, `RETRACTS`, `MATERIALIZES_PROVENANCE_OF`, `archived`, reasoner-category/flag properties).
- **SDD-001 charter note stands:** gateway-behavioral contracts flip to required at the gateway build (the harness's own rule).

---

## T-16 — DECIDED_ON edge-catalog omission (RATIFIED: fix-now, pointer entry)

**Ruling:** audit's TRUE stands; remedy narrowed. The edge is defined — §5 keystone, covered by §3's closing deferral — but §3's Decision/audit sub-catalog includes `REVIEWED→Artifact` (also cross-family) while the verdict edge defers, so the placement practice is inconsistent and a §3 reader misses the load-bearing edge. Fix: §3's Decision/audit sub-catalog gains a **pointer entry** — *GateDecision verdict edge `DECIDED_ON {outcome}` → Solution: defined at the Solution keystone (§5)* — preserving single-home discipline. Declined: duplicating the definition (drift surface; one-edge-per-relationship); relocating REVIEWED (churn, moves an audit-shaped edge off the audit sub-graph). Rides Item-5 batch.

---

## T-18 — no-PHI enforcement contradiction (RATIFIED: fix-now)

**Ruling:** two claims about two layers, conflated by the document — §1's "gateway-enforced" = the runtime mechanism; §7 #13's CI-only placement = the conformance verification. Reconciliation rests on two facts: **(structural)** the PHI exposure window at graph entry is zero by construction — ADR-002 §2.5 + DDR-001's gateway prohibitions mean no write path exists except through the enforcing component, so no interval precedes enforcement (scoped to graph entry; intake-side classification on pre-graph workflow state is service behavior outside DDR-002's scope); **(fetched, T-15)** #13 is already in the built harness's 1b set (`test_classification.py`) — gateway-behavioral contract, required-flip at gateway build.

**Fix (DDR-002 v1.2.0 batch, coordinated with T-15's §7 marker edits):** #13's entry + exposure-window paragraph gain the layer reconciliation and the structural co-location sentence. ADR-002 §2.7 untouched — its soundness claim is now substantiated downstream. No decision change. Declined: pulling #13 from the CI-only set (membership correct; only its characterization was flat).

---

## T-19 — GateDecision `ingested` vs the internal three-hat gate (RATIFIED, intent confirmed)

**Intent (Tad):** the approval act is external to SOFIA and mirrored in SOFIA; may later move into SOFIA (human approval in SOFIA), and in a future state SOFIA may issue approvals under certain conditions — design must account for these eventualities. **Three gate senses fenced:** (1) platform-development gate (ADR-001 §6 three-hat review — governance OF SOFIA, not graph content); (2) enterprise SDLC gate on produced Solutions (= `GateDecision`: external authority decides, SOFIA mirrors, `ingested` + `source_record_ref`); (3) SOFIA-internal human approval (= `PromotionDecision` / approval-authored artifacts). 64e28d99's collision was senses 1↔2, never fenced in the corpus.

**Spec (DDR-002 v1.2.0 batch + one ADR-001 clause):**
1. §2.4 glosses `GateDecision` as the **enterprise** SDLC gate on produced Solutions (external authority; SOFIA mirrors as captured reference).
2. Fencing clause: three-hat design review is platform-development governance, not a graph-captured gate (home — ADR-001 §6 or §2.4 posture note — picked in the Code-prompt spec).
3. **Named Gaps: consolidated *gate-decision origin evolution* entry** (restructures T-06's ratified entry — preconditions preserved verbatim): current = `ingested` (external SoR, mirrored); future-1 = approval-in-SOFIA → `origin_mechanism: authored`, Actor = human — live §1 value, #17-exempt, genuinely no re-architecture; preconditions = approval/governance-state-manager SDD designs (RBT-21/22); future-2 = SOFIA-issued approval = T-06's gap as the far stage (three preconditions stand).
4. Decided-in-SOFIA mechanics routed by name to the approval + governance-state-manager SDDs; `approval_token_id` untouched (T3).

---

## T-20 — ProvenanceSummary frozen-set completeness (RATIFIED: amend-with-decision)

**Ruling:** T-13's remedy species — an unverifiable claim becomes checkable by writing down the rule. Span defined: the originating-Evidence set of a promotion = closure over `PROPOSED_FROM` targets — `Evidence` → itself; `ReasoningProgress` → its `SUPPORTED_BY` Evidence set; `ObservedPattern` → nothing to freeze (durable KG node, live-traversable); `RejectedAlternative` → no Evidence (`WOULD_HAVE_USED` is not Evidence-mediated). Two named Evidence-reaching edges (`PROPOSED_FROM`, `PROPOSED_FROM∘SUPPORTED_BY`); closure computed by the gateway in the materialization transaction.

**Spec (DDR-002 v1.2.0 batch):** §5 guarantee gains the span definition (future Evidence-reaching edges amend the rule — contract maintenance, not hedge); **#20 gains the completeness clause** (existence AND completeness against the span at materialization); tier unchanged (follow, gateway-behavioral — guards post-expiry audit, not ground-truth entry). Routed, not decided: `RejectedAlternative`-expiry survival → the existing DDR-003 ProvenanceSummary-retention hand-off. Harness: #20 lands in the T-15 catch-up ticket in completeness form directly — never built twice. Floor note: the closure rule is Claude's formalization of §5's chain prose; ratified.

---

## T-21 — approved_conditional undefined for GateDecision→Solution (RATIFIED: small amend + named gap)

**Ruling:** the outcome value stays — under T-19's mirroring posture, "approved with conditions" is a real enterprise gate outcome a captured reference must be able to represent; restricting the vocabulary is a capture-fidelity failure. The SA's "no Condition attachment path for GateDecision" is **correct design**, not the defect — promotion `Condition` = applicability predicate (retrieval admission); gate condition = remediation obligation; reuse would be the exact gate↔promotion leakage §2.4's de-conflation prevents. Under mirroring, the conditions live in the external record, reachable via `source_record_ref`. **Pinned interim (T-02 checkpoint spirit — never auto-admit on unevaluated conditions):** `approved` remains the sole selection-constituting outcome; a mirrored `approved_conditional` records faithfully and does not constitute §5 selection.

**Spec (DDR-002 v1.2.0 batch):** §2.4/§5 clarifying clause (mirror-faithful, non-selecting, de-conflation stated); Named Gaps entry — *conditionally-approved-Solution semantics* (lifecycle advancement policy; whether a gate-condition structure is ever warranted) → governance-state-manager + solutioning SDDs, additive on first real mirrored instance. Floor note: non-selecting interim is the safe default; enterprise gate-taxonomy reconcile (gate_0/1/2) may revisit.

---

## T-22 — PromotionDecision origin_mechanism unspecified (RATIFIED: amend-with-decision, four pieces)

**Ruling:** the value was implied by the design's own logic — **`authored`** (`§1`: human/SOFIA-authored; the EA's approval act made in SOFIA). Everything reconciles on statement: matrix marks `source_record_ref` N/A on `authored` (= §2.4's existing "no source_record_ref," now constraint-backed); #17 never fires. Closes the T-19 loop structurally: GateDecision `ingested` / PromotionDecision `authored` encode the external/internal issuing split the de-conflation prose describes.

**Four pieces (DDR-002 v1.2.0 batch):** (1) PromotionDecision `origin_mechanism: authored` explicit at §2.4, approving Actor = human EA; (2) Condition `authored` (same issuing act); (3) §1 matrix note — SOFIA-recorded human decisions are the `authored → primary` case (closes ede8ad3e's matrix gap); (4) entry-path rule stated for Governance-plane types generally (mirrored → `ingested` + ref; SOFIA-issued/registered → `authored`, no ref) — Attestation `authored` (thinner inference, flagged); **Actor/Role routed** to governance-state-manager SDD (deployment-shaped sourcing), bounded by the rule. Floor: PromotionDecision/Condition are clean derivations; Attestation flagged; Actor/Role not guessed.

---

## T-23 — Mutual authoring dependency, capability bar (RATIFIED: reject-with-rationale + T-04 spec rider)

**Ruling:** audit's TRUE stands; the structure exists as described and is **acceptable-as-designed** — the house delegation pattern (deferral-then-discharge, T-11 precedent): upstream commits the principle, downstream realizes the detail at its altitude, reference resolves once both ratified. The "unverifiable at acceptance time" charge is a greenfield bootstrapping artifact, closed the day DDR-001 landed. Test applied (stated for the record, first outright reject of a decision-bearing finding): delegation explicit + delegate ratified + reference resolves — all three hold; any failing flips the bucket. **Rider on T-04's in-flight spec:** §2.2's substitution sentence cites the bar by named home ("Substitution-Contract Capability Bar, DDR-001") — discharge-gloss pattern, one clause, zero new work.

---

## T-24 — ProvenanceSummary + Artifact family under the §2.2 deferral (RATIFIED: fix-now via T-11 clause extension)

**Ruling:** audit's TRUE stands; the authority chain the finding tested is misattributed — neither family claims ADR-001 §2.2's deferral. ProvenanceSummary's authority = DDR-001 Versioning & Temporal Model (summary-on-evidence-expiry), cited at its definition; Artifact family's authority = DDR-001 solution dual-home, cited verbatim at §5. What's genuinely true: **ADR-001-side reader gap** — §2.2's deferral reads as the sole channel for node families near the reasoning region, with no signpost that two families route through DDR-001. Fix: T-11's §2.2 parenthetical generalizes by one clause — structural containers, retention-mechanism nodes, and the produced-deliverable Artifact family take their authority from DDR-001/DDR-002 §4–§5, not from this capture contract. No DDR-002 change (citations already correct). **Instrument note:** validates the calibration-2 coherence charter (B1-class detection live); nuance for future audits — the detector can fire on a misattributed chain while flagging a real reader hazard; disposition should test claimed vs cited chains before sizing the remedy.

---

## T-25 — Firestore state-class narrowing (RATIFIED: fix-now, two clauses)

**Ruling:** downstream realization is the intent; upstream label is stale reboot-era vocabulary — another completed delegation whose upstream wording never caught up (ADR-002 §2.4 itself delegates persistence patterns to DDR-001). Edits: **(1)** ADR-002 §2.4 Firestore row → *immutable produced-solution snapshots (per-version; dual-home model → DDR-001)* — deliberately NOT widened to produced-artifact class (only the Solution instance is ratified; family generalization arrives additively when a second artifact type dual-homes, per T-06 discipline); **(2)** DDR-001 Firestore row — the "concretized here as" reconciliation preamble simplifies to a plain citation (the bridge prose retires with the gap). No decision change. Rides Item-5 batch.

---

## T-26 — Confidence-rollup upper bound has no §7 check (RATIFIED: amend-with-decision; run-006 unadmitted — validity ruled TRUE here)

**Ruling:** T-13/T-20 species — pin the comparator, the check becomes real. Committed: ceiling = **max of supporting `Evidence.confidence`** (§4's own canon: Evidence.confidence IS the path's inherited strength); `weight` affects aggregation below the ceiling, never the ceiling; zero-evidence case → SDD with the rollup function.

**Spec (DDR-002 v1.2.0 batch):** §4 rollup sentence gains the comparator pin (same region as T-01's edits — Code prompt coordinates); new §7 check — `ReasoningProgress.confidence ≤ max(SUPPORTED_BY Evidence.confidence)`, scoped to conclusions with supporting evidence; **follow tier** (guards reasoning-quality integrity, not ground-truth entry — EA gate remains the accountability control); graph-state species → T-15 catch-up ticket. Amendability bound to §4's canon: if the SDD's rollup redefines path strength, the comparator amends with it. Floor: single-draw unadmitted evidence; max-not-weighted is a ratified judgment.

---

## T-27 — decided_at verdict-precedence tie-break absent (RATIFIED: amend-with-decision — monotonicity, not tie-break; run-006 unadmitted — validity ruled TRUE here; discharges F-3's CandidatePromotion leg)

**Ruling:** prevention over resolution — ties made structurally impossible rather than arbitrarily resolved. ID-ordering tie-break **rejected as accountability-hostile** (contradictory governance verdicts resolved by primary-key assignment). Committed: **per-candidate strict `decided_at` monotonicity, gateway-enforced** — a new `DECIDED_ON` edge on a candidate must carry `decided_at` strictly greater than any existing edge's on that candidate; governance is append-only and every write flows through the sole gateway, so the invariant is cheap at the chokepoint (T-18's zero-exposure species).

**Spec (DDR-002 v1.2.0 batch):** §2.4 verdict-precedence gains the ties-structurally-excluded sentence; **#15 gains the well-definedness clause** (no new check number) — inherits #15's safety-critical tier, since the clause is what makes the safety-critical check deterministic. Harness (catch-up ticket): 1a assertion (no per-candidate `decided_at` duplicates on `DECIDED_ON`) + 1b gateway-behavioral write contract. Floor: single-draw unadmitted; collision probability low with a human EA gate — ruling rests on the principle (safety-critical checks admit no undefined cases), not likelihood.

---

## T-28 — Terminal-token reuse: retraction completes at `status: promoted` (RATIFIED: middle path; memory-sourced F-3 leg, verified at HEAD)

**Ruling:** keep the economy's core (one FSM tracking *proposal* lifecycle — `promoted` = effect materialized, both directions), close the query hazard (direction discoverable only by edge traversal → property-filtered reads silently sweep opposite events). T-17's own precedent: explicit discriminator over derive-at-read where it's the filter surface.

**Spec (DDR-002 v1.2.0 batch):** (1) `CandidatePromotion` gains **`proposal_kind`** — T2, indexed, enum `{promotion, retraction}`; (2) new §7 sync check — `proposal_kind` ↔ `RETRACTS`-edge presence (dependency_manifest species); **follow tier** (guards ledger consumption/audit, not ground-truth entry); rides catch-up ticket; (3) §2.3 gloss — FSM tracks proposal execution, economy stated so it stops reading as accident; (4) **declined: terminal-token rename** (`promoted`→`executed`) — churns a locked T2 enum through prose, checks, and harness constants for a hazard the discriminator closes; named reversal condition: real consumer confusion at SDD authoring rides that amendment with its constants refresh. Floor: prospective hazard, zero promotions run, no upstream mandate — ratified on the lock-now/retrofit-later asymmetry, second-guessing a framed-as-deliberate economy with Tad's eyes open.

---

## T-29 — E-3: DDR-002 normative contract density (RATIFIED: reject-as-non-issue — E-3 discharged)

**Ruling:** the held distillation-era EA call discharges on three evidence lines, weights stated: (1) three stance-isolated adversarial draws produced **zero** density findings — every finding attacked a specific contract's correctness/grounding, never contract quantity; the one density-adjacent true finding (f59dd120) was a one-paragraph altitude defect, fixed at T-15 (weak-but-real: small sample, density not an explicit charge); (2) tonight's triage ran the question ~54 times in miniature and the corpus **thickened on demand** — dispositions added precision (comparator pins, span closures, monotonicity, discriminators); removals were unsupported *claims*, never excess *contracts*; (3) the density-management machinery (T1–T4 tiering, Named Gaps, routing map, contested-T2 flags + spike-generalization pass) already operates and resolved every too-much? moment tonight. Floor: memory-sourced — ruled on the question as memory carries it; re-scope available if E-3's original text was narrower.

---

## Item 4 — Notion reconciliation (EXECUTED 2026-07-02, plan + gate ruling ratified)

**Gate ruling (ratified):** the SDD-001 gate converted from open decision to mechanical condition — Now closed as "triage complete, amendments spec'd"; SDD-001's gate = **doc-fix PR merged**. Write landed on the SOFIA page (five coordinated edits): Now item → "Land the triage-001 doc-fix PR" with record pointer; SDD-001 entry → new gate + charter notes (safety-critical-tier contract; 1b flip-to-required incl. T-13/T-17/T-27 checks; T-09 write-authority principle); **Next tier gains** KG-entry-governance ADR (ahead of DDR-003; charter Appendix A) + Author DDR-003 (after the ADR; gates detection-promotion SDD; Appendix C) + provenance line discharging the memory-carried frontier (E-1–E-3, F-1–F-3); **Later gains** cost-capability decision record (with RBT-25; gates cost-estimation SDD; Appendix E); **BUILD note** — 1b flip at knowledge-service build; Increment 2 = BUILD leg. **Flagged addition (one beyond plan):** Retired-band wording clarified ("document-level enforcement-mechanization") + parenthetical that the graph conformance harness was built (RBT-33 Increment 1) — closes the T-15 misreading trap at its source; Tad may strike.

---

## Appendix A — Charter: KG-entry-governance ADR (authoring-session substrate)

> **Resolved (RBT-59, 2026-07-17):** the "KG-entry-governance ADR" this charter scopes is now **ADR-008 (Ground-Truth Mutation Governance)**, ACCEPTED v1.0.0. The charter text below is preserved as the authoring-session substrate; ADR-008 is the authority of record.

1. **Principle:** human-accountable checkpoint on mutation of enterprise ground truth — entry AND un-promotion — calibrated per source class.
2. **Scope:** entry paths (ingestion, distillation, promotion) + un-promotion/retraction (T-05 Leg 4). Supplies retraction the upstream authority DDR-002 §7 #21 currently lacks.
3. **Per-source-class calibration (Tad's stated intent):** authoritative-source ingestion → verification-weight checkpoint on the captured representation; operational distillation → substantive review of the distilled judgment (noisy-signal pollution is the driving risk); promotion → the existing EA gate as the already-built instance.
4. **Inherited constraint (R30 declined-option):** "gate all KG writes" was declined for bottleneck reasons — per-pattern EA action must not make Operational unwritable. The calibration must answer this without abandoning the checkpoint.
5. **Open question the ADR must rule:** Environment plane posture — CMDB-observed deployed reality: per-write review vs confidence-weighting; volume/bottleneck is a real design constraint.
6. **Leading mechanism pattern (named, not decided):** the proposal-class shape — `CandidatePromotion` analogue for distillation (candidate-`ObservedPattern`, excluded from ground-truth traversal until approved).
7. **Named need:** evidence-visibility affordance for the checkpoint reviewer (`source_record_ref` is the existing hook; whether candidates carry evidence summaries pre-approval is design work).
8. **Surviving R30 distinction:** Operational vs authoritative *selection* knowledge (Catalog/Standards) — the sharper line survives even as the tier framing dies.
9. **Altitude recommendation:** new ADR (platform governance guarantee cited by DDR-003, ingestion ADR-004 slot, multiple SDDs); the authoring session's deliberation gate may overrule the home.
10. **Mandatory substrate:** R30 full text; this record §T-02; DDR-003 boundary (§T-05).

## Appendix B — Named-gap content: Solution-level aggregate confidence

Carried in §T-01's DDR-002 spec. Key design questions for the realizing amendment: per-candidate reasoning-attribution linkage (new edge vs rollup-scope rule vs SDD-computed); frozen-at-synthesis vs recomputed; write-authority home (T-09/Artifact-authority ruling); relation to the §4 canonical confidence definition (Solution qualifies as a "derived/reasoned thing").

## Appendix C — DDR-003 charter additions

Position: Next, after the KG-entry-governance ADR; gates the detection-promotion SDD. Cites the KG-entry ADR as authority for its promotion-gate criteria. Inherits from DDR-002's routing map: remedy-boundary, batch-eligibility, condition lifecycle, archival policy, ProvenanceSummary retention windows, judgment-consolidation health, multi-condition interim posture.

## Appendix D — Conventions ratified + patterns observed

1. **No story-telling in ADR/DDR/SDD documents** (ratified 2026-07-02): normative documents carry contracts; history lives in change-log rows and session/review records. Permanent home: `author-decision-record` bedrock skill (ticket at Item 5; HEB-48's sibling).
2. **Triage-record-as-carrier** (ratified): this artifact is the single durable carrier for triage substrate; Notion frontier entries, Linear tickets, and kickoff prompts point here. Chain precedent: runs → audits → triage.
3. **Capture-fidelity pattern (observed, 2 instances):** R30 and R3 both recorded more confidence than the facts warranted at ruling capture; de-ledgering then promoted the overclaims into bare normative prose. Examine T-08 (R23, cost plane) with this pattern explicitly in hand.
4. **Doc-vs-repo status drift (observed at T-15):** reviewers see only the four documents; posture claims the repo has overtaken generate findings true-on-the-document and false-against-reality. Remedy species: status markers in the document (T-05 Leg 2 / T-15 pattern), kept current.
5. **Correction registry:** retired ledger is reachable via Tad (deliberately excluded, not lost); "fabricated" retracted at T-02; a claimed-but-unrun vendor verification was owned and then actually performed at T-04; over-swept-retirement read retracted at T-15 (the mechanization was built).

## Appendix E — Charter stub: cost-capability decision record

Home: own record or the cost-estimation SDD's pre-authoring deliberation gate (authoring session rules the home). Position: Later, with RBT-25; gates the cost-estimation SDD. Substrate: R23 full text (to be supplied — run the capture-fidelity check on arrival); DDR-002 §2.6 as-built (RateCard / CostFactor / CapabilityCostEstimate, compute-on-read model, estimate-vs-actual variance intent); the exemplar-vs-capability justification split (§T-08); §5 cost correction-surface + T-10's conclusion_type mapping outcome.

---

*Extended per ratification. Next: T-06 ruling → remaining items → Item 4 (Notion reconciliation, creates the frontier section) → Item 5 (output routing: Code prompt for doc fixes, Linear tickets, charters).*

---

## Addendum — PR #8 review ratifications (2026-07-03)

PR #8 (`triage-001-doc-fix`, squash-merged to main as `c935c68`) executed the batch. Four execution judgment calls ratified at review: (1) ADR-001 **minor bump stands** (changed normative check phrasing; the corpus has no patch-release species); (2) T-19 fencing clause **homed at ADR-001 §6** — point of definition; DDR-002 §2.4 carries the complementary enterprise-gate gloss; (3) T-28 reconciliation — the two `promotion_type: retraction` references moved onto `proposal_kind: retraction`; `promotion_type` restored to the pure subject/kind axis (no locked value-set churned; the declined rename stays declined); (4) `proposal_kind` field-add placed at **§5** (`CandidatePromotion`'s defining home — the spec's "§2.3" was a section-cite slip, as was T-04's "§5.3" for ADR-002's §5.2); the → KG-entry-governance routing-map entry and the ADR-002 spike-findings→Capability-Bar re-point stand as cross-reference-integrity edits under the same ratification.

**Correction logged (capture-fidelity pattern, fourth instance):** T-28's premise "direction discoverable only by edge traversal" was inaccurate at HEAD — direction was already property-encoded as a `promotion_type: retraction` overload (§5, §7 #21). The ruled remedy stands and is strengthened by the reconciliation: the overload retired rather than left as a competing direction encoding.

**RBT-48 rider:** the `schema_constants.py` refresh includes `proposal_kind {promotion, retraction}` and carries **no** `promotion_type: retraction` constant.
