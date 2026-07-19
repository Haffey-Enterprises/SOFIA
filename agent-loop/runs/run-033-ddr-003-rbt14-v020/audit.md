# Cold Audit — run-033-ddr-003-rbt14-v020

| Field | Value |
|---|---|
| **Document** | runs/run-033-ddr-003-rbt14-v020/audit.md |
| **Status** | AUTHORED — 2026-07-19 (claude.ai, cold, from the run folder; every figure recomputed from `ledger.json` + `action-log.jsonl`) |
| **Run** | run-033-ddr-003-rbt14-v020 (confirming review of DDR-003 v0.2.0 with the run-032 docket rulings in substrate; `max_passes=3`, gen-12, author sandbox-apply dry mode) |
| **Method** | run-supervision.protocol.md §5; cross-ledger overlap analysis vs run-032 (token-Jaccard on locus+claim); scored against the committed PRE-REGISTRATION criteria |

## 1. Executive result

**`run_aborted — LoopBoundExceeded` at 3 passes: the primary question is answered in the negative, decisively.** No mechanical CONVERGED occurred, and the reason is now measured rather than guessed: `open_cbm` rose monotonically 17 → 27 → 39 with **zero reopens and zero oscillation** — reviewers surfaced genuinely new material faster than the author closed it. Cross-ledger analysis: of the 50 open decision-bearing findings at abort, **42 are genuinely new loci** (mean overlap with run-032 ≈ 0.17), 6 related, only **2 repeat-like**. This is third-draw excavation, not churn and not re-escalation. Combined with run-032 (and the four ADR-008 runs before it), the empirical shape is settled: **adversarial multi-hat review of a governance-dense record does not exhaust** — each pass is an independent draw from an unsaturated finding distribution, and arrival (~15–20 MATERIAL/pass) exceeds close rate (~10/pass) indefinitely. The protocol's own §2 gate 3 predicted this ("decision-dense records never exhaust"). **Consequence, ruled by the operator this session: for dense records the loop's terminal state is ratified acceptance with review of record (the ADR-008 Path-A precedent); mechanical CONVERGED remains a small-target outcome** unless reviewer-side delta-mode is ever built (trigger-gated future work, not commissioned).

## 2. The rulings-as-authority contract — validated live

**All 9 `author_satisfied` closes cite the run-032 docket rulings or their upstream authority by name** ("run-032 docket ruling D1/D4/D5/D8-adjacent…", ADR-008 §2.2 direct) — every re-ask of a ruled decision resolved satisfied-by-authority, exactly the contract the run-025 rulings file established and run-028 first exercised. Satisfied volume nearly doubled vs run-032 (9 vs 5) with the rulings available; 1 evidence-fail correctly blocked. This is the strongest evidence yet for the operator's target operating model (rulings → author → re-run): **the ruling cycle works; non-convergence is reviewer generativity, not ruling failure.**

## 3. Streams

Health: 0 retries, 0 drops, 0 reopens, 0 anchor-fails, 1 benign preamble-strip; `ephemeral_5m = 0` (857k cache-creation tokens all 1-hour bucket). Ledger recomputed: 80 findings (48 M / 14 C / 18 P); classifications 35 resolvable / 27 decision-bearing as-issued, 62 high / 7 medium / 0 low — conservative bias held; hats balanced (coherence 23 / LAA 21 / SA 21 / EA 15); POSITIVE 18/80 ≈ 22%, proportional. Author: 3 edits + 9 satisfied vs 20 refused (9 of the "authority does not uniquely determine the fix" species — same wording-underdetermination class as run-032, no RELIT). **No decision docket was emitted by the runner** — `LoopBoundExceeded` bypasses the HALT_DECISION escalation path, so the 50 open decision-bearing stood unescalated in the ledger; the docket was produced by audit-time extraction + coalescing (§4). *Instrument note:* a loop-bound abort leaving counted decisions unescalated is worth one protocol line — audit-time extraction is the sanctioned recovery, as exercised here.

## 4. Docket and disposition

The 50 coalesced to **eleven decisions (E1–E11)**, all wording-precision or basis-cite, zero design reopens — ratified per item by the operator 2026-07-19 (carrier: `agent-loop/deliberation/ddr-003-feedback-loop-governance/run-033-docket-rulings.md`) and realized as DDR-003 v0.3.0. **Diminishing-returns curve, now measured:** run-032's docket carried nine decisions including genuine design-tension items; run-033's eleven are uniformly finer-grained wording items. A third run would purchase a fourth-draw docket of still-finer nits at ~$23; declined under §2 gate 4. Acceptance proceeded on the reviewed-and-ratified basis (v1.0.0 change-log row).

## 5. Cost — and a correction to the run-032 audit

Four-line-item recompute at `claude-opus-4-8` list rates ($5/$25/$10/$0.50 per M): **$23.08** (input $7.06 · output $1.62 · cache-write $8.57 · cache-read $5.83). Within envelope. **Correction (registry pattern):** the run-032 audit §6 computed $69.7 using legacy Opus rates and declared an envelope breach — wrong; at the model's actual list rates run-032 recomputes to **≈$23.2**, inside its envelope. The correction is logged in that audit's addendum. What survives of the finding: the four-line-item reporting convention (honored by this run's RAW-RESULT), and the cost-structure observation (arbiter/author cache-read volume as the dominant line) for the cost-architecture workstream.

## 6. Empirical floor

n=2 real-target runs on one record; the non-exhaustion conclusion additionally rests on the four ADR-008 runs (n=6 dense-record runs, zero mechanical convergences). The rulings-as-authority validation is n=9 satisfied closes in one run. Stated; no isolation run recommended — the record is landing on the ratified basis and the next natural runs are other records' reviews.
