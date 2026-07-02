# Design-Review Loop — Walking Skeleton

Authored on claude.ai as the design/prompt artifact set. **Claude Code implements
the runner to this spec.** These files are specs and prompts (data), not the
implementation. Repo placement and any git transactions are Tad's.

## What this skeleton is for

The full loop is a set of isolated-context agents that drive a design-document set
to convergence, halting only to surface a decision Tad hasn't made. This skeleton
is the **plumbing** underneath that loop. Its only job is to prove — on a dummy
case, with the reviewers stubbed — that the durable spine and the mechanical gates
fire correctly:

- the **ledger** is written, fresh-fetched, and carries finding identity across passes;
- the **convergence counter** is dumb, mechanical, and unanchored;
- the **oscillation detector** trips on recurrence and on plateau;
- the **arbiter-classifier** labels each finding resolvable vs. decision-bearing,
  biased conservative;
- the **router** composes those into exactly three exits.

Real reviewers are **not** instantiated here. The architecture commits to three
stance-isolated antagonists (LAA / SA / EA) plus a cross-set coherence sweep; the
build does not lock that roster before the plumbing is trustworthy. This skeleton
runs on a **single canned antagonist stub** and a **canned coherence stub** that
emit fixed findings from the dummy case, so every gate outcome is deterministic and
assertable.

## Ratified architecture this skeleton must honor

- **Convergence is mechanical and quantifiable.** No LLM judgment on the "done"
  decision. The counter counts; the router composes booleans.
- **The only LLM judgment on the exit path is the arbiter-classifier**, applied
  per open unclassified finding of severity BLOCKING, MATERIAL, or COSMETIC,
  biased conservative (unsure → decision-bearing). POSITIVE findings are never
  classified (a decision-bearing POSITIVE is incoherent) and never reach the
  halt payload (amended 2026-07-02 — run-004 spent ~120k tokens classifying
  survived-attack credits).
- **Author fixes only resolvable findings, and only by conforming to cited
  authority** — never by adopting an antagonist's suggested fix, which can smuggle
  in a decision.
- **A finding must cite authority** (canonical artifact, stated design intent,
  internal-coherence conflict, or a genuine soundness defect). "I'd have designed
  it differently" is not a finding and is dropped at admission.
- **Continuity lives in the ledger, not in any agent's context.** Every agent
  fetches substrate + current record(s) + ledger fresh each pass.
- **No cross-anchoring between reviewers.** Within a pass, each reviewer judges
  against a frozen prior-pass ledger snapshot, in isolation; no reviewer sees another
  reviewer's current-pass findings, which are joined only afterward by the arbiter.
  Parallel-vs-sequential scheduling sits *below* this invariant, not in place of it.
  (Skeleton reviewers are stubs, so this holds trivially; the real-hat wiring must
  satisfy it structurally — see `antagonist-stub.prompt.md`.)

## Build order (do not reorder)

1. Ledger read/write + admission gate (`ledger-schema.md`).
2. Mechanical gates: counter, oscillation, router (`mechanical-gates.md`).
3. Arbiter-classifier (`arbiter-classifier.prompt.md`).
4. Canned antagonist stub + coherence stub (`antagonist-stub.prompt.md`).
5. Drive the four dummy scenarios; assert expected exits (`dummy-case.md`).

Only once all four scenarios pass do the three real hat-contexts and the real
coherence sweep get authored (separate claude.ai deliverable) and wired in.

## Dry mode

The skeleton — and every run until the classifier earns unattended trust — runs in
**dry mode**: the author stub *proposes* resolutions and the router *proposes*
escalations, but nothing is applied to any real document and no real Linear ticket
is opened. Intended actions are logged. Run one is not autonomous.

## Downstream flags

- **Ledger home.** Recommendation: repo-local, git-versioned file (high-churn,
  transient, fresh-fetchable). Not ratified — flagged.
- **Severity vocabulary — RATIFIED 2026-07-01.** The house `code-review` ladder
  (`BLOCKING / MATERIAL / COSMETIC / POSITIVE`) is the single vocabulary across all
  Haffey tools/agents/systems; the counted-for-convergence set is
  `{BLOCKING, MATERIAL}`. See `ledger-schema.md` §Severity.
