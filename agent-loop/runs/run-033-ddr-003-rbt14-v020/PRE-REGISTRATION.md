# run-033 — Pre-Registration (DDR-003 v0.2.0 confirming review)

| Field | Value |
|---|---|
| **Run** | `run-033-ddr-003-rbt14-v020` |
| **Target** | DDR-003 — Feedback Loop Governance, PROPOSED v0.2.0 (RBT-14) |
| **Pre-run HEAD** | `ca410614a30919e39c25807550ccbb5e5499de73` (feature branch; run-032 close-out commit) |
| **Prompt authority** | `agent-loop/design/rbt-14-run-033-prompt.md` (committed at pre-run HEAD) |
| **Calibration** | gen-12, all six prompts |
| **max_passes** | 3 |
| **Model / params** | claude-opus-4-8, max_tokens 8192 (as run-032) |
| **Author mode** | sandbox-apply dry mode (§9); trust ramp not advanced |

Lawful pre-registration per `run-supervision.protocol.md` §2 — committed criteria +
prompt at a pre-run HEAD. The run-033 prompt, the DDR-003 deliberation record, and
`run-032-docket-rulings.md` are its committed substrate.

---

## §2 spend-discipline gates (answered explicitly)

**1. Units before dollars.** Answers the one question no suite or captured run can:
**does the loop reach a clean verdict on a document whose escalated decisions have
been ruled and whose rulings are in substrate** — the first-live-CONVERGED question
run-032 could not reach, now under its designed conditions (operator rulings
available to the arbiter as authority). Secondary: does the run-032 finding
population resolve against the rulings rather than re-escalate.

**2. Bound to the minimum passes.** `max_passes = 3`: pass 1 reviews the amended
record, pass 2 lets the author work any residue with a re-review, pass 3 confirms.
Expected outcomes: CONVERGED or a small honest docket — either is a disposition.

**3. Match the target to the question.** v0.2.0 is the question: a converge-believed
record with its decision surface ruled — the loop's designed operating point, never
yet observed.

**4. Mine captured fixtures first.** Done. run-032's folder answered everything it
could (the docket, the cold audit, the instrument findings). Whether the *ruled*
state converges is in no captured run.

## Cost envelope (four-line-item convention — ratified; rate correction noted)

The docket-ratified convention: report cost from **all four usage line items** —
uncached input, output, cache-write (1h premium), cache-read. Adopted in full; the
§3e cost-runaway watch tracks the four-line-item total, not the uncached subset.

**Rate note (flagged for the cold audit, not a deviation from the method).** The
prompt's ≈$50–75 expectation and the docket's "run-032 real cost ≈$69.7" figure are
computed at **legacy Opus rates ($15 input / $75 output / $30 1h-write / $1.50 read
per MTok)**. The model under test, `claude-opus-4-8`, lists at **$5 / $25 / $10 /
$0.50** (claude-api skill, authoritative, cached 2026-06-24). run-032's four-line-item
total at the correct rates was **$23.23** (breakdown carried all four items:
input $7.09 · output $1.51 · cache-write $8.84 · cache-read $5.78) — it did **not**
omit cache economics; the 3× gap is entirely the per-token rate. This run's cost will
be reported both ways for reconciliation. Expected four-line-item total at
`claude-opus-4-8` list prices: **≈$17–25** at 3 passes on this substrate shape
(slightly higher than run-032 — the added rulings file enlarges the cached substrate
prefix). Acknowledged before pass 1.

## Substrate (fresh, hash-pinned per §3 — run-032 recipe + one addition)

- `authorities/` (9, unchanged recipe): ADR-001 · ADR-002 · ADR-008 · DDR-001 ·
  DDR-002 · DDR-004 · SDD-001 (from `docs/` at pre-run HEAD) · ddr-template +
  author-decision-record SKILL (bedrock).
- `design-intent/` (4): ddr-003-deliberation-record · **run-032-docket-rulings (NEW
  — ratified rulings; arbiter/reviewers read as authoritative design intent)** ·
  triage-001-charter · sofia-vision (carried forward frozen).
- Per-file origin + SHA-256 in `substrate/manifest.json`.

## Disposition rules (pre-committed)

- Report-and-STOP: raw results only. **If CONVERGED, state it plainly — it would be
  the loop's first.** No success scoring, no docket grouping, no ticket writes, no
  commit — all upstream (claude.ai cold audit + Tad's git).
- Abort only on protocol §3e / §9 triggers, cost watch on the four-line-item total.
  No in-loop intervention otherwise.
