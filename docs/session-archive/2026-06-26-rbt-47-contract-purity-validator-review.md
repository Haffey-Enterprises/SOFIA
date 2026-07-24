# File: docs/reviews/2026-06-26-rbt-47-contract-purity-validator-review.md
# Author: Tad Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-26
# Description: Combined three-hat + antagonistic review-of-record for the RBT-47 / HEB-36 execution-leg artifacts (validate-docs-structure.sh contract-purity check + apply-prompt). Serves the pre-execution gate before the Tier-1 apply-prompt is handed to Claude Code.

# Three-Hat + Antagonistic Review — RBT-47 / HEB-36 Execution Leg — 2026-06-26 (Pre-Execution Gate)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-26 |
| **Reviewer** | claude.ai — three-hat (LAA / SA / EA) + antagonistic streams, verification-only per DIRECTIVE-032 §32.3; dispositions ratified by Tad Haffey (EA), Haffey Enterprises LLC (claude.ai-assisted authoring under DIRECTIVE-026 / -032) |
| **Scope** | `scripts/validate-docs-structure.sh` (complete-replacement vendor) + the RBT-47 contract-purity-validator apply-prompt, checked against DMS §7.4–§7.9, DIRECTIVE-023, R043 / R027 / R044–R046, ENG-STD-002, ENG-STD-003, and the RBT-47 / HEB-36 ratified records |
| **Authority** | DIRECTIVE-007 (multi-role review + severity vocabulary); DIRECTIVE-032 (antagonistic review + between-pass discipline); ENG-STD-001 §12.6 (three-hat); the RBT-47 / HEB-36 ratification records |
| **Outcome** | **PASS WITH FINDINGS** — converged across three passes; all 2 BLOCKING + 4 MATERIAL findings dispositioned and folded into the final artifacts (or ratified on the record); COSMETIC items folded or no-action; forward-pointers triaged. Gate satisfied: artifacts ready for Claude Code execution, subject to the two operator close-out items in §3. |

---

## §0 Review Structure & Convergence Arc (first review-of-record for a DIRECTIVE-023 mechanization)

This is the first close-record for a DIRECTIVE-023 contract-purity *mechanization* (prior contract-purity work — HEB-38 Phase-1/Phase-2 — was doctrine + spec; this is the running check). Two reviewer streams ran in parallel and were merged at convergence:

- **Three-hat stream (LAA / SA / EA):** Pass-1 surfaced findings; Pass-2 re-anchored per §11.7.7 against the updated artifacts and confirmed the Pass-1 fixes.
- **Antagonistic stream (DIRECTIVE-032 §32.3, verification-only):** a Pass-1-vintage adversarial pass against the original artifacts.

The streams were complementary, not redundant: the **antagonistic stream caught both Blockers** (B-1 AMBER-trigger-vs-ratification, B-2 baseline-SHA contradiction) that the three-hat stream missed in both passes, while the **three-hat stream caught several Materials/Cosmetics** (rename-coverage, smoke-test relocation, label-query `--limit`, `ACM`→`ACMR` doc-drift) that the antagonistic stream did not raise. Cross-stream coverage is the explicit value recorded here. Convergence reached after the operator dispositioned both Blockers (B-1 ratified; B-2 live-verified) and the artifacts were re-sandboxed (§11.7.4). A finding-ID crosswalk to each stream's original numbering is in §2.6.

---

## §1 Scope

### 1.1 In-scope

- **`scripts/validate-docs-structure.sh`** (complete-replacement vendor) — DMS §1.2 governed-set collection + §2.2/§3/§5 structural checks + the new DIRECTIVE-023 / DMS §7.4–§7.9 contract-purity check (surface-scoped, concrete-ID-anchored), scope flags, AMBER tier, vacuous-green hardening; ENG-STD-002 v2.3.0 conformance.
- **`…/2026-06-26-rbt-47-contract-purity-validator-apply-prompt.md`** — phase structure, pre-flight discipline, vendoring + CI wiring, verification gates, pause-points; ENG-STD-003 v3.0.1 conformance; fidelity to the RBT-47 / HEB-36 ratified records.

### 1.2 Scope boundary stated up front (jurisdiction)

Neither artifact is a DMS §7.5 morphing body — the validator is an ENG-STD-002 script, the apply-prompt an ENG-STD-003 artifact (DMS §7.6 places both classes *outside* DMS contract-purity jurisdiction). The DIRECTIVE-007 §7.2.1 contract-purity lens therefore does **not** bind this review, and inline ruling / tracker / finding IDs in their comments are legitimate (out of §7.6 jurisdiction, and the `[BM]-\d+` matcher does not match `S-`/`C-` prefixes regardless). Findings use the DIRECTIVE-007 §7.2 severity vocabulary with remedy tags.

### 1.3 Out of scope (deliberately)

- **Kit `-template` promotion mechanics** — R045-staged; gated on SOFIA-Reboot's next authoring cycle. The `-template` is authored *fresh against DDR-001*, not by mutating this script (§13.5.9).
- **LILY render** — R045 non-gating cross-consumer corroboration; blocked on HEB-14 → HEB-12.
- **HE-Bedrock self-application** — R046, rides HEB-44.
- **Live `.github/workflows/ci.yml` content** — no SOFIA-Reboot repo access this session; the §2.1b `str_replace` `old_str` uniqueness is asserted (fetched @ `6c76410a`) and verified by the executor at apply time.

---

## §2 Findings

Findings carry **severity** (§2.1–§2.4) and **remedy** (add/fix · remove/relocate · none-default) per DIRECTIVE-007 §7.2. Every finding below is RESOLVED at convergence; each carries its as-resolved disposition. Per DIRECTIVE-032 §32.3 the reviewer surfaced; the operator dispositioned.

### 2.1 BLOCKING findings — must resolve before the pre-execution gate proceeds

#### Finding B-1: Live AMBER trigger contradicted the RBT-47 ratified design note

**Remedy:** none (resolved by ratification, not artifact change)

**Location:** `validate-docs-structure.sh` `check_contract_purity` (unbalanced-fence guard, "First live AMBER trigger"); apply-prompt §0/§4.4 + commit message.

**Description:** RBT-47's ratified Design section stated verbatim that the AMBER tier ships "present-but-untriggered … no AMBER trigger this leg." The implementation shipped a live AMBER trigger (the unbalanced-code-fence reduced-assurance guard, DMS §7.7). The guard itself is sound honest-empirical-floor behavior (an odd fence count makes the awk stripper unreliable); the block was on the discipline (as-built vs. written ratification), not the behavior — runtime impact nil (AMBER = exit 0).

**Why blocking:** under no-presumed-alignment / per-item ratification, an as-built that diverges from the authoritative ticket cannot be treated as final until artifact and record agree.

**Disposition:** **RATIFIED, not stripped.** The trigger is sanctioned; the "no AMBER trigger this leg" line is superseded. Recorded on the RBT-47 trail (reconciliation comment, 2026-06-26). Remaining: the RBT-47 description banner wants an in-editor paste to match the as-built (operator close-out item, §3).

#### Finding B-2: Baseline SHA contradicted the HEB-36 ledger's cited SOFIA-Reboot develop tip

**Remedy:** add/fix (reconcile against live develop before execution)

**Location:** apply-prompt frontmatter `develop_sha_baseline: 6c76410a`, §0, §0.5, §1.3.

**Description:** the apply-prompt asserted SOFIA-Reboot develop tip = `6c76410a` ("post RBT-35 / PR #11, nothing merged since"), while the HEB-36 ruling ledger (R045 Primary-sources, fresh-fetched same day) cited develop @ `d4fc742f` for the post-PR-#11 state — two SHAs both labelled the post-PR-#11 tip. The §1.3 gate makes a wrong base safe (it halts on mismatch) but dead-on-arrival; fresh-fetch-over-recall required reconciliation before execution.

**Why blocking:** a contradicted baseline is exactly the recall-drift the discipline targets; it must be reconciled before execution.

**Disposition:** **RESOLVED — `6c76410a` live-verified.** Operator read `refs/heads/develop` and `refs/remotes/origin/develop` = `6c76410a` (2026-06-26); develop advanced past the HEB-9-era `d4fc742f`. Apply-prompt baseline correct. The HEB-36 ledger's `d4fc742f` is the stale anchor — corrected on the Linear trail when next touched (frozen ledger, DIRECTIVE-031 §31.7; not amended). Recorded on the RBT-47 trail.

### 2.2 MATERIAL findings — folded in-scope

#### Finding M-1: Missing §6.9 LABEL-EXISTENCE-CHECK before PR-open

**Remedy:** add/fix · **Location:** apply-prompt (absent between §1 pre-flight and §4.4 `gh pr create … --label "semver: minor"`).
ENG-STD-003 §6.9 is a MUST: an apply-prompt authoring a PR label verifies it in pre-flight, not at the terminal `gh pr create`. **Disposition: RESOLVED** — new §1.8 LABEL-EXISTENCE-CHECK added (`command grep -qxF`, RED + exit 1 if absent), with the `--limit 100` currency fix (see C-5).

#### Finding M-2: `--base` missing-arg path exited 1, not 2

**Remedy:** add/fix · **Location:** `validate-docs-structure.sh` arg-parse (`--base`).
The original `BASE_REF="${2:?…}"` exits 1 under `set -u`; ENG-STD-002 §4.4 classes argument errors as exit 2 (consistent with the unknown-argument path). **Disposition: RESOLVED** — explicit `[ "$#" -ge 2 ] || { RED; exit 2; }` guard.

#### Finding M-3: Ruling-provenance misattribution — "ratified HEB-36"

**Remedy:** add/fix · **Location:** `validate-docs-structure.sh` `check_contract_purity` scope-discipline comment.
The comment read "(R043 spec + R027 surface-scoping, ratified HEB-36)". Per the authoritative ledgers, R043 was ratified under **HEB-38 Phase-2** (the check-spec) and R027 under **HEB-9 Phase-1** (surface-scoping); HEB-36 (R044/R045) is the *deployment* decision. The misattribution shipped in a kit-bound artifact (R045 zero-relocation ride) and is precisely the ruling-ID-provenance class HEB-41 is chartered to root-cause-fix. **Disposition: RESOLVED** — re-attributed to "R043 check-spec [ratified HEB-38 Phase-2] + R027 surface-scoping [ratified HEB-9 Phase-1]; deployed inside this validator per HEB-36 R044/R045." *(Severity-axis divergence recorded: three-hat stream rated this MATERIAL — kit-bound provenance + HEB-41 class; antagonistic stream rated it COSMETIC — comment, no behavioral effect. Classified MATERIAL here.)*

#### Finding M-4: Rename-with-edit of a morphing body escaped the gate (`--diff-filter=ACM`)

**Remedy:** add/fix · **Location:** `validate-docs-structure.sh` `collect` (diff mode).
`--diff-filter=ACM` excludes status `R`, so a renamed-and-edited ADR/DDR/SDD escaped contract-purity at that touch — a coverage gap in the gate's touch-time mandate. **Disposition: RESOLVED** — collector now `--diff-filter=ACMR`; `--name-only -z` emits the single new (post-image) path for a rename, which is what gets scanned. Robust whether rename-detection is on (status `R`, caught by `R`) or off (`D`+`A`, caught by `A`).

### 2.3 COSMETIC findings — folded or no-action

- **C-1** — `# Author: Thaddeus Haffey` vs corpus-standard `Tad Haffey` (sibling scripts, DDR-001). — add/fix — **RESOLVED** (→ `Tad Haffey`).
- **C-2** — apply-prompt §1.0 cited "§6.10 BASH-INTERPRETER-PROBE" for what is a runtime `${BASH_VERSION:-}` guard (the FP-5 mitigation); §6.10 is the authoring-time per-block `bash -n` probe. — add/fix — **RESOLVED** (comment now distinguishes the runtime guard from the §6.10 authoring-time probe).
- **C-3** — `TRACKER_PREFIX` comment implied the kit `-template` is rendered by substitution from this script (the §13.5.9 prior-art-as-authority pattern R045 rejects). — add/fix — **RESOLVED** (now: `-template` authored fresh against DDR-001, NOT by mutating this file).
- **C-4** — diff-mode smoke test ran pre-commit against an empty diff (`HEAD == base`), with a rationale that mis-stated type-filtering as the cause. — add/fix — **RESOLVED** (relocated to §2.3b post-commit, where the committed delta is real; rationale corrected).
- **C-5** — §1.8 label query omitted `--limit` (gh defaults to 30 → pagination false-RED risk vs the §6.9 canonical form). — add/fix — **RESOLVED** (`--limit 100`).
- **C-6** — cold-read §0 + PR-body described the collector as `…ACM` after the script moved to `ACMR`. — add/fix — **RESOLVED** (both synced to `ACMR`).
- **C-7** — awk body-strip + `SCRIPT_DIR`/`REPO_ROOT` command-subs were unguarded under `set -e` (a bare non-zero abort with no `RED:` line, a seam in the fail-loud posture). — add/fix — **RESOLVED** (awk guarded → RED exit 2; cd command-subs guarded → RED exit 2). Also routed to §3 (FP-4) for the residual `~~~`/indented-block fence limitation.
- **C-8** — aggregate summary uses `FAIL —` / `PASS —` rather than §4.3.1 `RED:` / `GREEN:` prefixes. — no-action — consistent with the `verify-pin-currency.sh` sibling house pattern (`FAIL:` / `OK:` aggregate alongside per-check tier prefixes).
- **C-9** — shipped comments cite pass-local review-finding IDs (`review S-2`, `review C-6`, `SA-2`) that do not map 1:1 to this RoR's canonical numbering (see §2.6 crosswalk). — no-action — jurisdiction-clean (§1.2); useful "why" provenance. Optional future genericization.
- **C-10** — cold-read "(post RBT-35 / PR #11)" reads `6c76410a` as the PR-#11 tip when develop has since advanced (B-2). — no-action — baseline is live-verified correct; the reconciliation comment records the advance.

### 2.4 No-drift confirmations (POSITIVE)

- **P-1 — §13.8 command-grep:** every verification-gate grep uses `command grep` (header check, doctype check, fence count, contract-purity match, label check); awk is a transform and the gate grep on its output is command-prefixed.
- **P-2 — Concrete-ID anchoring + co-traveling-ref pass:** `[^[:alnum:]_]` boundaries correctly pass the §7.4-permitted refs — `ADR-NNN`/`DDR-NNN`/`SDD-NNN`/`ENG-STD-NNN`/`DIRECTIVE-NNN` none match the ID classes; `§X.Y` and `DOC@X.Y.Z` pins pass; schematic teaching forms (`R{N}`/`B-N`) carry a non-digit and never match. Faithful to R043 / R027.
- **P-3 — Surface-scoping per R045 / DMS §7.5:** fence-toggle precedes section detection (teaching tokens in fenced examples skipped); `## Change Log` + `Cross-References`/`References` section + `**References**` row all stripped; morphing-body doctype gate (ADR/DDR/SDD) + whole-exclusion of audit-surface doctypes.
- **P-4 — Vacuous-green hardening:** git / work-tree / base-resolvability / cd / mktemp / collector pre-conditions all RED exit 2; collector captured to a tempfile with its own exit checked. The legitimate empty scan (0 `.md` touched in a script-only PR) is a true green, not a vacuous one.
- **P-5 — `--all` + DIRECTIVE-029 per R046:** `--all` = full-corpus structural; contract-purity correctly OFF under `--all` (grandfather-until-touched, §7.9); CI `push → --all` preserves full-corpus structural coverage.
- **P-6 — POSIX-ERE portability:** identifier classes use `[^[:alnum:]_]` boundaries (not `\< \>`), identical under BSD (macOS local) and GNU (CI) grep.
- **P-7 — Version pins + exit-code conventions:** script `# Standard: ENG-STD-002 v2.3.0` and apply-prompt `governing_standard: ENG-STD-003 v3.0.1` both match live headers; script uses the ENG-STD-002 §4.4 2-tier exit codes, apply-prompt the ENG-STD-003 §3.4 flat exit-1 — no cross-contamination.
- **P-8 — ENG-STD-002 §3.5 header:** complete; `# Revised:` carries the RBT-47 parenthetical (Bucket-A); §0.5 asserts §13.7 author-against-committed-state; §6.10 authoring-time `bash -n` sweep run 17/17 clean.
- **P-9 — DIRECTIVE-026 tier discipline + §7.6 jurisdiction:** claude.ai authors → Downloads staging → Claude Code executes; no auto-post to Linear/Notion; post-merge three-layer capture left to the operator (§5). Inline operational IDs in both artifacts are jurisdiction-clean (§7.6) — no false self-finding.
- **P-10 — Apply-prompt ruling-citation accuracy:** §0.5 "R043 spec + R027"; cold-read R044/R045; out-of-scope R045 kit-promotion-staging; close-records R044–R046 — all map correctly to the HEB-36 SoR + HEB-38 Phase-2 SoR.
- **P-11 — `set -euo pipefail` + accumulator is `-e`-safe** across the hot path (every command-sub / pipeline / `&&`–`||` list guarded), including the awk/cd seams closed under C-7.

### 2.5 Normative interpretation

No open normative-interpretation question requires in-cycle codification. The matcher's context-blindness (standalone `R2` / `B-12` / `M-1` false-RED with no AMBER escape valve) is a property of the ratified R043 closed-subset spec, not an RBT-47 defect; the natural refinement (ambiguous-ID → AMBER) is routed forward (FP-1). The B-1 AMBER-trigger ratification is captured on the RBT-47 trail, not as a new ruling.

### 2.6 Finding-ID crosswalk (stream traceability)

| RoR ID | Three-hat stream | Antagonistic stream | Note |
|---|---|---|---|
| B-1 | — (missed both passes) | B-1 | AMBER trigger vs ratification |
| B-2 | — (deferred SHA, not cross-checked) | B-2 | Baseline contradiction |
| M-1 | (Pass-2 independently added §1.8) | M-1 | §6.9 label check |
| M-2 | — | M-2 | `--base` exit code |
| M-3 | S-1 (MATERIAL) | C-1 (COSMETIC) | provenance — severity split |
| M-4 | S-2 | — | rename `ACMR` |
| C-1 | — | C-4 | author name |
| C-2 | (Pass-2 independently fixed) | C-3 | §6.10 cite |
| C-3 | W-1 | C-2 | template wording |
| C-4 | S-3 | — | smoke-test relocation |
| C-5 | C-7 | — | label `--limit` |
| C-6 | C-8 | — | `ACM`→`ACMR` drift |
| C-7 | S-4 | C-5 | fail-loud guards + `~~~` limitation |
| C-8 | S-5 | — | `FAIL —`/`PASS —` vocab |

---

## §3 Forward-Pointer Triage

### Candidate RBT-38 (existing) — context-blind ID classes; no AMBER escape valve

**Source:** FP-1 (antagonistic) / W-2 (three-hat). **Description:** `R\d+` / `[BM]-\d+` match standalone `R2`, `B-12`, `M-1` tokens (requirement labels, registers, releases) in a consumer ADR/DDR/SDD body, routing all hits to RED with no AMBER ambiguity path while CI-bypass is prohibited. Faithful to the ratified R043 spec; grandfather-until-touched bounds the blast radius. **Proposed disposition:** fold into RBT-38 (growable-checker) or a R043 / DIRECTIVE-023 refinement — an "ambiguous-ID → AMBER" path is the natural future move. Not an RBT-47 defect.

### Candidate (kit `-template` authoring) — foreign-prefix tracker IDs slip the matcher

**Source:** FP-2 (antagonistic). **Description:** `HEB-36` in a SOFIA-Reboot body matches neither `RBT-\d+` nor a boundary-clean `[BM]-\d+` (the `B` in `HEB` is alnum-preceded). Known closed-subset blind spot; the §7.2.1 lens covers it at PR review. **Proposed disposition:** note at kit `-template` authoring (cross-consumer prefix generalization) and/or the R043 refinement.

### Candidate (kit `-template` authoring) — `is_exempt` governance-class inversion at promotion

**Source:** FP-3 (antagonistic). **Description:** `is_exempt` whole-exempts `docs/governance/*` + DMS as consumed read-only standards — correct for SOFIA-Reboot-as-consumer, but in HE-Bedrock those are *authored morphing bodies*. **Proposed disposition:** promotion-time concern, already gated on SOFIA-Reboot's next-authoring cycle (R045 / HEB-36 3a); flag for the `-template` authoring.

### Candidate RBT-38 (existing) — `~~~` / indented-block fence-strip limitation

**Source:** C-7 / FP-4. **Description:** the awk stripper handles backtick fences only; `~~~` fences and 4-space indented blocks are not stripped (a teaching token inside one would reach the matcher). Corpus convention is backtick fences across all templates; documented in-script as a limitation. **Proposed disposition:** RBT-38 if SOFIA-Reboot bodies ever adopt `~~~`.

### Operator close-out items (not forward-pointers — close-out actions)

| Item | Owner | Note |
|---|---|---|
| RBT-47 description banner update | Tad | In-editor paste before close: supersede "no AMBER trigger this leg" + the script-only scope framing to match the as-built (DIRECTIVE-026 manual-paste caveat) |
| HEB-36 ledger stale SOFIA-Reboot tip (`d4fc742f`) | Tad | Correct on the Linear trail when next touched; frozen ledger not amended (DIRECTIVE-031 §31.7) |

### Forward-pointer triage summary

| Proposed venue | Summary | Disposition |
|---|---|---|
| RBT-38 / R043 refinement | Context-blind ID classes; ambiguous-ID → AMBER | Route forward (not RBT-47 defect) |
| Kit `-template` authoring | Foreign-prefix tracker IDs slip the matcher | Note at promotion / R043 refinement |
| Kit `-template` authoring | `is_exempt` governance-class inversion at promotion | Gated on R045 / HEB-36 (3a) |
| RBT-38 | `~~~` / indented-block fence-strip limitation | Route forward if `~~~` adopted |

---

## §4 Audit Outcome

> **PASS WITH FINDINGS.** Across three passes (three-hat Pass-1 → Pass-2; antagonistic Pass-1), the combined review surfaced **2 BLOCKING** findings (B-1 AMBER-trigger-vs-ratification → ratified on the RBT-47 trail; B-2 baseline-SHA contradiction → `6c76410a` live-verified), **4 MATERIAL** findings (M-1 §6.9 label check, M-2 `--base` exit code, M-3 ruling provenance, M-4 rename coverage — all folded into the final artifacts), and **10 COSMETIC** items (eight folded, two no-action). All forward-pointers are triaged to RBT-38 / R043-refinement / kit-`-template` authoring (§3). The converged artifacts were re-sandboxed (§11.7.4).

**Gate satisfied:** the RBT-47 / HEB-36 execution-leg artifacts are ready for Claude Code execution, subject only to the two operator close-out items in §3 (RBT-47 banner paste; HEB-36 ledger trail-correction), neither of which is an artifact defect. The dual-stream design is recorded as load-bearing: the antagonistic stream caught both Blockers the three-hat stream missed, and the three-hat stream caught four Materials/Cosmetics the antagonistic stream did not.

---

## §5 Cross-References

- **Authority:** DIRECTIVE-007 (multi-role review / severity); DIRECTIVE-032 §32.3–§32.4 (antagonistic + between-pass); ENG-STD-001 §12.6 (three-hat); DIRECTIVE-026 (claude.ai ↔ Claude Code role discipline).
- **Documents reviewed:** `scripts/validate-docs-structure.sh`; `…/2026-06-26-rbt-47-contract-purity-validator-apply-prompt.md`.
- **Spec authorities:** DIRECTIVE-023; DMS §7.4–§7.9; R043 (check-spec, HEB-38 Phase-2); R027 (surface-scoping, HEB-9 Phase-1); R044–R046 (deployment, HEB-36).
- **Disposition tracking:** RBT-47 reconciliation comment (2026-06-26); HEB-36 ruling-rationale SoR (R044–R046); HEB-38 Phase-2 SoR (R043).
- **Related work:** RBT-47 (execution leg); HEB-36 (source); RBT-35 (governed-set + glob-hardening substrate); RBT-38 (growable-checker, forward-pointer venue); HEB-41 (ruling-ID-registry root-cause, M-3 class); HEB-44 (Bedrock self-application, R046).
- **Forward cadence:** kit-promotion review at SOFIA-Reboot's next authoring cycle (R045 validating second case); `-template` authored fresh against DDR-001.
