# Claude Code run prompt — run-034 (ADR-003 Platform Patterns, RBT-9)

You are launching a design-review-loop draw on **ADR-003 — Platform Patterns, PROPOSED v0.1.0** (RBT-9): the reframed platform-patterns record — agentic orchestration, graph-anchored governance, coordination trajectory — authored 2026-07-20 from an eight-item ratified deliberation. Fresh-read `agent-loop/design/run-supervision.protocol.md` (including the §2 spend-discipline gates and §5 watches), `agent-loop/design/run-prep.contract.md`, and `agent-loop/deliberation/adr-003-platform-patterns/record.md` before anything else — do not run from memory or from this prompt's paraphrases.

## Phase 0 — Pre-registration commit (you execute; Tad verifies; run fires only on Tad's explicit go)

1. Confirm you are in `$SOFIA_ROOT` with `develop` at or descended from `a61936c`. Create/switch to branch `feature/rbt-9-a3-author-adr-003-platform-patterns` from `develop`.
2. The three pre-registration artifacts are already in the working tree, authored on claude.ai: `docs/adr/ADR-003-platform-patterns.md` (PROPOSED v0.1.0) · `agent-loop/deliberation/adr-003-platform-patterns/record.md` (the ratified deliberation record) · `agent-loop/design/rbt-9-run-034-prompt.md` (this prompt). If any of the three is absent, **stop and report — do not launch.**
3. Commit **exactly those three files** (suggested message: `docs(adr): ADR-003 platform-patterns PROPOSED v0.1.0 + deliberation record + run-034 prompt (pre-registration, RBT-9)`). No other files, no push, no ticket writes.
4. **Report the commit SHA and STOP.** That SHA is the pre-run HEAD. Committed draft + record + prompt at a pre-run HEAD is the lawful pre-registration carrier (protocol §2). Proceed to the run only when Tad explicitly says go.

## §2 spend-discipline checklist (answer in the pre-registration report, explicitly)

1. **Units before dollars** — mechanics are unit-proven and the instrument phase is closed (runs 029–031 landings; run-032/033 were the first real engagements). This run answers only what no suite or captured fixture can: (a) **fresh-record behavior on a reframed principle ADR** — whether authority-cited review finds real contradictions between the new orchestration model and the dense standing canon (ADR-001/002/008, DDR-001/002/003/004, SDD-001) that the authoring-session self-review missed — the proven catch class; (b) **decision-docket quality** — whether escalations are genuinely underdetermined decisions rather than re-litigations of the eight ratified items (the deliberation record is in substrate; reviewers and arbiter resolve against it); (c) a **record-class datapoint** — an ADR-class principle record against the dense-record non-exhaustion doctrine (n=6 runs, zero mechanical convergences; this draw is n=7).
2. **Bound to the minimum passes** — `max_passes = 3` (operator-ruled, 2026-07-20). Enough for review-fix-review plus a confirming pass on a single fresh record; the low bound forces a cheap honest disposition if it halts instead. A `LoopBoundExceeded` halt with unescalated decisions is an acceptable outcome — report it raw; audit-time extraction is sanctioned upstream, not yours.
3. **Match the target to the question** — ADR-003 is the ratified head of the design frontier and the soft prerequisite for the three reasoning-critical service designs; the question is exactly this record's soundness against canon, and only this record answers it.
4. **Mine captured fixtures first** — no captured run contains this record (authored today); runs 025–033 are already mined for instrument learning. This question spends or goes unanswered.

**Cost envelope (estimate, not measurement):** single draw, single-document set, full-canon substrate with per-actor 1-hour prompt caching live — expect **≈$23** at `claude-opus-4-8` list rates. Report cost as **all four line items** (uncached input $5/M · output $25/M · 1h-cache-write $10/M · cache-read $0.50/M); the protocol §3e cost-runaway watch tracks the **four-item total**. Acknowledge before pass 1; abort on runaway per §3e.

## Run prep (run-prep.contract.md governs; this run's recipe)

- `run_id: run-034-adr-003-rbt9`.
- **Documents:** header set = `["ADR-003"]`; snapshot `docs/adr/ADR-003-platform-patterns.md` from the clean working tree at the pre-run HEAD (gate 2: `docs/` clean — true once Phase 0 commits; gate 8: hash-verified at launch). Single-document set — the coherence hat reviews doc-vs-substrate.
- **Substrate (NEW recipe for THIS target — do not reuse any prior run's frozen substrate; assemble fresh, hash-pinned per §3):**
  - `authorities/`: `ADR-001-reasoning-architecture.md` · `ADR-002-graph-system-of-record.md` · `ADR-008-ground-truth-mutation-governance.md` · `DDR-001-data-architecture.md` · `DDR-002-graph-schema.md` · `DDR-003-feedback-loop-governance.md` · `DDR-004-inherited-confidence-derivation.md` · `SDD-001-knowledge-service.md` (all from `docs/` at the pre-run HEAD; note DDR-003 is now ACCEPTED canon and joins the authority set for the first time) · `adr-template.md` + `author-decision-record` SKILL.md (from the bedrock checkout — the ADR template this time, not the DDR template).
  - `design-intent/`: `agent-loop/deliberation/adr-003-platform-patterns/record.md` (the eight ratified items — **authoritative design intent for this review**, including the operator's reframing away from the prior-cycle hub-and-spoke/bus pattern and the coordination-trajectory drafting constraint; the external voice-first experience design is *encoded in this record* — reviewers judge against the record, not against any repository outside the substrate) · `triage-001-charter.md` + `sofia-vision.md` (as carried in run-033's substrate, unchanged).
  - Manifest records origin + SHA-256 per file (§3); empty substrate is a prep failure.
- **Prompts:** gen-12, all six, hashes recorded fresh; `calibration.generation: 12`. **Zero intended instrument variables vs run-033** — anything observed is document-driven, which is the point.
- **Author: sandbox-apply dry mode per protocol §9, unchanged.** Edits land in `runs/run-034-adr-003-rbt9/documents/` and nowhere else; no canonical write, no ticket write, no network write. The trust ramp is **not** advanced this run.
- Model, parameters, transport: as run-033 (Opus, max_tokens 8192) unless the protocol says otherwise.

## During the run

Supervise per protocol §3 + the author streams (§9f/g). Do not intervene in-loop. Abort only on the protocol's own triggers: parse-drop storm · volume swamp (fresh-document guideline >~50 admitted pass-1 findings) · cost runaway vs the envelope above (four-item total) · mechanical misbehavior · anchor-fail storm.

## Capture and report (report-and-STOP; no audit authoring, no post-run commit)

Deliver raw results only — the cold audit is authored on claude.ai against protocol §5 (edit-region-overlap watch, RELIT-class recurrence watch, interpretive-satisfied-close-at-medium-confidence watch, docket-discipline surfacing check: audit acts, not yours):

- Run folder complete in the working tree: `action-log.jsonl`, `ledger.json`, `emissions/`, `manifest.json` (finalized), per-pass documents state, `substrate/`. Leave it **uncommitted** — vendoring rides the landing PR upstream.
- A RAW-RESULT summary: per-pass counts of `author_edit` / `author_satisfied` / `author_satisfied_evidence_fail` / `author_refused`; the `classified` split with confidence distribution; `open_cbm` trajectory; open decision-bearing at halt or the CONVERGED stamp (and if `LoopBoundExceeded`, say so plainly with the unescalated count); the router disposition; per-hat finding volumes; total cost as the four line items with the cache-read/creation split.
- Do NOT score success, do NOT group the docket, do NOT author the audit, do NOT touch RBT-9 or any ticket, do NOT commit or push anything post-run. The audit, docket coalescing, convergence ruling, and all further git transactions are upstream of you.

STOP after the report.
