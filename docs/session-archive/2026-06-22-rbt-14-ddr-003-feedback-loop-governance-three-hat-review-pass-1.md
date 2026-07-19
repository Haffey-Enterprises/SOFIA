# File: docs/reviews/2026-06-22-rbt-14-ddr-003-feedback-loop-governance-three-hat-review-pass-1.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-22
# Description: Three-hat (LAA/SA/EA) review of DDR-003 Feedback Loop Governance (v0.1.0, PROPOSED), Pass 1 — content conformance to ADR-001/ADR-002, DDR-001 v1.1.0, the landed DDR-002 v1.1.0 schema, and ledger R22/R24/R25/R26/R27/R29/R30/R31. Pass-1 findings for ratification; not yet the converged review of record.

# Three-Hat Review (Pass 1) — DDR-003 Feedback Loop Governance

| Field | Value |
|---|---|
| **Review Date** | 2026-06-22 |
| **Reviewer** | Claude (claude.ai) — three-hat (LAA / SA / EA) simulation under DIRECTIVE-007 §7 / §7.5; per-finding dispositions pending Tad's ratification |
| **Scope** | DDR-003 v0.1.0 (PROPOSED) content conformance to its upstream ADRs/DDRs and the governing ledger rulings |
| **Authority** | DIRECTIVE-007 (multi-role review); RBT-14 acceptance gate ("three-hat → ACCEPTED"); DIRECTIVE-032 review-until-zero-findings cadence |
| **Outcome** | **PASS WITH FINDINGS** — gate **NOT** satisfied at Pass 1 (1 BLOCKING open). Path: fix B-1/M-1/M-2 (M-3 optional) → Pass-2 propagation re-verify → convergence → ACCEPTED. |

---

## §0 Context (Pass-1 preamble)

This is Pass 1 of the DIRECTIVE-007 three-hat review that gates DDR-003's promotion from PROPOSED (0.1.0) to ACCEPTED (1.0.0). It is **not** the converged review of record — that is authored at zero-findings convergence (the DDR-001 / DDR-002 pattern).

The draft was reviewed against fresh-fetched canonical authorities: ADR-001 v1.0.0 (§2.4 operational-feedback substrate, §2.5 EA-gated consolidation, §6 compliance checks), ADR-002 v1.0.0 (§2.4 store-authority, R9), DDR-001 v1.1.0 (feedback-loop architecture / data-path, check #4, RG-retention posture), and — critically — the **landed DDR-002 v1.1.0** (RBT-43, on `develop` @ `1764fd9`), not the stale v1.0.0 in project knowledge. Ledger rulings R22 / R24 / R25 / R26 / R27 / R29 / R30 / R31 were fetched from the Reboot Decision Ledger. DMS §2.2 / §2.3.1 and the DDR template governed the doc-shape checks.

**Overall assessment:** the draft is substantively strong and schema-accurate against the landed v1.1.0. It correctly avoided the one precise trap (edge-only retraction, no `applicability_state: retracted`). The findings below are one navigability defect (B-1) plus localized cross-reference / enforcement-attribution corrections — all mechanically fixable, none reaching into the soundness of the governance ruling itself.

---

## §1 Scope

### 1.1 In-scope

- `docs/ddr/DDR-003-feedback-loop-governance.md` (v0.1.0, PROPOSED) — full content review.
- Conformance to upstream: ADR-001 v1.0.0, ADR-002 v1.0.0, DDR-001 v1.1.0, DDR-002 v1.1.0.
- Conformance to governing rulings: R22 (architecture/governance split), R24 (durable-not-transient), R25 (reversibility-scoped completeness), R26 (Operational durable distillation + archival), R27 (CI-only enforcement posture), R29 (parameter-mechanism-now / values-deferred), R30 (derive/promote authority seam), R31 (supersession-vs-retraction boundary).
- Doc-shape: DMS §2.2 header, §2.3.1 ADR/DDR/SDD metadata, DDR-template structure, R18 single-artifact lifecycle.
- ADR-001 §6 design-time compliance checks (the standing every-DDR gate).

### 1.2 Out of scope (deliberately)

- The schema contract itself (DDR-002 v1.1.0 — ACCEPTED, landed; cited not re-reviewed).
- The feedback-loop data-path architecture (DDR-001 v1.1.0 — ACCEPTED).
- Service realization (the SDD hand-offs — RBT-15/16/17/22/25; reviewed only for *correct routing*, not designed).
- Runtime / CI enforcement mechanics (RBT-33).

---

## §2 Findings

### 2.1 BLOCKING — must resolve before the ACCEPTED gate

#### Finding B-1: Pervasive dangling internal §-number cross-references

**Location:** `§Decision` (all of Decision.1–Decision.6) and inline throughout the body.

**Description:** The document body is organized by **named** headers (`## The EA Gate (the spine)`, `## Signals & Detection`, `## Retention, Audit, Provenance-Survival`, `## Conditional Governance & Retraction`, …) with **no section numbers**. But the Decision's testable components and many inline references cite numbered sections that do not exist:

- Decision.1 → `§3`; Decision.2 → `§3.2`; Decision.3 → `§3.3`; Decision.4 → `§4`; Decision.5 → `§5`; Decision.6 → `§6`.
- Inline: `§3.2` (diagnosis), `§5.2` (audit, cited ~4×), `§5.3` (provenance-survival, cited ~4×), `§6.1` (conditional transition), `§6.2` (multi-condition).

Every one of these is a dangling pointer. This is the same defect class as DDR-002's M-A (a substrate→template restructure artifact — the numbering dropped when named headers were authored).

**Why blocking:** The Decision section is the document's testable-ruling spine, and *all six* of its component pointers dangle; the inline `§5.2` / `§5.3` / `§6.1` refs that carry the audit-first, provenance-survival, and conditional-transition cross-links also dangle. For a foundational DDR cited by twelve SDDs, an SDD author following "per §5.2" hits a dead end. Navigability of the normative ruling is broken throughout.

**Disposition (recommended):** Restore the section numbering the §-refs already presuppose. The numbers map **exactly** to the ordinal position of the `##` / `###` headers — §1 Decision, §2 Rationale, §3 EA Gate (§3.1 Authority, §3.2 Diagnosis, §3.3 Action-routing, §3.4 Batch, §3.5 Authorship), §4 Signals & Detection, §5 Retention/Audit/Provenance (§5.1 Retention-class, §5.2 Audit, §5.3 Provenance-survival), §6 Conditional & Retraction (§6.1 Conditional transition, §6.2 Multi-condition, §6.3 Retraction) — so adding the numbers makes every dangling ref resolve with **no content change**. Lower-touch and authorial-intent-preserving vs. converting all refs to named form.

**Severity note (pending Tad's calibration):** Rated BLOCKING here on pervasiveness (the entire §-numbering scheme is referenced but absent, including the Decision spine). The DDR-002 precedent rated its *narrower* version (refs to one removed section) MATERIAL, fixed in-leg. If calibrated to strong-MATERIAL, the disposition is identical: fix before ACCEPTED.

### 2.2 MATERIAL — in-scope fix

#### Finding M-1: Cross-References mis-lists a DDR-002 §7 invariant

**Location:** `§Cross-References` → "← DDR-002 v1.1.0" boundary-routing entry.

**Description:** The list "`§7 invariants #4/#9/#15/#19/#20/#21`" includes **#4**, but DDR-002 §7 #4 is *one-active-version-per-business_key* — unrelated to the feedback loop. The proposal-visibility check the author means is **DDR-001 check #4** (correctly cited elsewhere in the body) and is **DDR-002 §7 #9** (already present in the list). The `#4` is a DDR-001-vs-DDR-002 numbering conflation.

**Why material (not blocking):** A reader chasing "DDR-002 §7 #4" lands on the wrong invariant; but the substance is correct elsewhere (the body reads "confirms DDR-001's proposal-visibility / check #4") and the References metadata line lists only #15/#20/#21 (correct). Localized to one list.

**Disposition:** Drop `#4` from the DDR-002 §7 list. (Proposal-visibility is `#9` there; DDR-001's check #4 is separately and correctly cited under the "← DDR-001 v1.1.0" entry.)

#### Finding M-2: The spine's "enforceable authority" claim rests on a check that does not enforce it

**Location:** `§The EA Gate (the spine)` → "Authority & accountability"; echoed in Decision.1.

**Description:** The draft states "DDR-002 check #15's role-authorization tightens onto this authority," presenting Enterprise-Architect promotion-approval as "the one concrete **enforceable** authority." But DDR-002 §7 #15 enforces the *existence of a governing approving `PromotionDecision`* — it is **role-agnostic** (any approver). The EA-role pin (the approver on the `(Actor)-[:APPROVED {role}]->(Decision)` edge being an EA) is a **new** governance constraint DDR-003 introduces; check #15 does not carry it. As written, the spine's enforceability is attributed to a check that doesn't check role.

**Why material:** This touches the spine — the single authority the gate "cannot function without." Claiming it is enforced by #15 papers over a genuine enforcement gap an antagonistic reviewer would press: *where is EA-role actually enforced?* Leaving it mis-attributed risks a Position-1-adjacent failure (an un-role-gated promotion path that reads as governed but isn't).

**Disposition:** Reframe. DDR-003 **rules** EA-promotion-approval as governance; its **enforcement** (the `role` on the `APPROVED` edge = EA) is routed to the gateway / RBT-15 + RBT-33, or named explicitly as an enforcement gap. Either soften "one concrete enforceable authority" → "ruled authority; enforcement routed," or name the enforcement route — so the spine's enforceability is not claimed via #15's existence check.

#### Finding M-3 (EA-hat; leaning COSMETIC): ADR-001 §6 deterministic/probabilistic locus not made legible

**Location:** `§Signals & Detection` (detection + distillation-generalization); cross-cuts the §6 standing check.

**Description:** DDR-003 satisfies ADR-001 §6 **substantively** — the Position-5 → Position-4 commitment is central (the loop *is* the §2.5 engine), there is no Position-1-leaning LLM-as-reasoner language, and the EA diagnosis is correctly framed as human-reasoned. What it does not do is state the deterministic/probabilistic **locus** of the detection step and the distillation-*generalization* step. ADR-001 §2.4 explicitly flags the operational-feedback substrate as carrying *provisional* probabilistic shapes, confirmed at detail design — so a DDR-level note closes that pointer.

**Why material (leaning cosmetic):** Substance passes; this is an audit-legibility improvement. The corpus pattern (DDR-001 / DDR-002) is to thread §6 rather than carry a checklist section, so this is a recommendation, not a required section.

**Disposition:** Add a one-liner — detection = deterministic graph traversal (recurrence/threshold); the generalization-algorithm's deterministic/probabilistic classification defers to the SDD per ADR-001 §2.4's provisional-feedback-substrate framing; the EA diagnosis is human-reasoned over SOFIA-prepared context. Tad to rule M or C.

### 2.3 COSMETIC — noted

- **C-1 — Mixed reference style.** Some internal refs are §-numbers (the B-1 set), others are informal named refs ("(§Retention)", "(§EA-gate)", "(§Signals)", "(§Cross-References)"). After B-1's numbering, normalize to one form for uniformity. *(Location: throughout.)*
- **C-2 — Pre-Acceptance phrasing (process, not a doc defect).** "this PR lands the draft at PROPOSED for that review" implies a land-at-PROPOSED-then-promote two-step; the DDR-001 / DDR-002 precedent is author → three-hat → land at ACCEPTED in one leg (single-artifact lifecycle, R18). This section is rewritten to "discharged" at acceptance regardless (as DDR-002's was). Worth confirming the sequencing intent. *(Location: §Pre-Acceptance Conditions.)*

### 2.4 No-drift confirmations (POSITIVE — required, DIRECTIVE-007 §7.2)

- **P-1 — Version pins, all correct and truthful.** ADR-001 v1.0.0, ADR-002 v1.0.0, DDR-001 v1.1.0, DDR-002 v1.1.0 — authored against the *landed* v1.1.0 (R8 consumer-reads-landed-schema; truthful citation).
- **P-2 — Retraction shape exact.** Modeled edge-only — `RETRACTS` + reversing `CandidatePromotion{promotion_type: retraction}`, EA-gated, durable rationale, retained + read-excluded, never hard-deleted — with **no** `applicability_state: retracted` marker. Matches DDR-002 v1.1.0 §5 / §7 #21 precisely (the RBT-43 M-2-fold trap, avoided).
- **P-3 — ProvenanceSummary exact.** `frozen_fact_summaries`, `frozen_source_version_pins`, `origin_mechanism: derived`, `MATERIALIZES_PROVENANCE_OF`→`CandidatePromotion`, materialize-at-promotion / §7 #20 — matches DDR-002 v1.1.0 §4.
- **P-4 — Archival.** `ObservedPattern.status: archived`, demotion-not-deletion, reversible — aligns to DDR-002 §2.3 (v1.1.0) + R26 A-5; the dwell-trigger/cadence correctly held as DDR-003 policy, deferred.
- **P-5 — R30 derive/promote seam.** Operational = non-EA-gated `derived` staging tier; promotion EA-gated; correctly identified as *why* the distillation write does not breach ADR-001's SOFIA-never-self-modifies invariant.
- **P-6 — R29 values-deferred.** Applied faithfully throughout (threshold / lookback / cadence / retention windows / dwell / batch guardrails all ruled-as-mechanism, valued-at-onboarding). The retention *relative-ordering*-ruled / *absolute-windows*-deferred treatment is a clean exemplar.
- **P-7 — R31 boundary.** Supersession (default, wrong-but-replaceable) vs. retraction (exception, never-should-have-been-promoted) matches the ledger and DDR-002 §2.4 / §5.
- **P-8 — Store assignments + R24.** PromotionDecision → Neo4j Governance; calibration config + operational audit trail → PostgreSQL — per ADR-002 §2.4 / R9. The R24 tension (durable governance audit vs. excluded transient disposition stream) is proactively addressed and correctly resolved.
- **P-9 — Signal-chain schema accuracy.** The override-recurrence chain (`ReasoningProgress{overridden_by_human}` → `REJECTED` → `RejectedAlternative{human_accepted}` → `WOULD_HAVE_USED`) traces real DDR-002 §4 / §5 edges. Signal taxonomy by `PROPOSED_FROM` + action path, with Operational track-record included and KG as ground-truth-checked-against, matches the ratified A-fork substrate.
- **P-10 — Proposal-visibility / never-self-modify.** Check #4 correctly attributed to DDR-001 (body); the loop-proposes / human-materializes contract honored; `CandidatePromotion` proposal-class exclusion correctly cited.
- **P-11 — Doc-shape + substrate gate.** DMS §2.3.1 metadata table, §2.2 header (no `# Revised` — correct per R18 initial authoring), single 0.1.0 Change Log row, PROPOSED status; DDR-template section structure; DIRECTIVE-034 deliberation-grounded substrate gate satisfied (RBT-14 ratified substrate). R8 one-way reference posture honored.

---

## §3 Forward-Pointer Triage

No out-of-scope forward-pointer candidates surfaced. All findings are in-scope fixes to DDR-003; no new tickets warranted (DIRECTIVE-025-clean). The SDD / RBT-33 hand-offs the draft already names (RBT-15 gateway enforcement + provenance reverse-lookup; RBT-16/17 detection/portal; RBT-22 Condition vocabulary; RBT-25 cost volume; RBT-27 consolidation health; RBT-33 #20/#21 mechanization) are correctly routed, not absorbed.

---

## §4 Audit Outcome

> **PASS WITH FINDINGS — gate NOT satisfied at Pass 1.** 1 BLOCKING (B-1, recommended; pending Tad's severity calibration) + 3 MATERIAL (M-1, M-2, M-3 [M-3 leaning C]) + 2 COSMETIC (C-1, C-2), against 11 POSITIVE no-drift confirmations. The governance ruling itself is sound and schema-accurate against the landed DDR-002 v1.1.0; the findings are navigability (B-1), cross-reference precision (M-1), enforcement-attribution (M-2), and audit-legibility (M-3) corrections.

**Gate status:** the three-hat acceptance gate is **open**. Recommended path: ratify dispositions per finding (B-1 first) → apply fixes (claude.ai authors the corrected DDR-003 + apply-prompt; Code vendors, DIRECTIVE-026) → Pass-2 propagation re-verify (DIRECTIVE-032 §32.4 — confirm prior fixes landed + zero new findings introduced) → convergence → promote 0.1.0 PROPOSED → 1.0.0 ACCEPTED, vendoring the converged review of record.

**Three-hat lens summary:**

- **LAA (daily-driver / buildability):** Policy/data-path/schema/SDD boundaries are clean and the SDD hand-offs are crisp. B-1 hurts the builder most (an SDD author can't resolve "per §5.2"). PASS pending B-1.
- **SA (migration / substrate consistency):** Schema citations align to landed v1.1.0 exactly; no migration (greenfield). Consistency findings are M-1 (cross-ref) and M-2 (check #15 over-attribution). PASS pending M-1/M-2.
- **EA (governance / pattern enforcement):** Position-5/4 commitment central, R29/R30/R31 faithfully applied, no Position-1 drift, never-self-modify honored via the R30 seam. EA findings: M-2 (enforceability of the spine authority) and M-3 (§6 locus legibility). PASS pending M-2/M-3.

---

## §5 Cross-References

- **Authority:** DIRECTIVE-007 (multi-role review), DIRECTIVE-032 (review-until-zero-findings cadence), RBT-14 acceptance gate.
- **Document under review:** `docs/ddr/DDR-003-feedback-loop-governance.md` v0.1.0 (PROPOSED).
- **Upstream checked against:** ADR-001 v1.0.0; ADR-002 v1.0.0; DDR-001 v1.1.0; DDR-002 v1.1.0 (landed `develop` @ `1764fd9`, RBT-43).
- **Ledger:** R22 / R24 / R25 / R26 / R27 / R29 / R30 / R31.
- **Standards:** DMS §2.2 / §2.3.1; DDR template; ADR-001 §6.
- **Next:** Pass-2 propagation re-verify after fixes land; converged review of record authored at zero-findings convergence.

---

*Pass-1 findings — not the converged review of record. Per-finding dispositions pending Tad's ratification.*
