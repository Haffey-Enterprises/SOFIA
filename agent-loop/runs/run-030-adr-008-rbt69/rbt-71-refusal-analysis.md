# RBT-71 — Run-030 Refusal Analysis (empirical leg)

| Field | Value |
|---|---|
| **Document** | rbt-71-refusal-analysis.md |
| **Status** | AUTHORED — 2026-07-19 (claude.ai, fresh from run-030 captured artifacts; $0, no new runs) |
| **Ticket** | RBT-71 (decision-surface inflation) |
| **Method** | Full replay-reconstruction of the document state at every author action, from the pristine pin `24461d3f` + the 20-edit stream (author emissions), verified **byte-identical** to the captured end-state. Every one of the 46 refusals hand-read against (a) the document at the pass-start when its finding was raised and (b) the document at the moment of refusal. |
| **Empirical floor** | n=1 — one run, one document (ADR-008). Percentages below are measurements of this run, not constants. |

## 1. Verified core arithmetic (independently recomputed)

72 classifications → 66 resolvable / 6 decision-bearing (65 high-conf). Author: 20 edits, 46 refusals (70% of resolvables served), refusals per pass 12/8/13/13. Every refusal escalates via `_escalate` → 6 born + 46 escalated = **52 open decision-bearing**. Confirmed. The arbiter is conservative-correct; the ticket's driver attribution holds.

## 2. The headline correction to the ticket's hypothesis

The ticket suspected ⅓–½ of the "already conforms" refusals were **reviewer false positives**. Raise-time validation shows most are not: for 11 of the 14 already-conforms/no-anchor refusals, the flagged defect **genuinely existed in the document at the pass-start snapshot the reviewer reviewed**, and the text became conformant *mid-pass* — an earlier finding in the same pass's serial author queue fixed the same defect. The reviewer was right; the pipeline served the same defect N times.

Why N findings per defect: identity is `(target, normalize_locus(locus), altitude)` — cross-hat duplicates are *by design* distinct records (ratified RBT-69 counting-semantics feature, roster-independence evidence), and same-hat cross-pass re-descriptions of a locus produce distinct normalized loci. The arbiter classifies each in isolation; the author serves them serially; the first edit satisfies the rest; `_escalate` turns each satisfied residue into an operator decision.

## 3. Categorization of all 46 refusals

| Category | n | Meaning | Correct routing |
|---|---|---|---|
| **NOOP-SATISFIED** | 11 | Defect real at raise; fixed mid-pass by a sibling finding's edit; nothing remains to edit | Close satisfied — never an operator decision |
| **STALE-FLAG** | 3 | Defect did not exist at raise-time pass start (2 re-derived from rulings without checking live text: `5bf63210`, `66ef5ab4`; 1 flagged text its own cited authority endorses: `8dbbe46a`) | Close satisfied + reviewer-side rule |
| **RE-LITIGATED-RATIFIED** | 4 | The "decision" requested was already made in ratified design intent (RBT-59 Item 3 provenance-survival timing), re-raised 4× across passes/hats | Close satisfied-by-authority |
| **TOOLING-LIMIT** | 1 | Fix fully determined (Ruling G verbatim replacements), two loci; single-find-replace limit forced escalation | Author capability or determined-split; not a decision |
| **GENUINE-UNDERDETERMINED** | 27 | Defect real; authority genuinely underdetermines/conflicts | Decision-bearing — but see coalescing |

**Phantom escalations: 19/46 (41%)** — inside the ticket's ⅓–½ estimate, but with the mechanism recast: only 3 of 19 are true reviewer over-production; 11 are duplicate-service no-ops; 4 are re-litigation of ratified intent; 1 is tooling.

## 4. The second inflation axis: duplicate decisions

The 27 genuine escalations collapse to **10 distinct underlying decisions**:

| Family | Findings | The one decision |
|---|---|---|
| subj-name | 8 | Which subject-name for the forthcoming ingestion record is canonical (variant introduced by the pass-1 Ruling-G edit itself) |
| tense-1 | 4 | §1 Context earned-tense posture for a PROPOSED record |
| B-stmt | 3 | Ruling B relationship-statement placement/wording |
| n0-posture | 3 | Environment n=0 accountability disclosure posture |
| perwrite-batch | 3 | 'Per-write (EA)' label vs batch PromotionDecision |
| D-vs-column | 2 | Ruling D status label vs uniform-column contract (the churn conflict) |
| tense-5.2 | 1 | §5.2 distillation-bullet tense |
| G-anchor | 1 | §7 pointer-sentence re-anchoring under subject-name rule |
| role-name | 1 | Which role holds per-policy Environment accountability |
| ddr2-22 | 1 | DDR-002 §7 #22 listing precision |

The 6 **arbiter-born** decision-bearing findings collapse the same way — into exactly 2 families (`perwrite-batch` ×3, `role-name`/accountability ×3), **both already present in the escalated set**. Total distinct genuine decisions across the whole run: **~10**. Decision surface surfaced: 52. **Inflation ≈ 5×** — roughly half from phantom escalations, half from duplicate-decision multiplication.

## 5. Third phenomenon (new, not in the ticket): semantic churn invisible to the oscillation guard

The §2.2 Environment "Realization routes to" cell was rewritten in **every pass** (5 distinct states p1→p5), pinballing between "Ruling D status label present" and "destination-only uniform column." The §2.3 Ruling-F qualification was re-edited in all 4 passes. `recurrence = 0` throughout — every round is a fresh finding-id (different hat or re-worded locus), so the recurrence trigger, which watches same-id reopen, is blind to it. This is run-028's trading class resurfacing at the semantic level. The underlying authority conflict (D-vs-column) reached the ledger only as 2 late escalations, never as one decision — and the author behaved inconsistently across its duplicates: it **refused** `a9058ede` (destination-only conversion = "unratified choice") and then **performed that exact conversion** the same pass for sibling finding `bc334c81`.

## 6. Where the false positives sit

Evenly spread — refused findings by hat: SA 12, EA 12, LAA 11, coherence 11; refusals per pass 12/8/13/13. Not concentrated in one hat or pass. The STALE flags cite the rulings/skill rather than quoting live document text. Concentration is by **authority-family**, not by hat: Ruling D (13 refusals + 8 edits), subject-name/Ruling G (9), Ruling F (4), provenance/RBT-59 (4).

## 7. Implications for the fix loci (deliberation input, not conclusions)

1. Defect 1 (ticket) confirmed exactly: `_escalate` is one-signal routing; a refusal carries at least five meanings (satisfied / stale / already-decided / underdetermined / tooling) and only one of them is an operator decision. The dominant single fix is a **satisfied-close** disposition.
2. Defect 2 (ticket) recast: raise-time reviewer over-production is real but small (3/46). The reviewer-prompt fix is cheap and worth taking, but it is not the volume lever. The volume levers are the satisfied-close and **decision coalescing** (52 findings → ~10 decision-docket entries).
3. New: the churn/conflict phenomenon suggests a per-locus re-edit signal and/or conflict surfacing — candidate for explicit deferral with a named follow-up.

Per-finding table: `categorization.json` (all 46, with per-finding evidence notes).
