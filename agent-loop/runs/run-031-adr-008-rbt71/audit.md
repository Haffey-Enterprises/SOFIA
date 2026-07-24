# Cold Audit — run-031-adr-008-rbt71

| Field | Value |
|---|---|
| **Document** | runs/run-031-adr-008-rbt71/audit.md |
| **Status** | AUTHORED — 2026-07-19 (claude.ai, cold, from the run folder; Code's RAW-RESULT not taken as authority — every figure independently recomputed) |
| **Run** | run-031-adr-008-rbt71 (RBT-71 proving run; `max_passes=3`, target pin `24461d3f`, HEAD `461ad0c`, gen-12) |
| **Method** | run-supervision.protocol.md §5, scored against `rbt-71-decision-surface.spec.md` §6 + the RBT-71 DoD. Documents state replay-reconstructed from pristine + the 9-edit emission stream — **byte-identical** to the captured end-state, so every per-close validation runs against the exact text at close time. |
| **Variables** | Two vs run-030, declared: author `close_satisfied` path; gen-12 reviewer rule 9. Substrate byte-identical to run-030 (hash-of-hashes verified); same pristine target pin. |

## 1. Executive result

run-031 ran 3 passes and halted **`HALT_DECISION: oscillation`** on a genuine single-finding recurrence — the loop's first **live** oscillation stamp, fired exactly as designed. No aborts, no storms, `ephemeral_5m = 0`, cost **$22.83** (recomputed from the llm_call stream; vs run-030's ~$32–33 for 4.5 passes).

**The decision surface is materially de-polluted.** Open decision-bearing at halt: **19** (18 escalated refusals + 1 authority-resolution miss; **0 arbiter-born**), against run-030's 52 (and ~38 at run-030's comparable pass-3 boundary). Of the 19, **16 are genuinely underdetermined**, 3 are the known already-ratified-intent residual (§4). Docket-grouped per the ratified triage discipline, the 19 records collapse to **~5 distinct decisions** — one of which is the same question the oscillation halt flags. Run-030's equivalent surface: 52 records, ~41% phantom. Run-031: 19 records, ~16% residual (3/19), zero of the dominant NOOP/STALE classes.

**Recommendation: promote `rbt-71-decision-surface.spec.md` PROPOSED v0.1.0 → ACCEPTED v1.0.0** (§6), with the n=1 floor and three named residuals recorded honestly.

## 2. Satisfied-close — the fix under proof (spec §6 live criteria)

**13 `author_satisfied`, 0 `author_satisfied_evidence_fail`** — every emitted close carried evidence that verified mechanically (independently re-verified in reconstruction: all `evidence_present` strings occur, all `evidence_absent` strings absent, at the exact close-time document state). Evidence kinds: both-fields and single-field forms observed; confidence 12× high, 1× medium.

**Hand-validation (all 13, not a sample): 13/13 genuinely satisfied — zero live defects closed.** 12 are clean duplicate-service closes: the claimed defect was real at raise and removed by a same- or prior-pass sibling edit (the Ruling-D Environment row ×3, Ruling-F §2.3 qualification ×2, Ruling-E/G §5.2/§7 families ×7 — precisely run-030's NOOP-SATISFIED class, which produced 11 phantom escalations there and produced **zero** here). 1 close (`561cdce9`, medium confidence) rests on an interpretive-but-natural reading (a §6 compliance check read as a forward obligation, not a present-tense claim) — defensible, logged here as the class to watch at the "satisfaction requires interpretation → refuse" boundary.

**The never-hides property held live:** no satisfied-closed finding was ever re-raised or reopened (`recurrence_count = 0` across all 13). The one reopen of the run (§3) was of an **edit**-closed finding — and the alarm designed as the satisfied-close's safety net fired loudly for it.

## 3. The oscillation halt — honest, unbundled, first live stamp

Finding `bbb0327c` (§2.4 provenance-survival commitment vs §5.3 retention-gap concession): classified resolvable → author edit (pass 2, medium confidence) → same-identity re-raise pass 3 → reopen, `recurrence_count = 1` → router halts `oscillation`, payload exactly one unbundled finding + one `proposed_escalation`. This is the reopen stream the author prompt's dry-mode note names as the trust signal ("an edit a later pass reopens smuggled something") surfacing precisely as designed — and it is the *same underlying question* as the 3-refusal already-ratified residual (§4), so the docket presents it as one flagged decision, not two items.

Note for the operator: run-031's target is the **stale sandbox fixture** (pin `24461d3f`), not canonical ADR-008 (ACCEPTED 1.0.0, different text). The run's content findings are fixture-relative machinery evidence; **no ADR-008 canon action follows from this docket.**

## 4. Refusal stream and the residual

18 refusals + 1 unresolved, all correctly escalated, grouping to ~5 decisions: §7/subject-name forward-reference family (5 — incl. the Ruling-G multi-locus tooling limit, deferred with trigger, behaving as accepted), Ruling-B/Supersedes relationship statement (5), **§2-enumeration vs §2.4 revalidation coherence (5 — a genuinely new family this run, fresh coverage not churn)**, provenance-survival timing (3), Ruling-D residual (1).

**Named residual 1 — already-ratified-intent refusals (3/19).** The provenance-timing findings cite RBT-59 Item 3 (ratified) yet refuse-escalate rather than close satisfied — the RELIT class from the run-030 taxonomy persisting. Root cause is honest: these claims fault a *judgment posture*, not a quotable text state, so the evidence-anchor contract correctly does not reach them. Disposition: accept at docket cost (one grouped line) and name a gen-13 candidate rule ("a finding whose asked decision is itself ratified design intent closes satisfied-by-authority") **only if** the class recurs across runs — under-govern until it hurts.

## 5. Reviewer stream under gen-12 (second variable)

Claims this run quote live document text verbatim throughout (spot-verified across the satisfied and refused sets — the rule-9 contract is visibly landing). Two observable shifts, both n=1: **0 born decision-bearing** (run-030: 6) — all 53 classifications resolvable/high, consistent with better-grounded claims giving the arbiter nameable authority; and the STALE class (raise-time-invalid findings) — **0 observed** (run-030: 3). Volumes stayed healthy (74 findings/3 passes vs 76/4.5; POSITIVE 22, within proportionality; hats balanced). No evidence gen-12 suppressed real coverage: a new legitimate finding family (§2-enumeration) appeared this run.

## 6. Scorecard vs spec §6 and the RBT-71 DoD

| Criterion | Result |
|---|---|
| Unit + replay gate (S-SAT-1…6, R-1/R-2) | **MET** pre-run (348 passed, 100% coverage; R-2: 52→33 mechanical) |
| Live: refusal stream splits satisfied vs refuse | **MET** — 13 satisfied / 18 refused / 0 evidence-fail |
| Live: no live defect satisfied-closed | **MET** — 13/13 hand-validated against reconstructed states |
| Live: halt surface ≈ genuinely-underdetermined (+ born) | **MET** — 19 vs 52; 16/19 genuine; 0 NOOP/STALE phantoms; residual 3/19 named |
| DoD: FP rate established | **MET** (design leg: 41%, all 46 validated) |
| DoD: satisfied-close exists, tested, never hides | **MET** — incl. live never-hides (0 satisfied-close reopens; reopen alarm proven live on an edit) |
| DoD: reviewer over-production addressed | **MET** — gen-12 landed; STALE class 0 this run (n=1) |
| DoD: proving run shows material de-pollution | **MET** — 52 → 19 records, ~10 → ~5 decisions, phantom 41% → ~16% residual |

## 7. Instrument findings (route per §8)

1. **PRE-REGISTRATION.md absent from the run folder.** The pre-registration is nonetheless discharged with unusual strength: the criteria (spec §6) and the §2 gate answers (proving-run prompt) were **committed at `461ad0c` before launch** — git history is the timestamped pre-registration. Recommend recording this in the protocol reading (a committed spec/prompt pair satisfies §2's pre-registration intent) rather than backfilling a file post-hoc.
2. **`unclassified = 22` at halt is not a defect** — all 22 are POSITIVEs, which the arbiter correctly never classifies. Worth one clarifying line in ledger-schema.md if it confuses a future audit.
3. **Event `pass: null` logging gap persists** (run-030 audit finding #4, unfixed) — pass attribution still inferred from `emission_path`. Same one-line fix candidate, still cheap, still unclaimed.
4. **Author preamble strips: 8** (gen-10 seam working; parser never needed beyond it). Transport retries: 2, within policy.

## 8. n=1 floor

One run, one document, two simultaneous variables (attributed by stream, not isolated by run — a deliberate §2-gated economy). The 0-born-decision-bearing and 0-STALE observations are single-run measurements; the satisfied-close never-hides property carries the S-SAT suite behind it, not just this run. The cold-audit watch continues on the next natural runs; no dedicated isolation run is recommended.
