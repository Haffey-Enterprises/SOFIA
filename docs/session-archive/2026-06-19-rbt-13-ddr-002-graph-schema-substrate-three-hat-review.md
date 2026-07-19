# File: docs/reviews/2026-06-19-rbt-13-ddr-002-graph-schema-substrate-three-hat-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: Pre-authoring three-hat review (Pass 1) of the ratified DDR-002 Graph Schema design substrate (RBT-13). Serves the substrate-readiness gate before Claude Code authors DDR-002 from this substrate under DIRECTIVE-026.

# Three-Hat Review — 2026-06-19 (RBT-13 DDR-002 Graph Schema Substrate — Pre-Authoring Readiness Gate, Pass 1)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-19 |
| **Reviewer** | Claude (claude.ai design instance) — Pass-1 three-hat reviewer wearing LAA / SA / EA hats, under DIRECTIVE-026, on behalf of Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC |
| **Scope** | The ratified `DDR-002 Graph Schema — Ratified Design Substrate` (RBT-13, 2026-06-19) as input to authoring `docs/ddr/DDR-002-graph-schema.md` — is it sound and clear enough to author the DDR? |
| **Authority** | RBT-13 acceptance criterion (three-hat review → ACCEPTED); ENG-STD-001 §12.6 (three-hat) + CSD DIRECTIVE-007 (multi-role review, §7.2 severity vocabulary); operator direction (2026-06-19 session). |
| **Outcome** | **PASS WITH FINDINGS** — 0 BLOCKING, 6 MATERIAL (all fold into the substrate / authoring handoff before Code authors), 2 COSMETIC. All three hats: `proceed-with-changes`. The readiness gate is satisfied conditional on the MATERIAL findings being folded before the authoring handoff. |

---

## §0 Historical Context (First-Execution Preamble)

This is the **first pre-authoring *substrate* three-hat review** in the Reboot. Prior three-hat passes ran on *authored* artifacts (ADR-001 / RBT-7, ADR-002 / RBT-8, DDR-001 / RBT-12) or on a script (RBT-35). DDR-001 was authored from a "ratified v0.3 design substrate," but its three-hat cycle (Pass 1→3) executed against the authored DDR, not the substrate.

This review establishes a distinct, earlier gate: a fresh-eyes pass on the *ratified substrate* before it is handed to Claude Code for authoring. It does **not** replace the post-authoring DDR-acceptance three-hat that RBT-13's acceptance criterion still requires against the authored `DDR-002-graph-schema.md`. Two gates, two artifacts:

- **This gate (pre-authoring):** is the substrate sound and clear enough to author from?
- **The RBT-13 acceptance gate (post-authoring):** does the authored DDR-002 conform and promote to ACCEPTED?

Cadence: per the established two-clean-cycles-to-promote discipline, the natural follow-on is an independent Pass-2 fresh-eyes read of the *revised* substrate (after MATERIAL findings are folded) confirming a clean substrate before the Code authoring handoff.

---

## §1 Scope

### 1.1 In-scope per RBT-13 + operator direction

- `DDR-002 Graph Schema — Ratified Design Substrate` (the uploaded artifact, 2026-06-19) — soundness and clarity as authoring input across all sections (§0 Frame through §8 Boundary routing + Appendix ratification trace).
- Internal consistency of the substrate (cross-references, ruling-citation sets, invariant scoping).
- Conformance of the substrate's framing and citations to the **fresh-fetched** canonical authorities: the Reboot Decision Ledger (rulings R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25), ADR-002 (Graph as System of Record, ACCEPTED), DDR-001 status (RBT-12), and the RBT-13 ticket itself.
- The R8 one-way reference discipline (architecture → schema; DDR-001 not re-opened) and the R22 feedback architecture/governance split, as they bound what DDR-002 may own.

### 1.2 Sources fresh-fetched for this review (per DIRECTIVE-026 §26.5 / ENG-STD-003 §13.5.9)

- **Linear RBT-13** (state, relations, comments) — In Progress; blockedBy RBT-12; blocks RBT-15…RBT-26; relatedTo HEB-9; zero comments.
- **Linear RBT-12** (the blocker / DDR-001) — **Done** 2026-06-19; DDR-001 v1.0.0 ACCEPTED on `develop` @ `15ff20f` (PR #12).
- **Notion Reboot Decision Ledger** (`374caeea…`) — all cited rulings read in full.
- **ADR-002** (project knowledge) — §2.2 / §2.3 plane model, §2.6 reasoning-state write authority, §4.1 Community alternative.

### 1.3 Out of scope (deliberately)

- The **authored** DDR-002 — does not exist yet; its conformance is the post-authoring RBT-13 acceptance gate, not this review.
- **DDR-001's internal completeness** (e.g., whether its spike-findings section fully grounds the ADR-002 §2.2 capability bar) — DDR-001 is landed (RBT-12 Done); its internals are owned upstream of this schema DDR.
- **DDR-003 governance content** (RBT-14) and **SDD-level realization** (RBT-15/RBT-25 et al.) — owned elsewhere by R22 / R8; only the *boundary* is in scope here.
- **ADR-002's stale author-identity string** — already tracked corpus-wide as **RBT-36** (see §3); not re-filed here.
- Conformance *mechanization* — owned by **RBT-33**; this review checks that the substrate names the invariant set, not that CI enforces it.

---

## §2 Findings

### 2.1 BLOCKING findings — must resolve before the readiness gate is satisfied

**None.** The substrate is the product of section-by-section ratification; every cited ruling resolves against the fresh-fetched ledger; the sole blocking dependency (DDR-001 / RBT-12) is landed and correctly sequenced ahead of RBT-13. No finding rises to BLOCKING — no design contradiction, no un-landed upstream, no un-ratified commitment.

### 2.2 MATERIAL findings — fold into substrate / authoring handoff

#### Finding M-1: "Six planes" framing contradicts the canonical "five core planes + Extension" model

**Location:** Substrate §0 Frame (line 15, "enterprise ground truth, six planes"); §2 section header (line 43, "The six planes — node schemas").

**Description:** The substrate's headline framing counts the Extension/cost plane as one of "six planes." The canonical model fixed upstream is **five core planes plus an Extension plane**: ADR-002 §2.2 ("five planes plus Extension and the RG") and §2.3 ("five planes plus an Extension plane"); ledger **R5** ("five KG planes (+ Extension)"); ledger **R23** explicitly rules cost is realized "**not as a sixth core plane**" but as the first Extension registration. The substrate itself knows this distinction — §1 line 31 ("Core planes are fixed by DDR-001; the registry is the Extension surface") and §2.6's "R23 exemplar" framing — but the headline "six planes" elides it.

**Why material (not blocking):** The underlying *design* is correct (cost-as-Extension). This is a framing/labeling drift, not a design error, and is fixable by reframing without re-deliberation. But if carried verbatim into DDR-002, "six planes" would put the DDR in tension with an ACCEPTED ADR (ADR-002 §2.2/§2.3) and with R23 — the precise core/Extension boundary R23 was authored to preserve. That is debt worth removing before the author inherits it.

**Disposition:** Reframe §0 and the §2 header to "five core planes + the Extension plane (cost = first Extension registration per R23)," or add a one-line clarifier that §2 enumerates five core planes (§2.1–§2.5) plus the Extension surface (§2.6). Fold into the substrate before the authoring handoff.

#### Finding M-2: Dangling internal cross-references to a non-existent §9

**Location:** Substrate §0 Frame (line 13, "it is routed in §9"); §2.5 (line 85, "`Process` node deferred, §9").

**Description:** The substrate has no §9. Boundary routing and conscious exclusions live in **§8** ("Boundary routing & doc frame"). Both "§9" pointers are broken and resolve to nothing.

**Why material:** Broken cross-references propagate into the authored DDR if not corrected, and the §0 routing pointer is load-bearing (it tells the reader where named-but-not-owned concerns are routed). A reader following "§9" lands nowhere.

**Disposition:** Repoint both "§9" references to **§8**. Mechanical fix; fold into the substrate.

#### Finding M-3: Bare "§2.6" cross-references collide with the substrate's own §2.6

**Location:** Substrate §4 (line 142, "Write authority (§2.6 invariant)"); §7 (line 194, "§2.6 write-authority"); §8 boundary map (line 207, "full `ReasoningProgress` fields (§2.6)").

**Description:** The substrate's own §2.6 is "Extension mechanism + cost plane." The three bare "§2.6" references above mean **ADR-002 §2.6** (Reasoning-state write authority — ASA authors ReasoningProgress, AOE owns ReasoningSession lifecycle, fields are SDD-level), as confirmed by fresh-fetch of ADR-002. As written, each reads as a pointer to the substrate's *own* §2.6 (cost/Extension), which is the wrong target. (Two other §2.6 references are fine: line 31 is a correct substrate-internal pointer to the `PlaneDefinition` registry; line 135 is correctly qualified "ADR-002 §2.6.")

**Why material:** Cross-references that resolve to the wrong section corrupt the conformance-invariant trail (the §7 list and §8 boundary map are exactly the surfaces RBT-33 will mechanize against). The write-authority invariant must point unambiguously at ADR-002 §2.6.

**Disposition:** Qualify the three bare references as "**ADR-002 §2.6**." Fold into the substrate.

#### Finding M-4: §5 feedback-loop content risks restating DDR-001 architecture / pre-empting DDR-003 governance

**Location:** Substrate §5 (Cross-graph linkage + the feedback loop), esp. the "CandidatePromotion + feedback loop (R22)" and "Generalized correction mechanism" prose (lines 157–169).

**Description:** R8 routes feedback-loop *architecture* (the RG → `CandidatePromotion` → EA-gated → `PROMOTES_TO_KNOWLEDGE` mechanics) to **DDR-001**, and R22 routes feedback-loop *governance* (signal definitions, thresholds, EA approval criteria, cadence, retention/audit policy) to **DDR-003 (RBT-14)**. The substrate correctly states the routing — §5 line 169 ends "Loop architecture → DDR-001; governance → DDR-003; workflow → SDD." But the surrounding prose describes the mechanism (Refine / Request-new / Correct-scope; "the EA-gate is a *diagnosis*, not a mechanical bump"; the append-only/terminal-status promotion semantics) at a depth that blurs the line between *schema contract* (DDR-002's to own — the node/edge shapes and the structural invariants like exclusion-by-label and append-only) and *architecture/governance* (DDR-001's / DDR-003's, to be cited, not re-authored).

**Why material:** This is the R8 one-way-reference discipline at its most load-bearing. If the DDR author carries §5's narrative verbatim, DDR-002 risks duplicating DDR-001's accepted architecture (a drift surface between two documents) or stating DDR-003 governance before DDR-003 exists (pre-emption). The substrate is not itself unsound here — it names the boundary — but it does not draw the in/out line crisply enough to author safely from.

**Disposition:** Add an explicit in/out delimiter to §5: enumerate what DDR-002 *owns* (the `CandidatePromotion` node schema; the promotion-edge grammar; the structural invariants — exclusion-by-label, append-only, the provenance-chain traceability) versus what it *cites* (the promotion *mechanics/data-path* → DDR-001; the *diagnosis policy / EA approval criteria* → DDR-003; the *workflow* → SDD). Fold into the substrate so the author has a bright line.

#### Finding M-5: Provenance invariant overstated in §1 relative to §7/§8 scope, and partial across RG node types

**Location:** Substrate §1 ("Provenance on every node. Every node carries a provenance group"); §7 ("Existence constraints on the provenance group … on every **core-plane** node"); §8 native conformance ("every **KG** node carries a plane label + provenance"); §4 RG schemas — `ReasoningSession` (line 137) and `ReasoningProgress` (line 138) **carry** `provenance (T1)`; `Evidence` (line 139) and `RejectedAlternative` (line 140) **omit** it.

**Description:** §1 states the provenance group is universal ("every node"), but the enforced scope in §7/§8 is narrower ("every core-plane / KG node"). RG nodes are not KG/core-plane nodes, yet two RG types carry provenance and two do not — an unexplained split. The author cannot tell whether Evidence/RejectedAlternative omit provenance by design (e.g., inheriting it via the parent `ReasoningProgress` edge, with `source_node_version` + `observed_at` as the RG-native provenance surrogate) or by oversight.

**Why material:** The provenance group is a DB-enforced existence constraint and a named conformance invariant (RBT-33 territory). An invariant stated as universal in §1 but scoped to KG nodes in §7/§8, with an unexplained RG carve-out, will produce either an over-broad constraint (failing valid Evidence/RejectedAlternative writes) or a silent gap — exactly the ambiguity conformance authoring cannot absorb.

**Disposition:** Reconcile in the substrate: (a) scope §1's statement to "every KG node" (or state the RG-inclusion intent explicitly), and (b) either add the provenance group to `Evidence`/`RejectedAlternative` or document the RG-provenance exception and its surrogate (`source_node_version` + the `SUPPORTED_BY`/`REJECTED` edge to a provenance-bearing `ReasoningProgress`). Fold into the substrate.

#### Finding M-6: Two non-matching governing-ruling lists (§0 omits R9; §8 includes R9)

**Location:** Substrate §0 Frame ("Governing rulings: R3, R5, R6, R8, R10, R18, R20, R22, R23, R24, R25" — **no R9**); §8 doc-frame ("references … rulings R3/R5/R6/R8/**R9**/R10/R18/R20/R22/R23/R24/R25").

**Description:** The substrate presents two ruling sets that differ by R9 (three-store). R9 is genuinely referenced (the §6 dual-home snapshot store = Firestore per R9, routed to DDR-001 in §8), so inclusion is correct; §0's omission is the discrepancy. The DDR's `References` field needs one authoritative set.

**Why material:** The References field is a governed artifact surface; a substrate that hands the author two different ruling sets forces a silent judgment call and risks an incomplete References block.

**Disposition:** Add **R9** to §0's governing-rulings list (reconciling to §8's superset). Fold into the substrate.

### 2.3 COSMETIC findings — noted, no-action required

- **C-1 — "R10 (no PHI)" citation label.** §0 cites "R10 (no PHI)." R10's headline ruling is *"No CMEK initial build"*; no-PHI-by-design is the enforced-constraint clause *within* R10 ("classification at intake / ingestion"). Substantively correct (R10 does establish the no-PHI enforced constraint); the shorthand label just isn't R10's headline. Tighten when authoring if convenient — cite R10's no-PHI-by-design clause specifically.
- **C-2 — existence-constraint capability attributed to "ADR-002/R20."** §7 line 191 credits "the Enterprise edition committed in ADR-002/R20" for buying existence constraints. The existence-constraint *capability* is an Enterprise-*edition* feature — ledger **R3** (edition). **R20** is the *runtime-placement* ruling (self-managed on GKE). ADR-002 §2.2 bundles both, so "ADR-002" is the right ADR; the dedicated edition ruling is R3, not R20. Tighten the ruling pointer when authoring if convenient.

### 2.4 No-drift confirmations (positive findings)

- **DDR-001 "landed, upstream" claim — verified.** Substrate §8 asserts "RBT-12/DDR-001 (landed, upstream)." Fresh-fetch: RBT-12 **Done** 2026-06-19, DDR-001 v1.0.0 ACCEPTED on `develop` @ `15ff20f` (PR #12); RBT-13 moved to In Progress at 14:28, *after* RBT-12 closed at 14:11. The blocker is discharged and the sequencing is clean. (The Linear `blockedBy` relation persists structurally; it is satisfied, not open.)
- **R8 one-way reference honored.** The substrate routes architecture, three-store persistence, plane-model, gateway, and feedback-loop *architecture* one-way to DDR-001 (§0, §8 "Cited, never re-opened"); it does not re-open DDR-001. Structurally conformant (the §5 prose-depth caveat is M-4, not a re-opening).
- **ADR-002 §2.6 anchor — correctly cited and faithfully stated.** The RG write-authority claim (§4 line 142: ASA authors ReasoningProgress; AOE owns ReasoningSession lifecycle; writes via knowledge-service) and the "ReasoningProgress fields are SDD-level" claim (§4 line 135) both match ADR-002 §2.6 verbatim in substance. (Disambiguation of the *bare* pointers is M-3; the *content* is faithful.)
- **RG label reconciliation aligns to canon.** `Inference → ReasoningProgress`, `Hypothesis → RejectedAlternative`, `Evidence`/`ReasoningSession` kept — consistent with ADR-002 §2.6 and ADR-001 §2.2 vocabulary.
- **R23 cost-via-Extension correctly cited.** The substrate cites R23 for the cost plane (ratified 2026-06-19 in this very RBT-13 cycle) and models cost as the first Extension registration — exactly R23's ruling. (The substrate is *ahead of* the RBT-13 ticket's stale ledger line — see FP-1.)
- **Community-rejection not re-derived.** The substrate cites R3 (Enterprise) without re-litigating the Community failure; the durable home stays DDR-001's spike-findings per the R3 clarification, honoring ADR-002 §2.2/§4.1's forward-point. No re-derivation, consistent with "Closed — not to be re-derived per session."
- **R18 single-artifact authoring posture — correct.** Substrate header + §8: `0.1.0` PROPOSED → `1.0.0` ACCEPTED, single original-authoring Change Log row — matches R18.
- **R24 / R25 correctly applied.** Operational holds distilled `ObservedPattern`s (not telemetry); Governance holds `GateDecision` references (not the disposition-event stream) — R24. Completeness is reversibility-tiered (T1–T4), not a uniform dial — R25.
- **R6 no-vector invariant present** as a documented invariant + conformance check (§1, §7, §8). Conformant.
- **Filename / landing path consistent.** Substrate header + §8 land at `docs/ddr/DDR-002-graph-schema.md`; RBT-13 acceptance specifies `docs/ddr/DDR-002-*.md`. Match.

### 2.5 Normative-interpretation note

No new normative-interpretation question requiring codification surfaced. The one interpretive call worth recording is **scope-of-the-provenance-invariant** (M-5): "does *every node* carry provenance, or *every KG node*?" — this is a substrate-internal reconciliation (resolve in the DDR), not a governance-doc amendment. It does not need a ledger ruling; it needs the §1↔§7/§8 reconciliation called for in M-5.

---

## §3 Forward-Pointer Triage

Out-of-scope items surfaced during review, routed rather than absorbed. **No Linear/Notion writes are made by this review** — all captures below are held for explicit operator ratification (deliberation discipline; DIRECTIVE-026 keeps claude.ai out of unilateral tracker writes, and DIRECTIVE-025 dedup applies to any *new* ticket).

### FP-1 — RBT-13 ticket's stale "Ledger" line mis-cites cost ruling

**Source:** LAA-hat scope check (substrate vs ticket).

**Description:** RBT-13's description Ledger line reads "R8 (split — schema half), R6 (no vector properties), **R12 (cost plane folded)**." Fresh-fetch of the ledger shows **R12 = "Fresh-set inventory ratified"** (unrelated to cost); the cost ruling is **R23 (Cost plane via Extension registration)**, ratified 2026-06-19 *after* the ticket was written (2026-06-03). The substrate is correct (cites R23); the ticket is stale.

**Proposed disposition:** Update the RBT-13 description Ledger pointer to the substrate's actual governing set (at minimum R8 / R6 / **R23**, plus R24 / R25 as ratified this cycle). This is a description-hygiene edit to an *existing* ticket (no new ticket; no dedup sweep needed). **Held for ratification.**

### FP-2 — ADR-002 stale author-identity string

**Source:** SA-hat cross-check of ADR-002 during anchor verification.

**Description:** ADR-002 carries `# Author: Thaddeus Haffey — Enterprise Architect, Haffey Enterprises` (the pre-reconcile string). The current canonical identity is *Executive Architect, Haffey Enterprises LLC*.

**Proposed disposition:** **No new action — already tracked.** The ledger's RBT-35 close-out records **F1 → RBT-36** (corpus-wide pre-schema author-identity sweep, explicitly scoping ADR-001/002 + 5 reviews of record + 1 handoff). Noted here only so the DDR author authors **DDR-002 with the current string** ("Executive Architect, Haffey Enterprises LLC") from the outset.

### FP-3 — Substrate-declared post-merge filings (confirm, don't lose)

**Source:** Substrate §8 ("New items to file post-merge").

**Description:** The substrate itself names three post-merge filings: a **`Process` node-type ticket** (Standards will want it; the §2.5/§9→§8 deferral), the **detection/correction SDD**, and the **selection-edge preference-landing**. These are the substrate's own forward dependencies, not review findings.

**Proposed disposition:** Confirm these are filed post-merge (with a DIRECTIVE-025 dedup sweep at filing time). Surfaced here so they ride the same triage ledger. **Held for ratification.**

### Forward-pointer triage summary

| Proposed ID | Summary | Disposition |
|---|---|---|
| RBT-13 (update) | Ticket Ledger line mis-cites cost as R12; should be R23 (+R24/R25) | Description-hygiene edit to existing ticket — **held for ratification** |
| RBT-36 (existing) | ADR-002 stale author-identity string | **Already tracked** — author DDR-002 with current string; no new action |
| (new, post-merge) | `Process` node-type ticket | Substrate-declared — confirm filing post-merge w/ dedup — **held** |
| (new, post-merge) | Detection/correction SDD | Substrate-declared — confirm filing post-merge w/ dedup — **held** |
| (new, post-merge) | Selection-edge preference-landing | Substrate-declared — confirm filing post-merge w/ dedup — **held** |

---

## §4 Audit Outcome

> **PASS WITH FINDINGS.** Zero BLOCKING findings; six MATERIAL findings, all dispositioned to fold into the substrate (or the authoring handoff) before Claude Code authors DDR-002 — M-1 (five-core-+-Extension framing), M-2 (§9→§8 cross-refs), M-3 (bare §2.6 → ADR-002 §2.6), M-4 (§5 in/out boundary line), M-5 (provenance-invariant scope reconciliation), M-6 (add R9 to §0 ruling list); two COSMETIC citation-precision items (C-1, C-2) recorded, no-action. Three forward-pointer items routed (FP-1 ticket-hygiene edit held for ratification; FP-2 already tracked as RBT-36; FP-3 substrate-declared post-merge filings held). Ten no-drift confirmations recorded, including the load-bearing one: DDR-001 is landed (RBT-12 Done @ `15ff20f`) and RBT-13 is sequenced behind it.

**Per-hat verdicts (ENG-STD-001 §12.6 aggregation — any BLOCKING → `pause`; else any MATERIAL → `proceed-with-changes`; else → `proceed`):**

| Hat | Findings raised | Verdict |
|---|---|---|
| **LAA** — *what is this change?* | Substrate matches RBT-13 scope (the R8 schema half) and declares its forward deps; M-4 (scope-creep risk at the §5 feedback boundary); M-6 (references-set consistency); FP-1 (ticket Ledger drift). | `proceed-with-changes` |
| **SA** — *how does it conform?* | M-1, M-2, M-3, M-5, M-6 raised; C-1, C-2 noted. Cited rulings all resolve against fresh-fetched ledger; ADR-002 §2.6 anchor faithfully cited (M-3 is disambiguation only). | `proceed-with-changes` |
| **EA** — *should it land in this shape, now?* | Concurs M-1 (core/Extension is a deliberate posture from ADR-002/R23 — don't blur it) and M-4 (R8/R22 boundary posture — don't restate DDR-001 / pre-empt DDR-003). Confirms: timing is right (DDR-001 landed); reversibility sound (R25 reversibility-tiered completeness); no position committed that warrants amendment-class deliberation beyond what's already ratified (R23/R24/R25 this cycle). | `proceed-with-changes` |

**Gate decision:** The substrate-readiness gate is **satisfied conditional** on folding the six MATERIAL findings before the Code authoring handoff. No hat reads `pause`; none reads a clean `proceed` (MATERIAL findings outstanding) — so the honest aggregate is `proceed-with-changes` across all three. Recommended next step: fold M-1…M-6 into the substrate, then an independent **Pass 2** fresh-eyes read confirms a clean substrate (two-clean-cycles convention) before Claude Code authors `DDR-002-graph-schema.md`.

---

## §5 Cross-References

- **Authority for this review:** RBT-13 acceptance criterion; ENG-STD-001 §12.6 (three-hat); CSD DIRECTIVE-007 (multi-role review; §7.2 severity vocabulary BLOCKING/MATERIAL/COSMETIC/POSITIVE).
- **Substrate reviewed:** `DDR-002 Graph Schema — Ratified Design Substrate` (RBT-13, 2026-06-19), authoring target `docs/ddr/DDR-002-graph-schema.md`.
- **Canonical authorities fresh-fetched:** Reboot Decision Ledger (`374caeea…`) rulings R3/R5/R6/R8/R9/R10/R18/R20/R22/R23/R24/R25; ADR-002 §2.2/§2.3/§2.6/§4.1; Linear RBT-13 (state/relations/comments) and RBT-12 (Done @ `15ff20f`, PR #12).
- **Findings disposition tracking:** M-1…M-6 → fold into substrate before authoring handoff; FP-1 → RBT-13 description edit (held); FP-2 → RBT-36 (existing); FP-3 → post-merge filings (held).
- **Role boundary (DIRECTIVE-026):** This review is claude.ai design/acceptance work; Claude Code authors DDR-002 and executes all git operations from the (revised) substrate via the `author-decision-record` skill.
- **Related reviews:** `docs/reviews/2026-06-19-rbt-12-ddr-001-data-architecture-three-hat-review.md` (DDR-001, the upstream architecture half — sibling post-authoring three-hat); ADR-002 review cycles (`docs/reviews/2026-06-15-…`, `…-2026-06-16-…-cycle-2.md`).
- **Future review cadence:** Pass 2 (independent fresh-eyes) on the revised substrate → then the separate post-authoring RBT-13 acceptance three-hat against the authored DDR-002.
