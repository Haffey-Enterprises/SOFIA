# Run-Supervision Protocol — Attended First Dry Run

| Field | Value |
|---|---|
| **Document** | run-supervision.protocol.md |
| **Status** | RATIFIED — 2026-07-02 |
| **Date** | 2026-07-02 |
| **Author** | Thaddeus Haffey (Executive Architect), authored on claude.ai |
| **Companions** | run-prep.contract.md; runner-real-hats.contract.md; ledger-schema.md |
| **Applies to** | run-001 and every attended run until the classifier earns unattended trust |

Run one is attended; nothing is autonomous. This protocol defines what the
supervisor (Tad) watches live, when to kill a run, and how the run's output
is scored into evidence afterward. The run exists to start answering one
held empirical question — whether three stance-isolated hat contexts
produce independent-enough findings to justify their cost — and this
protocol is the instrument that turns an attended run into data.

Hat expansions, canonical: LAA = Lead Application Architect,
SA = Solution Architect, EA = Enterprise Architect.

---

## §1 — Instrument panel

Two live surfaces, one post-hoc surface:

- **Live stream:** `tail -f agent-loop/runs/<run-id>/action-log.jsonl`
  (the §7 live sink). Every event of interest arrives here: `llm_call`
  (site, tokens, latency), `llm_retry`, `parse_dropped`, admission drops,
  `coherence_skip`, `classified` (with confidence), `continue` / `halt` /
  `converged`, `proposed_escalation`.
- **Between passes:** `ledger.json` — read the findings admitted in the
  pass just completed. Passes are minutes apart (sequential LLM calls),
  which is enough time for a between-pass skim, not a full audit.
- **Post-run:** the full run folder (ledger, log, manifest) — the audit
  substrate for §5.

Division of attention: live watching is **anomaly-spotting** (§3's abort
triggers); between-pass skims are **orientation**; real scoring is
**post-run** (§5). Do not attempt live scoring — it produces rushed
judgments and misses the run.

## §2 — Pre-run checklist

1. Prep gates (run-prep contract §8) all passed — the runner enforces
   them, but confirm the manifest was written and records the expected
   HEAD SHA (`48e031a` or its descendant) and all six prompt hashes.
2. Cost envelope acknowledged. Order-of-magnitude, stated honestly as
   estimate not measurement: the four distilled docs are ~145 KB ≈ ~36k
   tokens; with substrate and snapshot, each reviewer call is roughly
   45–55k input tokens; pass 1 is therefore ~200k input tokens across the
   four reviewers plus small arbiter calls; a full run of 2–5 passes lands
   in the hundreds-of-thousands to ~1M input-token range at Opus-class
   pricing. If that envelope is unacceptable, stop before pass 1, not
   during.
3. Terminal arranged: one pane running the loop, one tailing the log.

## §3 — Live watch streams and abort triggers

The four chartered streams, plus operational health. For each: what it
looks like live, and what (if anything) justifies killing the run.

**a. Stance leakage.** A hat's findings reading like another hat's job —
LAA emitting enterprise-consequence claims, EA emitting line-level
soundness nitpicks, any antagonist emitting cross-document findings
(coherence's axis). Live: skim claims between passes for obvious
misfit. Abort trigger: none — leakage is evidence, not malfunction.
Score it post-run (§5); do not restructure or re-prompt mid-run.

**b. Cross-hat overlap, SA↔coherence seam especially.** The same defect
surfacing from multiple hats. Watch the seam: SA's axis is conformance
to cited authority; coherence's is internal and cross-document
consistency. A doc contradicting its own cited authority (SA) versus
contradicting a sibling doc (coherence) is the boundary case to note.
Abort trigger: none — overlap is the roster question's primary
evidence. Note candidates live; match formally post-run.

**c. Arbiter confidence stream.** `classified` events carry confidence.
Live: watch the distribution and note every low-confidence
classification for hand-check. The conservative bias should show as
decision-bearing classifications dominating ambiguous cases. Abort
trigger: none for values; §3e covers malformation.

**d. POSITIVE volume and placement.** Required-but-proportionate,
survived-attack framing. Live: per-hat POSITIVE counts and whether each
names what was attacked and survived. Soft alarm (note, don't abort):
POSITIVEs exceeding ~a third of a hat's emissions, or generic praise
without an attack narrative — both are prompt-defect signals for the
post-run review.

**e. Operational health — the only abort triggers.** Kill the run
(Ctrl-C is safe; §4) on any of:
  1. **Parse-drop storm:** a hat whose emissions are mostly/entirely
     `parse_dropped` in a pass. That hat is effectively absent — the
     independence evidence is corrupted, and the cause is a prompt or
     assembly defect. Fix the defect; new run.
  2. **Volume swamp:** admitted findings so numerous the post-run
     hand-audit becomes infeasible (guideline: >~50 admitted findings in
     pass 1). The audit *is* the product of run one; a run that can't be
     audited shouldn't continue burning tokens.
  3. **Cost runaway:** cumulative tokens tracking far outside the §2
     envelope.
  4. Anything that looks like the loop misbehaving mechanically
     (repeating a pass, ledger not advancing). Design says impossible;
     attended runs exist because design has been wrong before.
  Transport failure needs no human trigger — the emitter aborts loudly
  on its own (run-prep contract §6).

## §4 — Abort and re-run semantics

There is no resume. A killed or aborted run keeps its folder untouched as
evidence (commit it if it taught anything; delete it if it's pure noise —
supervisor's call, recorded either way). The retry is a **new run-id**
with the defect fixed. The ledger being file-backed makes Ctrl-C safe at
any point: at worst the current pass's admissions are partially recorded,
and the folder is abandoned evidence, not corrupted state.

## §5 — Post-run audit

The scoring pass, done cold (same day is fine; mid-run is not). Every
admitted finding gets a hand ruling on four axes, recorded in a scoring
table (`runs/<run-id>/audit.md`, authored on claude.ai from the run
folder):

1. **Validity:** true finding / false positive / can't-rule. Ground truth
   is the fetched documents and substrate, nothing else.
2. **Stance fit:** on-stance / off-stance / ambiguous, judged against the
   emitting hat's prompt charter.
3. **Duplication:** independent / duplicate-of(finding-id) / partial
   overlap. Hand-matched by locus + claim substance, not string
   similarity. The SA↔coherence pairs get individually written rulings.
4. **Baseline match:** matched / missed / novel, against §6's baseline
   set.

Plus three stream-level checks: arbiter hand-check (every low-confidence
classification and a sample of the rest — was the conservative bias
honored? any false-resolvable is a serious miss), POSITIVE proportionality
(per-hat volume + survived-attack framing), and per-hat cost from the
manifest (tokens per hat per pass — the denominator of the roster
question).

## §6 — Baseline comparison set

The human-review baseline for the four docs: the review records in
`docs/reviews/` at HEAD, plus the cold-review artifacts in ~/Downloads
(`COLD-REVIEW-Findings.md`, `COLD-REVIEW-2-Findings.md`) — assembled into
the run folder at audit time (not run time; the loop never sees them).
Only **still-live** defects count as missable: a baseline finding that the
distillation already resolved is out of scope for recall scoring.

One named calibration marker, pre-registered here so the audit can't
rationalize it afterward: the confidence roll-up conflict (DDR-001's
`ReasoningSession` aggregate-confidence language vs DDR-002's roll-up on
`ReasoningProgress`) was a persistent BLOCKING in the cold reviews; the
distillation's change log claims a terminology correction. Whether the
defect is truly dead is exactly the kind of cross-document question the
coherence sweep exists for. Three clean outcomes: (a) fixed and not
re-found — correct silence; (b) fixed but re-found — false positive,
score it; (c) not fully fixed and found — recall credit; (d) not fully
fixed and missed — the most instructive miss available.

## §7 — Evidence discipline: the roster question

Run one **starts** answering the independence-per-cost question; it does
not answer it. n=1 is the empirical floor and is stated as such in the
audit. The audit produces the independence measurements (overlap rates,
per-hat unique-true-finding counts) and the cost measurements (per-hat
tokens); it draws **no roster conclusion**. Restructuring the three-hat
roster on run-one data alone is explicitly out of scope — the ratified
fence against restructuring on intuition extends to restructuring on a
single sample.

## §8 — Outputs

A supervised run is complete when the run folder contains: `ledger.json`,
`action-log.jsonl`, `manifest.json` (finalized), `substrate/`, and
`audit.md` — and the folder is committed by Tad as the run artifact. The
audit's findings-about-the-instrument (prompt defects, seam blur, arbiter
miscalibration) route to the design docs as amendments through the normal
ratify-then-implement path; findings-about-the-documents route to the
Notion frontier or Linear per the standing three-surface split.

## §9 — The author step (sandbox-apply semantics, attended-first)

Companion to `author.prompt.md`; extends what dry mode means for the author,
and adds its supervision streams.

**What dry mode means for the author.** The author applies its conforming edits
to the run's document working copy — `runs/<run-id>/documents/` — and nowhere
else. The reviewed document evolves inside the run folder across passes (the
per-pass fresh re-read picks up the edit), which is what makes review-fix-review
mechanical rather than operator-driven. Dry mode's prohibition is unchanged in
force, re-scoped in target: no write to the canonical corpus (`docs/`), no real
ticket, no network write. A run's document is a snapshot copy, so writing it is
not a canonical edit — and the fetcher already reads only
`runs/<run-id>/documents/` (run-prep §2), so the author's blast radius is
bounded to the run folder by construction.

**First-target discipline.** Until the author has earned trust, its runs target
only a **sandbox draft** — a review fixture or an upcoming record not yet in the
canonical corpus — never a live canonical record. The sandbox draft is the
author's proving ground, exactly as dry mode is the classifier's.

**Author watch streams (added to §3).**
f. **Refusal stream** — each `refuse` is the arbiter↔author seam; score it cold,
   no abort.
g. **Edit-then-reopen stream** — a finding the author edited that a later pass
   reopens is the load-bearing trust signal (the edit smuggled something; the
   re-review caught it); no abort — the loop self-corrects and oscillation halts
   it to the operator by design.
Abort only on an **anchor-fail storm** (edits whose `old_string` never matches —
a prompt/assembly defect, same posture as a parse-drop storm).

**Trust ramp.** The author does not advance from sandbox-only to canonical
writes until the edit-then-reopen stream is boring across attended runs — the
author-side analog of the classifier's unattended-trust gate. n=1 is the floor;
state it.
