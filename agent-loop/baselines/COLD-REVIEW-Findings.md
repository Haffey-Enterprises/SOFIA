# Documentation Acceptance Review — Cold Coherence & Correctness Findings

**Scope reviewed:** ADR-001 (Reasoning Architecture, v1.0.0), ADR-002 (Graph as System of Record, v1.0.0), DDR-001 (Data Architecture, v1.2.0), DDR-002 (Graph Schema, v1.1.0) — four uploaded files, read as a self-contained corpus with no outside context.

---

## 1. Summary

The corpus holds together well overall. It is dense but internally disciplined: cross-document version pins are all valid, every intra-document `§`-reference resolves, the plane set / three-store backbone / write-authority assignments are consistent across all four documents, and the largest single artifact (DDR-002's 21-invariant conformance set) partitions cleanly with no orphaned or double-counted checks. A first-time reader can follow the ADR→DDR dependency spine without hitting a broken pointer or a structural break.

The friction is concentrated at the **DDR-001 ↔ DDR-002 design/schema seam** and in a handful of **self-descriptive claims the documents make about themselves** (reference direction, what a cited section records, what the metadata "Date" means). **18 findings total: 1 BLOCKING, 10 SHOULD-FIX, 7 NIT.**

**Single most important issue (B1):** DDR-001 states the Reasoning-Graph session root **"carries aggregate confidence,"** but DDR-002 — the document DDR-001 defers to for the schema — gives `ReasoningSession` no confidence property and deliberately omits it from its enumerated confidence-bearing surfaces. Design and owning-schema concretely disagree on where session-level confidence lives.

---

## 2. Findings

### BLOCKING

**B1. `ReasoningSession` "aggregate confidence" is asserted in DDR-001 but absent from DDR-002's schema and confidence model.**
- **Location:** DDR-001 → *Reasoning Graph — four structural roles*, "Session root" bullet; DDR-002 → §4 (`(:Reasoning:ReasoningSession)` schema line, and the "Confidence — canonical definition" paragraph).
- **What's wrong:** DDR-001 says the session root *"carries aggregate confidence."* DDR-002, which owns the schema (and which DDR-001 explicitly defers to: *"Formal labels/properties → DDR-002"*), defines `ReasoningSession` with only `session_id · lifecycle_state · created_at · provenance` — **no confidence property** — and its canonical confidence enumeration lists node-confidence on `Evidence`, `ObservedPattern`, `CapabilityCostEstimate`, and `ReasoningProgress` **but not `ReasoningSession`**. In DDR-002 the "aggregate" instead lives on `ReasoningProgress` as a rollup. A reader implementing from the authoritative schema will not produce the session-level aggregate confidence DDR-001's design calls for. Design and schema directly conflict on a concrete, load-bearing property.
- **Suggested resolution:** Either add `aggregate_confidence` to DDR-002's `ReasoningSession` (and its confidence enumeration), or strike "carries aggregate confidence" from DDR-001 and state that session confidence is derived by rollup over contained `ReasoningProgress`.

---

### SHOULD-FIX

**S1. RG composition model diverges: DDR-001 says Evidence and Rejected-alternative "compose `ReasoningProgress`"; DDR-002 makes them separate nodes.**
- **Location:** DDR-001 → *Reasoning Graph* ("the other three **compose** `ReasoningProgress`"; the Typed-conclusion / Evidence / Rejected-alternative bullets each tagged "Part of `ReasoningProgress`"); DDR-002 → §4.
- **What's wrong:** DDR-001 frames Evidence and Rejected-alternative as *part of / composing* `ReasoningProgress`. DDR-002 models `ReasoningProgress` as *"the typed conclusion (lean reading: no separate container),"* with `Evidence` and `RejectedAlternative` as **independent nodes** joined by `SUPPORTED_BY` / `REJECTED` edges. The write-authority story (all ASA-authored, gateway-mediated) is consistent, but the compositional relationship is stated two incompatible ways. DDR-001's "→ DDR-002 for labels/properties" softens this, but "compose" is a structural design statement, not just a label.
- **Suggested resolution:** Reword DDR-001's "compose `ReasoningProgress`" to "are ASA-authored reasoning content linked to `ReasoningProgress`," matching DDR-002's edge model.

**S2. The "one-way reference" claim is contradicted by DDR-001's own forward references to DDR-002 (and DDR-002 restates the same claim).**
- **Location:** DDR-001 → *Cross-References* ("*One-way reference: DDR-002 references this DDR, not the reverse*") and *Substrate-Stability Tracking*; DDR-002 → *Substrate-Stability Tracking* ("DDR-002 references DDR-001, never the reverse").
- **What's wrong:** Both documents assert DDR-001 does **not** reference DDR-002. DDR-001 in fact references DDR-002 repeatedly — Decision.6 ("*the node/relationship/constraint contract is DDR-002's*"), the Versioning table owners ("DDR-002 schema/field"), the feedback-loop write-authority section ("*schema is DDR-002's*"), the routing boundaries ("`CandidatePromotion` schema → DDR-002"), and the Appendix boundary map. A cold reader takes "not the reverse" at face value and immediately finds it false. The evident *intent* is one-way **authority/dependency** direction, but the literal claim is inaccurate.
- **Suggested resolution:** Rephrase to "the *authority* direction is one-way: DDR-002 depends on DDR-001; DDR-001 only routes schema concerns forward to DDR-002, it does not depend on it."

**S3. ADR-002 claims DDR-001's spike-findings records "the specific Enterprise capability the plane model depends on," which DDR-001 explicitly disclaims.**
- **Location:** ADR-002 → §2.2 and §4.1 (Alternative A); DDR-001 → *Spike Findings — Community → Enterprise*.
- **What's wrong:** ADR-002 twice attributes to DDR-001's spike-findings section "*the specific Enterprise capability the plane model depends on*." DDR-001's spike section records only a **structural** capability requirement (planes + edge types + cross-plane/cross-graph traversal) and then states outright: *"the specific edition-feature blocker from the original trial is **not** in the captured record and is **not reconstructed** here."* If "the specific Enterprise capability" means the specific edition feature Community lacked, the citation claims the target records something the target says it does not; if it means the structural requirement, the word "specific" overstates it. Either way the citing text and the cited section do not agree on what is recorded — and this underwrites a *ratified empirical rejection*, so precision matters.
- **Suggested resolution:** In ADR-002, change "the specific Enterprise capability" to "the *structural* capability requirement the plane model depends on," and note the specific edition-feature blocker is intentionally not reconstructed.

**S4. "SOFIA never self-modifies" is scoped three different ways across the corpus, and a non-EA-gated SOFIA write to the Operational KG plane sits under the strictest wording.**
- **Location:** ADR-001 §2.5; DDR-001 Decision.5 and Conformance check #4; DDR-002 §2.3.
- **What's wrong:** ADR-001 §2.5 scopes the invariant to *"SOFIA does not self-modify its **encoded reasoning** without EA approval."* DDR-001 broadens it, unqualified, to *"SOFIA **never self-modifies the KG**"* (Decision.5 and check #4). DDR-002 §2.3 then narrows it again — the distillation step writes `ObservedPattern` nodes into the **Operational KG plane** with `origin_mechanism: derived` and **no EA gate**, asserting this *"does not breach ADR-001's SOFIA-never-self-modifies invariant"* because Operational is a "staging tier." Operational is one of the five KG planes, so under DDR-001's unqualified wording a derived write to it *is* SOFIA modifying the KG. The reconciliation depends on an "Operational = staging tier below the EA gate" qualifier that DDR-001's own statement does not carry.
- **Suggested resolution:** Align the three statements on one scope, e.g. "SOFIA never self-modifies *authoritative/sanctioned* KG knowledge without EA approval; derived Operational staging-tier writes are exempt," and apply that wording in DDR-001 Decision.5 / check #4.

**S5. The metadata "Date" field means "creation date" in three documents but "latest-substantive-version date" in DDR-002.**
- **Location:** Metadata tables of all four documents vs. their `# Created:` headers and change logs.
- **What's wrong:** ADR-001 (Date 2026-06-03), ADR-002 (Date 2026-06-15), and DDR-001 (Date 2026-06-19) all set **Date = the `Created` header** (the v1.0.0 authoring date), even where the current version is higher (DDR-001 is v1.2.0). DDR-002 instead sets **Date 2026-06-22**, which is its **v1.1.0 amendment** date, diverging from its `Created: 2026-06-21`. A reader cannot tell whether "Date" is creation date or last-revision date, because the corpus uses it both ways.
- **Suggested resolution:** Pick one meaning corpus-wide (add a separate `Last-updated` field if both are wanted) and correct DDR-002.

**S6. DDR-002 §4 cites "ADR-001 §2.2 vocabulary" for four RG type names that ADR-001 §2.2 does not contain.**
- **Location:** DDR-002 §4 opening line; ADR-001 §2.2.
- **What's wrong:** DDR-002 says the RG types *"align to ADR-002 §2.6 / **ADR-001 §2.2** vocabulary: `ReasoningSession`, `ReasoningProgress`, `Evidence`, `RejectedAlternative`."* ADR-002 §2.6 does supply `ReasoningSession`/`ReasoningProgress`, but ADR-001 §2.2's illustrative artifact kinds are **`Finding` / `DirectiveCheck` / `Inference` / `Hypothesis`** — none of the four cited names appears there, and §2.2 explicitly defers canonical labels to the schema document. A reader checking §2.2 for "this vocabulary" finds different terms.
- **Suggested resolution:** Cite ADR-001 §2.2 for the capture *concepts* (evidence, rejected alternatives) and ADR-002 §2.6 for the two names it actually fixes; drop the implication that §2.2 supplies the four labels.

**S7. The three-hat review roles `LAA` and `SA` are never expanded anywhere in the corpus.**
- **Location:** ADR-001 §6 ("Enforcement"), ADR-002 §6 ("Enforcement"), and every "three-hat (LAA/SA/EA)" mention.
- **What's wrong:** The mandatory review gate is described as "three-hat (LAA/SA/EA)" but `LAA` and `SA` are never defined. `EA` is only *inferable* from the author byline ("Executive Architect"), and is used operationally as "EA gate/approval" without a hats-context definition. A newcomer cannot decode two of the three review roles that every SDD/DDR must pass.
- **Suggested resolution:** Expand LAA/SA/EA once at first use (e.g., in ADR-001 §6).

**S8. `ASD` is used but never expanded.**
- **Location:** DDR-001 (*Versioning* table "Solution (ASD)"; *Hybrid Persistence* "ASD bodies") and DDR-002 §2.1 ("Catalog never holds the produced ASD").
- **What's wrong:** "ASD" is used interchangeably with "the produced solution" / `(:Artifact:Solution)` but is never expanded in any of the four files. A first-time reader meets "(ASD)" with no referent.
- **Suggested resolution:** Expand ASD (e.g., "Architecture Solution Document") at first use, or replace it with "produced `Solution`."

**S9. Undefined proper noun "the Reboot."**
- **Location:** ADR-002 §2.2 ("*The trial itself predates the Reboot's formal capture…*").
- **What's wrong:** "the Reboot" is referenced as a known milestone/epoch with no definition anywhere in the corpus. A cold reader cannot place what "the Reboot's formal capture" refers to; the sentence only parses with unstated background.
- **Suggested resolution:** Replace with a self-contained phrase (e.g., "predates the current design corpus's formal capture") or define the term once.

**S10. Pervasive forward references to DDR-003, which is not part of the corpus.**
- **Location:** DDR-001 (footnotes, Versioning table, *Feedback-Loop Architecture*, *Cross-References*, Appendix) and DDR-002 (Decision, §2.3, §2.4, *Cross-References* "→ DDR-003", *Named gaps*); also ADR-001/ADR-002 "Feedback Loop Governance (forthcoming)."
- **What's wrong:** A large share of feedback-loop *governance* — thresholds, EA criteria, cadence, retention, remedy-boundary, condition vocabulary — is routed to DDR-003, which is not among the reviewed files. The references are honestly labelled "forthcoming/sibling," so nothing falsely claims DDR-003 already says X; but for a newcomer every "→ DDR-003" is a dead end, and the corpus is not self-contained on governance.
- **Suggested resolution:** Not necessarily a text defect if DDR-003 is a known forward dependency; if the corpus is meant to stand alone, add a one-line "DDR-003 is not yet authored" note where governance is first routed out.

---

### NIT

**N1. The 2026-07-01 "distillation" change-log entries reuse the prior version number in all four documents.**
- **Location:** Change logs of ADR-001 (two 1.0.0 rows), ADR-002 (two 1.0.0 rows), DDR-001 (two 1.2.0 rows), DDR-002 (two 1.1.0 rows).
- **What's wrong:** Each document has two change-log rows sharing one version number (authored vs. distilled), with the metadata Version/Date unchanged for the later edit. Defensible as a no-semantic-change reformat, but version number alone cannot distinguish "as authored" from "as distilled."
- **Suggested resolution:** Use an editorial suffix (e.g., 1.0.0-r2) or a dedicated "revision" column for non-semantic reformats.

**N2. DDR-002 §4 quotes a phrase from ADR-001 §2.5 that is not verbatim (and blends two promotion targets).**
- **Location:** DDR-002 §4 ("*per ADR-001 §2.5's 'EA-gated consolidation into encoded logic'*").
- **What's wrong:** The quotation marks imply a verbatim citation, but ADR-001 §2.5 contains no such string (it speaks of consolidating recurring reasoning "into encoded SOFIA logic" and "promotion into encoded knowledge"). Substantively, ADR-001 §2.5's promotion target is *encoded SOFIA logic (code)*, whereas the feedback loop DDR-002 attaches it to promotes RG findings into *KG ground-truth data nodes*; treating the two as the same "encoding-density-growth feature" slightly conflates logic-promotion and data-promotion.
- **Suggested resolution:** Drop the quotation marks (paraphrase), and note whether KG-fact promotion is intended as an instance of, or distinct from, §2.5's encoded-logic consolidation.

**N3. DDR-001's "four structural roles" vs. DDR-002's six `:Reasoning`-labelled node types.**
- **Location:** DDR-001 *Reasoning Graph* ("four structural roles"); DDR-002 §4/§5.
- **What's wrong:** DDR-001 describes the RG as four roles. DDR-002 tags six node types with the `:Reasoning` label — the four plus `ProvenanceSummary` and `CandidatePromotion` (added by later amendments). Reconcilable (the extra two are feedback-loop/provenance constructs, not synthesis-capture roles), but a reader counting `:Reasoning` nodes gets six against DDR-001's stated four.
- **Suggested resolution:** In DDR-001 note that feedback-loop constructs also reside in the RG region beyond the four synthesis roles.

**N4. DDR-001's "one per synthesis run / solution" is ambiguous on session granularity.**
- **Location:** DDR-001 *Reasoning Graph*, "Session root" bullet; DDR-002 §4 (`ReasoningSession` note).
- **What's wrong:** DDR-001 says the session is "one per synthesis run / solution." Read as "one per solution," it would contradict DDR-002's `PRODUCED` `0..*` (a session may produce several candidate solutions). DDR-002 has to disambiguate it ("one session per run, not one solution per session") while asserting consistency; the source phrasing is the ambiguity.
- **Suggested resolution:** Change DDR-001 to "one per synthesis run" and drop "/ solution."

**N5. Document-class acronyms `ADR` / `DDR` / `SDD` are never expanded.**
- **Location:** Throughout all four files.
- **What's wrong:** The document types are only ever used as ID prefixes; none is expanded. Mostly inferable from context, but a strict first-time reader has no definition of ADR / DDR / SDD anywhere in the corpus.
- **Suggested resolution:** Expand each once (e.g., in the first document's header block).

**N6. "BCDR plans" is used as an Artifact-family example without expansion.**
- **Location:** DDR-002 Decision.4 and §5 (`(:Artifact)` family examples).
- **What's wrong:** "BCDR" appears twice as a produced-deliverable example with no expansion.
- **Suggested resolution:** Expand once (e.g., "business-continuity / disaster-recovery plans").

**N7. DDR-001 Two-Graph-model table footnote numbers are not in reading order.**
- **Location:** DDR-001 *Knowledge Graph — five typed planes* table.
- **What's wrong:** The "Operational" row is marked footnote **²** while the "Governance" row below it is marked footnote **¹**; the superscripts descend as the reader moves down the table, and the footnote definitions (¹ then ²) are ordered opposite to the marker appearances.
- **Suggested resolution:** Renumber so footnote ¹ is the first marker encountered (Operational), ² the second (Governance).

---

## 3. Checked-Clean

The following were verified and came back clean:

1. **All cross-document version pins resolve and match the declared versions.** DDR-001 pins `ADR-001 v1.0.0` and `ADR-002 v1.0.0`; DDR-002 pins `ADR-001 v1.0.0`, `ADR-002 v1.0.0`, `DDR-001 v1.2.0` (in both its References line and its Cross-References). Every pinned version equals the version the target document actually declares. No stale or non-existent pin.
2. **All intra-document `§`-references resolve** in every file — ADR-001 (§2.1–§2.5, §4, §6 checks), ADR-002 (§2.1–§2.7, §4.1–§4.6, §5.2, §5.3), DDR-001 (all `ADR-002 §…` and `ADR-001 §…` pointers), DDR-002 (§1–§7, including all `§7 check #NN` back-references — #4, #9, #10, #14, #15, #17, #19, #20, #21 — and the contested-T2 pointers). No dangling `§`-pointer found.
3. **DDR-002's 21-invariant CI-only set partitions exactly.** Safety-critical tier {1, 7, 9, 11, 13, 14, 15, 16, 17, 19, 21} (11) and follow tier {2, 3, 4, 5, 6, 8, 10, 12, 18, 20} (10) together cover checks 1–21 with no overlap and no omission; the "19 → 21" change-log note matches the count.
4. **Plane set is consistent** across ADR-002, DDR-001, and DDR-002: five core planes (Catalog, Environment, Operational, Governance, Standards) **plus** Extension, with cost as the first Extension registration and explicitly *not* a sixth core plane. Same enumeration and order in all three.
5. **Three-store persistence backbone is consistent** across ADR-002 §2.4, DDR-001, DDR-002: Neo4j (system of record), PostgreSQL (workflow/audit/staging), Firestore (immutable snapshots), **no vector store** — stated identically and reinforced by the no-vector conformance checks.
6. **Write-authority assignment is consistent** across ADR-002 §2.6, DDR-001, and DDR-002 §4/§7 #7: ASA authors `ReasoningProgress`; AOE owns the `ReasoningSession` lifecycle only; all RG writes gateway-mediated and driver-less.
7. **Role acronyms `ASA` / `AOE` are defined once and used consistently** — Architecture Solutioning Agent / Agent Orchestration Engine (ADR-002 §2.6) — with no conflicting expansion elsewhere.
8. **`SOFIA` is expanded once** (ADR-001 §1) and never re-expanded differently.
9. **Section/heading numbering is sequential and unbroken** in all four documents (no skipped, duplicated, or impossible numbers; ADR-002's alternatives run A–F under §4.1–§4.6 cleanly; both DDRs' Decision.1–.6 are complete).
10. **The `approving-state` set `{approved, approved_conditional}`** is used consistently in DDR-002 §2.4 and §7 #15, and the six `conclusion_type` values map coherently onto the seven §5 correction-surfaces (integration and cost as noted variants).
11. **The Community→Enterprise spike is consistently reported as an empirical, ratified rejection** (trial occurred; Enterprise required) across ADR-002 §2.2/§4.1 and DDR-001's Spike Findings; DDR-001's guard against attributing the rejection to a single-database limit correctly cross-references ADR-002 §2.3 (the one caveat about *what specifically* is recorded is finding S3).
12. **ADR-002 §7's dependency claim checks out:** its statement that "§2.1 and §2.4 build on ADR-001 §2.2 and §2.3" resolves — ADR-002 §2.1 builds on ADR-001's capture invariant (§2.2), and ADR-002 §2.4 builds on ADR-001's deterministic/probabilistic framing (§2.3).
13. **"Governance" is explicitly disambiguated** (DDR-001 footnote): the Governance *plane* vs. feedback-loop *governance* (DDR-003) vs. three-hat *governance* — no term-collision left implicit.
