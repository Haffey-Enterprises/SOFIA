# File: docs/reviews/2026-06-15-adr-002-three-hat-review.md
# Author: Thaddeus Haffey — Enterprise Architect, Haffey Enterprises
# Created: 2026-06-15
# Description: Three-hat (LAA/SA/EA) review of record for ADR-002 (Graph as System of Record), executed under RBT-8 as the PROPOSED→ACCEPTED acceptance gate per ENG-STD-001 §12.6 / DIRECTIVE-007. Records dispositioned findings across the four-tier severity vocabulary and the per-hat verdicts.

# Three-Hat Review — ADR-002 (Graph as System of Record) — 2026-06-15 (RBT-8 Acceptance Gate)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-15 |
| **Reviewer** | Thaddeus Haffey — Enterprise Architect, Haffey Enterprises (claude.ai-assisted three-hat pass under DIRECTIVE-007) |
| **Scope** | Single-document three-hat (LAA/SA/EA) review of `ADR-002-graph-system-of-record.md` v0.1.0 PROPOSED, for conformance to the governance corpus, fidelity to the Decision Ledger rulings RBT-8 bakes in, and architectural soundness/timing. |
| **Authority** | RBT-8 ("A2 — Author ADR-002 …"; acceptance = three-hat → ACCEPTED), ENG-STD-001 §12.6, DIRECTIVE-007 (Multi-Role Review). |
| **Outcome** | **FINDINGS RAISED — NOT YET CONVERGED.** 1 BLOCKING + 3 MATERIAL open; ADR remains **PROPOSED** pending disposition + a Cycle-2 re-pass. Document is structurally and substantively strong; no fabricated rationale or strawman alternatives; the open items are an unfilled backlog-ID placeholder and three conformance/trace gaps. |

---

## §1 Scope

### 1.1 In-scope per RBT-8 + DIRECTIVE-007

- `~/Downloads/REBOOT_FILES/ADR-002-graph-system-of-record.md` (v0.1.0, PROPOSED, 2026-06-15) — full-document three-hat pass: §1 Context through §8 Change Log, plus the `# File:` header and metadata table.
- Conformance baseline: the ADR template, DMS §2.2/§4, ENG-STD-001 (§12.6 review gate, §25.1 deployment runtime), and the ACCEPTED exemplar ADR-001 (Reasoning Architecture).
- Ruling-trace baseline: Reboot Decision Ledger (R3, R4, R5, R6, R7, R9, R10, R12, R18, R19) and the RBT-8 ticket scope.

### 1.2 Method

Fresh-fetch of all canonical authorities (project-knowledge corpus read top-to-bottom; ledger and RBT-8 fetched live at review time, not from session recall, per the fresh-fetch discipline). Findings are organized by the four-tier severity vocabulary (DIRECTIVE-007 §7.2); the per-hat verdicts are summarized in §2.0 and aggregated per ENG-STD-001 §12.6 (any BLOCKING → `pause`; else any MATERIAL → `proceed-with-changes`; else → `proceed`).

### 1.3 Out of scope (deliberately)

- The forthcoming Data Architecture design (DDR-001 / RBT-12): plane enumeration, the graph-gateway API shape, read/write paths, snapshot mechanics — ADR-002 correctly defers all of these. Not verified here.
- Service-level realization (SDDs): the ReasoningProgress artifact's fields and write path — deferred to the relevant SDD; not verified here.
- Upstream template/kit naming (the `Executive Architect, Haffey Enterprises LLC` placeholder author-line vs. the realized fresh-set convention) — RBT-30's lane; noted as COSMETIC / forward-pointer only, not absorbed.
- Commit-message concerns (e.g., `Co-Authored-By` trailers) — the ADR is not yet committed; out of scope.

---

## §2 Findings

### 2.0 Per-hat verdict summary

| Hat | Question | Findings raised | Verdict |
|---|---|---|---|
| **LAA** — what is this change / scope match to RBT-8 | Ticket-to-artifact scope and ruling trace | M-2 | `proceed-with-changes` |
| **SA** — how does this conform | Template / DMS / ENG-STD / cross-reference conformance | **B-1**, M-1 (shared), M-3 | `pause` |
| **EA** — should it land in this shape at this time | Posture, reversibility, timing, cross-corpus integration | M-1 (shared) | `proceed-with-changes` |

All three `proceed` is required for approval; the SA hat is at `pause` on B-1, so the gate is **not satisfied** this cycle. The ADR remains PROPOSED.

### 2.1 BLOCKING findings — must resolve before the ACCEPTED gate is satisfied

#### Finding B-1: Unfilled `{{RBT-NN}}` placeholder in the Compliance section

**Location:** `ADR-002 §6` (Enforcement paragraph) — `enforcement-mechanization is tracked at {{RBT-NN — enforcement-mechanization backlog item, to file}}`.

**Description:** §6 carries a literal unfilled `{{double-brace}}` authoring placeholder for the enforcement-mechanization backlog item. The ADR template's default-compliance pattern (template §6) requires that the tracking backlog item be *filed* and its real identifier substituted — "aspirational compliance with a tracking item is honest; aspirational compliance with no tracking item is debt that compounds."

**Why blocking:** §6 is a normative section. An unresolved template placeholder cannot survive into an ACCEPTED normative document; it is exactly the kind of authoring-fill that the acceptance gate exists to catch. It also leaves the compliance commitment without a real tracking anchor.

**Disposition (proposed):** File the enforcement-mechanization backlog item (CI / schema validators for the store-authority and write-authority checks — the mechanizable subset §6 itself names), then substitute its real `RBT-NN` into §6. Captured below as forward-pointer candidate **RBT-NEW-1**. Resolvable in a single edit + ticket; no re-deliberation needed.

### 2.2 MATERIAL findings — in-scope-fix or dispositioned

#### Finding M-1: Neo4j-on-GKE runtime decision is attributed to this ADR but not carried by it

**Location:** `ADR-002 §2.2 / §5.2` (what is committed about the graph platform) vs. `CLAUDE.md §1.1` (platform-identity table) and `ENG-STD-001 §25.1`.

**Description:** CLAUDE.md §1.1 states, as settled platform identity, that *"Neo4j Enterprise is self-managed on GKE per the graph system-of-record ADR."* ENG-STD-001 §25.1 makes Cloud Run the default and requires the **GKE-over-Cloud-Run selection for a given service to be documented in an ADR** (stateful workloads being the canonical justification — Neo4j is exactly that case). ADR-002 *is* the graph system-of-record ADR, yet it makes no deployment-runtime commitment: it commits the graph platform (Enterprise, §2.2) and deliberately defers *topology* (cluster count / HA, §5.2) — but compute-runtime (GKE vs. Cloud Run) is a distinct axis from topology, and §5.2's deferral does not cover it. The result is a dangling cross-reference: CLAUDE.md points at this ADR for a decision the ADR does not contain, and a §25.1-required ADR home for the GKE choice is currently empty.

**Why material (not blocking):** The ADR's core principle (graph as system of record) is sound and complete without the runtime decision; this is a corpus-consistency / unhomed-decision gap, not a flaw in the principle. But it should not persist into ACCEPTED, because acceptance would freeze an active CLAUDE.md→ADR inconsistency and leave a §25.1 obligation unsatisfied.

**Disposition (proposed) — genuine fork, awaiting ratification:**
- **(a)** Add a deployment-runtime sub-decision to ADR-002 (Neo4j Enterprise self-managed on GKE, justified by §25.1's stateful-workload criterion). *Constraint:* there is **no ledger ruling** for a GKE-runtime decision today (R3 = edition; R4 = topology deferred). Per the pre-authoring discipline (DIRECTIVE-034) and no-fabrication rule, adding this sub-decision requires a deliberated, ratified runtime ruling first — it cannot simply be authored in.
- **(b)** Correct CLAUDE.md §1.1 to stop attributing the GKE-self-managed decision to this ADR (CLAUDE.md is project-owned and edited-to-fit), and route the runtime decision to its proper future home (operational/deployment design).

Recommend (a) if a runtime ruling is ready to ratify (it gives §25.1 its required ADR home); otherwise (b) to clear the inconsistency now and defer the runtime ADR. **Not to be actioned without explicit ratification of which fork.**

#### Finding M-2: RBT-8's ledger-citation list is incomplete relative to the ADR's ratified content

**Location:** `RBT-8` ("Ledger. R3, R4, R5, R6, R9, R10.") vs. `ADR-002 §2.5, §2.6`.

**Description:** RBT-8 cites the six rulings it "bakes in" (R3/R4/R5/R6/R9/R10), and all six are present and correctly placed in the ADR. But the ADR also carries two sub-decisions outside that cited set:
- **§2.6** (ASA authors ReasoningProgress; AOE owns ReasoningSession lifecycle) bakes in **R7** — and R7's own rationale explicitly designates **ADR-002 as the fresh-set home** for that ruling. So §2.6 is correctly in-scope by ruling; the defect is that RBT-8 never cites R7.
- **§2.5** (sole-owner graph-access gateway; knowledge-service sole Neo4j owner) expresses **R12** (fresh-set inventory) as realized in CLAUDE.md §6 ("knowledge-service: KG/RG gateway; sole Neo4j owner"). It is a faithful SoR-consequential expression, but its grounding is inventory-level (R12 + CLAUDE.md §6) rather than a discrete access-authority ruling, and it too is absent from the ticket's citation.

**Why material:** This is the LAA hat's scope-trace concern. The ADR content is *correct*; the gap is in the ticket-to-artifact trace ("each authoring issue cites its ledger ruling(s)" — ledger References). An incomplete citation weakens the audit trail and could later read as un-ratified scope creep when it is in fact ratified (R7) / inventory-grounded (R12).

**Disposition (proposed):** Update RBT-8's ledger citation to add **R7** (home = ADR-002) and reference **R12** for §2.5's gateway grounding. This is a three-layer-capture edit on the decided-upon ticket (RBT-8) — **held for ratification** before any Linear write, per capture-where-decided + no-presumed-alignment.

#### Finding M-3: The Community-rejection rests on an asserted, unspecified capability

**Location:** `ADR-002 §2.2` (Enterprise is load-bearing) + `§2.3` (single-instance logical subgraphs) + `§4.1` (Alternative A rejection) + `§2.2` substitution contract.

**Description:** §2.2/§4.1 reject Neo4j Community on the load-bearing grounds that *"Community cannot realize the plane model."* But the specific Enterprise-only capability is never named — §2.2 describes it only as "logical multi-plane traversal within a single instance," which is close to circular. This sits in apparent tension with §2.3's own framing that the planes are *"logical subgraphs within one Neo4j instance"* realized as *"first-class single-database graph operation[s]"*: a single-database, label/namespace-partitioned realization is not obviously Enterprise-gated. The §2.2 **substitution contract** ("any replacement must satisfy the logical multi-plane traversal capability this section names") is only testable if that capability is specifiable.

**Honest framing:** this gap is inherited from the ruling, not introduced by the ADR — ledger R3 likewise asserts "Community could not create the necessary planes" as "the load-bearing reason" without naming the capability. The ADR faithfully carries the ruling. This is an empirical-floor / verifiability note, not a contradiction.

**Why material:** §2.2's substitution contract and §4.1's rejection are both load-bearing commitments whose verifiability depends on naming the capability. Without it, a future reader cannot independently check the Community rejection or evaluate a proposed substitute against the contract.

**Disposition (proposed):** Name the specific Enterprise capability (or capability class) that the five-plane model requires — at the altitude appropriate to an ADR (the *class* of capability, with the precise mechanism owned by DDR-001). If the original deliberation did not establish the specific capability, record that honestly rather than back-fill a rationalization. Resolvable in scope; does not block the principle.

### 2.3 COSMETIC findings — noted, no-action

- **Template author-line divergence.** ADR-002's `# Author:` line reads `Thaddeus Haffey — Enterprise Architect, Haffey Enterprises`, which **matches the ACCEPTED exemplar ADR-001 exactly** and the operator's realized identity. The ADR template / consumed-standard headers still carry the kit-author placeholder `Executive Architect, Haffey Enterprises LLC`. ADR-002 correctly follows the realized fresh-set convention; the divergence is an upstream template/kit concern (RBT-30 lane), not an ADR-002 defect. No action here.
- **Amendment Process row** omits the template's "Prior versions retained in version control." sentence — but this matches ADR-001's realized wording exactly, so it is conformant-to-precedent, not drift. No action.

### 2.4 No-drift confirmations (positive findings)

*Per DIRECTIVE-007 §7.2, these are required audit-trail substrate, not padding — each is an explicit "checked and conformant."*

- **Template / structural conformance.** Section order §1–§8 matches the ADR template; metadata rows (Document ID, Status, Version, Date, Authors, Reviewers, Supersedes, Amendment Process) match the ADR-001 exemplar; "Platform Version" correctly omitted (pre-release, no deployed service); `# File:` header path matches the intended `docs/adr/` placement; four-line authored header (no `# Revised:`) is correct for an original-authoring document.
- **R18 conformance (fresh-set history surfaces).** Single artifact at **Version 0.1.0 / PROPOSED**, single **"Original authoring."** Change Log row, **no `# Revised:`** line, DMS-governed **"Document ID"** and **"Change Log"** naming — all exactly per R18 and matching ADR-001.
- **No fabricated review entries (DIRECTIVE-007 §7.1).** §7 review table rows are empty with roles named; metadata "Reviewers" reads "Pending … See §7." Correct — not back-filled.
- **§4 alternatives faithfully grounded in deliberation (DIRECTIVE-034 / ADR-template load-bearing requirement).** §4.1↔R3, §4.2↔R5, §4.3↔R6, §4.4↔R10 all reflect the ledger rulings and their declined options accurately; §4.5 (diffuse access) is a fair, non-strawman alternative derived from the sole-owner principle. No fabricated or strawman alternatives.
- **§2.6 correctly placed; no RBT-11 pre-emption (EA).** §2.6 traces to **R7**, whose rationale designates ADR-002 as its fresh-set home; **R19** separately preserves RBT-11's distinct runtime Directives-Bridge charter. §2.6 commits the system-of-record authorship assignment and explicitly defers the service-level realization to the SDD — correct altitude, no charter collision.
- **CMEK / no-PHI posture (§2.7, §4.4).** Matches CLAUDE.md §1 operating-environment constraints and R10 (no CMEK; no-PHI-by-design with classification at intake/ingestion; future PHI → its own ADR).
- **Cross-references resolve.** ADR-001 §2.2 (capture invariant; rejected alternatives first-class) and ADR-001 §2.3 (deterministic/probabilistic framing; Position-5 burden of proof) both exist and carry the cited content; ASA/AOE map to CLAUDE.md §6 services (architecture-solutioning-agent / agent-orchestration-engine); internal §2.x references are consistent.
- **Compliance checks complete and well-mapped (§6).** Checks 1–6 map cleanly onto decisions §2.1→1, §2.5→2, §2.4→3, §2.3→4, §2.6→5, §2.7→6; the "enforced at three-hat review, mechanization deferred" pattern matches ADR-001 §6.
- **Internal consistency.** No-vector (§2.4/§5.2/§5.3), Enterprise + minor-version-pin-deferred (§2.2) + topology-deferred (§5.2/§5.3), and CMEK posture (§2.7/§4.4/§5.2/§5.3) are mutually consistent across decision, alternatives, consequences, and risks.
- **EA posture / reversibility.** Vector-out (§4.3/§5.3), topology (§5.2), and CMEK (§2.7) each carry explicit amendment triggers; the ADR is correctly altitude'd as a platform principle (passes the template's "delete every service and start over — would it still apply?" test).
- **Timing / sequencing.** ADR-002 precedes and unblocks DDR-001 (RBT-8 blocks RBT-12); ADR-before-DDR ordering is correct; the blocker RBT-7 (ADR-001) is ACCEPTED and landed on `develop` (`b0afa355`).

### 2.5 Normative interpretation

One latent normative question, recorded rather than left to drift: **does a §25.1-required GKE-runtime decision belong in the graph system-of-record ADR, or in a separate operational/deployment ADR?** CLAUDE.md §1.1 currently assumes the former (it cites "the graph system-of-record ADR"). The disposition is folded into Finding M-1's fork: resolving M-1 settles this interpretation (either ADR-002 becomes the home, with a ratified runtime ruling, or CLAUDE.md is corrected to point elsewhere). No separate codification needed beyond M-1's resolution.

---

## §3 Forward-Pointer Triage

### Candidate RBT-NEW-1 — Enforcement-mechanization for ADR-002 compliance checks

**Source:** Finding B-1.

**Description:** CI checks / schema validators for the mechanizable subset of ADR-002 §6 — specifically the store-authority check (§6.3) and the write-authority check (§6.5), which §6 itself flags as more mechanizable than judgment-based review. Until built, conformance stays at three-hat review.

**Proposed disposition:** File as a new RBT backlog item (Service-Layer or Governance lane); substitute its ID into ADR-002 §6 to clear B-1. Subject to DIRECTIVE-025 dedup check before filing.

### Candidate (ticket edit, not a new item) — RBT-8 ledger-citation completion

**Source:** Finding M-2.

**Description:** Add R7 (and reference R12) to RBT-8's ledger citation; three-layer capture on RBT-8.

**Proposed disposition:** Not a new backlog item — a citation edit on the decided-upon ticket, held for ratification.

### Candidate — Fresh-set vs. kit author-line reconciliation (low priority)

**Source:** §2.3 COSMETIC.

**Description:** The realized fresh-set author-line (`Enterprise Architect, Haffey Enterprises`) diverges from the kit/template/consumed-standard placeholder (`Executive Architect, Haffey Enterprises LLC`). Candidate for the RBT-30 upstream template-adaptation lane.

**Proposed disposition:** Route to RBT-30's vicinity; do not absorb into this review. Low priority.

### Forward-pointer triage summary

| Proposed ID | Summary | Disposition |
|---|---|---|
| RBT-NEW-1 | Enforcement-mechanization (CI/validators) for ADR-002 §6 checks 3 & 5 | File new item; substitute ID into §6 (clears B-1); dedup per DIRECTIVE-025 |
| RBT-8 (edit) | Add R7 + reference R12 to ledger citation | Citation edit on RBT-8; held for ratification |
| (RBT-30 lane) | Author-line: realized fresh-set vs. kit placeholder | Route to RBT-30 vicinity; low priority |

---

## §4 Audit Outcome

> **FINDINGS RAISED — NOT YET CONVERGED.** This is Cycle 1 of the RBT-8 three-hat gate. The pass produced **1 BLOCKING (B-1)** + **3 MATERIAL (M-1, M-2, M-3)** + 2 COSMETIC (no-action) findings, against a large set of POSITIVE no-drift confirmations. Per ENG-STD-001 §12.6 verdict aggregation, the SA hat is at `pause` (B-1), so the PROPOSED→ACCEPTED gate is **not satisfied** this cycle; the ADR remains **PROPOSED**.

The document is, on substance, strong: faithful to the ledger rulings RBT-8 bakes in, free of fabricated rationale or strawman alternatives, correctly altitude'd as a platform principle, internally consistent, and well sequenced ahead of DDR-001. The open items are tractable and mostly mechanical:
- **B-1** clears with one ticket + one substitution.
- **M-2** clears with a held-for-ratification citation edit on RBT-8.
- **M-3** clears in scope by naming the load-bearing Enterprise capability class.
- **M-1** is the one genuine decision point — a fork (carry the GKE-runtime decision in ADR-002 with a freshly-ratified runtime ruling, **or** correct CLAUDE.md and defer the runtime ADR) that requires Tad's explicit ratification before either direction is actioned.

**Gate status:** NOT satisfied this cycle. Recommended path: ratify M-1's fork → disposition B-1/M-2/M-3 → Cycle-2 re-pass → on convergence, promote 0.1.0 PROPOSED → 1.0.0 ACCEPTED with the §7 review-of-record rows filled (mirroring ADR-001's multi-pass acceptance).

---

## §5 Cross-References

- **Authority for this review:** RBT-8 (acceptance = three-hat → ACCEPTED); ENG-STD-001 §12.6 (three-hat gate + verdict aggregation); DIRECTIVE-007 (Multi-Role Review; §7.1 no-fabrication, §7.2 severity vocabulary).
- **Document reviewed:** `ADR-002-graph-system-of-record.md` v0.1.0 PROPOSED (2026-06-15).
- **Conformance baselines:** ADR template; DMS §2.2 / §4; ENG-STD-001 §25.1; ADR-001 (ACCEPTED exemplar).
- **Ruling trace:** Reboot Decision Ledger R3, R4, R5, R6, R7, R9, R10, R12, R18, R19 (fetched live 2026-06-15).
- **Findings disposition tracking:** B-1 → RBT-NEW-1 (to file); M-2 → RBT-8 citation edit (held); M-1 → ratification fork (held).
- **Related reviews:** ADR-001 three-hat review docs (same review type; Pass 1 → 1 BLOCKING + 6 MATERIAL, converged Pass 3 → PASS) — the calibration exemplar for this review.
- **Next:** Cycle-2 re-pass after dispositions; on convergence, RBT-8 → Done via claude.ai → Code commit per DIRECTIVE-026, unblocking RBT-12 (DDR-001).

---

*End of three-hat review — ADR-002.*
