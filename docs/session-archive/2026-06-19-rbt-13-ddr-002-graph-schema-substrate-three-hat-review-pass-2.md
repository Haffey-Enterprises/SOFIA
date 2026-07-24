# File: docs/reviews/2026-06-19-rbt-13-ddr-002-graph-schema-substrate-three-hat-review-pass-2.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: Pre-authoring three-hat review (Pass 2) of the DDR-002 Graph Schema design substrate v0.2 (RBT-13). Independent fresh-eyes pass verifying the Pass-1 fold and serving the substrate-readiness gate before Claude Code authors DDR-002.

# Three-Hat Review — 2026-06-19 (RBT-13 DDR-002 Graph Schema Substrate v0.2 — Pre-Authoring Readiness Gate, Pass 2)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-19 |
| **Reviewer** | Claude (claude.ai design instance) — Pass-2 three-hat reviewer wearing LAA / SA / EA hats, under DIRECTIVE-026, on behalf of Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC |
| **Scope** | `DDR-002 Graph Schema — Ratified Design Substrate (v0.2)` (RBT-13) — (a) verify the Pass-1 fold (M-1…M-6, C-1, C-2) landed and is sound; (b) independent fresh read for new findings introduced by the edits. |
| **Authority** | RBT-13 acceptance criterion; ENG-STD-001 §12.6 (three-hat) + CSD DIRECTIVE-007 (multi-role review, §7.2 severity vocabulary); the Pass-1 review of record (this doc's sibling); operator direction (2026-06-19). |
| **Outcome** | **PASS WITH FINDINGS — converging.** All six Pass-1 MATERIAL findings and both COSMETIC verified resolved (now no-drift confirmations). 0 BLOCKING; **1 MATERIAL** (M2-1, *conditional* on the M-5 ratification); 1 COSMETIC (optional). **1 open operator ratification** — the M-5 RG-provenance structural-inheritance posture, which the substrate correctly self-flags. Not yet a zero-findings clean pass. |

---

## §0 Historical Context

Second execution of the pre-authoring **substrate** three-hat for RBT-13 (the discipline's first execution is the Pass-1 review of record, `…-substrate-three-hat-review.md`, which carries the first-execution preamble — see it for the two-gates framing: this pre-authoring substrate gate vs. the separate post-authoring DDR-acceptance gate). This pass reviews **v0.2**, the revision that folds the Pass-1 findings.

---

## §1 Scope

### 1.1 In-scope

- `DDR-002 Graph Schema — Ratified Design Substrate (v0.2)` (uploaded, 2026-06-19) — start-to-finish.
- **Fold verification:** each Pass-1 finding (M-1…M-6, C-1, C-2) checked at its loci against v0.2.
- **Fresh-eyes pass:** new findings or regressions introduced by the v0.2 edits.

### 1.2 Sources (fresh-fetch posture, DIRECTIVE-026 §26.5)

The canonical authorities were fresh-fetched earlier **this session** and re-confirmed for Pass 2 (not worked from recall): the **Reboot Decision Ledger** was re-fetched at the top of this pass and is byte-identical to the Pass-1 fetch (no drift in R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25); **ADR-002** §2.2/§2.3/§2.6 is static project-knowledge state; **Linear RBT-13** (In Progress) and **RBT-12** (Done @ `15ff20f`, PR #12) are unchanged this session.

### 1.3 Out of scope (unchanged from Pass 1)

The authored DDR-002 (post-authoring gate); DDR-001 internals; DDR-003 governance content; SDD realization; conformance mechanization (RBT-33); ADR-002's stale author string (tracked at RBT-36).

---

## §2 Findings

### 2.1 BLOCKING findings

**None.**

### 2.2 MATERIAL findings

#### Finding M2-1: The structural-provenance surrogate for the derived RG types needs an explicit mandatory-parent-edge cardinality invariant

**Location:** Substrate §4 (lines 148–152, the M-5 RG-provenance posture); §1 (27); §7 (196, 199 — "relationship cardinality" invariant class).

**Description:** The M-5 resolution makes `Evidence` and `RejectedAlternative` carry **no** provenance group; their provenance is recovered *structurally* — `Evidence` via `source_node_version` + `observed_at` + `SOURCED_FROM` → a provenance-bearing KG node; `RejectedAlternative` via its parent `ReasoningProgress` (`REJECTED`) + `WOULD_HAVE_USED` → a KG node. This is sound **only if those structural edges are mandatory**: an orphaned `RejectedAlternative` (no parent `REJECTED`) or an `Evidence` with no `SOURCED_FROM` (e.g., a non-KG-sourced or operator-supplied fact) has *no* provenance at all, and the stated "provenance-chain" structural invariant (§5, line 172) breaks silently. The edits did not regress anything — this is a *new* dependency the M-5 fix itself introduces.

**Why material (not blocking):** The invariant *class* already exists — §7 lists "relationship cardinality" as a documented + CI-checked invariant. The gap is that the RG-provenance surrogate is now *load-bearing* on two specific edges' mandatoriness, and that load-bearing role is not made explicit in the conformance set. Without it, the auditability guarantee (provenance-chain traceability) rests on an unstated assumption. It does not block the gate because the fix is a one-line binding into an existing invariant class, and it is contingent on the M-5 posture being confirmed.

**Disposition (conditional on the M-5 ratification, §2.5):** If the structural-inheritance posture is confirmed, bind into §7's conformance-checked set: (a) every `RejectedAlternative` is reached via exactly one parent `ReasoningProgress` `REJECTED` edge; (b) every `Evidence` carries a mandatory provenance-bearing structural link (`SOURCED_FROM` to a provenance-carrying KG node, and/or a `SUPPORTED_BY` parent), with the non-KG-sourced-Evidence case either prohibited or given its own provenance treatment. If instead the posture is *not* confirmed (the two derived types carry the group after all), this finding dissolves.

### 2.3 COSMETIC findings — noted, no-action

- **C2-1 — "six sub-graphs" phrasing (§3, line 115).** The edge catalog is labelled "six sub-graphs." It is internally *correct* (one edge sub-graph per plane: five core + the Cost/Extension sub-graph, with Solution-centric edges deferred to §5), so it is not a defect — but for parallelism with the M-1 reframe ("five core planes + the Extension plane"), the author may optionally phrase it "five core-plane sub-graphs + the Cost/Extension sub-graph." Purely stylistic; no substance at stake.

### 2.4 No-drift confirmations (positive findings) — Pass-1 fold verified

Each Pass-1 finding was checked at its loci in v0.2 and confirmed resolved:

- **M-1 (five-core + Extension) — resolved.** §0 (17) "five core planes plus the Extension plane … Cost … not a sixth core plane (R23)"; §2 header (45) and lead (47) reframed; R5 described as "five logical planes + Extension" (19). No residual "six planes." Conforms to ADR-002 §2.2/§2.3 and R23.
- **M-2 (§9 → §8) — resolved.** §0 (15) and §2.5 (87) repointed to §8; zero `§9` references remain.
- **M-3 (bare §2.6 → ADR-002 §2.6) — resolved.** Disambiguated at §4 (144), §7 (199), §8 (212, 215); §4 (137) kept its existing correct qualifier; the legitimately-internal §2.6 reference at §1 (33) correctly left bare.
- **M-4 (§5 owns/cites boundary) — resolved.** New "Ownership line (R8 / R22)" lead at §5 (158) enumerates owns (schema contract: `Solution`/`CandidatePromotion` shapes, edge grammar, structural invariants) vs. cites (mechanics/data-path → DDR-001; diagnosis policy/criteria/thresholds/cadence → DDR-003; workflow → SDD); reinforced at (167) and (174). Schema substance retained in full; only the governance characterization is routed out. Clean bright line.
- **M-5 (provenance scope) — resolved structurally, with one design call surfaced (§2.5).** §1 (27) scoped to "every KG node"; §7 (196) scoped to KG nodes + the two authored RG types; dedicated §4 posture block (148–152). The derived-type omission is now *explained* (structural inheritance), not silent. (The remaining dependency this creates is M2-1.)
- **M-6 (R9 in §0) — resolved.** §0 (19) now lists R9; consistent with §8 (228), §6 (186), §8 boundary map (206).
- **C-1 (R10 label) — resolved.** §0 (19) now "R10 (no-PHI-by-design enforced constraint)."
- **C-2 (existence-constraint edition) — resolved.** §7 (196) re-cites the existence-constraint capability to the **edition ruling R3** (ADR-002 the ADR home), correcting the prior "ADR-002/R20."
- **Bonus folds (Pass-1 forward-pointers, picked up proactively):** identity string "Executive Architect, Haffey Enterprises LLC" set as the authoring instruction (§ header line 7, §8 line 228) per FP-2/RBT-36; post-merge filings annotated "with DIRECTIVE-025 dedup at filing" (§8 line 226) per FP-3.
- **No new dangling cross-references introduced** by the edits — §0→§8, §2.5→§8, §4→§5, §4→ADR-002 §2.6, §7→§4, §1→§4/§7, §6 self-refs all resolve.
- **Load-bearing Pass-1 positives still hold:** DDR-001 landed/upstream (now annotated `15ff20f` / PR #12 in §8); R8 one-way reference honored; ADR-002 §2.6 anchor faithful; R18/R23/R24/R25 correctly applied.

### 2.5 Open operator ratification — the M-5 RG-provenance posture

This is a deliberately-surfaced **design call**, not a defect — the substrate self-flags it (header line 9; §4 line 152: *"the one Pass-1 finding whose resolution is a design call — confirm before authoring"*). Recording it here as the one ratification this pass requires.

- **The call:** `Evidence` and `RejectedAlternative` carry **no** provenance group; provenance is recovered structurally (version-pin + `SOURCED_FROM` for Evidence; parent `REJECTED` + `WOULD_HAVE_USED` for RejectedAlternative). The existence constraint scopes to KG nodes + the two authored RG types only.
- **Reviewer read:** sound and reversibility-appropriate — structural provenance is recoverable and arguably *richer* than a redundant `source_class`/`ingested_at` group (it ties evidence to the specific KG node-version it snapshots). The only caveat is the guard in M2-1.
- **Ratification needed:** confirm the structural-inheritance posture. If confirmed, fold M2-1 (mandatory-edge cardinality into §7). If declined, add the provenance group to the two derived types and both M-5's residue and M2-1 dissolve.

---

## §3 Forward-Pointer Triage

No new forward-pointers this pass. Carried from Pass 1 (status unchanged — **held for ratification**, no tracker writes made):

| Proposed ID | Summary | Status |
|---|---|---|
| RBT-13 (update) | Ticket Ledger line mis-cites cost as R12; should be R23 (+R24/R25) | Held — description-hygiene edit to existing ticket |
| RBT-36 (existing) | ADR-002 stale author-identity string | Already tracked; v0.2 instructs DDR-002 to use the current string |
| (post-merge) | `Process` node-type ticket / detection-correction SDD / selection-edge preference-landing | Substrate-declared (now annotated "with DIRECTIVE-025 dedup at filing") — confirm filing post-merge |

---

## §4 Audit Outcome

> **PASS WITH FINDINGS — converging.** The v0.2 fold is verified complete and sound: all six Pass-1 MATERIAL findings and both COSMETIC are resolved (§2.4), with two Pass-1 forward-pointers folded proactively. Pass 2 surfaces **0 BLOCKING**, **1 MATERIAL** (M2-1 — bind the RG-provenance surrogate's mandatory-edge cardinality into the §7 conformance set, *conditional* on confirming the M-5 posture), and **1 optional COSMETIC** (C2-1). **One open operator ratification** remains — the M-5 RG-provenance structural-inheritance posture, which the substrate correctly self-flags. This is not yet a zero-findings clean pass.

**Per-hat verdicts (ENG-STD-001 §12.6 aggregation):**

| Hat | Read | Verdict |
|---|---|---|
| **LAA** — *what is this change?* | Still matches RBT-13's R8 schema-half scope; M-4 boundary fix verified (no creep into DDR-001/DDR-003); forward-deps + FP niceties folded. No LAA finding. | `proceed` |
| **SA** — *how does it conform?* | All cross-refs resolve (§9→§8, ADR-002 §2.6 qualified); ruling lists reconciled (R9); citations corrected (R3 edition, R10 clause). One new finding: M2-1 (surrogate needs the mandatory-edge cardinality bound into §7). | `proceed-with-changes` |
| **EA** — *should it land in this shape, now?* | Five-core-+-Extension posture restored (ADR-002/R23 conformance); the M-5 posture is a deliberate, sound, reversibility-appropriate design call, correctly surfaced for ratification. Endorses the call pending confirmation + the M2-1 guard. | `proceed-with-changes` |

**Gate decision:** The readiness gate is **one ratification + one conditional fold away from clean.** Path to "cleared to author": (1) confirm the M-5 RG-provenance posture; (2) if confirmed, fold M2-1 (and, optionally, C2-1) into the substrate; (3) a brief Pass-3 re-confirm verifies the §7 cardinality binding and closes the cycle. If the M-5 posture is declined instead, fold the provenance group onto the two derived RG types and re-confirm. Either branch is a short hop — the substrate is substantively sound.

---

## §5 Cross-References

- **Authority:** RBT-13 acceptance criterion; ENG-STD-001 §12.6; CSD DIRECTIVE-007 (§7.2 severity vocabulary).
- **Substrate reviewed:** `DDR-002 Graph Schema — Ratified Design Substrate (v0.2)`; authoring target `docs/ddr/DDR-002-graph-schema.md`.
- **Prior pass:** `docs/reviews/2026-06-19-rbt-13-ddr-002-graph-schema-substrate-three-hat-review.md` (Pass 1 — 6 MATERIAL, 2 COSMETIC; all folded into v0.2).
- **Canonical authorities (fresh-fetched this session, re-confirmed for Pass 2):** Reboot Decision Ledger (`374caeea…`, byte-identical to Pass-1 fetch); ADR-002 §2.2/§2.3/§2.6/§4.1; Linear RBT-13 / RBT-12 (`15ff20f`, PR #12).
- **Findings disposition tracking:** M2-1 → §7 cardinality binding (conditional on M-5 ratification); C2-1 → optional §3 phrasing; FP-1/FP-3 → held for ratification; FP-2 → RBT-36.
- **Open ratification:** M-5 RG-provenance structural-inheritance posture (§2.5).
- **Future review cadence:** Pass-3 re-confirm after the M-5 ratification + M2-1 fold → then the separate post-authoring RBT-13 acceptance three-hat against the authored DDR-002.
