# Reviewer Stubs + Real-Reviewer Contract

The skeleton proves plumbing, so its reviewers are **canned emitters**, not judgment
agents. They emit a fixed set of findings — the planted findings from
`dummy-case.md` — in ledger schema. This makes every gate outcome deterministic and
assertable. The real reviewers replace these stubs only after all four dummy
scenarios pass.

## Antagonist stub (canned)

Not a prompt — a deterministic emitter. Given a scenario id, it returns that
scenario's planted antagonist findings, verbatim, as ledger finding records. No LLM,
no judgment. It respects the admission gate: it will emit the one planted
preference-only "finding" so the gate can be observed dropping it.

## Coherence stub (canned)

Same shape. Emits the scenario's planted coherence findings. Critically, it emits
**conditionally on document state**: a planted coherence finding that only appears
"after DOC-A is changed" is withheld until the author stub has recorded that change
in the ledger. This lets the skeleton exercise "closing one finding opens another"
and the coherence-reruns-on-any-change rule without real coherence logic.

## Author stub (canned, dry)

Given a `resolvable` finding and its `authority_locus`, it records a *proposed*
resolution and marks the finding `closed` in the ledger — but applies nothing to any
real document. For scenarios that require "the fix changes DOC-A," it records that
state change in the ledger so the coherence stub can react. It never touches a
`decision-bearing` finding.

---

## Real-reviewer contract (forward reference — NOT built in the skeleton)

When the plumbing is trusted, the three real antagonists and the real coherence
sweep are authored as a **separate claude.ai deliverable**. This is the interface
they must satisfy so they drop into the same plumbing unchanged. Written here so
Claude Code builds the runner against a stable contract — the hat prompts themselves
are deliberately not written yet (roster commits to three; build does not instantiate
until plumbing is proven).

**Each antagonist (LAA / SA / EA):**
- runs in its **own isolated context**;
- **sees** the full record(s) + substrate + ledger, fetched fresh;
- **judges** only from its own altitude's authority (this is stance isolation, not
  content isolation — full visibility, single-altitude judgment; this is what
  preserves seam-findings);
- is a **negative test** — it looks for defects, not for things to praise;
- must obey the scope rule: every finding carries a well-formed `cited_authority`
  (canonical / design-intent / coherence / soundness). A preference is not a finding;
- emits findings in the exact ledger schema; does **not** classify them (that is the
  arbiter) and does **not** propose fixes into the ledger (a suggested fix can smuggle
  a decision; the author derives fixes from authority instead).

### No cross-anchoring — the invariant the real hats must satisfy

This is the property the whole stance-isolation architecture exists to protect, so
it is stated as a first-class invariant rather than left implicit in the runner.

In the skeleton, the runner hands each reviewer the same in-pass ledger reference,
and the *only* thing preventing a later reviewer from reading an earlier one's
current-pass findings is that the canned stubs never look at current-pass findings.
That is a property of the stubs being dumb — **not** a property the runner enforces.
It must become enforced before the real hats are wired, because a real hat handed
the mutating in-pass ledger could anchor on another hat's current-pass findings and
every existing test would still pass. (Present in the skeleton runner as a comment
only; this section is that invariant's design home.)

The invariant, stated so the real-hat wiring satisfies it structurally:

- Each hat reads an **immutable prior-pass snapshot** of the ledger — fetched fresh
  and frozen, never the mutating in-pass reference.
- Each hat runs in **isolation**; it cannot observe another hat's findings from the
  same pass.
- Findings are **joined post-hoc by the arbiter**, the only component that sees a
  pass's findings together.

Because each hat's input is a frozen snapshot, parallel and sequential execution are
equivalent — which is exactly why parallel-vs-sequential is a mere scheduling detail
and this snapshot-isolation is the real architectural requirement. When the real
hats land, the runner changes from "reviewers mutate one shared in-pass ledger" to
"each hat is given a frozen prior-pass snapshot; the arbiter joins their outputs."

**Coherence** is not an altitude. It is a cross-set consistency sweep over the whole
document set — internal, cross-document, narrative-vs-substrate — and it **re-runs
whenever any document in the set changes**. It emits in the same schema with
`altitude: cross-set`.

**Severity vocabulary (ratified):** the whole system speaks the `code-review` skill's
ladder — `BLOCKING / MATERIAL / COSMETIC / POSITIVE` — as the single house
vocabulary. The counted-for-convergence set is `{BLOCKING, MATERIAL}` (see
`ledger-schema.md` §Severity). The real hats emit natively in this ladder; there is
no crosswalk to maintain.
