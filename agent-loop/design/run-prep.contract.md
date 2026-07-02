# Run-Prep Contract — Supervised First Dry Run

| Field | Value |
|---|---|
| **Document** | run-prep.contract.md |
| **Status** | RATIFIED — 2026-07-02 |
| **Date** | 2026-07-02 |
| **Author** | Thaddeus Haffey (Executive Architect), authored on claude.ai |
| **Implements** | Session ratifications: ledger home (item 1), fetchers (3a/3b), per-consumer input copies (3c), emitter (4a/4b/4c) |
| **Companions** | runner-real-hats.contract.md (§2 as amended 2026-07-02); ledger-schema.md; mechanical-gates.md |

This contract specifies the machinery that turns the wired-but-never-invoked
real-hat path into a runnable, supervised first dry run. It is authoritative
design: Claude Code implements it; conflicts resolve in this document's favor.
Everything stays **dry mode** — resolutions and escalations are proposed and
logged, never applied.

Hat expansions, canonical and inline wherever LLM-consumed:
LAA = Lead Application Architect, SA = Solution Architect,
EA = Enterprise Architect.

---

## §1 — Run folder and ledger home (ratified item 1)

Every run owns a folder: `agent-loop/runs/<run-id>/`.

- **run-id** format: `run-NNN-<slug>` — zero-padded ordinal plus a short
  human slug (run one: `run-001-distilled-set`). Ordinal assignment is
  manual at prep; the prep gate (§8) refuses an existing folder.
- **Contents** (all produced by the machinery, nothing hand-edited after
  prep):
  - `ledger.json` — the `LedgerStore` home. Fresh-fetched per pass exactly
    as today; no new store machinery.
  - `manifest.json` — the run manifest (§7).
  - `substrate/` — the frozen per-run substrate snapshot (§3).
  - `action-log.jsonl` — the live-streamed action log (§7).
- **Git posture:** the folder churns in the working tree during the run;
  Tad commits it once at run end as the run artifact. The runner never
  invokes git. `agent-loop/runs/` is **not** gitignored.

## §2 — Document fetcher (ratified 3a)

A real `DocumentFetcher` (`Callable[[list[str]], DocumentSet]`) replacing
`default_document_fetcher` for real runs:

- **Source:** the local repo working tree, `$SOFIA_ROOT/docs/`, and nowhere
  else. Never Downloads, never Notion, never a network source.
- **Resolution:** doc-id → file by prefix glob `docs/**/<doc-id>-*.md`.
  Zero matches or more than one match raises immediately with the doc-id
  and the match list — no fallback, no fuzzy matching.
- **Freshness:** invoked by the runner per pass (existing §5 semantics of
  the runner contract), reading the working tree each time. In dry mode the
  tree never changes mid-run; the discipline is kept because live mode's
  author will change it.
- **Content:** file text verbatim. The fetcher never edits, truncates, or
  annotates document content.
- Construction takes the docs root as an explicit argument (no hardcoded
  absolute paths; tests point it at a tmp tree).

## §3 — Substrate snapshot and fetcher (ratified 3b)

Substrate is **per-run frozen**; documents are per-pass fresh. Rationale is
recorded here as design intent: authorities changing mid-run would make
findings non-reproducible and the audit incoherent.

- **Layout:**
  - `runs/<run-id>/substrate/authorities/*.md`
  - `runs/<run-id>/substrate/design-intent/*.md`
  - `runs/<run-id>/substrate/manifest.json` — per file: logical id
    (filename stem), origin (path or URL it was snapshotted from),
    retrieval timestamp, SHA-256 of content.
- **Assembly** happens at run prep (§8), by hand or by prep tooling — the
  runner and fetcher never assemble substrate, only read it. Notion's role
  (pinned, item 3b): Notion is the upstream source-of-truth for
  design-intent substrate; in-scope pages are snapshotted into
  `design-intent/` at prep and the manifest records their origin. The
  runner never queries Notion.
- **Fetcher:** a real `SubstrateFetcher` (`Callable[[list[str]], Substrate]`)
  that reads the run's `substrate/` folder fresh from disk each pass and
  returns `Substrate(authorities={stem: content}, design_intent={stem:
  content})`. The `doc_ids` argument is accepted (port signature unchanged)
  and ignored — substrate scope is per-run, not per-doc. An empty or
  missing `substrate/` folder raises at first fetch: a real run with empty
  substrate is a prep failure, not a degraded mode (an empty authorities
  dict collapses SA = Solution Architect into internal-correctness review
  and corrupts the SA↔coherence overlap evidence).
- **Run-one substrate set** (recorded as prep intent, not code):
  authorities = `adr-template.md`, `ddr-template.md`,
  `author-decision-record` SKILL.md, snapshotted from the bedrock checkout;
  design-intent = the SOFIA vision pages Tad names at prep, snapshotted
  from Notion.

## §4 — Per-consumer copies of records and substrate (ratified 3c)

`_gather_then_admit` currently hands each reviewer its own deep copy of the
ledger snapshot but passes `records` and `substrate` as shared objects.
`DocumentSet` and `Substrate` are frozen dataclasses with **mutable dict
fields** — isolation is conventional, the failure shape the 2026-07-02 §2
amendment rejected.

- Each reviewer receives its **own deep copy** of `records` and
  `substrate`, made at the same point its snapshot copy is made.
- The plan's signature is unchanged (it never sees records/substrate).
- Probe test (§10): a reviewer that mutates its records/substrate copies
  cannot affect any later reviewer in the same pass, the admitted ledger,
  or any subsequent pass.
- This closes the carried §5-shared-inputs flag from PR #2; the runner
  contract's §5 note should be updated to point here.

## §5 — Emitter transport (ratified 4a)

A real `LlmEmitter` (`Callable[[str, str], str]` — signature unchanged)
behind `build_api_emitter`:

- **Transport:** the Anthropic Messages API via the official Python SDK,
  directly. Never a Claude-CLI or agent subprocess: agentic transports
  inject their own system prompts, tools, and environment into the
  reviewer's context — a structural violation of stance isolation that is
  invisible in the output.
- **Context is exactly the contract:** `system` = the prompt file's
  `## System` block verbatim (as loaded by `load_system_prompt`);
  `messages` = one user turn, the assembled §5 input block; **no tools, no
  extra turns, nothing else**.
- **API key:** `ANTHROPIC_API_KEY` from the environment only. Never a
  parameter, never in any log, manifest, or artifact.

## §6 — Call policy (ratified 4b), and the arbiter call site

- **Model:** one fixed model for all call sites in a run; run one:
  `claude-opus-4-8`. The model string lives in run configuration and is
  recorded in the manifest — never hardcoded in module code.
- **Parameters:** temperature 0; `max_tokens` 8192 (generous for a findings
  array; raise by config if truncation is ever observed — truncated JSON
  surfaces as a parse_drop, §10e).
- **Sequencing:** calls are sequential in admission order (LAA, SA, EA,
  coherence) — the existing gather loop already is; no parallelism.
- **Transport-level failure** (rate limit, 5xx, timeout, connection):
  **one** retry after a bounded backoff (30s), logged as `llm_retry`; a
  second failure raises and **aborts the run loudly**. A run that proceeds
  minus one hat corrupts the independence evidence — better dead than
  subtly wrong.
- **Content-level malformation** stays where it lives today: reviewer
  emissions that parse badly are `parse_dropped` by the §7 seam of the
  runner contract, never retried by the emitter.

**Arbiter (scope extension, flagged at ratification):** run one requires
the real arbiter — it is the sole LLM on the exit path and its confidence
stream is a named supervision watch. A real `Arbiter` adapter:

- Loads `agent-loop/design/arbiter-classifier.prompt.md` the same way
  reviewer prompts load (`## System` as data); assembles its user block
  from the finding under classification plus the substrate handed to
  `run_loop` (`authorities` / `design_intent` — position unchanged, runner
  contract §8).
- Same transport (§5) and call policy (this section) as reviewers.
- Output parse: strict — classification must be in the ledger schema's
  vocabulary; confidence must be present and valid against the arbiter's
  categorical vocabulary (`high` | `medium` | `low`), per
  arbiter-classifier.prompt.md and the ArbiterResult port. Malformed output:
  **one** content retry (logged), then abort. The conservative
  decision-bearing bias lives in the arbiter prompt, never fabricated by
  fallback code — a fabricated classification on the exit path is the
  worst silent failure available.

## §7 — Provenance, cost capture, and the live log (ratified 4c)

- **Per LLM call**, logged to the action log as `llm_call`: call-site
  label (`antagonist-LAA` … `coherence`, `arbiter`), model, parameters,
  SHA-256 of the system-prompt text, input tokens, output tokens, latency
  ms. Token counts come from the API response usage block.
- **Run manifest** (`manifest.json`), written at prep and finalized at run
  end:
  - prep: run-id, created timestamp, document set (doc-ids + resolved
    paths), `git rev-parse HEAD` of $SOFIA_ROOT, prompt-file SHA-256 for
    all five prompt files, substrate manifest reference, model + parameters.
  - run end: router exit, passes run, per-call-site token totals, run
    wall-clock. Per-hat cost is a first-class output — the held roster
    question is independence **per cost**, and run one must measure both
    halves.
- **Live log sink:** the action log streams to
  `runs/<run-id>/action-log.jsonl` as events are emitted (append per
  event, flushed), so the attended run can be tailed live — the
  supervision protocol (item 5) reads this stream. Additive change to
  `log.py` (an optional sink); the in-memory log and all existing
  consumers are unchanged.

## §8 — Run assembly and prep gates

A run entry module (`agent_loop.run_real`) owning assembly and prep
validation. Prep gates, all fail-loud before any LLM call:

1. `runs/<run-id>/` does not already exist; create it.
2. `git status --porcelain docs/` is empty — the HEAD SHA stamp is
   meaningless over a dirty docs tree. (Only `docs/` must be clean; the
   runs folder itself will churn.)
3. All doc-ids in the header set resolve (one match each) via §2.
4. `substrate/` is populated and its manifest validates (§3).
5. All five prompt files exist and yield a non-empty `## System`.
6. `ANTHROPIC_API_KEY` is present in the environment.

Assembly: `LedgerStore` at `runs/<run-id>/ledger.json`; §2 document fetcher;
§3 substrate fetcher; four reviewers via the existing `build_real_reviewer`
with per-call-site emitters from `build_api_emitter`; §6 arbiter adapter;
`run_loop` invoked with the real plan. `fix_changes` stays empty — the
author stub does nothing on real findings; expected run-one exits are
HALT_DECISION or a plateau/oscillation halt, both legitimate router exits.
`max_passes` for run one: 10 (attended; the default 50 is an unattended
bound).

## §9 — Unchanged surfaces

Admission, arbiter **position** (only LLM on the exit path), gates, router,
author stub, schema enums, severity vocabulary, dry mode, the stub path,
and the four dummy scenarios are untouched. `LlmEmitter`, `DocumentFetcher`,
`SubstrateFetcher`, and `Plan` signatures are unchanged — this contract
fills the ports, it does not move them.

## §10 — Test obligations

All tests run without a real API (fakes/injected transports); the real API
is exercised only in the supervised run itself.

a. **Fetcher resolution:** doc-id resolves to exactly one file (content
   verbatim); zero matches raises; multiple matches raises naming both.
b. **Substrate read:** populated folder → correct Substrate maps; empty or
   missing folder raises at first fetch; manifest validation failure
   raises at prep.
c. **Input isolation probe (§4):** reviewer mutates its records/substrate
   deep copies → later reviewers in the same pass, the admitted ledger,
   and the next pass are unaffected. Mirrors the existing §9h probe.
d. **Emitter policy:** transport failure → one logged retry → success path
   proceeds; two failures → raises and the run aborts with no partial
   admission for that pass. Parameters and system text reach the (fake)
   transport exactly as configured.
e. **Truncation surfaces as parse_drop:** a truncated/invalid JSON payload
   from the fake transport produces `parse_dropped`, never a crash.
f. **Arbiter adapter:** valid classification parses and stamps; malformed
   → one retry → abort; the adapter never fabricates a classification.
g. **Provenance:** `llm_call` events carry label/model/hash/tokens/latency;
   manifest carries HEAD SHA, prompt hashes, and per-site totals at
   run end.
h. **Live sink:** events appear in `action-log.jsonl` incrementally during
   a run, not only at exit; in-memory log unchanged.
i. **Prep gates:** each §8 gate failure aborts before any emitter call.
j. **Regression:** the stub path and S1–S4/S2b/S3b scenarios are untouched
   and green; coverage bar holds (100% line+branch on agent_loop).
