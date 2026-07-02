# agent-loop — Design-Review Loop Walking Skeleton

Dry-mode plumbing that proves the durable spine and the mechanical convergence
gates fire deterministically on a dummy case, with the reviewers stubbed. This
is the execution-surface implementation of the design authored on claude.ai
(`~/Downloads/Agent_Loop_Design_Review/`). It is **repo-agnostic** — self-contained,
no external dependencies beyond `pytest`/`pytest-cov`. Where it lands, and any git
transaction, is Tad's call.

## What it is (and is not)

- **Convergence is mechanical.** No LLM judgment on the "done" decision. The
  `CONVERGED` exit is a boolean conjunction over ledger state
  (`open_cbm == 0 ∧ no open decision-bearing ∧ not oscillating`).
- **The arbiter-classifier is the only LLM judgment** — and only classifies a
  finding `resolvable` vs `decision-bearing`. In the skeleton it is a **port**
  driven by a canned adapter (`CannedArbiter`) so the acceptance suite is
  deterministic; the production `LlmArbiter` adapter carries the prompt verbatim
  but is **unwired** (no network, raises in dry mode).
- **Dry mode throughout.** The author *proposes* resolutions and the router
  *proposes* escalations; nothing is applied to any document and no ticket is
  opened. Every intended action is logged as a structured event.
- **Reviewers are canned stubs.** The three real antagonist hats and the real
  coherence sweep are **not** built here — they are gated on this plumbing going
  green (a separate deliverable).

## Layout

| Module | Role |
|---|---|
| `agent_loop/identity.py` | Stable finding id = `hash(target+locus+normalized(claim))` |
| `agent_loop/ledger.py` | Records + file-backed store (fresh-fetch per agent) |
| `agent_loop/admission.py` | Mechanical scope gate + identity/dedup/reopen rule |
| `agent_loop/gates.py` | Counter, oscillation (recurrence + plateau), router |
| `agent_loop/arbiter.py` | Arbiter port; canned adapter; unwired LLM seam |
| `agent_loop/stubs.py` | Canned antagonist/coherence/author emitters |
| `agent_loop/scenarios.py` | The dummy-case fixture: S1, S2, S2b, S3, S3b, S4 |
| `agent_loop/runner.py` | The pass loop + dry-mode action log + loop bound |
| `agent_loop/demo.py` | `python -m agent_loop.demo` — dry-run summary of all scenarios |

## Run

```bash
cd agent-loop
python -m pytest          # acceptance suite + unit tests, 90% coverage gate
python -m agent_loop.demo # human-readable dry-run of every scenario
```

Acceptance = **S1–S4 (incl. S2b, S3b) all green**, deterministically across
repeated runs. The suite asserts each scenario's exit five times on fresh stores.

## Notes for the reviewer / next builder

- **`open_cbm_count` snapshot** is taken at routing time (post-admission,
  post-arbiter, pre-author) — the identical value the router reads for its
  convergence check. One value, no drift; it is the plateau signal.
- **Emission discipline** (why S1/S3 don't false-trip): seeds fire once (pass 1);
  coherence/trading findings fire on a doc-change trigger the author recorded in
  the prior pass. A stub must never re-emit a finding whose id is already closed.
- **Doc changes live in the ledger** (`Ledger.doc_changes`). The author-stub
  contract requires the fix's state change be recorded *in the ledger* (dry mode
  applies nothing to a real document); the schema table did not enumerate a
  location for it, so the harness carries an explicit in-ledger change log. This
  is a documented extension, flagged for the schema owner.
- **Loop bound** (`max_passes`, default 50) is a loud safety backstop, not a spec
  exit — it raises `LoopBoundExceeded` rather than returning a fake
  `CONVERGED`/`HALT`.

## Downstream flags

- **Ledger home** (open). Recommendation stands: repo-local, git-versioned file.
  Not ratified — flagged.
- **Severity vocabulary** (resolved, ratified 2026-07-01). The harness uses the
  house `code-review` ladder — `BLOCKING / MATERIAL / COSMETIC / POSITIVE` — as
  the single vocabulary; the convergence-counted set is `{BLOCKING, MATERIAL}`.
  This replaced the skeleton's earlier private `{critical, blocking, major}` set
  (major → `MATERIAL`, so the original strictness is preserved). See
  `design/ledger-schema.md` §Severity.
