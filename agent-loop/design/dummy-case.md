# Dummy Case — Acceptance Fixture

Four minimal scenarios. Each isolates **one** gate path and states its expected
router exit as an assertion. Documents are abstract stand-ins (`DOC-A`, `DOC-B`) —
the skeleton proves plumbing, not SOFIA review, so it deliberately does not touch the
real ADR/DDR set. Authorities are abstract too (`AUTH-1`, `AUTH-2`, `DI-1`).

`counted_severities = {BLOCKING, MATERIAL}`, `plateau_N = 3`, `mode = dry`.

---

## S1 — Happy path → CONVERGED

Proves: counter, resolvable→close→count-decrease, coherence-rerun-on-change, and the
CONVERGED conjunction.

Planted:
- `P1` antagonist · MATERIAL · DOC-A · cites `AUTH-1` → **resolvable**.
- `P3` coherence · MATERIAL · DOC-A×DOC-B · cites `AUTH-2` → **resolvable**, but the
  coherence stub withholds it until the author records the DOC-A change from fixing P1.

Expected:
- Pass 1: admit `P1`. arbiter → `resolvable`. `open_cbm = 1`. router → **CONTINUE**.
  Author closes `P1` (proposed), records DOC-A change.
- Pass 2: coherence stub now emits `P3` (DOC-A changed). arbiter → `resolvable`.
  `open_cbm = 1`. router → **CONTINUE**. Author closes `P3`.
- Pass 3: no open findings. `open_cbm = 0`, no decision-bearing, not oscillating.
  router → **CONVERGED**. ✅

Assert: converges in 3 passes; final `open_cbm == 0`; `P3` never appeared before
pass 2.

---

## S2 — Decision-bearing → HALT_DECISION

Proves: arbiter classification, decision exit, unbundled surfacing.

Planted:
- `P2` antagonist · BLOCKING · DOC-A · cites design-intent `DI-1`, where `DI-1` is
  **silent** on the fork the finding exposes → **decision-bearing**.

Expected:
- Pass 1: admit `P2`. arbiter → `decision-bearing` (authority silent on the fork).
  router → **HALT_DECISION** (reason `decision-bearing`, payload `[P2]`). ✅

Assert: halts on pass 1; exactly one escalation proposed; loop does not attempt a
fix on `P2`.

Variant S2b (severity-independence): re-run with `P2` at `COSMETIC`. `open_cbm == 0`,
but router must **still** → HALT_DECISION on the open decision-bearing finding.
Assert: convergence-by-count does not override a decision-bearing finding.

---

## S3 — Oscillation → HALT_DECISION

Proves: oscillation detector (both triggers), plateau over `plateau_N`.

Planted trading pair, no decision-bearing singletons:
- `P5a` coherence · MATERIAL · DOC-A · cites `AUTH-1`.
- `P5b` coherence · MATERIAL · DOC-B · cites `AUTH-2`.
- Rigged so the author's conforming fix to `P5a` makes the coherence stub emit
  `P5b`, and the conforming fix to `P5b` re-emits `P5a` (same `id`, reopened).

Expected:
- Pass 1: `P5a` open, resolvable → CONTINUE; author fixes `P5a`, records DOC-A change.
- Pass 2: `P5b` emitted, resolvable → CONTINUE; author fixes `P5b`, records DOC-B change.
- Pass 3: `P5a` re-emitted with same `id`, `recurrence_count → 1`, open.
  `recurrence(ledger) == true` → **HALT_DECISION** (reason `oscillation`). ✅

Assert: recurrence trips no later than the reopen; payload carries the trading
`id`(s); exit reason is `oscillation`, not a convergence claim.

Variant S3b (plateau without a clean reopen): rig `open_cbm_count` to hold flat at 2
across passes without a same-`id` reopen. Assert: `plateau(ledger)` trips at
`plateau_N + 1` passes → HALT_DECISION.

---

## S4 — Scope drop at admission

Proves: the mechanical admission gate — "I'd have designed it differently is not a
finding."

Planted:
- `P4` antagonist · MATERIAL · DOC-B · `cited_authority = null` (or a bare-preference
  ref) → must be **dropped at admission**.

Expected:
- Pass 1: `P4` never enters the ledger. `open_cbm == 0` (nothing else planted), no
  decision-bearing, not oscillating → **CONVERGED**. ✅

Assert: `P4` absent from ledger; not counted; a dropped-finding log line exists so
the drop is observable (silent drops are indistinguishable from bugs).

---

## Skeleton acceptance = all four green

The plumbing is trustworthy only when S1–S4 (incl. S2b, S3b) all produce their
asserted exits deterministically across repeated runs. Only then do the real
three-hat contexts and the real coherence sweep get authored and wired. Until then,
no real reviewer, no live mode, no autonomous run.
