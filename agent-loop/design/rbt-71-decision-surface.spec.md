# File: rbt-71-decision-surface.spec.md
# Created: 2026-07-19
# Description: Design spec for the RBT-71 decision-surface fixes — the author
#   satisfied-close disposition, the triage docket-coalescing discipline, the
#   gen-12 reviewer live-text grounding rule, and two explicit deferrals with
#   named promotion triggers.

| Field | Value |
|---|---|
| **Document** | rbt-71-decision-surface.spec.md |
| **Doctype** | Construct-local design spec (ruled via the `author-decision-record` / `author-standard` gate: not ADR/DDR/SDD — governs the agent-loop construct's machinery only, survives no platform test, cited by construct documents; same ruling and genre as `rbt-69-loop-optimization.spec.md`) |
| **Status** | PROPOSED v0.1.0 |
| **Date** | 2026-07-19 |
| **Ticket** | RBT-71 |
| **Author** | Thaddeus Haffey (Executive Architect), authored on claude.ai |
| **Ratification** | Six items ratified per item by Tad, 2026-07-19 (analysis frame; satisfied-close shape; triage coalescing; gen-12 reviewer rule incl. same-run incorporation; multi-locus deferral; churn-guard deferral-with-watch) |
| **Empirical driver** | run-030 refusal analysis (`runs/run-030-adr-008-rbt69/rbt-71-refusal-analysis.md` + `rbt-71-categorization.json` beside it): all 46 refusals hand-validated against replay-reconstructed document states (byte-identical to captured end-state) |

---

## 0. Scope and problem

On run-030 (ADR-008, 4 complete passes + partial 5th) the loop drove the open decision-bearing set to **52**, of which **19 were phantom** (no decision existed) and the remaining 33 findings carried only **~10 distinct decisions**. The arbiter is not the driver (6 born decision-bearing, conservative-correct). The driver is the author's escalate-on-refuse path: a refusal carries at least five meanings — **satisfied / stale / already-decided / underdetermined / tooling-limited** — and `_escalate` routes all five identically to the operator surface.

RBT-69 (ACCEPTED v1.0.0) is unaffected: identity, caching, and disposition-honesty all held on run-030. This spec is a distinct axis — the honesty of the *contents* the disposition surfaces.

**Hard invariants preserved (not re-opened).** Execute-vs-reason bright line; no LLM on the "done" decision; cost-down never coverage-down. A satisfied-close is accepted only on a mechanically verified evidence anchor; a failed anchor falls back to today's escalate — the change can close nothing the current loop would have surfaced without machine-checkable evidence.

**Empirical floor.** n=1 — one run, one decision-dense document. The 41% phantom rate and the family groupings are measurements of run-030, not constants.

---

## 1. Piece A — Author satisfied-close disposition (ratified Item 2)

### Decision

The author gains a third action, **`close_satisfied`**, alongside `edit` and `refuse`, lawful only when the finding's demand is *already met by the current document text* and that satisfaction is **quotable**. The closure is accepted only after a mechanical evidence check; on any failure it degrades to the current behavior (escalate).

### Schema (author output)

```json
{
  "action": "close_satisfied",
  "finding_id": "<id>",
  "evidence_present": "<verbatim substring of the current document showing the conformed state, or null>",
  "evidence_absent": "<the offending string the finding targets, which must not appear in the current document, or null>",
  "authority_satisfied": "<the authority + locus the current text already conforms to>",
  "rationale": "<one terse sentence, <=30 words>",
  "confidence": "high" | "medium"
}
```

Construction invariants: at least one evidence field non-null; `confidence` `high`/`medium` only (unsure means refuse/escalate, mirroring the edit bias); `authority_satisfied` non-empty.

### Mechanical verification (code, not model)

- `evidence_present` supplied → it must occur **at least once**, verbatim, in the current target document (presence, not uniqueness — this is evidence, not an edit anchor).
- `evidence_absent` supplied → it must occur **zero** times.
- Both supplied → both must verify. Any failure → log `author_satisfied_evidence_fail` and `_escalate` exactly as today. **A malformed or unverified satisfied-close can never close a finding.**

### Ledger semantics

`status = "closed"`, `pass_closed` stamped, `resolution_note = "satisfied: already conforms to <authority_satisfied>"`. **No new status value, no new ledger field** — `open_cbm`, plateau, and the router are arithmetically untouched. New action-log event `author_satisfied` (`finding_id`, evidence kind(s), `authority_satisfied`, `confidence`).

### Safety property (load-bearing)

A *wrong* satisfied-close is caught by the existing recurrence trigger: a reviewer re-raising the same identity next pass reopens the closed id, increments `recurrence_count`, and halts the run loudly as `oscillation`. A bad closure converts into the loudest signal the loop has, never silence. Residual (watched, n=1): a stale re-flag of a genuinely satisfied finding would trip the same halt falsely; observed closed-id re-raise rate in run-030 is zero across four rejection-biased passes.

### Which run-030 classes this routes correctly

NOOP-SATISFIED (11 — `evidence_present`), the not-found flavor (`evidence_absent`), STALE-FLAG (3), RE-LITIGATED-RATIFIED (4 — the current text embodies the ratified posture; `authority_satisfied` cites the design intent). The 27 GENUINE-UNDERDETERMINED remain refusals and escalate — correctly.

### Prompt amendment (`design/author.prompt.md`)

Third action added to the Output section; new hard rule: *"Close-satisfied only on quotable evidence. `close_satisfied` is lawful only when the conforming state is quotable verbatim from the current document (or the offending text is verifiably absent). If satisfaction requires interpretation, argument, or reading between loci — refuse. The evidence fields are checked mechanically; a closure whose evidence does not verify escalates."* Bias section extended: the asymmetry now runs *fabricated fix > fabricated satisfaction > needless refusal* — when torn between `close_satisfied` and `refuse`, refuse.

---

## 2. Piece B — Docket coalescing at the triage surface (ratified Item 3)

### Decision

**No runner change.** Findings remain unbundled, distinct records in the ledger and the halt payload (RBT-69 counting semantics preserved). Coalescing is codified as the **required presentation shape of the triage step**:

- `design-review-loop` skill, triage section: when a halt's decision set is surfaced to the operator, the triage surface first proposes a grouping into **distinct underlying decisions** — each group one ratification ask, member finding-ids listed, body-evidence per group, splittable on operator demand. Per-item ratification is per *decision*, not per finding record.
- `run-supervision.protocol.md` §5: one matching line in the surfacing guidance.

### Rationale (alternatives rejected)

Runner-side mechanical grouping by authority tokens **over-groups on real data** (subj-name and G-anchor share identical citations; tense-1 and tense-5.2 share "tense is earned by enforcement") — bundling two decisions into one ask is the worst-direction error. Runner-side LLM grouping adds a model judgment inside the loop for a presentation concern. Triage-layer grouping is where the judgment is human-supervised and where a wrong merge is caught at the moment of ruling. Escalation path if triage-layer grouping proves error-prone across runs: a runner-side assist, designed then.

---

## 3. Piece C — Gen-12 reviewer live-text grounding rule (ratified Item 4)

Added to the shared Contract block of all four reviewer prompts (three hats + coherence sweep), as rule 9; prompt generation stamped **12**:

> **9. Ground every non-conformance claim in the live text.** A finding that alleges the document fails to conform MUST quote verbatim, in `claim`, the current document text it faults at the named locus — or state explicitly that text the authority requires is absent at that locus. Re-deriving a defect from an authority, a ruling, or memory of a prior pass without locating it in the current text is not a finding: if you cannot quote the live text you are faulting (or name the absence), do not emit.

Driver honestly stated: 3/46 (hygiene, not the volume lever). Absence-findings stay raiseable by construction. Side benefit: the cold audit gains a per-finding quote mechanically checkable against the reviewed snapshot; the named escalation path (not built) is a mechanical admission check `quoted text ∈ document`. Ratified to ride the same proving run as Piece A; the audit attributes by stream (refusal stream vs finding stream).

---

## 4. Deferrals (ratified Items 5, 6) — explicit, with promotion triggers

**D-1 Multi-locus tooling limit — DEFERRED.** n=1 (`60f8dfe4`). The named follow-up shape, pre-agreed: a bounded multi-edit action (list of find-replaces, each anchor-checked, applied all-or-nothing). Promotion trigger: determined-multi-locus refusals recurring across runs (> once per run rather than once ever, per cold audits). Until then the class escalates and costs one docket glance.

**D-2 Semantic-churn runner guard — DEFERRED; audit watch ADDED.** The recurrence guard is blind to semantic trading (run-030: the §2.2 Environment cell rewritten in all 5 pass-states, recurrence = 0). A runner-side detector keyed on `(target, normalize_locus)` under-detects its own motivating case (the churn arrived under differing locus wordings) — rejected. Instead, `run-supervision.protocol.md` §5 gains an audit check: **cross-pass edit-region overlap** — two edits whose anchor regions intersect in the document across passes, computed from captured emissions at $0. The gap becomes documented and instrumented. Promotion trigger: post-fix audits still showing cross-pass edit-region churn → a mechanical same-region re-edit trigger routed into the oscillation family, designed against post-fix data.

---

## 5. Protocol amendment — run-supervision §2 spend discipline (ratified 2026-07-19)

Carried verbatim as ratified; insert into §2 Pre-run checklist **before** the existing cost-envelope item. See `run-supervision-s2-amendment.md` for the exact insert text and placement instruction. (Companion architectural levers — Batch API, per-actor model mix — tracked as RBT-72.)

---

## 6. Correctness tests (the proving obligation)

Unit (S-suite additions):

- **S-SAT-1** — `close_satisfied` with verifying `evidence_present` closes the finding; it never appears in a halt payload.
- **S-SAT-2** — `close_satisfied` whose `evidence_present` does not occur in the document escalates; the finding stays open. (The never-hides-a-live-finding test.)
- **S-SAT-3** — `close_satisfied` whose `evidence_absent` *does* occur in the document escalates.
- **S-SAT-4** — a re-raised satisfied-closed identity increments `recurrence_count` and routes to `HALT_DECISION:oscillation` (pins the safety net).
- **S-SAT-5** — `low`-confidence or evidence-less `close_satisfied` fails construction → parse/escalate path, never applied.
- **S-SAT-6** — router/`open_cbm`/plateau arithmetic unchanged by satisfied-closes (a closed-satisfied finding counts exactly as a closed-edited one).

Replay (captured-fixture, $0):

- **R-1** — the 46 captured run-030 refusals parse and route unchanged under the new parser (backward compatibility of the `refuse` path).
- **R-2** — run-030 ledger replay with the 19 phantom-class findings closed-satisfied (fixture outcomes per `rbt-71-categorization.json`) asserts the open decision-bearing set at the halt boundary = **33** (6 born + 27 genuine), not 52.

Live proving run (after unit + replay pass), bounded per §2: `max_passes = 3`, target ADR-008 — the decision-dense target is *matched to the question* (does the surface de-pollute on the document that polluted?). Success: the author's refusal stream splits into `close_satisfied` (phantom classes) vs `refuse` (genuine); open decision-bearing at halt ≈ born + genuinely-underdetermined; cold audit hand-validates a sample of satisfied-closes against the reconstructed pass states (no live defect closed). Expected ≈ 3-pass cost, well under run-030's.

---

## 7. Amendment set (files this spec touches)

| File | Change |
|---|---|
| `agent_loop/author.py` | `AuthorSatisfied` dataclass + parse + mechanical evidence verification + `author_satisfied` / `author_satisfied_evidence_fail` events; escalate fallback |
| `design/author.prompt.md` | Third action schema + quotable-evidence hard rule + bias extension |
| `design/antagonist-{LAA,SA,EA}.prompt.md`, `design/coherence-sweep.prompt.md` | Contract rule 9 (identical in all four); generation → 12 |
| `design/ledger-schema.md` | `resolution_note` satisfied variant + the two new action-log events documented |
| `design/mechanical-gates.md` | **No change** (stated explicitly; router untouched) |
| `run-supervision.protocol.md` | §2 spend-discipline insert (verbatim, ratified); §5 edit-region-overlap audit check; §5 docket-discipline surfacing line |
| `design-review-loop` SKILL (bedrock) | Triage section: docket-coalescing presentation shape |

Follow-ups named (never silent): D-1 bounded multi-edit (trigger-gated); D-2 same-region re-edit trigger (trigger-gated); mechanical admission check for rule-9 quotes (trigger-gated); gen-stamp hygiene rides the existing RBT-70 fast-follow.

*End of spec.*
