# Claude Code commit prompt — RBT-71 (post-implementation, Tad-authorized)

You are committing the RBT-71 implementation. This commit is authorized by Tad and gated: **verify every precondition below against the actual working tree and test run — if any fails, report and STOP without committing.**

## Preconditions (verify fresh, do not trust your prior report)

1. Full test suite green, including **S-SAT-1…6** and replay **R-1/R-2** (run it now; paste the summary in your report).
2. `agent-loop/design/mechanical-gates.md` — `git diff` empty for this file (it must be untouched).
3. The **shared Contract region** (the `**Hard rules.**` heading through the `OUTPUT DISCIPLINE` line, rules 1–9 inclusive) is **byte-identical** across `antagonist-LAA.prompt.md`, `antagonist-SA.prompt.md`, `antagonist-EA.prompt.md`, `coherence-sweep.prompt.md` (extract that region and diff/hash it; rule 9 present in all four). The coherence sweep's two pre-existing sweep-specific disciplines (PROPERTY-LEVEL ASSERTIONS, UPSTREAM-AUTHORITY RULE) sit outside this region and are expected — verify they are **unchanged**, not absent.
4. `run-supervision.protocol.md` §2: the spend-discipline block matches `run-supervision-s2-amendment.md` **verbatim** and sits **before** the cost-envelope item; §5 carries the edit-region-overlap audit check and the docket-discipline surfacing line.
5. `agent_loop/author.py`: `close_satisfied` evidence verification failure path escalates (never closes) — confirm by pointing at the test that pins it (S-SAT-2/3).
6. No changes outside the spec §7 amendment table plus tests, the RBT-71 deliverable docs, and `agent_loop/run_real.py` (the gen-11→12 calibration stamp + rationale — a legitimate companion to the reviewer-prompt change, noted post-spec; the stamp lives there pending the gen-stamp-hygiene fast-follow).

## Commit (SOFIA repo)

Single commit on the current branch. Scope — stage exactly:

- `agent_loop/author.py`, `agent_loop/run_real.py` (gen-12 stamp), the new/changed tests (incl. the gen-12 pin in `test_run_prep.py`)
- `agent-loop/design/author.prompt.md`, the four reviewer prompts, `design/ledger-schema.md`
- `agent-loop/design/run-supervision.protocol.md` *(path as it exists in-tree)*
- `agent-loop/design/rbt-71-decision-surface.spec.md`, `rbt-71-implementation-prompt.md`, `run-supervision-s2-amendment.md`, `rbt-71-commit-prompt.md`, `rbt-71-proving-run-prompt.md`
- `agent-loop/runs/run-030-adr-008-rbt69/rbt-71-refusal-analysis.md`, `rbt-71-categorization.json`

Do NOT sweep in unrelated untracked files (older run folders, rbt-69 prompt, etc.).

Message:

```
RBT-71: decision-surface de-pollution — author close_satisfied (evidence-anchored), gen-12 reviewer live-text grounding, §2 spend discipline, §5 audit watches

- author.py: close_satisfied action w/ mechanical evidence verification (fail -> escalate, never close); events author_satisfied / author_satisfied_evidence_fail; tests S-SAT-1..6 + run-030 replay R-1/R-2
- reviewer prompts gen-12: Contract rule 9 (quote the live text you fault)
- run-supervision: §2 spend-discipline gates (ratified 2026-07-19); §5 edit-region-overlap watch + docket-discipline line
- spec rbt-71-decision-surface PROPOSED v0.1.0 + analysis artifacts (46 refusals categorized, 41% phantom)
- mechanical-gates.md untouched; router/open_cbm semantics unchanged (S-SAT-6)

Ratified per item by Tad 2026-07-19. RBT-71.
```

**Do not push.** Report the commit hash + `git show --stat` output; the push is Tad's.

## Bedrock repo (separate transaction)

The `design-review-loop` SKILL triage change lives in the bedrock repo. Commit it there separately, same discipline (verify the triage section matches spec §2; commit, do not push):

```
RBT-71: design-review-loop triage — docket coalescing discipline (group by distinct underlying decision; ratify per decision; splittable)
```

Report both hashes and STOP.
