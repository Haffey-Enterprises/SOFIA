# Session Handoff — RBT-46 Leg-2 Starter (DDR-002 v1.2.0)

| Field | Value |
|---|---|
| **Date** | 2026-06-23 |
| **From** | RBT-45 (DDR-001 v1.2.0) landed + captured — Phase-1 leg 1 close |
| **To** | RBT-46 (DDR-002 v1.2.0) authoring session — Phase-1 leg 2 |
| **Companion (authoritative for scope)** | `2026-06-23-session-handoff-ddr-003-corrective-to-phase-1-upstream.md` — the dual-leg handoff. **Its §3 "→ RBT-46" table and §4 "RBT-46 pre-author fresh-fetch" are the authoritative five-touch scope and fetch set; its §8 carries the learnings.** This starter only updates world-state and the session-open sequence; it does not restate or supersede that scope. |
| **Repo** | `$SOFIA_REBOOT_ROOT` · develop @ `6c76410a` |
| **Role discipline** | DIRECTIVE-026 — claude.ai authors/reviews/captures; Code does git only (pause-point); Tad holds all merge gates |

---

## 0. Read-me-first

Phase-1 **leg 1 (RBT-45, DDR-001 v1.2.0)** is **landed and fully captured**. This session executes **leg 2: RBT-46 (DDR-002 v1.2.0)** — the five DDR-003-review-driven schema touches — then Phase 1 is complete and the cycle returns to RBT-14 (DDR-003 re-author, Phase 2, a separate session).

Do **not** trust this document as authority. Run the session-open ceremony (§3), fresh-fetch the canonical sources, and reason from the landed corpus + the ticket + the RBT-14 plan-of-record — not from this summary or the companion handoff's prose. Prior-art-as-authority is prohibited (ENG-STD-003 §13.5.9). The companion handoff orients you to the five-touch scope; the **RBT-46 ticket and the RBT-14 plan-of-record comment are the disposition source of record**.

---

## 1. What changed since the dual-leg handoff was written

The dual-leg handoff was authored **before** leg 1 landed, so it describes RBT-45 as pending. State now:

- **RBT-45 landed.** PR #19 squash-merged to develop; **develop @ `6c76410a`** (commits `ce7f1192` DDR-001 v1.2.0 + `7fd26e7c` three-hat review of record). DDR-001 is now **v1.2.0 ACCEPTED** on develop, with the feedback-loop write authority homed (the three writes → named gateway-routed components; conformance check 7 added; graph-home-agnostic).
- **RBT-45 captures done.** Linear RBT-45 → **Done** (three-layer); Notion build-leg **LANDED** entry appended (the `6c76410a` baseline + RBT-46 resume pointer live there).
- **Baseline shift.** RBT-46 now stages on **`6c76410a`**, not the `73cb956d` the dual-leg handoff cites. **Re-verify the live develop tip at session-open** (it should be `6c76410a` unless something landed since).

**Important — DDR-002 content baseline is unchanged.** RBT-45 touched only DDR-001. **DDR-002 on develop @ `6c76410a` is still v1.1.0 (RBT-43 @ `1764fd9` content)** — the newer develop tip carries the DDR-001 change, not a DDR-002 change. So the five RBT-46 touches stage against the same landed DDR-002 v1.1.0 the dual-leg handoff anticipated; only the develop tip moved.

---

## 2. Leg-2 scope (pointer, not restatement)

RBT-46 is **DDR-002 v1.1.0 → v1.2.0**, an **additive MINOR** amendment, **five touches** — B-1 (§1), B-2 (§7 #22), M-2 (§2.3), M-5 (§4/§5), M-11 (PromotionDecision). The exact touch text, routing, and rationale live in:

- **RBT-46 ticket** — the five-touch scope + pre-author fresh-fetch (fetch it fresh, `includeRelations: true`).
- **RBT-14 plan-of-record comment** (2026-06-23) — the disposition source of record; its §3 "→ RBT-46" routing is authoritative.
- **Companion dual-leg handoff §3/§4** — orientation to the above.

**Hard checks this leg carries (flagged so they aren't missed):**
- **§7 invariant count must read 21 before adding #22.** Confirm the landed DDR-002 §7 set is **21** (RBT-43 took it 19→21), then #22 (retracted-node read-exclusion, safety-critical) takes it to **22**. A miscount here is a substrate-fidelity defect.
- **#22 → RBT-33 is downstream, not a Phase-1 action.** #22 extends RBT-33's conformance set exactly as #20/#21 did (captured in the RBT-33 comment, no new ticket — DIRECTIVE-025). Do not open RBT-33 work in this leg.
- **R8 one-way reference** holds in the other direction here — DDR-002 *may* reference DDR-001 (it's the downstream consumer), so the §1 label-taxonomy / CandidatePromotion home-pending touch can name DDR-001 constructs. (Contrast leg 1, where DDR-001 could not name DDR-002's `ProvenanceSummary`.)
- **M-5 / M-11 graph-home-agnosticism.** `CandidatePromotion` graph-home stays deferred (RBT-44); the M-11 PromotionDecision Neo4j-home and M-5 ProvenanceSummary widening are schema-structural, not graph-home rulings.

---

## 3. Session-open ceremony (run before any work)

1. **Deep read** of the full governance corpus in project knowledge: CLAUDE.md, CSD, DMS, ENG-STD-001/002/003, ADR-001, ADR-002, DDR-001 (now v1.2.0), DDR-002 (v1.1.0), templates (ddr / review / apply-prompt), and the companion dual-leg handoff.
2. **Fresh-fetch the mutable authorities:**
   - **Linear** — RBT-46 (full description, `includeRelations: true`, capture its exact `gitBranchName`) + the **RBT-14 plan-of-record comment** (the §3 "→ RBT-46" routing).
   - **Notion** — Reboot Decision Ledger (page `374caeea-1325-818d-8f9f-f5f56898b133`); confirm **R30 / R31** verbatim (they back the §2.3 seam and the retraction remedy-boundary) and read the build-leg tail (the RBT-45 LANDED entry is the current tail).
   - **Filesystem (local clone, `$SOFIA_REBOOT_ROOT`)** — landed **DDR-002 v1.1.0** §1 / §2.3 / §2.4 / §4 / §5 / §7, fetched fresh from develop @ `6c76410a` (DIRECTIVE-026.5; the companion handoff notes DDR-002 v1.1.0 is also current in project knowledge after the 2026-06-23 refresh — but fetch the live clone for anchor fidelity). **Confirm the §7 count = 21.**
3. **Confirm clean develop working tree.** The parked superseded DDR-003 draft stays out-of-repo at `${HOME}/Downloads/PARKED-DDR-003-feedback-loop-governance-superseded-draft.md` (set aside in leg 1; do not carry it back in). Leg 2 runs on develop with a clean tree.

---

## 4. Authoring shape (same pattern as leg 1, RBT-43/RBT-45 precedent)

claude.ai authors a **complete-replacement DDR-002 v1.2.0 staging file** + a **three-hat review of record** (LAA/SA/EA + antagonistic pass to convergence) + an **apply-prompt** (ENG-STD-003), against fresh-fetched landed authorities. Two-commit PR (the v1.2.0 doc + the review vendored under `docs/reviews/`). No `Co-Authored-By` trailer. Squash-merge to develop. Tad holds the merge gate; Code executes the apply-prompt in pause-point mode.

**Versioning:** additive MINOR, DDR-002 **1.1.0 → 1.2.0**. The `# Revised:` line already exists (RBT-43); replace it with the RBT-46 dated line (single-line, most-recent-only, DMS §2.2). Add the v1.2.0 Change Log row. Atomic-refresh pairs: Version cell ↔ Change Log Version; `# Revised:` date ↔ Change Log Date.

**Deliberation pause-points (no presumed alignment):** the five touches are richer than leg 1's single touch — surface them **one at a time** for ratification (M-5's ProvenanceSummary widening and M-11's per-dimension PromotionDecision structure especially carry design judgment, e.g. the per-dimension value-set is T2-contested pending first real use). Do not bundle the five into one ask.

**Post-merge captures (claude.ai-side, after leg 2 lands):** three-layer RBT-46 → Done; Notion build-leg LANDED entry; the RBT-33 #22 conformance-extension comment (no new ticket). No new R-rulings — these realize already-ratified dispositions (the RBT-43/RBT-45 build-leg precedent). Verify-after-write on every Linear/Notion write.

---

## 5. Carry-forward / still-open (non-blocking)

- **RBT-45 apply-prompt vendor** — deferred to a separate doc-only PR to `docs/session-handoffs/apply-prompts/` (RBT-43 precedent). Can ride with the RBT-46 apply-prompt vendor as a batched doc-only PR, or stay separate — Tad's call at close.
- **Parked DDR-003 draft** — stays out-of-repo; Phase 2 (RBT-14) re-authors DDR-003 fresh against the landed v1.2.0s.
- **Phase sequence after leg 2:** Phase 1 complete → RBT-14 (DDR-003 re-author + single-leg ACCEPTED landing, Phase 2) → RBT-15 (knowledge-service SDD, unblocks once DDR-003 lands).

---

## 6. Canonical pointers

- **RBT-46** — DDR-002 v1.2.0 ticket (five-touch scope + pre-author fresh-fetch).
- **RBT-14 plan-of-record comment** (2026-06-23) — disposition source of record; §3 "→ RBT-46" routing.
- **Companion:** `2026-06-23-session-handoff-ddr-003-corrective-to-phase-1-upstream.md` — §3/§4 scope detail; §8 learnings (carry forward: "the loop hasn't run ≠ no empirical warrant"; the durable-frozen-record thesis as an un-elevated ledger candidate).
- **R30 / R31** (Notion ledger) — the §2.3 seam citation and the retraction remedy-boundary.
- **RBT-44** — `CandidatePromotion` graph-home (deferred, non-blocking).
- **RBT-33** — conformance mechanization (downstream consumer of #22; not Phase-1).
- **Landed corpus** (develop @ `6c76410a`): ADR-001 v1.0.0, ADR-002 v1.0.0, DDR-001 **v1.2.0**, DDR-002 **v1.1.0**.

---

*End of leg-2 starter. Leg 2 = RBT-46 (DDR-002 v1.2.0), one Code session, two-commit PR. Then Phase 1 is complete and the cycle returns to RBT-14 (Phase 2).*
