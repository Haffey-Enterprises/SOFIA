# Code Authoring Handover — DDR-001 Data Architecture (RBT-12)

> **For: Claude Code (in-repo, SOFIA-Reboot, on `develop`).** This is the DIRECTIVE-026 authoring
> leg. The design is fully ratified and three-hat **PASS-CONVERGED** (review of record provided).
> You author the DDR file and run the git operations (branch → place → commit → push → PR),
> pause-point mode. **You are rendering a decided, three-hat-converged design — not authoring cold.**
> Do not re-litigate the design. claude.ai did the design and will do the post-merge Notion/Linear
> captures.

## Inputs (provided with this prompt)
- **`DDR-001-design-substrate-v0.3.md`** — the ratified, three-hat-converged design. **Authoritative:** author the DDR from it; reproduce its content and structure faithfully. **Strip its preamble + disposition log** (design-process scaffolding, not DDR content).
- **`2026-06-19-rbt-12-ddr-001-data-architecture-three-hat-review.md`** — the review of record. **Vendor to `docs/reviews/`.**

## Author `docs/ddr/DDR-001-data-architecture.md`
Conform to the DDR doctype conventions and the governance corpus: ADR-002 v1.0.0, ADR-001 v1.0.0, ledger R3/R5/R6/R7/R8/R9/R10/R20/R22, DMS, ENG-STD-001, CLAUDE.md §3.4. The v0.3 substrate is the authoritative content — author the DDR as its faithful realization.

**Metadata / header:**
- `# File: docs/ddr/DDR-001-data-architecture.md` · `# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC` · `# Created: 2026-06-19` · `# Description: …` · **no `# Revised:`** (initial authoring, R18).
- Document ID **DDR-001** · **Version 1.0.0 ACCEPTED** (design three-hat-converged; the review of record is the acceptance evidence) · **Platform Version row deleted** · Authors **Thaddeus Haffey (LAA / SA / EA)** · Supersedes **None** · single original-authoring Change Log row at 1.0.0.

**Fidelity-critical (all already in the substrate; reproduce exactly — do not "simplify"):**
- **RG write-authority is two-component:** ASA authors `ReasoningProgress` content; **AOE owns the `ReasoningSession` lifecycle**. "Session root corresponds to `ReasoningSession`." The gateway RG-write role carries **both** writers, gateway-mediated, driver-less. **Never write "single-writer."**
- **§ Decision** as numbered **Decision.1–Decision.6**, each one-line testable, prose following.
- **References** section-pinned: ENG-STD-001 §25.1 (GKE exception), §18 data-classification (pin the exact subsection against a fresh ENG-STD-001 read); ledger R-numbers; ADR-001/002. No bare "touchpoints."
- **Old-corpus citations** qualified "prior-SOFIA DDR-NNN (intent source, not a live Reboot reference)" per CLAUDE.md §3.4.
- **Firestore** = ADR-002 §2.4's "immutable workflow snapshots," concretized to per-version produced-solution (ASD) snapshots.
- **Spike findings** record the structural capability requirement + recovery-boundary note; do **not** reconstruct the trial's edition-feature blocker; do **not** attribute the rejection to Community's single-database limit (contradicts §2.3).
- **§ Conformance checks** (six), aspirational per DIRECTIVE-024 §24.1, citing **RBT-33** for all six.
- **Cross-refs:** upstream ADR-001/002; sibling-forward DDR-003 (RBT-14); downstream DDR-002 (RBT-13) + SDDs, **R8 one-way** (never cite DDR-002 as authority).
- **No "Humana"; source systems by class, not vendor product.**

## Vendor the review of record
Place `2026-06-19-rbt-12-ddr-001-data-architecture-three-hat-review.md` in `docs/reviews/`.

## Git (pause-point mode)
- Branch **`feature/rbt-12-ddr-001-data-architecture`** off `develop`.
- Place the DDR + the review of record; commit (atomic, or two commits: DDR; review). Commit subject e.g. **`docs(ddr): accept DDR-001 Data Architecture (RBT-12)`**; body **`Refs RBT-12`**; **no `Co-Authored-By` trailer** (standing convention per the ledger).
- Push; open **PR → `develop`**. Confirm the required check **`validate-docs-structure`** is green.
- **PAUSE before merge — operator gate.** Report: branch, files placed, CI status, PR link.

## On operator "go"
Squash-merge to `develop`; report the new `develop` SHA; delete the feature branch (remote + local).

## Not your job (claude.ai handles post-merge)
RBT-12 → Done (three-layer capture); ledger build-leg entry (develop SHA advance); RBT-13 (DDR-002) unblocked. Just report the merge + SHA and stop.
