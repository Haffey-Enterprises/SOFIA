# Runner Contract — Real Hats

**Specified on claude.ai; implemented by Claude Code. This document is a
contract, not an implementation.** It turns the no-cross-anchoring invariant —
whose design home is `antagonist-stub.prompt.md` §No cross-anchoring — into
the concrete runner changes required before the real reviewers
(`antagonist-LAA/SA/EA.prompt.md`, `coherence-sweep.prompt.md`) are wired.
Repo placement of the resulting code and all git transactions remain Tad's.

The stub path is not removed: the canned stubs and the four dummy scenarios
(`dummy-case.md`) remain the regression harness and must stay green after
every change below.

---

## 1. Reviewer port

Current skeleton port (`agent_loop/stubs.py`):

```
Reviewer = Callable[[int, Ledger], list[Finding]]   # handed the mutating in-pass ledger
```

Real-reviewer port:

```
RealReviewer = Callable[[pass_number: int,
                         snapshot: Ledger,           # immutable prior-pass view — §2
                         records: DocumentSet,       # fetched fresh — §5
                         substrate: Substrate],      # fetched fresh — §5
                        list[Finding]]
```

The stub `Reviewer` signature may be adapted to the new port or kept behind an
adapter — Code's choice — provided the dummy scenarios pass unchanged.

## 2. Snapshot semantics

- Taken **once per pass, at pass start**, from the fresh `store.load()`,
  **before any current-pass admission**.
- **All** reviewers scheduled in the pass (three hats + coherence when
  scheduled) receive the **same snapshot state — each as its own frozen
  copy** (ratified 2026-07-02). Isolation must be structural, not
  conventional: with one shared snapshot object, a reviewer that mutated its
  input would leak to reviewers running after it in sequence while every test
  stayed green — the no-cross-anchoring failure shape one level down.
  Per-reviewer copies remove the seam.
- Frozen means frozen: reviewers must hold no reference to the ledger instance
  that admission mutates, nor to another reviewer's snapshot copy. Deep copy
  per reviewer, or a per-reviewer `store.load()` that is never written back —
  either satisfies the contract; sharing a mutable instance between reviewers,
  or with admission, does not.
- Because every reviewer's input is this frozen snapshot, **parallel and
  sequential execution are equivalent**. Scheduling is an implementation
  choice below the invariant, not a substitute for it.

## 3. Gather-then-admit

The current runner admits each reviewer's emissions inline inside the reviewer
loop. That must change:

1. Run all scheduled reviewers to completion against the snapshot; collect all
   emissions.
2. Then admit all collected emissions through the existing admission gate, in
   a **fixed deterministic order**: LAA, SA, EA, coherence (emission order
   preserved within each reviewer). Determinism keeps ids, dedup outcomes, and
   logs reproducible across runs.
3. No admission interleaves with any review.

## 4. Isolation

Each reviewer invocation is its **own LLM call in its own context** — no
shared conversation, no context reuse between hats, no hat receiving another
hat's current-pass output through any channel. The prompt files are loaded as
data: `## System` from the reviewer's `.prompt.md`, the `## User` block
assembled by the runner from §5 inputs.

## 5. Input assembly

Per pass, the runner assembles fresh (no reviewer fetches for itself in this
iteration; the runner is the fetch point):

- the full document set under review (per the ledger header `set`);
- the substrate: ratified canonical authorities + stated design intent in
  scope for the set;
- the §2 snapshot.

Each reviewer receives its **own deep copy** of the document set and substrate
— not a shared reference — made at the same point as its §2 snapshot copy, per
`run-prep.contract.md` §4 (ratified 2026-07-02). This closes the shared-inputs
seam carried from PR #2: `DocumentSet` and `Substrate` are frozen dataclasses
with mutable dict fields, so conventional sharing left the same one-level-down
cross-anchoring seam the §2 amendment rejected for the snapshot.

## 6. Coherence scheduling

The real sweep is **runner-scheduled**, not self-gating (each real invocation
costs an LLM call; the stub's every-pass self-gating predicates stay on the
stub path only):

- invoke on **pass 1** (initial sweep);
- invoke on pass N **iff** a document change was recorded in pass N−1
  (`ledger.doc_changed_in_pass`, matching the existing fire-on-trigger
  semantics);
- otherwise skip, and **log the skip** (a silent skip is indistinguishable
  from a bug).

The three hats run every pass.

## 7. Emission parsing seam

Real reviewers emit a JSON array of reviewer-field findings (see the prompts'
Contract block). A runner-side adapter:

- validates shape and vocabulary, constructs `Finding` templates;
- **stamps `source` and `altitude` from the invoked reviewer's identity**,
  ignoring any value the model emitted. (**Ratified 2026-07-01:**
  `ledger-schema.md`'s "set by: reviewer" is satisfied at the port boundary,
  not trusted from LLM text; the schema §Identity carries the matching note.)
- drops a malformed emission (bad JSON, missing field, invalid enum) with a
  **logged, observable line** — never silently, never by crashing the pass.
  Dropped-at-parse is distinct in the log from dropped-at-admission.

Before JSON parsing, the seam strips well-defined markdown code fences — an
opening ``` or ```json line and a closing ``` line — and surrounding
whitespace from the emission. This is transport unwrapping, not content
repair: no other tolerance is added, and prose preambles, trailing
commentary, or malformed structure still drop (amended 2026-07-02).

## 8. No change elsewhere

- `Source`/`Altitude` enums already carry the real-hat values; no schema
  change.
- `POSITIVE` severity becomes actually-used; no gate change (never counted,
  never blocks — already true).
- Author stub, arbiter position (joins post-hoc, classifies after all
  admissions), gates, and router are untouched by this contract.
- Mode stays `dry` throughout; nothing here advances live-mode readiness,
  which remains gated on the classifier earning unattended trust.

## 9. Tests this contract requires

a. **Structural no-cross-anchoring:** a probe reviewer inspecting its snapshot
   observes no current-pass findings, regardless of what other reviewers
   emitted in the same pass.
b. **Gather-then-admit ordering:** no admission occurs until all scheduled
   reviewers have returned; admission order is LAA, SA, EA, coherence.
c. **Snapshot immutability:** admission-time mutations are not visible through
   any reviewer's snapshot reference.
d. **Coherence scheduling:** invoked pass 1; skipped (with logged skip) on a
   no-change pass; invoked on the pass after a recorded doc change.
e. **Identity stamping:** emitted `source`/`altitude` values are overridden by
   the invoking hat's identity.
f. **Malformed-emission drop:** logged and observable; the pass completes.
g. **Regression:** S1–S4 (incl. S2b, S3b) all green on the stub path after the
   runner changes.
h. **Per-reviewer snapshot isolation (ratified 2026-07-02):** a probe reviewer
   that mutates its own snapshot copy cannot affect any later reviewer's view,
   the scheduling plan's view, or the admitted ledger.
