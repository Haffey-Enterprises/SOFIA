# Session Handoff — DDR-003 Corrective Cycle → Phase-1 Upstream Amendments

| Field | Value |
|---|---|
| **Date** | 2026-06-23 |
| **From** | DDR-003 (RBT-14) corrective-cycle disposition sweep |
| **To** | Phase-1 upstream amendment session (RBT-45 → RBT-46) |
| **Disposition source of record** | RBT-14 plan-of-record comment (Linear, 2026-06-23) — *this handoff orients you to it; it is authoritative, not this file* |
| **Repo** | `$SOFIA_REBOOT_ROOT` · develop @ `73cb956` |
| **Role discipline** | DIRECTIVE-026 — claude.ai authors/reviews/captures; Code does git only (pause-point); Tad holds all merge gates |

---

## 0. Read-me-first (the one thing that matters)

This handoff exists because the DDR-003 review cycle surfaced findings that **reach upstream into landed schema and architecture**. DDR-003 cannot be finished or re-reviewed until that upstream work lands, or its citations dangle. So two amendment legs are **injected ahead of completing RBT-14**:

- **RBT-45** — DDR-001 v1.2.0 (architecture: feedback-loop write-authority)
- **RBT-46** — DDR-002 v1.2.0 (schema: five review-driven amendments)

**This session executes Phase 1: land RBT-45 then RBT-46.** It does **not** touch DDR-003 authoring (that's Phase 2, after these land) and does **not** open RBT-33 (that's downstream — see §2).

Do **not** trust this document as authority. Run the session-open ceremony (§6), fresh-fetch the canonical sources (§7), and reason from the landed corpus — not from this summary. Per ENG-STD-003 §13.5.9, prior-art-as-authority is prohibited.

---

## 1. How we got here (context, one read)

DDR-003 (Feedback Loop Governance) was authored by Code as a 221-line draft, paused pre-commit on `feature/rbt-14-d3-author-ddr-003-feedback-loop-governance` (off develop @ `73cb956`). It then went through two reviews:

- **Three-hat Pass-1** — PASS WITH FINDINGS (1 BLOCKING-recommended / 3 MATERIAL / 2 COSMETIC, 11 POSITIVE).
- **Antagonistic review** — FAIL (2 BLOCKING / 12 MATERIAL / 4 COSMETIC).

Both reviews were **fully dispositioned** across a one-fork-at-a-time deliberation sweep (every finding ratified by Tad). The dispositions split by *where each lands*: some reach **upstream** (DDR-001 / DDR-002 amendments — Phase 1), most are **DDR-003-internal** folds (Phase 2), a few are **mechanical hygiene** (Phase 2). This handoff carries the **upstream (Phase-1)** work in execution detail, and the rest as the map you need to understand *why* the upstream injection is load-bearing.

---

## 2. The injection — why RBT-45/RBT-46 go AHEAD of RBT-14, and where RBT-33 sits

**The R8 rule (consumer-reads-landed-schema):** DDR-003, once corrected, will cite: the new §7 #22 invariant, the widened `ProvenanceSummary`, the `PromotionDecision` diagnosis-verdict structure, the `CandidatePromotion` home-pending flag, and the DDR-001 feedback-loop writer. **All of those must be landed schema/architecture before DDR-003 is re-authored and re-reviewed**, or the corrected draft trips on dangling citations and the three-hat re-review fails on referential conflict. This is the identical reason RBT-43 (DDR-002 v1.1.0) preceded DDR-003 the first time.

So the dependency chain is:

```
RBT-45 (DDR-001 v1.2.0)  ──lands first──►  RBT-46 (DDR-002 v1.2.0)  ──lands second──►  RBT-14 (DDR-003 finish + accept)
   [architecture]                              [schema]                                    [Phase 2 + 3]
```

**Two relationships a cold reader must not conflate:**

- **Injected-ahead (Phase 1, this session):** RBT-45, RBT-46. New work, must land before RBT-14 resumes.
- **Consumed-downstream (NOT this session):** **RBT-33** (conformance mechanization). RBT-46 adds §7 **#22** (safety-critical tier). That **extends RBT-33's conformance set** — exactly as #20/#21 did via RBT-43. **No Phase-1 action on RBT-33**; it is held In Progress (Increment 2 open) and absorbs #22 when it next runs. The handoff names this only so you don't mistake "#22 → RBT-33" for a Phase-1 task. It isn't.

**Order within Phase 1:** RBT-45 → RBT-46. This is the R8 architecture-before-schema layering convention, but it is a **soft** dependency — the DDR-002 touches don't strictly cite the DDR-001 writer, so the order is cleanliness, not a hard gate. Co-process both in **one Code session as two sequential PRs** (the original PR-A shape).

---

## 3. WHAT ROUTED WHERE — the full disposition map

Every finding from both reviews, by destination. **Phase-1 items are RBT-45 / RBT-46.** The rest is shown so the upstream scope is anchored in the whole.

### → RBT-45 — DDR-001 v1.2.0 (Phase 1, lands first) — 1 touch

| # | Touch | Finding |
|---|---|---|
| 1 | DDR-001 Feedback-Loop Architecture assigns **write authority for the three feedback-loop writes** — the `CandidatePromotion` proposal (feedback job, pre-approval), the `ProvenanceSummary` snapshot (gateway, at-promotion), the materialized KG node (gateway, on EA approval) — as named, gateway-routed components, reconciled against **ADR-002 §2.6's "component-scoped, not diffuse"** principle (§2.6 names only ASA→`ReasoningProgress` and AOE→`ReasoningSession`; the feedback-loop writer is a third authorized class). Closes the mandatory **ADR-002 §6 check-#5** gap. Write-**authority** only; `CandidatePromotion`'s graph-**home** stays deferred to RBT-44. | antagonistic **B-1** |

### → RBT-46 — DDR-002 v1.2.0 (Phase 1, lands second) — 5 touches

| # | Touch | Finding |
|---|---|---|
| 1 | **§1** — label-taxonomy codification (base-class = contract-bearing, e.g. `:Decision:` vs namespace = region marker, e.g. `:Reasoning:` / `:Artifact:`) **+** `CandidatePromotion` **home-pending flag** (provisional label, pending RBT-44) | **B-1** |
| 2 | **§7 #22** — retracted-node read-exclusion invariant, **safety-critical tier**, parallel to #9/#19; CI-only set **21 → 22**; mechanization → RBT-33 | antagonistic **B-2** |
| 3 | **§2.3** — wording crispness: "entry into the KG" → "entry into **authoritative** KG knowledge (Catalog/Standards)" (Operational staging tier receives non-EA-gated derived writes; the R30 seam stays as landed) | antagonistic **M-2** |
| 4 | **§4/§5** — `ProvenanceSummary` frozen-content **widened to the `PROPOSED_FROM`-source basis** (esp. the `RejectedAlternative` override-chain), not just the `Evidence` layer; exact structuring → RBT-15 named gap | antagonistic **M-5** |
| 5 | **`PromotionDecision`** — **per-dimension diagnosis-verdict structure** (queryable; weights stay EA judgment, R29-safe); **Neo4j home** per M-4's accountable-bundle; per-dimension value-set T2-contested pending first real use | antagonistic **M-11** |

### → DDR-003-internal (Phase 2 — the corrected re-author, NOT this session)

M-2 seam statement · M-3 retention ≥ lookback binding invariant · M-4 audit-first (Neo4j-atomic) + PostgreSQL operational-secondary demotion · M-6 target-keyed signal de-dup · M-7 de-dup-against-rejected + two lift-paths (EA-initiated + auto-re-open on material change, threshold deferred) · M-8 §2.4-"workflow" config placement (owner = detection-promotion mechanism, **not** RBT-22) · M-9 tiered exposure-window subsection (R27 pattern — 8 DDR-003-native exposures, 4 safety-relevant / 4 follow, + 2 DDR-002 §7 cross-refs) · M-10 config-change-log integrity requirement · 3H-M2 (folded into M-9) · 3H-M3 determinism-locus one-liner (ruled M).

### → Bucket-3 hygiene (Phase 2 — mechanical, fold at authoring)

Section numbering (resolves the dangling §-refs; 3H-B1 / Ant-M12) · drop #4 from the DDR-002 §7 citation list (3H-M1 / Ant-M13) · normalize ref style (C-1) · rewrite Pre-Acceptance to ACCEPTED-form (C-2, Path A).

### Contingent / Deferred

- **Contingent:** a **one-line ADR-002 §2.4** acknowledgment — *only if* a three-hat reviewer balks on M-8's "workflow"-class placement of calibration config. Not planned; held as a fallback that would add an ADR-level touch.
- **Deferred (non-blocking):** **RBT-44** — the third-graph hypothesis ("is KG-mutation-rationale a peer graph to the KG/RG"). `CandidatePromotion`'s graph-home is parked there; DDR-003 is authored **graph-home-agnostic**. Do not pull this into Phase 1.

---

## 4. Phase-1 execution detail (per leg)

Both legs follow the **RBT-43 apply-prompt pattern**: claude.ai authors a **complete-replacement staging file** + an **apply-prompt**, against **fresh-fetched landed authorities** (DIRECTIVE-026.5 — do not reconstruct from memory); Code executes the apply-prompt in **pause-point mode**; Tad holds the merge gate. Two-commit shape (the v1.2.0 doc + its three-hat review of record vendored under `docs/reviews/`). No `Co-Authored-By` trailer. Squash-merge to develop.

**RBT-45 (DDR-001 v1.2.0) — pre-author fresh-fetch:**
- ADR-002 **§2.6** (write-authority) + **§6 check #5** — verbatim, to pin the exact closed-writer language and confirm the third-class framing.
- DDR-001 **Feedback-Loop Architecture** section (the scheduled-job / detect → propose → gate → materialize path) — for the exact insertion point and to confirm it doesn't already half-say this.
- Verify develop tip before branching.

**RBT-46 (DDR-002 v1.2.0) — pre-author fresh-fetch:**
- Landed **DDR-002 v1.1.0 §1 / §2.3 / §2.4 / §4 / §5 / §7** (now current in project knowledge after the 2026-06-23 refresh).
- **R30 / R31** from the Notion ledger — for the §2.3 seam citation and the retraction remedy-boundary citation.
- Confirm the §7 invariant count is **21** before adding **#22** (set 21 → 22).
- After RBT-45 merges, re-verify develop tip so RBT-46 stages against the post-RBT-45 baseline.

**Versioning:** both are **additive MINOR** amendments (1.1.0 → 1.2.0 / 1.1.0 → 1.2.0). DDR-002 v1.1.0 → v1.2.0; DDR-001 v1.1.0 → v1.2.0. First `# Revised:` line already exists on both (R18 satisfied at prior amendments); add the new dated revision line.

**Post-merge captures (claude.ai-side, after each leg lands):** three-layer ticket capture (RBT-45 / RBT-46 → Done) + Notion build-leg log entries. No new R-rulings (these realize already-ratified dispositions — build-leg landings, the RBT-43 precedent). Verify-after-write on every Linear/Notion write.

---

## 5. Parked DDR-003 state (do not build on it)

The DDR-003 draft (221 lines) is **uncommitted** on `feature/rbt-14-d3-author-ddr-003-feedback-loop-governance` (off develop @ `73cb956`), Code paused pre-commit. It is **reference substrate, superseded** — Phase 2 re-authors DDR-003 **fresh** against the landed v1.2.0s (it is not an edit of this draft). It goes stale the moment the v1.2.0s advance develop past `73cb956`.

**Phase-1 implication:** Phase 1 runs on **develop** (new branches for RBT-45/RBT-46), which needs a **clean working tree**. So the fresh session **sets the parked draft aside** (stash or simply don't carry it) and starts clean on develop. Nothing depends on preserving it in-repo — this handoff carries its state.

---

## 6. Session-open ceremony (run this before any work)

1. Deep read of the full governance corpus in project knowledge: CLAUDE.md, session directives, ADR-001, ADR-002, DDR-001 v1.1.0, DDR-002 v1.1.0, DMS, ENG-STD-001/002/003, templates (ddr / review / apply-prompt).
2. Fresh-fetch the mutable authorities:
   - **Linear** — RBT-45, RBT-46 (full descriptions; `includeRelations: true`), and the **RBT-14 plan-of-record comment** (the disposition source of record).
   - **Notion** — Reboot Decision Ledger (page `374caeea-1325-818d-8f9f-f5f56898b133`); confirm R29/R30/R31 and the build-leg log tail.
   - **Filesystem** — landed DDR-001 v1.1.0 + DDR-002 v1.1.0 on develop (confirm tip = `73cb956` or later if anything landed since).
3. Confirm clean develop working tree (set aside the parked DDR-003 draft).

---

## 7. Canonical pointers

- **RBT-14 plan-of-record comment** (Linear, 2026-06-23) — *the* disposition source of record. Every routing in §3 traces to it.
- **RBT-45** — DDR-001 v1.2.0 ticket (scope + pre-author fresh-fetch).
- **RBT-46** — DDR-002 v1.2.0 ticket (5-touch scope + pre-author fresh-fetch).
- **RBT-44** — third-graph hypothesis (deferred, non-blocking; the `CandidatePromotion` graph-home park).
- **RBT-33** — conformance mechanization (downstream consumer of #22; not Phase-1).
- **Reviews** — the three-hat Pass-1 review + the antagonistic review (the two source documents the disposition sweep ran against). Provide them to the fresh session if it needs to re-read a finding verbatim.
- **Landed corpus** (project knowledge, current as of 2026-06-23): ADR-001 v1.0.0, ADR-002 v1.0.0, DDR-001 v1.1.0, DDR-002 v1.1.0.

---

## 8. Learnings to carry (incorporated this session; apply going forward)

**A. "The loop hasn't run" ≠ no empirical warrant.** Several findings had a zero-in-system-instance flavor that initially read as "defer / name-as-gap." The correction: when a frequency is **knowable from the domain** (independent of SOFIA running), that *is* the warrant. M-11 (catalog promotions happen frequently — confirmed from real-world practice), M-6 (weakness-driven overrides are a common pattern), and M-7 (rejected-then-later-warranted is a normal catalog-lifecycle event) were all **ruled now** on external warrant rather than deferred. **Going forward:** before defaulting toward name-as-gap on a "hasn't run yet" item, check for external/domain-knowable warrant. (M-7's auto-re-open *threshold value* still defers as calibration — the mechanism is ruled, the value isn't.)

**B. The durable-frozen-record thesis (future ledger-elevation candidate, NOT yet elevated).** A through-line under M-5, M-3, M-10, and M-11: *decisions are made against a moving world, so the record must durably freeze the world-state and the basis as they were at decision time.* M-5 (snapshot the `PROPOSED_FROM` basis), M-3 (keep the signal alive to be counted), M-10 (the audit record must be tamper-evident, not append-only-by-convention), M-11 (capture the per-dimension diagnosis basis queryably) are the same principle wearing four hats — and it *is* ADR-001's auditability moat. It reads like a cross-cutting R-series ruling, but it is **unratified and the loop hasn't run**, so it was deliberately **not** elevated. Flagged here as a candidate to elevate after DDR-003 lands, with Tad's ratification.

---

*End of handoff. Phase 1 = RBT-45 → RBT-46, one Code session, sequential PRs, then back to RBT-14 for Phase 2.*
