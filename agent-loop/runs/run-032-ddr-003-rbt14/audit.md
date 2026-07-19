# Cold Audit — run-032-ddr-003-rbt14

| Field | Value |
|---|---|
| **Document** | runs/run-032-ddr-003-rbt14/audit.md |
| **Status** | AUTHORED — 2026-07-19 (claude.ai, cold, from the run folder; Code's RAW-RESULT not taken as authority — every figure independently recomputed from `ledger.json` + `action-log.jsonl`) |
| **Run** | run-032-ddr-003-rbt14 (first real engagement; target DDR-003 PROPOSED v0.1.0; pre-run HEAD `e3d2bcd`; `max_passes=4`, gen-12, author sandbox-apply dry mode) |
| **Method** | run-supervision.protocol.md §5 incl. the three armed watches (edit-region overlap · RELIT-class recurrence · interpretive satisfied-closes), scored against the committed PRE-REGISTRATION criteria. Baseline comparison (§6): **n/a — fresh document, no prior human-review record exists**; recall scoring not applicable. |

## 1. Executive result

run-032 ran 3 passes and halted **`HALT_DECISION: oscillation`** — a natural router halt at pass 3, not the `max_passes` bound. Operationally clean: 0 retries, 0 parse drops, 0 anchor-fails, `ephemeral_5m = 0` (all 884,467 cache-creation tokens in the 1-hour bucket; hats read from cache on passes 2+ — RBT-69 C3 satisfied on a real target). Recomputed ledger state: **77 findings (44 MATERIAL / 17 COSMETIC / 16 POSITIVE)**; 63 classified events; final state **40 open decision-bearing / 21 resolvable (8 closed, 13 open in-flight at halt) / 16 unclassified = the POSITIVEs** (correct arbiter behavior). Hats balanced: LAA 21 / SA 23 / coherence 22 / EA 11. POSITIVE proportionality 16/77 ≈ 21%, within bounds; confidence 52 high / 11 medium / 0 low — conservative bias held.

**The fresh-document questions are answered.** (1) Fresh-document behavior: orderly volume (28/31/18 per pass), no swamp, no BLOCKING — consistent with a self-reviewed record arriving healthy. (2) The docket is real: the 40 open decision-bearing records coalesce to **9 distinct decisions** (§8) — dominated by wording-precision and Decision-enumeration-completeness families, zero re-litigation of ratified design intent. (3) No natural CONVERGED: the author's high refusal rate (19 refused vs 5 edits + 5 satisfied) reflects wording-choice under-determination on a governance-dense record, not instrument failure; open findings accumulated faster than closes.

## 2. Satisfied-close stream

**5 `author_satisfied` (all high confidence), 1 `author_satisfied_evidence_fail`.** The evidence-fail (`ce3f595a`, §5.1 family) fired correctly — claimed `evidence_present` had 0 matches, close blocked, finding stayed open: the S-SAT gate catching a bad close live. Hand-validation of the 5: `c391218f` and `f89a475e` are clean duplicate-service closes (the Decision.3 carve-out edit and the Decision.5 placement edit had landed; the closes verified against the post-edit state). `ce544023` (per-dimension recording already enumerated in Decision.2) is a valid already-satisfied-at-raise close. `8ec60612`/`1450d89d` (Cross-References invariant list) were true at close time against the then-current text — but see §3. **First satisfied-close reopen observed** (`1450d89d`, recurrence 1): run-031's 0-reopen record breaks, and honestly — the close was valid at close time; a sibling edit (`7b9361fb`) then changed the same region and pass 3 legitimately re-raised. The never-hides alarm fired loudly, exactly as designed. This is region-churn interplay, not a hidden defect.

## 3. The oscillation halt — honest, correctly unbundled

Two findings reopened (recurrence 1 each), router halted with two `proposed_escalation`s (proposed, not opened — dry-mode discipline held):

- **`796e0e36` (§8 conformance item 1 — enforcement-state label).** The genuine oscillation: the draft said "(mechanized)"; DDR-001's own Conformance Checks header says "aspirational; mechanization deferred"; the author's edit flipped the label to "aspirational per DDR-001" — overcorrecting, since the DDR-002 §7 safety-tier checks cited in the same item ARE mechanized (harness Increment 1). Both flat labels are wrong; the correct wording is a split, which the author could not determine alone. Legitimate escalation; joins docket D5.
- **`1450d89d` (Cross-References invariant list).** The satisfied-close reopen of §2 — same underlying question as the open `a6a80e7d` (whether #20/#25 are cited-in-body or trimmed from the list); joins docket D9. Presented as one decision, not two items.

**Edit-region overlap watch:** 5 edits across 5 distinct loci; one region (Cross-References invariant list) shows cross-pass interplay (edit + satisfied-close + reopen). Single-region, cause-understood; the D-2 mechanical-trigger threshold ("churn persists post-fix") is not met.

## 4. Refusal stream — and the RELIT watch

19 refusals, uniformly of one species: *"the named authority does not uniquely determine the fix"* — the author correctly declining wording choices among multiple conforming edits (Decision-enumeration phrasings, tense qualifications, cite-vs-trim). **RELIT-class count: 0** — no refusal re-asks a decision the deliberation record (in substrate this run) had already ratified; one potential RELIT (`c391218f`, the ratified holder-set carve-out) was correctly closed satisfied instead. **The gen-13 rule's trigger has NOT fired** — the class did not recur on a real target with the deliberation record available to reviewers. Recommend the gen-13 candidate stays shelved. 2 `author_unresolved` (cause: target) are cross-document findings naming sibling docs outside the single-doc set — both pre-discharged by standing vehicles (DDR-004's stale ADR-002 v1.1.0 pin → the operator-ruled pin-currency ticket; DDR-001's aspirational-checks header → docket D5's wording split).

## 5. Reviewer stream

Claims quote live text verbatim throughout (spot-verified across the odb and refusal sets; 17 `claim_divergence` events all gen-12 grounding corrections, none fatal). 0 arbiter-born decision-bearing; 18 `dedup_open` absorptions (identity guard working); the semantic families (§5.1 raised 8×, executed-retraction ownership 6×, References pin 6×, §7.3 tense 4×) arrived as cross-hat sibling records — admitted separately by design, collapsed at the docket layer. One instrument catch worth naming: the loop found a residual "Class-4" token in §8 item 2 that the authoring-session self-review missed after fixing four sibling instances — independent-verification value demonstrated on its first real target.

## 6. Cost — envelope breached; live tracking under-computed (instrument finding)

Recomputed from the `llm_call` stream at Opus-class list pricing: uncached input 1,417,509 ($21.26) + output 60,580 ($4.54) + 1h-cache writes 884,467 ($26.53) + **cache reads 11,559,111 ($17.34)** ≈ **$69.7** — vs the reported ~$23 (≈ uncached input + output only) and the pre-registered $30–50 envelope. Two findings: (a) **the live cost figure omitted cache-write premium and cache-read charges (~3× under-count), so the §3e cost-runaway watch was effectively blind** — the RAW-RESULT convention and the §2 envelope arithmetic must include the four usage line-items; (b) the cost *structure* is the RBT-72 case in miniature: 63 arbiter + 30 author calls re-reading a ~160k-token cached prefix accounts for most of the read volume — per-actor model-mix and substrate-slimming for the arbiter/author sites are the levers. Route: protocol/RAW-RESULT template line + RBT-72 substrate.

## 7. Instrument findings (route per §8 of the protocol)

1. Cost-reporting convention (§6a) — protocol §2/§3e + RAW-RESULT template. 2. Single-doc-set actionability seam: cross-doc findings arrive `author_unresolved(cause: target)` and stay open — correct-but-noisy; note for the design-review-loop skill's target-set guidance (multi-doc set or a routed-outward disposition class). 3. `doc_changes` ledger entries carry null pass/finding/region fields — a logging gap (same species as the standing `pass: null` item); edit provenance was reconstructed from `action-log` + diff. 4. 4 author preamble strips (gen-10 seam working). 5. First satisfied-close reopen (§2/§3) — no rule change recommended; the alarm is the design.

## 8. Docket — 40 records, 9 decisions (grouped per the ratified coalescing discipline; splittable)

D1 References-pin currency (6 + 1 unresolved) · D2 §5.1 interim-posture wording vs DDR-002 §2.3's defined write shape (8) · D3 §7.3 per-dimension traversal-reachability tense vs deferred structured capture (4) · D4 Decision-enumeration completeness (Decision.3/.7/.10 vs body nuances) (7) · D5 §8 enforcement-state labels (split mechanized/aspirational; "holds by construction" qualification; safety-relevant-but-aspirational tiering) (7, incl. oscillation `796e0e36`) · D6 executed-retraction detection-analogue ownership wording vs DDR-002 §2.4's routing (6) · D7 §4 "working-tier retention windows" plurality (3) · D8 Position-4 trajectory note request (1) · D9 Cross-References invariant-list cite-vs-trim (2, incl. reopen `1450d89d`). Member finding-ids and per-decision recommendations in the session docket presentation; rulings are the operator's.

## 8a. Correction addendum (2026-07-19, post-run-033; registry pattern)

§6's $69.7 recompute and the envelope-breach finding are **corrected**: the arithmetic used legacy Opus per-token rates; at the run's actual model (`claude-opus-4-8`) list rates ($5/$25/$10/$0.50 per M), run-032 recomputes to **≈$23.2** — inside the $30–50 envelope, and consistent with the live figure. What survives of §6: the four-line-item reporting convention (adopted; honored by run-033's RAW-RESULT) and the cost-structure observation (cache-read volume at the arbiter/author sites as the dominant line — cost-architecture substrate). The §3e "watch was blind" claim is withdrawn. The audit's error, not the runner's — logged per the correction-registry discipline.

## 9. Empirical floor

One run, one fresh document, n=1 for every fresh-document observation. The 0-RELIT and 0-arbiter-born observations are single-run measurements on a target whose deliberation record was in substrate — the favorable conditions are part of the result. No isolation run recommended; the docket rulings + amendment cycle are the next natural data.
