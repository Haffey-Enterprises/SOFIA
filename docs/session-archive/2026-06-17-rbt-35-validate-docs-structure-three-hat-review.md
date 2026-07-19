# File: docs/reviews/2026-06-17-rbt-35-validate-docs-structure-three-hat-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-17
# Description: Three-hat (LAA/SA/EA) review of record for the RBT-35 amendment to scripts/validate-docs-structure.sh (governed-set collection scope + non-ASCII/preflight hardening; absorbs RBT-31 identity reconcile). Serves the pre-merge gate for the RBT-35 PR and the deferred HEB-9 SOFIA-Reboot skill deploy it unblocks.

# Three-Hat Review — 2026-06-17 (RBT-35 `validate-docs-structure.sh` Pre-Merge Gate)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-17 |
| **Reviewer** | Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC, wearing all three hats LAA / SA / EA (claude.ai-assisted authoring under DIRECTIVE-007 + DIRECTIVE-026) |
| **Scope** | The RBT-35 revision of `scripts/validate-docs-structure.sh` — static three-hat pass plus executed sandbox verification — to confirm the script is error-free and effective once deployed. |
| **Authority** | RBT-35 (`Discipline: Three-hat review per DIRECTIVE-007; ENG-STD-002 governs the script amendment`). |
| **Outcome** | **PASS — CONVERGED (Cycle 2).** No BLOCKING findings in either cycle; 2 MATERIAL + 1 COSMETIC raised in Cycle 1 resolved and re-verified in Cycle 2; 1 COSMETIC acknowledged no-action; forward-pointers routed and addressed by the authoring session. |

---

## §1 Scope

### 1.1 In-scope per RBT-35

- `scripts/validate-docs-structure.sh` (artifact under authoring, staged at `${HOME}/Downloads/`) — full static three-hat review against ENG-STD-002 v2.2.0 and the DMS clauses it enforces, plus executed sandbox verification of both the happy path and adversarial cases.
- The RBT-35 design question itself: whether the **durable governed-set collection** (narrow to `docs/` + `scripts/`) correctly supersedes the minimal `.claude/skills/` exemption and unblocks the deferred HEB-9 SOFIA-Reboot skill deploy (header-less, frontmatter-first `.claude/skills/<name>/SKILL.md`).
- The absorbed RBT-31 identity reconcile (`# Author:` tuple), verified against the RBT-31 finding.

### 1.2 Verification discipline

Static review against fresh-fetched substrate: ENG-STD-002 v2.2.0 (full), DMS §1.2/§1.3/§2.2/§2.3.4/§3/§5/§9, CSD DIRECTIVE-007, the live RBT-35 and RBT-31 tickets, the actual SOFIA-Reboot repo tree and headers, and `.github/workflows/ci.yml`. Empirical verification by **executed sandbox** — a throwaway git repo running the byte-identical script (SHA-matched to the staged file) against fixtures mirroring the real repo plus adversarial cases. Both review cycles re-fetched the staged script byte-for-byte rather than reasoning from session recall.

### 1.3 Out of scope (deliberately)

- The substantive content/conformance of files the checker *exempts or excludes* (consumed standards, `.claude/**`, root files) — out of DMS §1.2/§1.3 governance scope by construction.
- Author-**value** conformance of governed documents — this validator checks for the *presence* of `# Author:`, not its value; identity-string stragglers elsewhere in the corpus are forward-pointers, not findings against this script (see §3, F1).
- Bash 3.2 *execution* — the sandbox runs bash 5.2; 3.2 compatibility was confirmed by static construct scan, not by 3.2 execution.

---

## §2 Findings

Severity vocabulary per DIRECTIVE-007 §7.2: **BLOCKING / MATERIAL / COSMETIC / POSITIVE**. Findings were raised in **Cycle 1** (Pass 1: static + sandbox) and dispositioned/verified in **Cycle 2** (Pass 2: re-fetch + fresh-eyes + re-run). All MATERIAL/COSMETIC items were **inherited from the RBT-3 bootstrap baseline**, not regressions introduced by RBT-35.

### 2.1 BLOCKING findings

**None** — in either cycle.

### 2.2 MATERIAL findings

#### Finding M-1: Non-ASCII / special-character paths are git-quoted, garbling the loop variable

**Location:** collection loop, `done < <(git ls-files … )` and `check_header()`.

**Description:** Under default `core.quotepath`, `git ls-files` C-quotes any path containing non-ASCII bytes (or `"`, `\`, newline) — wrapping it in literal double-quotes with `\xNN` escapes. The loop variable `$f` then holds a pseudo-path that does not exist on disk, so `check_header`'s `grep '^# File:' "$f"` cannot open the real file. Cycle-1 sandbox evidence: a non-ASCII fixture that carried a *correct* `# File:` line produced a **spurious `missing '# File:'` violation** plus an escaped display path (13 total violations).

**Why not BLOCKING:** the net CI outcome is fail-safe — a non-ASCII filename still produces a RED violation (which §5.3 wants), and the defect over-reports rather than under-reports. But the surfaced reason is wrong and would mislead an operator triaging CI, so it warranted an in-scope fix.

**Disposition — RESOLVED (Cycle 2).** Collection rewritten to NUL-delimited reading: `git ls-files -z 'docs/*.md' 'scripts/*.md'` consumed by `while IFS= read -r -d '' f`; the `| sort -u` pass dropped (git's output for these disjoint pathspecs is already sorted and duplicate-free). Cycle-2 sandbox evidence: the same non-ASCII fixture now yields exactly **one** correct violation (the legitimate §5.3 flag) with **no** spurious `missing '# File:'` — confirming `check_header` opened the real path; total dropped 13 → 12.

#### Finding M-2: No git/work-tree pre-condition → silent vacuous PASS

**Location:** top-of-script, after `cd "$REPO_ROOT"`.

**Description:** With no pre-condition guard, an invocation where `git ls-files` produces nothing — run outside the work tree, with git absent from PATH, or (post-RBT-35) a future pathspec typo such as `doc/*.md` — falls through the loop with `SCANNED=0` and reports `PASS` / exit 0. Cycle-1 sandbox evidence: running in a non-git directory produced `scanned 0` / `PASS` / exit 0. For a CI conformance gate, a vacuous green that masks a broken gate is the worst failure mode.

**Why not BLOCKING:** not live on the CI happy path — `.github/workflows/ci.yml` runs the gate from the `actions/checkout@v4` root where git is present and the pathspec is valid. The exposure is local/sub-directory invocation or a future pathspec regression.

**Disposition — RESOLVED (Cycle 2).** Added `cd "$REPO_ROOT" || exit 2` plus two pre-conditions: `command -v git` and `git rev-parse --is-inside-work-tree`, each failing RED with exit 2 (environment error per ENG-STD-002 §5.4 / §4.4). Cycle-2 sandbox evidence: not-a-work-tree → `RED: not inside a git work tree … exit 2`; git-absent (curated PATH) → `RED: git not found on PATH … exit 2`. The vacuous-pass path is closed.

### 2.3 COSMETIC findings

- **C-1 — strict-mode header self-description inaccurate.** Cycle 1: the header read `set -euo pipefail (accumulator pattern, bracketed per §3.2)`, but no bracketed `set +e`/`set -e` region exists — strict mode stays fully on and accumulation is via per-check guards; with no flag omitted, §9.3 does not even apply. **RESOLVED (Cycle 2):** reworded to `set -euo pipefail — fully retained; violations accumulated via per-check guards (no bracketed set +e)`.
- **C-2 — space filename double-reports.** A filename containing a space trips both the spaces rule and the disallowed-character rule, emitting two messages for one root cause. **Acknowledged — no-action** (COSMETIC/optional; legitimate §7.2 disposition). Unchanged in Cycle 2; a single `continue` after the spaces hit would single-report if ever desired, but it is not a defect.

### 2.4 No-drift confirmations (positive findings)

- **Governed-set collection is a faithful operationalization of DMS §1.2** — `docs/` + `scripts/` (companions) at any depth; verified empirically that git pathspec `*` matches across `/` and is anchored (a sibling `mydocs/` tree is not captured).
- **HEB-9 unblock holds by construction** — the header-less, frontmatter-first `.claude/skills/<name>/SKILL.md` is never collected; the deploy PR passes this gate. This is the central effectiveness criterion for RBT-35, confirmed end-to-end.
- **Root files and `.github/**` excluded by construction** — no denylist to maintain as external-tool conventions land.
- **`docs/templates/**` exemption survives the rewrite correctly** — document templates' `# File:` lines carry target-output paths by design (verified against the real template headers); they must be exempt, and they are, at any depth.
- **Script templates are unaffected** — `scripts/templates/` holds `.sh` templates per DMS §3.6.2, so the wider `scripts/*.md` reach does not drag them into the path-match check.
- **Consumed-snapshot conformance honored by exemption** — every consumed snapshot (DMS, `docs/governance/**`, root-level CSD) is exempt or excluded, so the hard `# Created:` requirement never false-positives on a reduced-header snapshot (DMS §2.2 / §2.3.4).
- **RBT-31 identity reconcile applied and corpus-aligned** — `# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC`, matching the canonical tuple confirmed in the RBT-31 finding.
- **All ENG-STD-002 §3.5 header fields present**; `# Revised:` accurately names the RBT-35 hardening and the absorbed RBT-31 reconcile.
- **Filename regexes match DMS §5.1/§5.2** — uppercase doctype prefix, zero-padded `[0-9]{3,}`, lowercase-hyphenated slug.
- **Bash 3.2-safe** — no `declare -A` / `mapfile` / `${var,,}`; `read -r -d ''` and `command -v` are 3.2-valid; process substitution `< <(…)` is portable.
- **Checker still bites** — all seven injected violation classes (header/path mismatch, missing header lines, wrong directory, non-zero-padded NNN, uppercase slug, filename hygiene) are caught with exit 1; a single file carrying four defects produced all four violations, confirming the per-check accumulator is genuinely `set -e`-safe (no first-failure abort).
- **No regression on the real governed set** — `scripts/verify-repo-state.md` (now collected via `scripts/*.md`, not exempt) carries a conformant header and passes.
- **CI invocation compatible** — `.github/workflows/ci.yml` runs the gate from the checkout root on PR + push to `main`/`develop`.

### 2.5 Sandbox verification record

Executed against the byte-identical staged script (Cycle 1 SHA `693f4461…`; Cycle 2 SHA `ae948b29…`), git 2.43, fixtures mirroring the real repo plus adversarial cases.

| Test | Cycle 1 (pre-fix) | Cycle 2 (post-fix) |
|---|---|---|
| Pathspec `docs/*.md` matches nested & is anchored | PASS (verified) | PASS (verified) |
| Run A — clean governed set | `scanned 4` / PASS / exit 0 | `scanned 4` / PASS / exit 0 |
| `.claude/skills/**/SKILL.md` (header-less) | Never collected | Never collected |
| Root + `.github/**` exclusion | Excluded | Excluded |
| `docs/templates/**` + `docs/governance/**` deep-subtree exemption | Exempt | Exempt |
| `scripts/verify-repo-state.md` companion | Collected, passes | Collected, passes |
| Run B — 7 violation classes injected | FAIL / exit 1 / 13 (incl. M-1 spurious) | FAIL / exit 1 / 12 (M-1 spurious gone) |
| Multi-defect single file | 4 violations from one file | 4 violations from one file |
| M-2: run outside work tree | `scanned 0` / PASS / exit 0 *(defect)* | `RED … exit 2` |
| M-2: git absent from PATH | (not yet guarded) | `RED … exit 2` |
| Bash 4+ construct scan | clean | clean |

---

## §3 Forward-Pointer Triage

Surfaced during review, out of scope to fix in the RBT-35 script change. **Per operator confirmation (2026-06-17), all forward-pointers below have been addressed by the authoring session this cycle**; the specific dispositions are captured by the authoring session and their respective venues/tickets. Recorded here for the audit trail.

| Ref | Summary | Source | Status |
|---|---|---|---|
| **F1** | `docs/adr/ADR-002-graph-system-of-record.md` still carries the pre-schema identity `Enterprise Architect, Haffey Enterprises` (this validator checks `# Author:` presence, not value). | EA pass / real-repo read | Addressed by authoring session |
| **F2** | Date-prefixed docs (reviews / handoffs / ruling-rationale) are not checked for §5.3 lowercase-slug or the `YYYY-MM-DD-slug` pattern; only the four doctype prefixes get lowercase-slug enforcement. Pre-existing coverage gap in the "minimal-and-growable" checker. | LAA pass | Addressed by authoring session |
| **F3** | The wider `scripts/*.md` reach is not symmetrically exempted at `scripts/templates/*`. Inert today (script templates are `.sh`; no such `.md` exist), latent if md template-companions ever land there. | SA pass | Addressed by authoring session |
| **F4** | RBT-35's cited ruling ledger was not present at `docs/ruling-rationale/2026-06-16-heb-9-phase-2-rulings.md`; R030 *intent* (exempt `.claude/**` as external-tool-convention) was confirmed via the ticket, exact ledger wording unverified at review time. | Substrate fetch | Addressed by authoring session |
| **F5** | Close **RBT-31** as absorbed when RBT-35 merges (the `# Revised:` line absorbs the identity reconcile into this change). | EA pass | Addressed by authoring session |

---

## §4 Audit Outcome

> **PASS — CONVERGED (Cycle 2).** No BLOCKING findings in either cycle. The two MATERIAL findings (M-1 non-ASCII git-quoting; M-2 missing git/work-tree pre-condition) and one COSMETIC (C-1 header self-description) raised in Cycle 1 are resolved in the Cycle-2 staged script and re-verified by executed sandbox; the remaining COSMETIC (C-2 space double-report) is acknowledged no-action. The RBT-35 design intent is met end-to-end: the durable governed-set collection unblocks the deferred HEB-9 SOFIA-Reboot skill deploy by construction, the checker continues to catch every governed-set violation class, and the absorbed RBT-31 identity reconcile is correctly applied. All MATERIAL/COSMETIC items were inherited from the RBT-3 baseline, not introduced by this change. Forward-pointers F1–F5 are out of scope for this script and have been addressed by the authoring session.

**Gate status:** the pre-merge gate for the RBT-35 PR is **satisfied**. Per the cycle discipline, Pass 3 is skipped on a clean Cycle-2 PASS.

*(Note: this review artifact is itself self-conformant with the validator it reviews — date-prefixed `docs/reviews/` filename, lowercase-hyphenated slug, ASCII, with a `# File:`/`# Author:`/`# Created:`/`# Description:` header whose path matches its directory of record.)*

---

## §5 Cross-References

- **Authority:** RBT-35 (Three-hat review per DIRECTIVE-007; ENG-STD-002 governs the amendment).
- **Artifact reviewed:** `scripts/validate-docs-structure.sh` (RBT-35 revision; absorbs RBT-31).
- **Governing standards:** ENG-STD-002 v2.2.0 (§3.5 header, §4.3/§4.4 severity/exit, §5.4 pre-condition, §9 accumulator, §13 AI-implementation); DMS §1.2/§1.3 (governed set), §2.2/§2.3.4 (headers + consumed-snapshot reduction), §3.1/§3.5/§3.6.2 (directories of record), §5.1/§5.2/§5.3 (filename patterns), §9 (CI enforcement); CSD DIRECTIVE-007 §7.2 (severity vocabulary).
- **Related tickets:** RBT-3 (CI bootstrap baseline), RBT-31 (identity reconcile, absorbed), HEB-9 (skill deploy, unblocked).
- **Related reviews:** prior three-hat reviews of record under `docs/reviews/` (ADR-001, ADR-002 cycles).
