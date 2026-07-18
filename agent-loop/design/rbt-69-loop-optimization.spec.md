# File: agent-loop/design/rbt-69-loop-optimization.spec.md
# Author: Thaddeus Haffey (Executive Architect), authored on claude.ai
# Created: 2026-07-18
# Description: Design spec for three ratified refinements to the design-review-loop
#   machinery — cross-pass finding-identity, reviewer-substrate caching, and
#   clean-stop — with the correctness invariants each demands.

| Field | Value |
|---|---|
| **Document** | rbt-69-loop-optimization.spec.md |
| **Doctype** | Construct-local design spec (ruled via `author-decision-record` gate: not ADR/DDR/SDD — see below) |
| **Status** | PROPOSED v0.1.0 |
| **Date** | 2026-07-18 |
| **Ticket** | RBT-69 |
| **Author** | Thaddeus Haffey (Executive Architect), authored on claude.ai |
| **Amends** | `ledger-schema.md` (§Identity); `mechanical-gates.md` (§2 oscillation / §3 router); `transport.py` caching (RBT-49, previously uncontracted — this spec gives it a contract section) |
| **Companions** | run-prep.contract.md; runner-real-hats.contract.md; ledger-schema.md; mechanical-gates.md |
| **Empirical driver** | run-028-adr-008 (halted `HALT_DECISION:oscillation` at pass 4); run-025/026 (clean single-pass decision halts) |

**Doctype ruling.** Ruled via the `author-decision-record` gate. Not an ADR (deleting every service would not preserve it — it constrains one construct, not the platform across services). Not a DDR (constrains neither multiple services nor the platform data model — only the runner's internals). Not an SDD (not a whole-service design; three targeted amendments to a construct that already carries its design in construct-local contracts). It is a construct-local design spec in the genre of `mechanical-gates.md` / `ledger-schema.md`, matching how RBT-49/54/67 captured comparable machinery refinements. The empirical deliberation basis is folded into each piece's Rationale rather than split to a separate deliberation record.

**Design authority.** This surface (claude.ai) authors this spec; Claude Code implements it — applying the amendment language below to the named sibling contracts and writing the code and tests. Git transactions are Tad's. On any divergence between this spec and the implemented code, this spec and the amended contracts are authority (design over code).

---

## Purpose and scope

Three performance-and-honesty refinements to the design-review-loop runner (`$SOFIA_ROOT/agent-loop/`), deliberated to per-item ratification under RBT-69:

1. **Cross-pass finding-identity** — a stable identity for "the same finding" across passes that is robust to surface-text mutation, so re-emissions collapse instead of inflating the open set, while genuinely-distinct findings never merge.
2. **Reviewer-substrate caching** — the frozen per-run substrate cached per actor across the run instead of re-sent full-price every pass.
3. **Clean-stop** — an honest terminal disposition for a non-converging run, split out of the "oscillation" label it is currently mislabeled under.

**Hard invariants preserved (ratified under HEB-58 / RBT-67, not re-opened here).** The execute-vs-reason bright line (the gate is executed against `agent_loop/`, never reasoned by the model); no LLM on the "done" decision (`CONVERGED` stays the mechanical conjunction `open_cbm == 0 ∧ no open decision-bearing ∧ not oscillating`); cost-down may never be coverage-down (every finding the un-optimized loop surfaces must still surface). Pieces 1 and 2 are performance changes carrying a hard coverage-preservation obligation; piece 3 is a disposition-honesty change that terminates strictly earlier-or-equal, never later, and never converts a real finding into silence.

**Empirical floor.** The driver is run-028, a single run on a single document (ADR-008). Where a claim rests on that one run, it is marked n=1 and its constant is held contested; the *form* of each fix is defensible from first principles and is what this spec fixes now.

---

## Piece 1 — Cross-pass finding-identity (the crux)

### Decision

Finding identity is derived from **`(sorted(target), normalize_locus(locus), altitude)`** — the claim text is **removed** from the identity hash and retained on the record. A **claim-divergence guard** captures, without discarding, a materially-different claim that admits to an existing open identity.

### Rationale (empirical- and first-principles-grounded)

The prior key `hash(target + locus + normalize_claim(claim))` is too fine along the claim axis. In run-028 the EA hat re-emitted substantively the same §2.3 finding in passes 1, 2, 3, and 4 — locus byte-stable, claim reworded each pass — and because the claim text is in the hash, each rewording minted a fresh id and was admitted as net-new. The same defect was counted four times. This is the dominant driver of run-028's monotonic `open_cbm` climb (18 → 24 → 41 → 55 with zero recurrences): identity-failure inflation, not net-new coverage.

The obvious coarsening — keying on locus alone — is forbidden: the §2.3 locus legitimately carries four *distinct* findings (LAA claim-fidelity, SA conformance, EA reversibility, coherence cross-reference). Merging them by locus would hide three real findings, the exact coverage regression the hard invariant forbids. Adding **altitude** to the key threads the needle: a hat's re-emission of its own finding is stable under wording drift (same target+locus+altitude), while two distinct-stance findings at one locus stay separate (different altitude). The discriminator moves from the brittle claim sentence to the stable stance-at-locus.

The change must stay mechanical — identity is a deterministic function, not an LLM judgment (execute-vs-reason bright line). No semantic-similarity or embedding step: those are non-deterministic and would reintroduce a reasoned identity.

**Empirical support and its floor.** Over run-028, `(target, locus, altitude)` collapses 78 fine-key defect ids to 69 groups, and there were **zero** cases of a single hat raising two distinct findings at one identical `(target, locus, altitude)` in one pass — i.e. the coarser key would not have merged any two real findings on this run. This is **n=1**. The claim "a single hat never raises two distinct findings at one identical locus" is an observation, not a theorem, and its failure mode is a silent merge of two real findings — the regression we are most obligated to prevent. The zero-collision result is therefore a **held threshold-override, watched by the cold audit, not a settled constant.** The claim-divergence guard is the safety net for the residual.

### Amendments

**`ledger-schema.md` §Identity — replace the identity rule.**

- Identity is derived at first emission from `(sorted(target), normalize_locus(locus), altitude)` and preserved thereafter. `altitude` enters the key; `claim` leaves it.
- `normalize_locus` is a new deterministic normalizer analogous to `normalize_claim`: lowercase, strip markdown/punctuation/quoting noise, collapse whitespace. It does **not** semantically alter the locus (quoted section anchors are preserved) — it only absorbs formatting drift. Kept conservative because over-normalizing a locus risks merging distinct loci.
- `claim` remains a mandatory record field (unchanged), now purely descriptive, no longer identity-bearing.
- **Counting-semantics note (ratified as a feature).** Because altitude is now in the key, two hats raising the *identical* claim at one locus no longer dedup to one record — they are two records at two altitudes. This preserves cross-hat overlap as the roster-independence evidence the run protocol measures (run-supervision §5.3, §7), which the prior claim-only key destroyed by deduping. It also means a defect independently found by two altitudes counts twice toward `open_cbm`; this is intended and is not double-counting of the *same* finding (distinct altitude = distinct instrument's finding).

**`identity.py` — signature and body.**

- `derive_id(target, locus, altitude)` replaces `derive_id(target, locus, claim)`. `normalize_claim` is retained (now used only by the divergence guard, below), and `normalize_locus` is added.
- Admission reads `finding.altitude` (already stamped from the invoked reviewer's identity at the parse seam before admission — `real_hats.parse_emissions`) to derive the id.

**`admission.py` — the claim-divergence guard.**

- On the `dedup_open` path (an incoming emission matches an already-open id): if `normalize_claim(incoming.claim) != normalize_claim(existing.claim)`, the finding stays open (nothing hidden), the incoming claim is appended to a new `claim_variants: list[str]` field on the existing finding, and a `claim_divergence` action-log event is emitted (`finding_id`, `existing_claim`, `incoming_claim`). No new record is created; no claim is discarded.
- Rationale: the only residual risk of the coarser key is two distinct findings sharing one `(target, locus, altitude)`. The guard guarantees the loop's safety property exactly — *a live finding is never hidden; it stays open, surfaces, and carries every divergent claim variant* — and routes the sole residual risk (under-counting two-as-one) to the cold hand-audit (run-supervision §5), which is equipped to split it. This respects "under-govern until it hurts": no similarity apparatus, just never throw the variant away.

### Correctness invariant

Carry-forward/suppression can never hide a finding that is still live, and can never silently merge two distinct findings without preserving both claims for audit.

### Required tests (BLOCKING before push)

- **T1 — surface-mutation dedup.** Same `(target, locus, altitude)`, claim reworded across passes → same id → `dedup_open`, no new record, no `open_cbm` inflation. (The run-028 EA/§2.3 case.)
- **T2 — distinct-finding non-merge (the adversarial test).** Two genuinely distinct findings at one identical `(target, locus, altitude)`, materially different claims → the divergence guard fires: `claim_divergence` logged, both claims retained (`claim` + `claim_variants`), the finding stays open. Prove neither claim is discarded and both are recoverable from the ledger.
- **T3 — cross-altitude non-dedup.** Identical claim, identical locus, different altitude → two distinct ids (overlap evidence preserved).
- **T4 — oscillation survives the key change.** Close a finding, then re-emit the same `(target, locus, altitude)` with reworded claim → recognized as the same id → reopen + `recurrence_count += 1`. (This is a *strengthening*: the prior claim-key would have missed this reopen; the new key catches it. The bad-fix catch must be proven intact.)
- **T5 — normalize_locus stability.** Formatting-only locus drift collapses to one id; a genuinely different locus does not.

---

## Piece 2 — Reviewer-substrate caching

### Decision

The frozen per-run substrate is made a **cacheable leading prefix for each actor** (each hat, the arbiter, and the author's stable inputs), using an explicit **1-hour cache TTL** so the cache survives the multi-minute gaps between passes. Caching is content-neutral by construction. A single shared cross-actor substrate prefix is **out of scope** (deferred).

### Rationale (empirical- and first-principles-grounded)

In run-028 the hats' system block is already marked cacheable, yet per-site `cache_read ≈ 0` (LAA 2,564; SA/EA/coherence 0) against ~150k substrate re-sent every pass. Cause: passes run ~5.7 min apart (1370s / 4 passes) and the default ephemeral cache TTL is 5 minutes, so the cache expires *between* passes. The arbiter escapes this only because its many per-finding calls land back-to-back inside one pass (run-028 arbiter `cache_read` 11.4M) — its across-findings prefix reuse fits inside the 5-minute window; the hats, running once per pass, get no within-window reuse to catch.

Two design facts follow. First, the enabling lever is the **1-hour TTL**, not the reorder alone: without it, a per-hat substrate prefix still expires before the next pass and buys almost nothing. Second, literal cross-hat sharing (one cache entry read by all four hats) is architecturally blocked — prompt caching matches an exact prefix from the start of the request, and each hat's stance-bearing `## System` (pinned verbatim by run-prep §5) diverges the prefix before the substrate block is reached. Hoisting substrate ahead of every actor's stance to force one shared entry would trade the verbatim-system contract and stance clarity to save ~5 one-time cache writes across a run — not worth it. The ratified target is therefore **once per actor per run**, not once per run; the residual (~6 writes vs 1) is deferred as an ambition, not pursued here.

Content-neutrality makes the two guarded invariants — the arbiter's frozen-substrate authority-independence (run-prep §6) and the hats' stance-isolation — safe by construction, not by test luck: both are properties of *what each context contains*, and caching provably does not alter content.

### Amendments

**`transport.py` / `real_hats.assemble_user_prompt` — hat substrate as cache prefix.**

- Reorder the hat `## User` assembly to lead with the frozen substrate: `SUBSTRATE → DOCUMENT SET → LEDGER SNAPSHOT → recency directive` (was `DOCUMENT SET → SUBSTRATE → …`). This mirrors the arbiter's existing Ra-2 reorder (`_assemble_arbiter_substrate` before the finding).
- The hat transport call passes the leading substrate block as `cache_prefix`. Per the existing `_user_content_blocks` construction, the cached head is **sliced from the call's own assembled `user` string** — so the bytes the model receives are byte-identical to the uncached assembly regardless of the prefix. This is the content-neutrality guarantee and it is not to be weakened (never hand-build a substrate string that could diverge from what is sent).

**Cache TTL — 1 hour for run-frozen blocks.**

- The substrate block and the system block (both stable across a run for a given actor) are marked with the 1-hour cache TTL; the arbiter's substrate prefix is likewise raised to 1 hour to harden it against a high-finding-count pass whose classifications span past 5 minutes. The morphing surface — the document set (author-mutated in live mode) and the growing per-pass ledger snapshot — is **never** cached; it stays the uncached tail. (Claude Code verifies the exact Anthropic API mechanism/header for the 1-hour TTL at implementation; the design intent is a run-length cache window.)
- Cost trade, stated honestly: a 1-hour cache write is priced above a 5-minute write; reads are equally cheap. Net-positive whenever substrate is re-read across ≥2 passes (the expensive multi-pass runs), mildly wasteful on a single-pass run (which is cheap regardless).

**Author stable-input caching (same rule).**

- The author (`LlmAuthor`) re-sends the run document(s) and resolved authority per finding — the single largest input sink in run-028 (2.12M input tokens, 59 calls). Its stable per-run inputs (the run document text, and any authority text shared across findings) are brought under the same content-neutral leading-prefix + 1-hour-TTL rule. The per-finding-variable portion (the specific resolved authority for that finding) stays the uncached tail. Exact split is Code's to determine against the current `_assemble_author_user` layout; the rule is the same content-neutrality guarantee.

### Correctness invariant

What each actor sees is provably the frozen per-run substrate set, byte-identical to the uncached path; no stale or cross-run bleed.

### Required tests (BLOCKING before push)

- **C1 — byte-identity.** For every call site (hats, arbiter, author), the reconstructed sent content (head + tail cache blocks) equals the single-block uncached assembly byte-for-byte, for an arbitrary `cache_prefix`.
- **C2 — cross-run isolation.** Two runs with different substrate produce different leading-prefix bytes; assert the prefixes differ whenever substrate differs (content-addressed keying makes cross-run reuse of a genuinely-different substrate impossible; a hit on identical bytes is correct by construction and is not bleed).
- **C3 — empirical (supervised-run acceptance, not a unit test).** A multi-pass supervised run shows hat-site `cache_read > 0` on passes 2+, where run-028 showed ≈ 0, and per-site token totals drop accordingly. Recorded from the manifest's existing `cache_creation`/`cache_read` split (RBT-49 §4).

---

## Piece 3 — Clean-stop

### Decision

The **non-recurrence plateau** is split out of the `oscillation` disposition into its own honest terminal exit, **`HALT_DECISION:non-convergence`**, whose payload surfaces the open decision-bearing findings the operator must rule (unbundled), plus a context line that the resolvable surface was not exhausted. No new ledger status is added; the existing author `_escalate` path (resolvable → decision-bearing, status open) remains the mechanism for a structurally-unfixable resolvable.

### Rationale (empirical- and first-principles-grounded)

The kickoff framed clean-stop as "structural-unfixable resolvables churning to max_passes." The empirical record refutes that mechanism: run-028 shows **zero recurrences** and a **monotonic `open_cbm` climb** (18 → 24 → 41 → 55), with 108 findings, 7 closed, 54 classified decision-bearing. The loop did not churn on the author trading with a hat over an unfixable resolvable — `author.py` already escalates such a resolvable to decision-bearing on refuse/anchor-fail/unresolved. It churned because the hats surfaced net-new findings every pass faster than the author closed them, while a decision-bearing backlog that dry mode never drains accumulated — and then the **plateau** detector fired and *mislabeled* the result `oscillation`.

That mislabel is the defect. `mechanical-gates.md` folds two genuinely different conditions into one exit: **recurrence** (a closed finding reopened — real two-altitude trading) and **plateau** (`open_cbm` stops strictly decreasing while positive — accumulation, no trade). Calling accumulation "oscillation" tells the operator two altitudes are fighting when the truth is "there is a pile of decisions to rule and the surface is not exhausted." The honest fix separates the two and gives each its true disposition and payload.

The already-built escalate-to-decision-bearing transition is confirmed as the correct and sufficient mechanism for the unfixable-resolvable case; it correctly refused `status="escalated"` precisely because that would drop the finding out of `open_cbm` (false progress) and out of the router's open-only view (a silent drop of a discovered decision). Piece 3 adds **no** status and does not touch that path.

**Interlock.** The plateau signal is only *meaningful* after Piece 1. Before the identity fix, `open_cbm` climbed on re-wording inflation and the plateau fired on noise; after it, "`open_cbm` not decreasing" genuinely means real net-new findings are still accumulating or the author is making no net progress — a true non-convergence signal worth halting on. Piece 2 makes the passes leading to that detection cheap, so a 4-pass non-convergence detection is a cheap, honest "operator, come rule these," not an expensive churn.

### Amendments

**`mechanical-gates.md` §2 and §3 / `gates.py` — split the disposition.**

- Retain `recurrence(ledger)` and `plateau(ledger)` as defined. Retain `oscillating = recurrence or plateau` only as an internal predicate for the top-precedence backstop position; the **router disposition** it produces is now split:
  - `recurrence(ledger)` → `HALT_DECISION(reason="oscillation", payload=recurring findings)`. Unchanged.
  - `plateau(ledger) and not recurrence(ledger)` → `HALT_DECISION(reason="non-convergence", payload=…)`.
- **Non-convergence payload.** The open decision-bearing findings, surfaced unbundled, one escalation each (the operator's actionable), **plus** a single context line recording that the resolvable surface was not exhausted (net-new still arriving) and the plateaued `open_cbm` value. If there are no open decision-bearing findings at the plateau (pure resolvable non-progress), the payload falls back to the plateaued open counted findings with the same context line.
- **Precedence unchanged.** The backstop still outranks everything: `[recurrence-oscillation | non-convergence-plateau] → open-resolvable (CONTINUE) → decision-bearing (HALT) → CONVERGED`. RBT-67's rule (an open resolvable outranks the *static* decision-halt, so one COSMETIC decision cannot starve the author) is untouched. The only change is that a non-decreasing open set now halts honestly instead of masquerading as oscillation.

**No change to** `author.py`'s `_escalate` (resolvable → decision-bearing, status open) or to any ledger status enum.

### Correctness invariant

The loop terminates with an honest disposition: recurrence halts as oscillation; accumulation halts as non-convergence carrying the decisions to rule; a run whose only remainder is decision-bearing-or-escalated reaches a clean stop, and the change never terminates later than today and never converts a real finding into silence.

### Required tests (BLOCKING before push)

- **S1 — recurrence still oscillation.** Reopen a finding → `HALT_DECISION:oscillation`, payload = recurring findings.
- **S2 — accumulation is non-convergence (run-028 replay).** Feed the run-028 finding/pass trajectory → assert `HALT_DECISION:non-convergence`, payload = open decision-bearing unbundled + context line — not `oscillation`.
- **S3 — clean decision halt unchanged.** Resolvables exhausted, decisions open, no plateau → `HALT_DECISION:decision-bearing` (the run-025/026 regression).
- **S4 — CONVERGED unchanged.** `open_cbm == 0 ∧ no open decision-bearing ∧ not oscillating/non-converging`.
- **S5 — escalate path regression.** Author refuses a resolvable → decision-bearing, status open → surfaces at the decision-bearing halt or in the non-convergence payload; never dropped, never `status="escalated"`.

---

## Consolidated test obligations

- The finding-identity suite (T1–T5) and the cache-provenance suite (C1–C2) are **BLOCKING before any push** (operator rider, RBT-69). C3 and the S2 run-028 replay are supervised-run / integration acceptance criteria.
- The existing coverage bar holds: 100% line + branch on `agent_loop` (run-prep §10j). Every new branch — the divergence guard, the reordered cache path, the split disposition — is covered.
- The stub path and the S1–S4 / S2b / S3b dummy scenarios stay green (runner-real-hats §9g); the three dummy scenarios that assert oscillation/plateau behavior are updated only where the disposition label legitimately changed (plateau-without-recurrence → non-convergence), and that change is itself asserted.

## Out of scope / deferred

- **Single shared cross-actor substrate prefix** (one cache write per run rather than one per actor) — the "ultimately" ambition. Requires hoisting substrate ahead of every actor's stance/system, trading the run-prep §5 verbatim-system contract and stance clarity for ~5 one-time writes per run. Logged, not pursued.
- **`design-review-loop` SKILL reference sync** — `references/convergence-machinery.md` (the three-exits summary gains `non-convergence`) and `references/reviewer-instrument.md` / `ledger-schema` §Identity mirror need a downstream sync once these land. Small: the skill points at the machinery rather than mirroring it. Named as a follow-up, not folded into RBT-69.
- **Early decision-surfacing trigger for unattended/live mode** (halt the moment the decision backlog grows, before resolvables exhaust). Not built: live mode is gated far out on the classifier earning trust, and the attended operator watching the stream (run-supervision §4) is the real-time backstop. Under-govern until it hurts.

## Cross-references

- `mechanical-gates.md` — the router/oscillation machinery this spec splits (Piece 3).
- `ledger-schema.md` — §Identity, the key this spec re-composes (Piece 1).
- `run-prep.contract.md` — §5 (verbatim system), §6 (arbiter authority-independence), §7 (per-site cache token capture) that Piece 2 preserves and relies on.
- `run-supervision.protocol.md` — §5 cold audit (the home of the claim-divergence and non-convergence review streams).
- run-028-adr-008 — the empirical driver (ledger + manifest).
- RBT-49 (prompt caching, arbiter substrate prefix); RBT-67 (router precedence reorder, author escalate path) — the prior refinements this spec builds on.

## Change Log

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-18 | Initial draft. Three RBT-69 pieces ratified per-item by Tad (identity, caching, clean-stop); doctype ruled construct-local design spec; empirical basis run-028. PROPOSED pending the test suites above going green. |
