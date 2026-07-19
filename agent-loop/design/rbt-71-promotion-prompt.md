# Claude Code prompt — RBT-71 close-out: spec promotion, run-031 landing, cleanup (Tad-authorized, incl. push)

Tad has ratified the run-031 cold audit (`runs/run-031-adr-008-rbt71/audit.md`) and the promotion of the RBT-71 spec to ACCEPTED. Execute the following exactly; verify every FROM state against the actual file first; on any mismatch, report and STOP.

## Preconditions

1. `git status` — working tree clean except untracked run/sandbox artifacts; on `develop`, level with `origin/develop` at `461ad0c` or a descendant.
2. Full test suite green (run it; paste the summary).

## Edits (three, all small)

1. **`agent-loop/design/rbt-71-decision-surface.spec.md`** — header status flip.
   FROM: `| **Status** | PROPOSED v0.1.0 |`
   TO: `| **Status** | ACCEPTED v1.0.0 — promoted 2026-07-19 on run-031 proving evidence (runs/run-031-adr-008-rbt71/audit.md); findings ratified by Tad |`

2. **`run-supervision.protocol.md`** (in-tree path as it exists) — append one sentence to the §2 spend-discipline block (after item 4, before the Batch-API paragraph), recording the ratified pre-registration reading:
   `A run's pre-registration is satisfied by criteria committed to git before launch (e.g. a spec §-criteria + launch-prompt pair at a pre-run HEAD); a separate PRE-REGISTRATION.md is the conventional carrier, not the only lawful one.`

3. **`agent-loop/design/ledger-schema.md`** — one clarifying line where `classification` is defined:
   `POSITIVE findings are never classified — the arbiter classifies defects only, so a POSITIVE remains `unclassified` for its whole life; an audit reading "N unclassified at halt" should reconcile it against the POSITIVE count first.`
   (Adjust surrounding formatting to match the file's style; keep it one line of substance.)

## Stage, commit, push (SOFIA repo — push IS authorized this time)

Stage exactly: the three edited files; the complete `agent-loop/runs/run-031-adr-008-rbt71/` folder (action-log, ledger, both manifests, documents/, substrate/, emissions/, `_stdout.log` if present, `audit.md`); and `agent-loop/design/rbt-71-promotion-prompt.md` (this file). Nothing else — the older untracked run folders and `sandbox/` stay out.

Commit message:

```
RBT-71: promote decision-surface spec to ACCEPTED v1.0.0 + land run-031 proving artifacts

- run-031-adr-008-rbt71: first live oscillation stamp (single unbundled recurrence);
  13/13 satisfied-closes hand-validated against reconstructed states, 0 evidence fails,
  0 satisfied-close reopens; decision surface 52 -> 19 records (~5 distinct decisions),
  phantom 41% -> ~16% named residual; $22.83 at 3 passes
- spec status flip on the ratified run-031 cold audit
- run-supervision §2: committed spec+prompt pair recognized as pre-registration
- ledger-schema: POSITIVE-stays-unclassified clarifying note

Findings + promotion ratified by Tad 2026-07-19. RBT-71 DoD complete.
```

Push `develop` → `origin/develop`. (bedrock repo: no changes this leg — do not touch it.)

## Explicitly OUT of scope (named follow-ups, do not do them)

- The `pass: null` action-log logging fix (instrument finding #3, carried since run-030 — lands with the next runner-touching ticket).
- The gen-13 already-ratified-intent rule (trigger-gated on recurrence across runs; recorded in audit §4).
- RBT-72 cost-architecture work.

## Report and STOP

Deliver: the diff summary for the three edits, `git show --stat` of the commit, the push confirmation (`git status -sb`), and the test summary. Nothing further.
