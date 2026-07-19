# Claude Code implementation prompt — RBT-69 design-review-loop optimization

**Role split.** This prompt hands you a ratified design. You implement it in `$SOFIA_ROOT/agent-loop/`; you do not re-open the design decisions. Git transactions (staging, commit, push) are Tad's — do not run git. Address the operator as Tad.

**Authority.** The design is `agent-loop/design/rbt-69-loop-optimization.spec.md` (PROPOSED v0.1.0). Fresh-read it in full before writing anything; on any divergence between this prompt and that spec, **the spec is authority**. Also fresh-read the contracts it amends — `ledger-schema.md`, `mechanical-gates.md`, `run-prep.contract.md`, `runner-real-hats.contract.md` — and the modules you will touch: `identity.py`, `admission.py`, `gates.py`, `transport.py`, `real_hats.py`, `author.py`, `ledger.py`, `runner.py`. Do not work from this prompt's summaries alone.

**Hard invariants — a change that violates any of these is wrong, not a trade-off.**
- Execute-vs-reason bright line: the gate logic stays executed against `agent_loop/`. Never move gate/identity/router logic into a prompt or an LLM call.
- No LLM on the "done" decision: `CONVERGED` stays the mechanical conjunction `open_cbm == 0 ∧ no open decision-bearing ∧ not oscillating`.
- Cost-down is never coverage-down: every finding the un-optimized loop surfaces must still surface. Pieces 1 and 2 are performance changes under a coverage-preservation obligation.
- Identity stays a pure deterministic function — no similarity/embedding/LLM step.

**Do not push until the blocking suites below are green.** This is an operator rider, not a guideline. The blocking suites are the finding-identity false-negative tests (T1–T5) and the cache-provenance tests (C1–C2). Implement test-first per the house `testing` skill.

---

## Sequence (identity first — piece 3 depends on it)

### 1. Piece 1 — cross-pass finding-identity

Amend `ledger-schema.md` §Identity and implement:
- `identity.py`: replace `derive_id(target, locus, claim)` with `derive_id(target, locus, altitude)` over `(sorted(target), normalize_locus(locus), altitude)`. Add `normalize_locus` (lowercase, strip markdown/punctuation/quoting noise, collapse whitespace — conservative; do not semantically alter the locus). Retain `normalize_claim` for the divergence guard.
- `admission.py`: derive the id from `finding.altitude` (already stamped at the `real_hats.parse_emissions` seam before admission). On the `dedup_open` path, if `normalize_claim(incoming) != normalize_claim(existing)`, keep the finding open, append the incoming claim to a new `claim_variants: list[str]` field, and emit a `claim_divergence` action-log event (`finding_id`, `existing_claim`, `incoming_claim`). Create no new record; discard no claim.
- `ledger.py`: add `claim_variants: list[str] = field(default_factory=list)` to `Finding`; ensure it round-trips through `_finding_from_dict` / `asdict` persistence.

Consequence to honor: adding altitude to the key means two hats raising the identical claim at one locus no longer dedup — that is intended (cross-hat overlap evidence). Do not "fix" it back.

**Blocking tests (T1–T5), per spec §Piece 1:**
- T1 surface-mutation dedup; T2 distinct-finding non-merge (the adversarial test — prove both claims retained and recoverable, finding stays open); T3 cross-altitude non-dedup; T4 oscillation survives (reopen + `recurrence_count += 1` under reworded re-emission of a closed finding); T5 `normalize_locus` stability.

### 2. Piece 2 — reviewer-substrate caching

Give RBT-49 caching a contract section (it was previously uncontracted, inline in `transport.py` only) — add it to `run-prep.contract.md` or a sibling, per the spec. Implement:
- `real_hats.assemble_user_prompt`: reorder to `SUBSTRATE → DOCUMENT SET → LEDGER SNAPSHOT → recency directive`.
- Hat transport path: pass the leading substrate block as `cache_prefix`, sliced from the call's own assembled `user` (preserve the `_user_content_blocks` byte-identity guarantee — never hand-build a substrate string that could diverge from what is sent).
- Raise the run-frozen blocks (hat substrate, system blocks, arbiter substrate) to a **1-hour cache TTL**; verify the exact Anthropic API mechanism/header for the 1-hour TTL. Never cache the document set or the ledger snapshot (the morphing surface stays the uncached tail).
- Author (`LlmAuthor`): bring its stable per-run inputs (run document text, any authority text shared across findings) under the same content-neutral leading-prefix + 1-hour-TTL rule; keep the per-finding-variable authority as the uncached tail.

Out of scope: a single shared cross-actor substrate prefix. Do not attempt it — the target is once-per-actor-per-run.

**Blocking tests (C1–C2), per spec §Piece 2:**
- C1 byte-identity (reconstructed sent content == uncached assembly, every call site, arbitrary prefix); C2 cross-run isolation (different substrate → different prefix bytes). C3 (multi-pass run shows hat `cache_read > 0` on passes 2+) is a supervised-run acceptance check Tad runs, not a unit test — surface it in the manifest as today.

### 3. Piece 3 — clean-stop

Amend `mechanical-gates.md` §2/§3 and implement in `gates.py`:
- Split the disposition: `recurrence` → `HALT_DECISION(reason="oscillation", payload=recurring)`; `plateau and not recurrence` → `HALT_DECISION(reason="non-convergence", payload=open decision-bearing unbundled + a context line recording the non-exhausted resolvable surface and the plateaued open_cbm)`. If no open decision-bearing at the plateau, payload falls back to the plateaued open counted findings with the same context line.
- Precedence unchanged: `[recurrence-oscillation | non-convergence-plateau] → open-resolvable (CONTINUE) → decision-bearing (HALT) → CONVERGED`.
- No new ledger status; do not touch `author.py`'s `_escalate` (resolvable → decision-bearing, status open).
- `runner.py`: the `HALT_DECISION` handling emits one proposed escalation per finding for the non-convergence payload exactly as for decision-bearing (unbundled).

**Blocking-for-piece tests (S1–S5), per spec §Piece 3:**
- S1 recurrence still oscillation; S2 run-028 replay → `non-convergence` not `oscillation`; S3 clean decision halt unchanged (run-025/026); S4 CONVERGED unchanged; S5 escalate-path regression (refused resolvable surfaces, never dropped, never `status="escalated"`).

---

## Regression and coverage

- Coverage bar holds: 100% line + branch on `agent_loop` (run-prep §10j). Cover every new branch — the divergence guard, the reordered cache path, the split disposition.
- Stub path + S1–S4 / S2b / S3b dummy scenarios stay green (runner-real-hats §9g). Update a dummy scenario's expected disposition only where it legitimately changed (plateau-without-recurrence now asserts `non-convergence`), and assert that change explicitly.
- All unit tests run without a real API (injected fakes/transports), per run-prep §10.

## What to hand back to Tad

A summary of: the files changed, the contract amendments made, the full test list with the T/C/S suites called out and their pass state, the coverage number, and any point where the spec was ambiguous and you had to make a judgment call (flag it for ratification rather than deciding silently). Do not push; leave the working tree for Tad's git transaction. The supervised run (C3 empirical + S2-in-the-wild) is the next leg after the suites are green.
