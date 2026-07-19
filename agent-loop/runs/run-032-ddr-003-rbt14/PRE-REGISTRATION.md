# run-032 — Pre-Registration (DDR-003 first real engagement)

| Field | Value |
|---|---|
| **Run** | `run-032-ddr-003-rbt14` |
| **Target** | DDR-003 — Feedback Loop Governance, PROPOSED v0.1.0 (RBT-14) |
| **Pre-run HEAD** | `e3d2bcd1343a004dfd7393e72d7d7ea45252e1a6` (develop; Merge PR #40) |
| **Prompt authority** | `agent-loop/design/rbt-14-run-032-prompt.md` (committed at pre-run HEAD) |
| **Calibration** | gen-12, all six prompts; zero intended instrument variables vs run-031 |
| **max_passes** | 4 |
| **Model / params** | claude-opus-4-8, max_tokens 8192 (as run-031) |
| **Author mode** | sandbox-apply dry mode (run-supervision §9); edits land only in `runs/run-032-ddr-003-rbt14/documents/` |

Lawful pre-registration per `run-supervision.protocol.md` §2 — committed criteria +
prompt at a pre-run HEAD. This file is the conventional carrier; the run-032 prompt
and the ratified deliberation record are its committed substrate.

---

## §2 spend-discipline gates (answered explicitly)

**1. Units before dollars.** The loop's mechanics are unit-proven (S-/T-suites;
S-SAT-1…6, R-1/R-2) and the instrument phase closed at run-031. This run answers only
what no suite or captured fixture can:
- (a) **fresh-document behavior** — finding volume, quality, and hat balance on a
  never-reviewed record;
- (b) **a real decision docket** — whether escalations are genuinely underdetermined
  decisions rather than re-litigations of ratified intent (the deliberation record is
  in substrate/design-intent; reviewers and arbiter can resolve against it);
- (c) **a first live natural CONVERGED** — now mechanically reachable; hoped for,
  never forced.

**2. Bound to the minimum passes.** `max_passes = 4`. A fresh document needs two full
review-fix-review cycles plus a confirming pass to reach a natural CONVERGED; 4 is the
minimum that can observe that outcome, and the bound forces a cheap honest disposition
if it halts instead. Not a high ceiling.

**3. Match the target to the question.** DDR-003 is the question: the loop's remaining
unknowns are answerable only by real work, and this record is the real work. It is
governance-dense but freshly authored and self-reviewed against the same substrate the
loop will hold it to — a plausible convergence candidate, unlike the decision-dense
stale fixtures.

**4. Mine captured fixtures first.** Done. run-030/031 taught everything the captured
folders could (phantom taxonomy, satisfied-close behavior, oscillation). No captured
run contains a fresh real document; this question spends or goes unanswered.

## Cost envelope (estimate, not measurement)

Substrate is roughly 2× run-031's (full canon set), with per-actor 1-hour prompt
caching live. At 3–4 passes expect roughly **$30–50**. Acknowledged before pass 1.
Abort on cost runaway per protocol §3e.

## Substrate (fresh, hash-pinned per §3 — no prior-run frozen substrate reused)

- `authorities/`: ADR-001 · ADR-002 · ADR-008 · DDR-001 · DDR-002 · DDR-004 · SDD-001
  (all from `docs/` at the pre-run HEAD) · ddr-template + author-decision-record SKILL
  (bedrock checkout).
- `design-intent/`: ddr-003-deliberation-record (ratified rulings — authoritative
  design intent) · triage-001-charter · sofia-vision (carried forward frozen).
- Per-file origin + SHA-256 recorded in `substrate/manifest.json`.

## Disposition rules (pre-committed)

- Report-and-STOP: raw results only. No success scoring, no docket grouping, no ticket
  writes, no commit — those are upstream (claude.ai cold audit + Tad's git).
- Abort only on protocol §3e / §9 triggers: parse-drop storm, volume swamp
  (>~50 admitted pass-1 findings on a fresh document), cost runaway, mechanical
  misbehavior, anchor-fail storm. No in-loop intervention otherwise.
- Author trust ramp holds: run-031's 1 reopen / 9 edits is not "boring," so canonical
  write-trust is not advanced this run — sandbox-apply only.
