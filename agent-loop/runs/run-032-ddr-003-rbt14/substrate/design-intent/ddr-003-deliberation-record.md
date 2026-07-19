# RBT-14 — DDR-003 Pre-Authoring Deliberation Record (Phase-2 re-author)

| Field | Value |
|---|---|
| **Session** | RBT-14 authoring leg, 2026-07-19 (claude.ai authoring surface) |
| **Artifact** | DDR-003 — Feedback Loop Governance (`docs/ddr/DDR-003-feedback-loop-governance.md`) |
| **Status** | Deliberation COMPLETE — Item 0 + doctype + 6 forks + 7 obligations + 3 RBT-46 touches + corrective-internals tranche + diagnosis-charter recovery, all ratified per item by Tad. DDR-003 drafted PROPOSED v0.1.0, three-hat solo self-review complete (§5.4 posture ruled (a)). Next: run-032. |
| **Substrate (fresh-fetched at develop `379457d`, not recalled)** | ADR-008 v1.0.0 (full) · ADR-001 §2.2/§2.5 · ADR-002 §2.6 · DDR-001 v1.5.0 (Decision block, Feedback-Loop Architecture) · DDR-002 v1.6.0 (§2.3/§2.4/§5/§6/§7 #9 #15 #19 #20 #21 #22 #25, Named Gaps, Change Log) · DDR-004 v1.4.0 §6 · SDD-001 v1.5.0 §3.5/§3.6/§9 · triage-001 record (Appendix A/C/D) · RBT-59 deliberation record · run-025/026 operator Rulings A–G · RBT-14/43/45/46/54/59/71 tickets + comments · run-031 audit · run-supervision.protocol.md (§2 spend insert live) · Reboot Decision Ledger R29–R31 (Notion, verbatim) · prior-SOFIA DDR-038 (intent source only) · `~/Downloads/ddr-003-substrate-handover.md` (2026-06-22 20:27, ratified-substrate carrier) · `~/Downloads/PARKED-DDR-003-…-superseded-draft.md` (2026-06-22 22:52, superseded reference) |

**Criterion-shift discipline applied throughout:** the seven-fork substrate (2026-06-22) and corrective-cycle dispositions (2026-06-23) predate ADR-008 and five DDR-002 versions; every item below was re-validated against landed canon in the applied-learning frame, not recycled or discarded.

---

## Item 0 — Canon re-anchor (RATIFIED)

The kickoff's author-against-v1.1.0 anchor is stale. PR-A (RBT-43) landed 2026-06-22; canon has advanced to DDR-002 v1.6.0 / DDR-001 v1.5.0 / DDR-004 v1.4.0 / SDD-001 v1.5.0 / ADR-008 ACCEPTED v1.0.0. Ruling: author against today's landed canon; landing is a **single-PR leg** (PR-B alone). New schema touches, if any, get their own dispositions — none were opened (all deferred; see below).

## Item 1 — Doctype & number (RATIFIED)

**DDR-003, `feedback-loop-governance`**, PROPOSED v0.1.0. ADR test fails (principle layer lives in ADR-008 — re-litigating the altitude boundary prohibited); SDD test fails (constrains multiple services + platform governance posture). Number 003 free in `docs/ddr/` and the corpus's standing subject-name referent. n=0 floor: form fixed, constants held contested.

**Citation convention (ratified):** DDR-002 §7 checks cited subject-first with the number as fetch-verified anchor ("the conditional-scope carry-forward invariant (DDR-002 §7 #22)"), never a naked "#NN". Ticket IDs never in body prose.

## Item 2 — Fork re-validation (six forks, each RATIFIED)

- **Fork B (EA gate) — stands, re-grounded.** Authority chain re-run through ADR-008 §2.1/§2.2 (ADR-001 §2.5 cited as sub-case). Schema-facing commitments converted to pointers (no-leak = #9; decline-terminal = §5 append-only; batch mechanics = §2.4 + #15). DDR-003 keeps the policy layer: diagnosis charter (five dimensions, weights deferred), batch-eligibility, decline semantics. R29 empirical-warrant cut holds.
- **Fork A (signals/detection) — legs 1–2 stand; leg 3 superseded-in-premise, re-stated.** Taxonomy re-anchored to landed `PROPOSED_FROM` grammar; single EA-owned parameter mechanism adopts DDR-004 §6 two-tier governance by pointer. "Non-EA-gated staging tier" dead (T-02 + ADR-008 §2.2 + Ruling A); the derive/promote seam survives as a **two-distinct-controls seam**: derive = distillation-class review (distinctness-bounded, evidence-visible, via forthcoming candidate shape); promote = per-write EA gate. Reviewer identity question routed to Obligation 2.
- **Fork D (retention) — stands, re-grounded on ADR-008 §2.4.** Preservation-trigger leg superseded-in-mechanism by landed at-promotion materialization (#20); re-stated as the retention-class model + decision-consumed-Evidence extension (Obligation 4). Archival: schema landed, policy DDR-003's; distillation-class review governs resolve/supersede/re-activate transitions. Cost leg unchanged (volume → RBT-25).
- **Fork E (audit/provenance-survival) — stands.** Leg 2 (at-promotion ProvenanceSummary) wholly landed → pointers; DDR-003's residual = retention windows that unblock the routed retrieval-affordance gap. Leg 1 (two-record audit model, audit-first) re-grounded on ADR-008 §3/§2.4; concrete form confirmed at M-4.
- **Fork F (conditional promotions) — stands.** Carry-forward → pointers at #22 + SDD-001 gate; DDR-003 owns the **EA re-scope deliberation obligation** (the workflow residual SDD-001 routes here). Scope-setting accountability re-grounded on ADR-008 §2.5. Multi-condition interim posture ("surface-to-EA, never silent auto-composition") authored here — DDR-002's Named Gaps entry already awaits it; schema half stays deferred.
- **Fork G (retraction) — stands.** Remedy boundary confirmed as DDR-003's centerpiece under ADR-008 §2.6 routing (criteria at Obligation 1); reversing-act + durable-rationale legs → pointers at #21/#25/SDD-001 §3.5.4. New inbound scope admitted: executed-retraction re-decision (Obligation 7).

## Obligations 1–7 (each RATIFIED)

1. **Remedy boundary:** replaceability-first operative test; retraction conjunctive (should-never-have-been-promoted AND no correct replacement); defect-at-promotion vs world-moved recorded as diagnostic axis (informs, never decides); EA per-write diagnoser; durable determination (remedy, replaceability finding, axis classification, for retraction why-no-replacement) on the existing audit shape. n=0 wrong promotions; test qualitative, form-fixed.
2. **Distillation-reviewer role:** distinct **role** from the promotion-gate EA role (two controls, two failure modes); interim **assignment**: EA holds both; holder-set RBAC-determined (assignment act via governance-state-manager routing, no DDR-003 amendment to separate). Per-distinct-lesson accountability; evidence-visibility as validity precondition; negative space: not a per-observation gate, not the promotion gate. Honesty boundary stated in-record: ADR-008 §2.2 fixes this control as *human* review — agent-holdership is an ADR-008 amendment question, not a DDR-003 config act. (Tad's RBAC-range remark was illustrative — no decision change.)
3. **Revalidation:** trigger = `active` pattern with `last_observed_at` beyond an EA-owned **staleness horizon** (new parameter in the unified config mechanism; single default + per-`pattern_type` override affordance; values deferred). **Surface-never-transition invariant**; disposition space = re-affirm (recorded outcome, horizon resets) / resolve / supersede / archive, each a reviewed act. Sweep rides the loop's scheduled cadence. Mechanics → detection-promotion SDD.
4. **Retention classes:** four classes — (1) durable governance ledger (never expires), (2) decision-consumed Evidence, (3) working reasoning tier (bounded, values deferred), (4) Operational archival posture (pointer). Decision-consumed defined by traversal: `SUPPORTED_BY` closure of a session's reasoning trail that `PRODUCED` a Solution reaching selection-constituting `approved`. **Interim: retention-exemption** for class 2 until the DDR-002 survival-mechanism extension lands (deferred by name). **Binding invariant (consumes M-3): retention ≥ lookback**, config-validation enforced.
5. **Candidate-`ObservedPattern`:** DDR-003 authors four candidate-stage requirements (structural exclusion until reviewer approval — #9 species; terminal-and-explainable rejection; evidence carriage; distillation-class approval act) + interim posture (**no conforming distillation write path exists** until shape + review surface land; binds at ADR-008 §6 design review). Node-vs-status realization NOT ruled (schema-layer). **Schema amendment deferred** to the detection-promotion SDD leg (first real consumer), subject-named both directions.
6. **Cross-class SCOPE_CONFLICT richer disposition:** EA resolves (scope-setter resolves); four buckets — re-scope (via #22 machinery) / remedy the promoted fact (Obligation-1 boundary) / **uphold with recorded rationale** / hold-for-investigation (non-terminal, named owner). Standing conflicts surface each loop cadence until ruled; no auto-timeout/auto-precedence. Detection stays structural-only (deliberate non-expansion; coverage boundary stated honestly).
7. **Executed-retraction analogue:** **re-admission is always a forward EA-gated act, never a verdict-flip side-effect** — read-exclusion stays keyed on the executed `RETRACTS` edge; un-retraction executes as **re-promotion** (fresh candidate, full gate, §6 supersession path — falls out of the replaceability-first test). Detection check (#15's species for executed retractions) → deferred DDR-002 amendment, non-load-bearing given the forward-act rule. n=0 retractions.

## RBT-46 survivors (each RATIFIED)

- **Touch 1 (label taxonomy + home-pending flag): defer, re-routed to RBT-44** (recorded there by comment, 2026-07-19; RBT-46 remains touch ledger). Not a DDR-003 dependency — authored graph-home-agnostic per standing ruling.
- **Touch 4 (ProvenanceSummary widening): superseded-by-better-remedy** — the **promotion-consumed-substrate retention exemption**: every `PROPOSED_FROM` target of a durable terminal-`promoted` candidate is retention-exempt. Closes M-5 with zero DDR-002 amendment; landed Evidence-scoped span and structuring stand.
- **Touch 5 (per-dimension diagnosis capture): split** — governance requirement into DDR-003 (per-dimension verdict on each of five charter dimensions, per candidate, durable; interim carrier = decision rationale); structured queryable capture deferred to additive DDR-002 amendment at first real use (EA-review surface build leg).

## Corrective-cycle internals (tranche RATIFIED)

Consumed: M-2 (→ Fork A seam), M-3 (→ Obligation 4), M-5 (→ touch 4). Stand unchanged: **M-4** (graph-native atomic audit-first; PostgreSQL operational-secondary) · **M-6** (target-keyed de-dup; one live candidate per (target, kind)) · **M-7** (de-dup-against-rejected + EA-initiated / material-change lift paths, threshold deferred) · **M-8** (config homes on detection-promotion mechanism; ADR-002 §2.4 one-liner stays contingent, unused) · **M-10** (config-change-log: actor/timestamp/old→new/rationale) · **3H-M3** (determinism locus: detection deterministic, diagnosis human). **M-9 rebuilt-as-pattern:** tiered conformance section with honest enforcement loci, enumeration rebuilt from tonight's ratified set.

## Diagnosis-charter recovery (RATIFIED)

The five diagnosis dimensions were absent from every durable carrier (RBT-14 comments, adjacent tickets, Notion ledger R29–R31, SOFIA + SOFIA-Reboot full history/branches/stash/handoffs, DDR-038 — which carries no dimension charter at all). **Recovered verbatim from `~/Downloads`:** `ddr-003-substrate-handover.md` §3.2 (2026-06-22 20:27 UTC, the ratified-substrate carrier) and the parked draft's Diagnosis policy section (2026-06-22 22:52 UTC). **The ratified five:** recurrence strength · evidence quality / source authority · genuine-pattern-vs-data-defect · target deprecation/staleness state · conditional-vs-unconditional applicability (drives `approved_conditional`). Weights/decision rules explicitly not ruled. Re-validated against current canon — all five stand; a fresh-proposed substitute set was withdrawn on recovery. **Capture lesson (harvest candidate):** ratified content living only in a chat session + uncommitted draft is one branch-switch from gone; the Downloads staging copies were the sole survivors. Follow-up task standing: end-of-session `~/Downloads` sweep for other uncommitted-but-should-be-durable artifacts.

## Self-review addendum (Leg 3, 2026-07-19)

Three-hat solo self-review of the v0.1.0 draft: LAA 1 MATERIAL (the §5.4 archival-demotion posture surfaced as decision-bearing — **ruled (a) by Tad:** archival of an already-terminal lesson after dwell is a policy-scheduled retention demotion; the reviewed judgments are resolve/supersede/re-activate; re-activation keeps demotion reversible); SA 1 MATERIAL fixed in-session ("class-4" session shorthand → "distillation-class review" anchored to ADR-008 §2.2 — the numbering resolves nowhere in ADR-008's body) + 2 COSMETIC fixed (RG/KG first-use expansion; class-2 closure wording tightened to session-produced trail); EA 0 findings. Full citation sweep verified against staged live text; no misses.

## Schema-touch consolidation (outcome of Item 0's reserved call)

**Zero DDR-002 amendments opened this cycle.** Four deferred-by-name: candidate-`ObservedPattern` shape (→ detection-promotion SDD leg) · executed-retraction detection check (→ first real instance) · structured diagnosis capture (→ EA-review surface leg) · decision-consumed survival mechanism (→ made non-load-bearing by retention exemption). Multi-condition schema stays the existing Named Gap. PR-B lands single-record.

## Standing to-dos

1. Three-layer capture on RBT-14 at landing; DDR-002/SDD-001/ADR-001 "forthcoming feedback-loop governance design" subject-name pointers resolve to concrete DDR-003 at landing (its DoD; anchor-capture pattern).
2. Durable placement of this record: this file (`agent-loop/deliberation/ddr-003-feedback-loop-governance/record.md`), landed in the run-032 pre-registration commit. The two recovered Downloads carriers are candidates for vendoring (Tad's call at landing).
3. Run-032: prompt at `agent-loop/design/rbt-14-run-032-prompt.md`; fresh hash-pinned substrate recipe; §2 spend gates walked in the pre-registration; author sandbox-apply dry mode; gen-12; `max_passes` 4.
4. End-of-session `~/Downloads` durability sweep (task standing).

*Next: run-032 (Code executes; report-and-STOP) → cold audit + coalesced docket on the authoring surface → converge → land (PR-B).*
