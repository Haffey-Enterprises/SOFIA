# File: docs/reviews/2026-06-03-adr-001-reasoning-architecture-three-hat-review.md
# Author: Thaddeus Haffey — Enterprise Architect, Haffey Enterprises
# Created: 2026-06-03
# Description: Three-hat (LAA/SA/EA) review of ADR-001 Reasoning Architecture (SOFIA as Reasoner) v0.2.0 PROPOSED, per RBT-7 acceptance gate. Findings-only artifact; dispositions deferred to the authoring session.

# Three-Hat Review — ADR-001 Reasoning Architecture (SOFIA as Reasoner) — 2026-06-03

| Field | Value |
|---|---|
| **Review Date** | 2026-06-03 |
| **Reviewer** | Thaddeus Haffey — LAA / SA / EA, Haffey Enterprises (claude.ai-assisted; DIRECTIVE-007 multi-role) |
| **Subject** | ADR-001 Reasoning Architecture v0.2.0 (PROPOSED) — first draft uploaded to the Reboot project |
| **Scope** | Conformance + substantive three-hat pass against the binding corpus (Decision Ledger R1–R17 + C-rulings; DMS; adr-template; CSD; ENG-STD-001; CLAUDE.md). RBT-7 acceptance gate. |
| **Authority** | RBT-7 acceptance criterion ("Three-hat (LAA/SA/EA) review → ACCEPTED"); DIRECTIVE-007; ENG-STD-001 §12.6; review-template severity vocabulary. |
| **Outcome** | **CHANGES REQUIRED** — 1 BLOCKING, 6 MATERIAL, 3 COSMETIC, 4 POSITIVE. Promotion to ACCEPTED withheld pending disposition of the BLOCKING item. Per-hat verdicts: LAA `proceed-with-changes` · SA `proceed-with-changes` · EA `pause`. |

> **Disposition note.** This artifact surfaces findings only. No findings are addressed here, by operator instruction — they return to the ADR-001 authoring session. Severities use the review-template four-tier vocabulary: **BLOCKING** (must resolve before the gate is satisfied), **MATERIAL** (should be fixed in scope), **COSMETIC** (noted, no-action), **POSITIVE** (explicit no-drift confirmation for audit trail).

---

## Authorities fetched (provenance)

Fresh-fetched this session rather than recalled (ENG-STD-003 §13.5.9 / fresh-fetch discipline):

- **Decision Ledger** (Notion, *Reboot — Decision Ledger*) — Interaction Ledger #1–14, Lightened Ruling-Capture R1–R17, Build-leg log.
- **RBT-7** + full Reboot ticket graph (RBT-1…RBT-29) via Linear.
- **adr-template.md**, **ddr-template.md**, **sdd-template.md**, **ruling-rationale-template.md**, **review-template.md** (project knowledge).
- **DOCUMENT_MANAGEMENT_STRATEGY.md** §2.2, §2.3, §2.4, §4.1–§4.8, §5 (project knowledge).
- **CLAUDE_SESSION_DIRECTIVES.md** — DIRECTIVE-024 (§24.1/§24.2), DIRECTIVE-023 (project knowledge).
- **ENG-STD-001-engineering-standards.md** §12.3–§12.8 (three-hat hat-semantics, solo-operator self-review) (project knowledge).
- **CLAUDE.md** — Authority Map, §1–§3 (project knowledge).
- **ADR-005-reasoning-architecture.md** (prior corpus) — intent source only per R2; §8 propagation + §9 review consulted for criterion-shift comparison.

**Coverage caveat (verify):** the `validate-docs-structure` CI checker itself was not reachable this session (the `Haffey-Enterprises/SOFIA-Reboot` repo is not visible to the connected GitHub token; the local clone was set aside per operator direction to source from project knowledge). SA conformance findings that depend on the checker's exact ruleset are flagged "verify" (see SA-7).

---

## LAA hat — *what is this change?* (scope, identity, ticket-fit)

**LAA-1 · POSITIVE.** The draft delivers exactly the RBT-7-scoped spine: the reasoning-capture invariant (§2.2), the Position 5 operating regime on a committed trajectory toward Position 4 (§2.1), and the KG + RG moat (§1, §3). It stays at principle level and does **not** leak downstream detail — no Neo4j edition, no three-store split, no topology, no schema DDL (correctly reserved to ADR-002 / DDR-002 per R3/R5/R9/R8). Faithful to R1 (spine) and R14 (the "Semantic Orchestration for Intelligent Architecture / Applications" expansion is used verbatim in §1).

**LAA-2 · MATERIAL.** Schema-term ownership tension. §2.2 explicitly disclaims specifying node labels ("The concrete node labels, property names … are the Graph Schema document's contract … this ADR does not specify them") — yet §2.2 and §6 use the specific label-like names **Finding / DirectiveCheck / Inference / Hypothesis** as though canonical. Under R8 (C4 disciplined split; reference flows architecture → schema only), the spine naming schema-owned artifacts risks inverting the dependency direction and pre-committing terms the Graph Schema doc (RBT-13 / DDR-002) is meant to own. The review needs the authoring session to decide whether these are *illustrative* categories (and mark them so) or *load-bearing* contracts (in which case they must be stated as owned-by-and-aligned-with the Graph Schema doc).

**LAA-3 · COSMETIC.** §2.1 promises "the full five-position taxonomy is set out in §4," but §4 presents Positions 1–3 as positions (Alternatives A–C) and Positions 4–5 as *binary-commitment* framings (Alternatives D–E). A reader expecting a clean 1→5 ladder finds a 3-positions-plus-2-binary-variants structure. A one-line framing note in §2.1 or §4 head would remove the friction.

**LAA verdict: `proceed-with-changes`.** Scope and identity are right; LAA-2 should be dispositioned before promotion.

---

## SA hat — *how does this change conform?* (standards, cross-references, internal consistency)

**SA-1 · MATERIAL.** Review-record internal inconsistency / premature attestation. The **Reviewers** metadata row states a three-hat review was "conducted 2026-06-03 — R1 first pass + R2 verification; findings incorporated. ACCEPTED-promotion pending," and §8 logs "0.2.0 … R1 review findings incorporated" — but **§7 Review Cycle R1 is empty** and no review artifact exists at `docs/reviews/`. The adr-template is explicit: "Do NOT fabricate review entries … leave the rows empty with reviewer roles named but dates/outcomes blank." As of this session, *this* is the R1 three-hat review and its findings are being surfaced now (not yet incorporated), so the row's claim is inaccurate. Secondary: "R1/R2" as review-cycle labels collides with the Decision Ledger's R1/R2 *ruling* IDs — confusable; recommend distinct labels.

**SA-2 · MATERIAL.** Aspirational-compliance tracking carries no backlog ID. §5.3 and §6 both say the enforcement-mechanization item is "carried forward to file" but cite no `RBT-NN`. DIRECTIVE-024 §24.1 and the adr-template both require a *tracked* backlog item ("aspirational compliance with no tracking item is debt that compounds"). The item must be filed and its ID cited in-line. (The DIRECTIVE-024 §24.1 citation itself is accurate — see SA-5.)

**SA-3 · MATERIAL.** Untracked propagation-directive deferral. §6 Propagation says "Codifying a dedicated propagation directive is deferred as a forward-pointer," naming neither a directive nor a tracking ticket. The prior corpus named this DIRECTIVE-035 (ADR-005 §8(d)); the reboot CSD does not carry it. Either cite a tracking item or, if RBT-11 (A5 — Directives Propagation Bridge) is the intended home, say so — but note RBT-11 concerns the runtime *Directives-Context-Envelope Bridge*, which may be a distinct concern from *reasoning-architecture* propagation; disambiguate before pointing there.

**SA-4 · MATERIAL (contingent on EA-1).** The header omits a `# Revised:` line, though the document is at v0.2.0 — i.e., it has taken a substantive revision per DMS §4.7. DMS §2.2 rule 5 + §2.4 (Bucket A: `# Revised: YYYY-MM-DD (TICKET_OR_SHORT_DESCRIPTION)`) expect the line once a substantive revision lands. This finding is **contingent on EA-1**: if the broad reading of R2 (no revision tracking on fresh docs) governs, the omission is correct; if the kit/DMS governs, the line is required.

**SA-5 · POSITIVE.** Conformance done right in several places: filename/path/slug (`docs/adr/ADR-001-reasoning-architecture.md`) conform to DMS §5.1 uppercase prefix + §5.2 lowercase-hyphenated slug, and the slug is stable from the prior ADR-005 (§5.2 stability preference); the `# File:` path matches the intended location; the **Platform Version** row is correctly omitted (pre-release, no deployed service — adr-template says delete the row, do not fabricate); the §6 compliance posture follows the DIRECTIVE-024 §24.1 "aspirational-with-tracking" pattern (modulo the missing ID at SA-2); and the DIRECTIVE-024 §24.1 and RBT-14 cross-references resolve correctly.

**SA-6 · COSMETIC.** The metadata uses "ADR ID" where DMS §2.3.1's generic pattern shows "Document ID." The adr-template (doctype-specific authority) uses "ADR ID," so this is acceptable; noted only for cross-corpus label consistency.

**SA-7 · MATERIAL (verify).** CI conformance unverified this session. Because the `validate-docs-structure` script was not reachable, confirm against the actual checker that the document passes — in particular (a) the header field-set it enforces, and (b) whether it expects a `## Change Log` heading (DMS §2.2 rule 4/5 names the section "Change Log") versus the adr-template's "## 8. Version History." A heading-name mismatch between DMS and the template could trip a strict checker; this also intersects EA-1.

**SA verdict: `proceed-with-changes`.** As written the document largely conforms to the adr-template/DMS — but that very conformance is what collides with R2 (escalated to EA-1), and SA-1/SA-2/SA-3 are substantive.

---

## EA hat — *should this land in this shape, at this time?* (posture, reversibility, precedent, timing)

**EA-1 · BLOCKING.** Ratified-authority conflict on history-bearing sections — and it is spine-level. The Decision Ledger **R2** rules the fresh set is authored "as a new product — **no version history, no Supersedes, no change logs, no DELTA trails**." The **same reboot** adopted the HE-Bedrock kit pristine (**R11**), whose **adr-template** and **DMS §2.4 / §4.7** affirmatively *require* a Version field, a Supersedes row, an Amendment Process row, and a §8 Version History (and `# Revised:`). The draft followed the kit — it carries the Supersedes row, the Amendment Process row, Version 0.2.0, and a §8 Version History (0.1.0 → 0.2.0) — and thereby sits in direct tension with R2.

Two defensible readings, not yet adjudicated:
- **Narrow R2** — "no *old-corpus* archaeology / morph-trail" (the trap R2's rationale names). Compatible with a clean fresh §8 that starts at 0.1.0.
- **Broad R2** — fresh docs carry *no* history-bearing sections at all (no §8, no Supersedes, no Reviewers/§7 history, no `# Revised:`).

The resolution is **load-bearing for the entire fresh set** (ADR-002…005, every DDR/SDD inherit it) and likely needs (a) an explicit ledger ruling and (b) either a reboot-specific template adaptation or a DMS carve-out reconciling R2 with the kit. Because ADR-001 is the spine the rest re-express under, this is the right document to settle it on — but it must be ratified, not resolved silently. **Affected surfaces in the current draft:** Version field, Supersedes row, Amendment Process row, Reviewers row, §7 Review and Approval, §8 Version History, and the `# Revised:` header line (SA-4).

**EA-2 · MATERIAL.** Criterion-shift on propagation-codification precedence (frame as applied learning, not contradiction). Prior ADR-005 §8(d) made propagation-directive codification (provisional DIRECTIVE-035) "a precondition for any subsequent reasoning-architecture-relevant detail session." New ADR-001 §6 reverses this to "not a precondition for downstream work." The reversal is *defensible* under R2 (prior = intent source only) and the reboot's non-carriage of DIRECTIVE-035 — but it is a substantive precedence change with **no backing ledger ruling**. Recommend the authoring session ratify the downgrade explicitly and capture it (pairs with SA-3's tracking gap).

**EA-3 · MATERIAL (externally-bounded / cross-corpus observation).** The renumber (R13/R15) has left dangling `§`-pointers elsewhere in the corpus. Decision Ledger R7 and tickets RBT-16 / RBT-17 reference "**ADR-001 §2.8**" for the ASA-writes-ReasoningProgress decision — but that is the *old* ADR-001 (Graph as System of Record), now renumbered to **ADR-002**. The *new* ADR-001 (this reasoning spine) has no §2.8. This is **not a defect in the document under review** (it correctly omits §2.8); it is flagged because the spine review is the natural moment to catch renumber-induced pointer drift before the dependent ADRs/SDDs are authored against stale references.

**EA-4 · POSITIVE.** The substantive architecture is sound and faithful. The Position 5 operating regime → Position 4 trajectory, the invariant-across-reasoners with locus/authoritative-flag varying (§2.2), the KG+RG moat framing (§1/§3), the EA-gated encoding-density promotion mechanism (§2.5 ↔ RBT-14), the deterministic/probabilistic + LLM-as-renderer framing (§2.3), and the §4 five-position treatment that rejects both binary commitments — all cohere with R1/R14 and with the downstream C-rulings without absorbing their detail. This is a strong spine.

**EA-5 · MATERIAL.** Promotion-readiness honesty / timing. The Reviewers row reads "ACCEPTED-promotion pending" and §8 implies findings are already incorporated, while in fact this spine blocks RBT-8/9/10/11 (and the whole set), and its three-hat review is only now occurring. The downstream eagerness creates pressure to over-state readiness. Recommend the document remain PROPOSED with §7/Reviewers reflecting the genuine in-progress state until this review's findings are dispositioned (overlaps SA-1; EA frames it as a posture/sequencing risk).

**EA verdict: `pause`** — on EA-1. The architecture is acceptable; the document's *shape* cannot be ratified until the R2-vs-kit authority question is settled, because that answer changes the metadata/history surfaces and sets precedent for the fresh set.

---

## Summary

| ID | Severity | Hat | One-line |
|---|---|---|---|
| EA-1 | **BLOCKING** | EA | R2 (no history/Supersedes/change-log) vs adopted kit/DMS (requires them); draft follows the kit; spine-level, sets precedent for the whole fresh set. |
| LAA-2 | MATERIAL | LAA | Schema-label terms (Finding/DirectiveCheck/Inference/Hypothesis) used while disclaiming label-specification; clarify illustrative vs Graph-Schema-owned (R8). |
| SA-1 | MATERIAL | SA | Reviewers row + §8 claim a completed R1 review with findings incorporated, but §7 is empty and no review artifact exists; premature/inaccurate; "R1/R2" overloads ledger ruling IDs. |
| SA-2 | MATERIAL | SA | Enforcement-mechanization "carried forward to file" with no backlog ID; DIRECTIVE-024 §24.1 requires a tracked ID. |
| SA-3 | MATERIAL | SA | Propagation-directive deferral names no directive and no tracking ticket; disambiguate from RBT-11 (runtime bridge) if pointing there. |
| SA-4 | MATERIAL (contingent on EA-1) | SA | `# Revised:` line absent at v0.2.0 (DMS §2.2 r5 / §2.4 Bucket A). |
| SA-7 | MATERIAL (verify) | SA | CI `validate-docs-structure` conformance unverified (checker not reachable); confirm header set + `## Change Log` vs "§8 Version History" heading. |
| EA-2 | MATERIAL | EA | Propagation precondition reversed from prior ADR-005 §8(d) with no backing ledger ruling; ratify the downgrade. |
| EA-3 | MATERIAL (externally-bounded) | EA | Renumber left "ADR-001 §2.8" pointers (ledger R7, RBT-16/17) aimed at the old ADR-001 (now ADR-002); remap across the set. |
| EA-5 | MATERIAL | EA | Promotion-readiness over-stated; keep PROPOSED with honest §7/Reviewers state until findings dispositioned. |
| LAA-3 | COSMETIC | LAA | "Five-position taxonomy" promised in §2.1; §4 presents 3 positions + 2 binary variants — add a framing line. |
| SA-6 | COSMETIC | SA | "ADR ID" vs DMS generic "Document ID" label (template-acceptable; noted only). |
| (LAA-3b) | COSMETIC | LAA | §2.1 "direction of travel from Position 1 toward Position 4" reads oddly (platform isn't at Position 1); minor wording. |
| LAA-1 | POSITIVE | LAA | Delivers the RBT-7 spine exactly; no downstream-detail leakage; faithful to R1/R14. |
| SA-5 | POSITIVE | SA | Filename/path/slug, Platform-Version omission, and the §24.1 compliance pattern all conform. |
| EA-4 | POSITIVE | EA | Substantive reasoning architecture is sound and coherent with the ledger and downstream C-rulings. |

**Gate result:** ACCEPTED promotion is withheld. One BLOCKING finding (EA-1) must be ratified, and the MATERIAL findings dispositioned, in the ADR-001 authoring session before a clean R2 cycle can converge.

*End of review.*
