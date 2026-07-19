# Cold Coherence Review — Round 2

**Corpus:** ADR-001 (Reasoning Architecture, v1.0.0) · ADR-002 (Graph as System of Record, v1.0.0) · DDR-001 (Data Architecture, v1.2.0) · DDR-002 (Graph Schema, v1.1.0)
**Method:** Independent cold read. The four uploaded files are the sole source of truth. No outside context imported; no charity applied to gaps; one document is not allowed to excuse another; a cross-reference counts as correct only if its target exists and says what the citing text claims. File/directory path mismatches (flat upload) are not treated as findings. No ship/reject recommendation is made and no document is rewritten.
**Round-1 relationship:** This is a re-review of updated documents. Every finding below was re-verified against the *current* text. Round-1 disposition is annotated per finding (**resolved / persists / narrowed / sharpened / new**) as a convenience for tracking the distillation's effect — it does not substitute for the fresh read.

---

## Summary

The corpus remains coherent as a set: all cross-document version pins resolve (ADR-001 v1.0.0, ADR-002 v1.0.0, DDR-001 v1.2.0 are cited correctly everywhere), every intra-document section reference resolves, DDR-002's 21 CI-only conformance checks partition cleanly into the safety-critical / follow tiers with no gaps or overlaps, and the load-bearing platform commitments (Neo4j Enterprise, three-store backbone, sole-owner gateway, no-vector, no-PHI/no-CMEK, Position 4–5, ASA/AOE write split) are stated consistently across all four.

The distillation cleaned up packaging and corrected several round-1 citation issues, but it did **not** touch the core cross-document seam. **15 findings: 1 BLOCKING, 6 SHOULD-FIX, 8 NIT.** The friction still concentrates in two places: the DDR-001 ↔ DDR-002 design/schema boundary (the single BLOCKING item and two SHOULD-FIX items live here), and a cluster of self-descriptive / attribution claims the documents make about each other (citations, the self-modification invariant's scope, and the one-way-reference assertion).

The one item that should be read first is unchanged from round 1 and remains unresolved: **DDR-001 says the RG session root carries aggregate confidence; DDR-002's schema gives `ReasoningSession` no confidence property at all** (B1).

**Resolved since round 1**

- Round-1 S6 partially closed: DDR-001 now bridges its RG-role vocabulary to **ADR-002 §2.6** (correct), not ADR-001 §2.2. (The DDR-002 side of the same mis-citation persists — see S3 below.)
- Round-1 S3 narrowed: DDR-001's spike-findings section now carries an explicit **Capability requirement** line, materially closing the gap ADR-002 pointed at. A residual overclaim remains — see S4.
- ADR-002's §5.2 stale internal cross-reference (flagged in its own change log) is corrected.

---

## Findings

### BLOCKING

#### B1 — `ReasoningSession` aggregate confidence: design asserts it, schema omits it
**Severity:** BLOCKING · **Δ:** persists (unchanged from round 1)
**Location:** DDR-001 §Reasoning Graph (session-root bullet) vs DDR-002 §4 (`ReasoningSession` schema + Confidence-canonical definition)

DDR-001 states the session root *"corresponds to `ReasoningSession`"* and *"carries aggregate confidence."* DDR-002 — the document DDR-001 explicitly defers formal properties to (*"Formal labels/properties → DDR-002"*) — defines `(:Reasoning:ReasoningSession)` with only `session_id`, `lifecycle_state`, `created_at`, and provenance: **no confidence property.** DDR-002's Confidence-canonical section then enumerates the surfaces that carry node confidence (`Evidence`, `ObservedPattern`, `CapabilityCostEstimate`, `ReasoningProgress`) and routes the roll-up onto **`ReasoningProgress`** (*"a … rollup over its `SUPPORTED_BY` Evidence"*) — a per-conclusion value, not a session-level aggregate. There is no session-level aggregate-confidence surface anywhere in the schema.

So the two documents disagree on whether a run-level aggregate confidence exists and where it lives. The deferral clause sharpens rather than excuses this: DDR-001 asserts a concrete property *while* delegating properties to DDR-002, and the delegated-to authority does not provide it.

*One-line fix:* either add an aggregate-confidence property to `ReasoningSession` in DDR-002, or strike *"carries aggregate confidence"* from DDR-001's session-root bullet and state that aggregate confidence is a `ReasoningProgress` roll-up with no session-level materialization.

---

### SHOULD-FIX

#### S1 — "SOFIA never self-modifies": the invariant's object drifts, and §2.5 is cited across a category line
**Severity:** SHOULD-FIX · **Δ:** sharpened (round-1 S4)
**Location:** ADR-001 §2.5 vs DDR-001 Decision.5 / check #4 vs DDR-002 §2.3 and §4 (Accountability boundary)

The same invariant is stated with three different objects, and one downstream use crosses a category line the ADRs draw:

- **ADR-001 §2.5** scopes it to *encoded reasoning*: *"SOFIA does not self-modify its encoded reasoning without EA approval,"* where the promotion target is *"encoded SOFIA logic"* (platform reasoning code, per §5.2).
- **DDR-001 Decision.5 / check #4** scope it to *the KG*, unqualified: *"SOFIA never self-modifies the KG."*
- **DDR-002 §2.3** then has SOFIA performing a **non-EA-gated `derived` auto-write to the Operational plane** — which *is* a KG plane (DDR-001 lists it among the five) — and reconciles this against *"ADR-001's SOFIA-never-self-modifies invariant"* only by adding a qualification that lives nowhere in DDR-001: *"Operational is the staging tier; the EA gate sits between it and authoritative knowledge."* A reader taking DDR-001 Decision.5 at face value finds DDR-002's Operational auto-write to breach it; only DDR-002's added staging-tier carve-out rescues it.

Separately, DDR-002 §4 justifies EA-gated promotion into a **KG fact** by citing ADR-001 §2.5's *"EA-gated consolidation into encoded logic"* and calling it *"the encoding-density-growth feature."* But §2.5's target is encoded logic (code/rules), not KG ground-truth data. Promoting a fact into the KG and consolidating a pattern into encoded logic are two different acts with two different targets; the citation equates them.

Net effect: a reader cannot cleanly determine whether the self-modification bar protects encoded logic, all KG state, or only *authoritative* KG state — nor whether ADR-001 §2.5's mechanism and DDR-001's feedback loop are the same mechanism or two.

*One-line fix:* state the invariant once with an explicit object — most likely *"SOFIA never writes authoritative KG knowledge except through the EA gate"* — carry that qualification into DDR-001 Decision.5, and distinguish "promotion into encoded logic (ADR-001 §2.5)" from "promotion of a finding into the KG (DDR-001/002 feedback loop)" rather than citing one to license the other.

#### S2 — RG structure: DDR-001 says three roles "compose `ReasoningProgress`"; DDR-002 makes them separate nodes
**Severity:** SHOULD-FIX · **Δ:** persists (round-1 S1)
**Location:** DDR-001 §Reasoning Graph vs DDR-002 §4 + RG-internal edges

DDR-001 states that Typed conclusion, Evidence, and Rejected alternative are each *"Part of `ReasoningProgress`"* and that *"the other three compose `ReasoningProgress`."* DDR-002 collapses `ReasoningProgress` to the typed conclusion itself (*"= the typed conclusion (lean reading: no separate container)"*) and makes `Evidence` and `RejectedAlternative` **separate node types**, joined to it by edges (`(ReasoningProgress)-[:SUPPORTED_BY]->(Evidence)`, `(ReasoningProgress)-[:REJECTED]->(RejectedAlternative)`). "Compose"/"part of" reads as containment; the schema is three sibling nodes with edges. The word `ReasoningProgress` means the whole ASA-authored content bundle in DDR-001 and a single specific node in DDR-002.

*One-line fix:* in DDR-001, describe the three as *linked to* / *reached from* `ReasoningProgress` by edges rather than *composing* it, matching DDR-002's node-plus-edge structure.

#### S3 — DDR-002 still cites "ADR-001 §2.2 vocabulary" for RG node names that are not in §2.2
**Severity:** SHOULD-FIX · **Δ:** persists on the DDR-002 side (round-1 S6; DDR-001 side resolved)
**Location:** DDR-002 §4 opening line

DDR-002 says the RG types *"align to ADR-002 §2.6 / ADR-001 §2.2 vocabulary: `ReasoningSession`, `ReasoningProgress`, `Evidence`, `RejectedAlternative`."* The **ADR-002 §2.6** half is correct for `ReasoningSession`/`ReasoningProgress`. The **ADR-001 §2.2** half is wrong: §2.2's illustrative kinds are Finding / DirectiveCheck / Inference / Hypothesis — none of the four RG node names appear there — and §2.2 explicitly disclaims being the vocabulary source (*"their canonical labels … are owned by the Graph Schema document, not fixed here"*). `Evidence` and `RejectedAlternative` trace to DDR-001's RG roles, not to either ADR section. DDR-001 already corrected its side of this to cite §2.6; DDR-002 did not.

*One-line fix:* drop *"/ ADR-001 §2.2"* from the citation; cite ADR-002 §2.6 for `ReasoningSession`/`ReasoningProgress` and DDR-001's RG roles for `Evidence`/`RejectedAlternative`.

#### S4 — ADR-002 claims DDR-001 records "the specific/named Enterprise capability"; DDR-001 records a structural requirement and declines to name the feature
**Severity:** SHOULD-FIX · **Δ:** narrowed (round-1 S3)
**Location:** ADR-002 §2.2, §4.1, §7 vs DDR-001 §Spike Findings

Three times, ADR-002 says DDR-001's spike-findings section records *"the specific Enterprise capability the plane model depends on"* (§7 sharpens this to *"the named Enterprise capability"*). DDR-001 now provides a **Capability requirement** stated *structurally* — the five planes + Extension + RG as co-resident logical subgraphs with the traversal complexity that implies — and immediately adds a **Recovery-boundary note**: *"the specific edition-feature blocker from the original trial is not in the captured record and is not reconstructed here."* So ADR-002 asserts DDR-001 records a *named/specific* Enterprise capability, while DDR-001 supplies a structural requirement and expressly does *not* name the edition feature. This underwrites a ratified rejection (the Enterprise-over-Community commitment), so the residual overclaim still matters even though DDR-001's new Capability-requirement line closed most of the round-1 gap.

*One-line fix:* soften ADR-002's phrasing to *"the structural capability requirement the plane model depends on"* (matching DDR-001), and drop *"specific"/"named"*.

#### S5 — Session cardinality: DDR-002's `0..*` PRODUCED attributes a reading to DDR-001 that DDR-001's wording doesn't unambiguously support
**Severity:** SHOULD-FIX · **Δ:** sharpened (round-1 N4)
**Location:** DDR-001 §Reasoning Graph (session-root bullet) vs DDR-002 §4 `ReasoningSession` note / §5 bridge edges

DDR-001 says the session is *"one per synthesis run / solution."* DDR-002 commits `(ReasoningSession)-[:PRODUCED]->(Solution)` at **`0..*`** — *"a session may explore multiple candidate solutions or conclude none"* — and asserts this is *"consistent with DDR-001 … which pins one session per run, not one solution per session."* But DDR-001's *"one per synthesis run / solution"* is genuinely ambiguous; the *"/ solution"* can be read as "one session per solution," which is the opposite of DDR-002's multi-solution cardinality. The schema makes a concrete cardinality commitment (which twelve SDDs inherit) resting on a reading of DDR-001 that DDR-001's text does not clearly state.

*One-line fix:* disambiguate DDR-001 to *"one per synthesis run (a run may produce zero or many candidate solutions)"* so the `0..*` PRODUCED edge is anchored, not asserted.

#### S6 — "One-way reference" claim is literally false as worded
**Severity:** SHOULD-FIX · **Δ:** persists (round-1 S2)
**Location:** DDR-001 §Cross-References + §Substrate-Stability vs DDR-002 §Substrate-Stability + §Cross-References

Both DDRs assert the reference is one-way — DDR-001: *"One-way reference: DDR-002 references this DDR, not the reverse"*; DDR-002: *"DDR-002 references DDR-001, never the reverse."* Yet DDR-001 references DDR-002 by name repeatedly: Decision.6 (*"the node/relationship/constraint contract is DDR-002's"*), the versioning table (*"DDR-002 schema / DDR-002 field"*), the downstream-consumers list, and the boundary-routing appendix. The claim is true only under an *authority/dependency* reading — DDR-002 pins and is bound by DDR-001; DDR-001's mentions of DDR-002 are forward boundary-routing, not upstream dependence — and that reading is sound and consistently intended. But the plain word "reference" is contradicted by DDR-001's own text, so a cold reader hits an apparent falsehood.

*One-line fix:* qualify the noun — *"one-way dependency: DDR-002 is bound by / pins DDR-001, not the reverse"* — leaving DDR-001's forward boundary-pointers unaffected.

---

### NIT

#### N1 — DDR-002 `Date` field follows neither the sibling convention nor its own latest change
**Severity:** NIT · **Δ:** persists/downgraded (round-1 S5)
DDR-002's header `Date` is 2026-06-22; its Created stamp is 2026-06-21 and its latest change-log row is 2026-07-01. The other three documents set `Date` = creation date. DDR-002's `Date` matches its 1.1.0 (RBT-43) amendment instead — inconsistent with the siblings and stale against its own latest row. *Fix: set `Date` to the creation date (2026-06-21) to match the convention, or define what `Date` means.*

#### N2 — "the Reboot" is undefined
**Severity:** NIT · **Δ:** persists/downgraded (round-1 S9)
ADR-002 §2.2 explains the spike's provenance via *"predates the Reboot's formal capture,"* but "the Reboot" is defined nowhere in the corpus. A cold reader has no referent. *Fix: gloss it at first use, or replace with a self-contained phrase ("predates the current formal-capture process").*

#### N3 — `LAA` / `SA` never expanded
**Severity:** NIT · **Δ:** persists/downgraded (round-1 S7)
Both ADRs enforce conformance at *"three-hat (LAA/SA/EA) review,"* the load-bearing review gate, but only `EA` is inferable (from the Executive-Architect byline). `LAA` and `SA` are never expanded anywhere. *Fix: expand once at first use.*

#### N4 — `ASD` never expanded
**Severity:** NIT · **Δ:** persists (round-1 S8)
DDR-001 uses *"Solution (ASD)"* and *"ASD bodies"*; DDR-002 uses *"the produced ASD."* `ASD` is never expanded, and is easily conflated with `ASA` (Architecture Solutioning Agent, which *is* expanded in ADR-002 §2.6). *Fix: expand `ASD` at first use.*

#### N5 — Document-class and artifact acronyms unexpanded
**Severity:** NIT · **Δ:** persists (round-1 N5/N6)
`ADR`, `DDR`, `SDD` are never expanded in any document; `BCDR` and "build sheets" appear only as illustrative Artifact-family members with no gloss. Low impact given context, but a cold reader meets them cold. *Fix: a one-line doc-class legend, or expand at first use.*

#### N6 — Pervasive forward references to DDR-003 (not in corpus)
**Severity:** NIT (scope note) · **Δ:** persists/downgraded (round-1 S10)
Both DDRs route governance, thresholds, cadence, retention, archival policy, condition governance, and the retraction remedy-boundary forward to **DDR-003**, which is not among the uploaded files. Every such reference is honestly labelled *forthcoming / sibling* and correctly directional, so a reader is never misled about what exists — but every `→ DDR-003` is a dead end within this set. If DDR-003 is simply out of this review's scope rather than missing, this is a non-issue by design. *No fix required unless DDR-003 was intended to be in scope.*

#### N7 — Two-Graph table footnote markers out of reading order
**Severity:** NIT · **Δ:** persists (round-1 N7)
In DDR-001's Two-Graph table, the `Operational²` row precedes the `Governance¹` row, so the superscripts read `² … ¹` against the footnote order below. Cosmetic. *Fix: renumber so markers ascend in reading order.*

#### N8 — 2026-07-01 distillation rows reuse the prior version number
**Severity:** NIT (likely intentional) · **Δ:** persists (round-1 N1)
All four change logs record the 2026-07-01 distillation without a version bump (two rows share 1.0.0 / 1.0.0 / 1.2.0 / 1.1.0 respectively). Each row states *"no decision change,"* so under a decision-semantic versioning rule this is defensible and consistent across the set — but a cold reviewer at minimum notices two rows sharing a version. *No fix required if the "editorial change ⇒ no bump" convention is intended; otherwise add a patch/editorial qualifier.*

---

## Checked clean

Verified and free of defect on this read:

- **Version pins.** Every cross-document pin resolves: DDR-001 and DDR-002 both cite ADR-001 v1.0.0 / ADR-002 v1.0.0; DDR-002 cites DDR-001 v1.2.0. No dangling or mismatched version reference.
- **Intra-document section references.** All `§`-pointers within DDR-002 (§1–§7) and the named-section references into DDR-001 (§Two-Graph Model, §Versioning & Temporal Model, §Hybrid Persistence Model, §Reasoning Graph) resolve to existing sections saying what the citing text claims.
- **DDR-002 §7 conformance set.** All 21 CI-only checks are referenced consistently; the safety-critical tier (#1, #7, #9, #11, #13, #14, #15, #16, #17, #19, #21) and follow tier (#2, #3, #4, #5, #6, #8, #10, #12, #18, #20) partition all 21 with no overlap and no gap.
- **Two-axis provenance.** The `origin_mechanism` × `derivation_class` matrix is total and internally consistent (`ingested→primary`, `authored→primary`, `derived→distilled|aggregated`, `promoted→N/A`), and §7 #17's `source_record_ref` obligations (ingested; distilled) align with §1's statement of them.
- **Confidence model.** The node-vs-edge confidence split in §3 and the Confidence-canonical definition in §4 agree with each other (the ReasoningSession issue in B1 is a DDR-001↔DDR-002 conflict, not an internal DDR-002 one).
- **Write-authority split.** ASA-authors-`ReasoningProgress` / AOE-owns-`ReasoningSession`-lifecycle is stated consistently across ADR-002 §2.6, DDR-001, and DDR-002 §7 #7.
- **Promotion / retraction symmetry.** The governing-edge logic (latest `decided_at`, `outcome ∈ {approved, approved_conditional}`) is consistent between §2.4 and §7 #15/#21; retraction (#21) is a faithful mirror of promotion (#15).
- **Provenance-survival.** The `ProvenanceSummary` node, `MATERIALIZES_PROVENANCE_OF` edge, and at-promotion materialization guarantee (#20) are consistent across §4, §5, §6, and §7.
- **Platform-commitment consistency across all four.** Neo4j Enterprise edition, three-store backbone, sole-owner knowledge-service gateway, no-vector-store, no-PHI/no-CMEK posture, Position 4–5 taxonomy, and the ASA/AOE identities are each stated without contradiction across the documents that touch them.
- **Artifact family.** DDR-002's introduction of the Artifact node-family ("neither a KG plane nor RG") is compatible with DDR-001's two-graph model and its dual-homed produced-solution treatment; no contradiction with the two-graph commitment.
- **Extension / cost plane.** Cost-as-first-Extension-registration (DDR-002 §2.6) is consistent with DDR-001's Extension mechanism and with the "five core planes, cost not a sixth" statement in DDR-002 Decision.2; `attaches_to: [Capability, Technology]` satisfies §7 #18.
- **Contested-T2 tracking.** All four flagged contested T2 value-sets (`conclusion_type`, `GateDecision.gate`, `polarity` neutral, `basis_strength`) resolve to the sections named in the §1 roster.
