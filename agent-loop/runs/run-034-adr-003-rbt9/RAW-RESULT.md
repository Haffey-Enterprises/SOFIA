# run-034 — RAW-RESULT (ADR-003 Platform Patterns, RBT-9)

Raw capture only. No success scoring, no docket grouping, no convergence ruling,
no audit — all upstream (claude.ai cold audit + Tad's git). Report-and-STOP.

| Field | Value |
|---|---|
| **Run** | `run-034-adr-003-rbt9` |
| **Target** | ADR-003 — Platform Patterns, PROPOSED v0.1.0 |
| **Pre-registration carrier** | `3c823fa` (three artifacts; docs/ byte-identical to launch HEAD) |
| **Manifest HEAD** | `d7eb329` (prep-layer instrument fix, RBT-9; docs/ unchanged vs 3c823fa) |
| **Document snapshot sha256** | `9120d921…86f0f486d` (gate-8 verified) |
| **Calibration** | gen-12, all six prompts |
| **max_passes** | 3 (operator-ruled) |
| **Model / params** | claude-opus-4-8, max_tokens 8192 |
| **Author mode** | sandbox-apply dry (§9); trust ramp NOT advanced |
| **Router exit** | **HALT_DECISION:oscillation** — pass 3 |
| **Wall-clock** | 923 s (15.4 min) |

## Prep-layer note (for the cold audit)

The run did not launch as the prompt literally specified. The `adr` recipe forces
`--from-run` (to carry the non-re-fetchable Notion `sofia-vision` block), and the
`--from-run` act-(c) pin asserted every overlapping logical_id — including repo
authorities taken fresh at HEAD — against run-033's snapshot. Five authorities
(ADR-001, ADR-008, DDR-001, DDR-002, SDD-001) drifted at commit `0058246`
(DDR-003→ACCEPTED corpus pointer resolution) between run-033's HEAD and the
pre-run HEAD, so prep failed loud. Operator-ratified fix (RBT-9, 2026-07-20,
ratify-then-implement; commit `d7eb329`): scope the act-(c) pin to `carry_forward`
specs only; repo specs are taken fresh (integrity = git + gate 8 + source-survival
assert). Full suite green, 100% line+branch. **This is a prep-layer change only —
no reviewer/arbiter/author/gate/prompt behavior touched.** Substrate then assembled
exactly to the prompt recipe: 10 authorities (ADR-001/002/008 · DDR-001/002/003/004
· SDD-001 · adr-template · author-decision-record-SKILL) + 3 design-intent
(adr-003-deliberation-record · triage-001-charter · sofia-vision carried unchanged
from run-033). The five drifted authorities verified byte-fresh at the pre-run HEAD.

## Per-pass admitted volumes

| Pass | Admitted | POSITIVE | Non-POSITIVE |
|---|---|---|---|
| 1 | 24 | 8 | 16 |
| 2 | 28 | 8 | 20 |
| 3 | 12 | 1 | 11 |
| **total** | **64** | **17** | **47** |

Pass-1 admitted (24) well under the §3e volume-swamp guideline (~50).

## Per-hat finding volumes (whole run, ledger `altitude`)

| Hat | Findings | POSITIVE |
|---|---|---|
| SA | 17 | 4 |
| cross-set (coherence) | 17 | 5 |
| EA | 16 | 4 |
| LAA | 14 | 4 |

POSITIVE share 17/64 ≈ 27% overall; per-pass POSITIVE ran 8/24, 8/28, 1/12
(pass-1/2 near §3d's ~⅓ soft-alarm line — noted, not acted on).

## Arbiter classification (48 calls across passes)

- **Split:** 29 decision-bearing / 19 resolvable.
- **Confidence:** 44 high · 4 medium · **0 low**.

## Author dispositions (dry sandbox-apply; two fix cycles between review passes)

| Fix cycle | author_edit | author_satisfied | author_satisfied_evidence_fail | author_refused |
|---|---|---|---|---|
| after pass 1 | 3 | 1 | 0 | 3 |
| after pass 2 | 4 | 0 | 0 | 3 |
| **total** | **7** | **1** | **0** | **6** |

7 edits applied to `runs/run-034-adr-003-rbt9/documents/ADR-003-*.md` only
(ledger `doc_changes` = 7); no canonical write, no ticket write, no network write.

## open_cbm trajectory

`pass1 continue → 11` · `pass2 continue → 25` · `pass3 → halt (oscillation)`.

## State at halt

- **Status:** 57 open · 7 closed (of 64).
- **Open decision-bearing (non-POSITIVE): 36.** Open resolvable: 4. Open POSITIVE: 17.
- **Router disposition:** HALT_DECISION on **oscillation**. Recurring finding
  (the halt payload / proposed escalation): **`efac49fd2de6ccde`** (SA,
  `recurrence_count = 1`, open) — one finding closed then reopened; the loop's own
  halt surfaced it to the operator. One `proposed_escalation` emitted
  (finding `efac49fd2de6ccde`; ticket proposed, not opened).
- The 36 open decision-bearing findings are surfaced raw here, ungrouped
  (docket coalescing is the upstream audit's act, not this capture's).

## Operational-health stream (§3 watches)

- **parse_dropped:** 1 (antagonist-LAA pass-1, malformed `cited_authority`) — single, no storm.
- **llm_retry:** 1 (antagonist-LAA pass-1 `reviewer_redraw`, below the 2-POSITIVE floor) — contracted gen-8 R-E1 redraw, not a transport failure.
- No `author_satisfied_evidence_fail`, no anchor-fail, no `run_aborted`, no transport retry.

## Cost — four line items (claude-opus-4-8 list: $5 / $25 / $10 / $0.50 per MTok)

| Line item | Tokens | Cost |
|---|---|---|
| Uncached input | 952,076 | $4.76 |
| Output | 61,587 | $1.54 |
| Cache-write (1h) | 950,103 | $9.50 |
| Cache-read | 9,892,494 | $4.95 |
| **Four-item total** | | **$20.75** |

0.90× the ~$23 envelope. All cache-creation landed in the 1h TTL bucket
(`ephemeral_1h` = `cache_creation`, `ephemeral_5m` = 0) — §7a C3 structural proof
the 1-hour TTL applied. Per-site cost: arbiter $6.21 (48 calls, 8.19M cache-read) ·
author $3.67 (554.9k uncached input — per-finding tails, uncached by design) ·
LAA $2.85 · coherence $2.70 · SA $2.68 · EA $2.64.

## Zero intended instrument variables vs run-033

gen-12, six prompts, same model/params/transport, dry sandbox-apply. Anything
observed is document-driven. (The prep-layer fix above is not a loop-instrument
variable — it changed which bytes prep admits, not how any reviewer/arbiter/author
/gate behaves.)
