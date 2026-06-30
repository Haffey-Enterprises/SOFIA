# File: docs/ruling-rationale/2026-06-03-adr-001-reasoning-architecture-spine.md
# Author: Thaddeus Haffey — Enterprise Architect, Haffey Enterprises
# Created: 2026-06-03
# Description: Ruling-rationale ledger per DIRECTIVE-031 §31.2 (Architecture α — 2 rulings). Captures the two ruling-bearing dispositions from the ADR-001 (RBT-7) authoring + three-hat review session, 2026-06-03. Companion to the Reboot Decision Ledger (Notion) Lightened Ruling-Capture, where these are recorded as R18 / R19.

---
session_date: 2026-06-03
develop_sha_baseline: 69dd598
session_close_status: COMPLETE
next_session_scope: RBT-30 (reboot template adaptation), then RBT-8 (ADR-002 Graph as System of Record)
---

# ADR-001 Spine Session Ruling-Rationale Ledger — Reasoning Architecture

## §0 Document Metadata

| Field | Value |
|---|---|
| **Session** | ADR-001 (RBT-7) authoring + three-hat review, 2026-06-03 |
| **Author** | Thaddeus Haffey — Enterprise Architect, Haffey Enterprises (claude.ai-assisted) |
| **Architecture** | **α** (operator-judgment exception; 2 rulings ≤ 3 — rulings enumerated directly, no §1 inventory) |
| **Develop SHA baseline** | `69dd598` (ledger-corroborated via the Decision Ledger build-leg log; private-repo connector gap precluded direct `git`/GitHub verification this session) |
| **Schema authority** | DIRECTIVE-031 §31.2 (Reboot uses the Lightened Ruling-Capture in the Notion Decision Ledger; this .md is the repo-committed companion) |
| **Cross-surface** | Recorded in the Notion Reboot Decision Ledger as **R18** / **R19** |
| **Status** | Ruling-bearing dispositions ratified at session 2026-06-03; substrate-of-record |

---

## §2 Ruling Details

### R18 — Fresh-set document history surfaces (Narrow R2)

**Ruling text.** Fresh-set documents retain the HE-Bedrock kit's history-bearing sections (Version, Supersedes, Amendment Process, Review & Approval, Change Log). R2's "no history" means no old-corpus archaeology and no pre-acceptance drafting/DELTA trail — not removal of those sections. A fresh document is authored as a single artifact: it holds Version `0.1.0` while PROPOSED (no per-revision bump trail; in-session review iterations are session process, captured in review/ruling-rationale artifacts, not document versions) and promotes to `1.0.0` at ACCEPTED. Its Change Log carries only the original-authoring row until post-acceptance amendments accrue; `# Revised:` is absent during initial authoring and begins at the first post-1.0.0 amendment. Where the kit's templates and the DMS conflict on naming, DMS governs (Document ID; Change Log).

**Rationale.**

(i) **Reconciles R2 with R11.** R2 (author-clean, no history) and the adopted pristine kit (R11), which mandates history-bearing sections, appeared to conflict. The narrow reading dissolves it: the sections stay; what R2 forbids is importing old-corpus lineage and accumulating a pre-acceptance morph/DELTA trail.

(ii) **The collapsed-trail middle was incoherent (empirical, this session).** Carrying a drafting-version trail (`0.1.0 → 0.2.0 → 0.3.0`) while collapsing the Change Log to one row produced three mutually inconsistent accounts of the document's state (Pass-2 SA-1). The single-artifact model (one advancing version, single original-authoring row) is the only form that keeps Version, Change Log, and Reviewers mutually consistent.

(iii) **Forward-maintenance is preserved.** Post-acceptance amendments accrue Change Log rows and `# Revised:` stamps normally — the "needed going forward" maintenance surface the operator required.

**Primary sources cited.**
- Reboot Decision Ledger R2 (author-clean), R11 (adopt pristine kit), F-kit-1 (consumed kit non-conformance + principled exemption path).
- DMS §2.2 (header/history), §2.3.1 (Document ID), §2.2 r5 (Change Log), §4.7 (drafting-version convention — overridden for fresh-set docs by this ruling).
- ADR-001 three-hat review Pass 1 (EA-1), Pass 2 (EA-1 persisted + SA-1 incoherence), Pass 3 (closure verification).

**Options considered and declined.**

1. *Broad R2 — drop all history sections.* Declined — loses the forward-maintenance Change Log the kit requires and the operator wants.
2. *Literal kit — full drafting-version trail in the Change Log.* Declined — reintroduces the DELTA trail R2 sheds and produces the version/Change-Log/Reviewers incoherence the review flagged.

**Forward implications.** Binds the entire fresh set (ADR-002…005, all DDRs/SDDs). Requires a reboot-specific template adaptation so downstream authors inherit the model by template, not per-document review → **RBT-30**. The kit templates remain consumed read-only; the adaptation is applied reboot-specifically via the F-kit-1 exemption-path precedent, and stands as an upstream observation for the next kit re-snapshot.

**Cross-references.** R2, R11, R13 (renumber), F-kit-1; sibling R19 (same session).

**Drift-risk flags.**
- *Avoids:* the morph-trail / version-archaeology pattern R2 exists to prevent; and the incoherent collapsed-middle surfaced at Pass 2.
- *Preserves as risk:* a downstream author copying the unadapted kit template could reintroduce the version-trail/naming pattern. *Mitigation:* RBT-30 (template adaptation), sequenced before RBT-8.

**Other.**
- *Ratification venue:* claude.ai design session 2026-06-03 (operator ratified "D1 ratified").
- *Cross-surface state:* Notion Decision Ledger R18; this ledger; ADR-001 v1.0.0 conforms in every particular.

---

### R19 — Reasoning-architecture propagation (no dedicated directive)

**Ruling text.** Propagation of the ADR-001 reasoning-architecture commitment across design work is carried by the ADR-001 §6 compliance checks plus the repo-root `CLAUDE.md` binding-record cross-reference; no dedicated propagation directive is required for that propagation. This is distinct from, and neither requires nor pre-empts, the runtime Directives-Context-Envelope Bridge under re-evaluation in A5 (RBT-11).

**Rationale.**

(i) **Criterion-shift from prior ADR-005 §8(d).** The prior corpus made propagation-directive codification a *precondition* for downstream reasoning-architecture work. Under the reboot's clean-author posture (R2) and the non-carriage of the prior provisional DIRECTIVE-035, the §6 architecture-review checks are themselves the propagation mechanism; a separate directive is redundant for reasoning-architecture propagation.

(ii) **Avoids overreach into an open charter.** An affirmative corpus-wide "no propagation directive" would brush against RBT-11 (A5), which is chartered to re-evaluate the (distinct, runtime) Directives-Context-Envelope Bridge. Scoping the stance to reasoning-architecture propagation and explicitly disclaiming pre-emption keeps the spine within its lane.

**Primary sources cited.**
- Reboot Decision Ledger R2; CSD DIRECTIVE-035 (RESERVED in the reboot CSD); prior ADR-005 §8(d) (intent source only).
- ADR-001 §6 (Compliance / Propagation); RBT-11 (A5 charter).
- ADR-001 three-hat review Pass 1 (SA-3), Pass 2 (EA-2).

**Options considered and declined.**

1. *Carry the prior "codification-is-a-precondition" stance.* Declined — blocks downstream work on an unbuilt directive.
2. *Affirmatively rule out any propagation directive corpus-wide.* Declined — overreaches RBT-11's open, distinct (runtime) charter.

**Forward implications.** Downstream reasoning-architecture work propagates via §6 + CLAUDE.md, no directive gate. RBT-11 remains free to decide the runtime directives-bridge question on its own terms.

**Cross-references.** R2; sibling R18 (same session); RBT-11 (A5).

**Drift-risk flags.**
- *Avoids:* an unbuilt-directive precondition blocking the fresh set; and spine overreach into a sibling ticket's charter.
- *Preserves as risk:* none material; the runtime-bridge question is explicitly left open to RBT-11.

**Other.**
- *Ratification venue:* claude.ai design session 2026-06-03 (operator confirmed "D2 confirmed").
- *Cross-surface state:* Notion Decision Ledger R19; ADR-001 §6 wording matches scope.

---

## Decisions Deferred (forward-pointer ledger only)

| Decision | Forward to | Why deferred |
|---|---|---|
| Reboot-specific template adaptation (R18 propagation by template) | RBT-30 | Distinct work item; should precede RBT-8 |
| ADR-002 §-anchor for the ReasoningProgress decision (EA-3) | RBT-8 authoring | Section pins when ADR-002 is authored |
| Upstream kit re-snapshot (F-kit-1 + RBT-30 deltas) | next kit re-snapshot | Consumed read-only; out of reboot's edit scope |

---

## Cross-References

- *Session-handoff:* `docs/session-handoffs/2026-06-03-adr-001-reasoning-architecture-spine.md`
- *Subject artifact:* `docs/adr/ADR-001-reasoning-architecture.md` (v1.0.0 ACCEPTED)
- *Governance authority:* DIRECTIVE-031 §31.2; Reboot Decision Ledger (Notion) R18 / R19
- *Format note:* Reboot uses the Lightened Ruling-Capture in Notion as the primary ruling instrument; this .md is the repo-committed companion.

---

*End of ADR-001 spine session ruling-rationale ledger v1.0.0.*
