# Deliberation Record — DDR-002 Additive Amendment Batch (RBT-54)

> Intended repo home: `agent-loop/deliberation/ddr-002-amendment-batch/record.md`

| Field | Value |
|---|---|
| **Session** | RBT-54 design/authoring session, 2026-07-13 (claude.ai surface) |
| **Ticket** | RBT-54 — DDR-002 additive amendment batch (Touches 1–3 + riders) |
| **Basis** | Ratified dispositions Items 3+4+5 (run-011 union disposition, 2026-07-05) · RBT-54 Touch-3 comment + three addenda (2026-07-10/11/12) · prep-addition + closure-obligation comments (2026-07-12) · run-010/011 audits (D2 family + riders) · DDR-004 v1.0.0 (Pre-Acceptance Conditions 1–2) |
| **Rulings** | Items A through G2 below, each ratified individually by Tad, 2026-07-13 |
| **Status** | RATIFIED — the authoring pass draws exclusively from this record; nothing here self-executes |
| **Governing skill** | `author-decision-record` @ bedrock 1.3.0 — SKILL.md sha256 `28a7696576cc6c2d2f2a313f812e3696bdcf3468ebade9bcb485fca71c012afe` (session cache verified against the pin at session open) |

## §0 Substrate manifest (fresh-fetched this session; pointers, not copies)

All canonical fetches at develop HEAD `4f4b79ebcfed00caff6340e296d45517098e5cd0` (Haffey-Enterprises/SOFIA):

- `docs/ddr/DDR-002-graph-schema.md` — blob `8dbabefa` · v1.2.0 ACCEPTED (landed 2026-07-03, PR #8, commit `c935c68`)
- `docs/sdd/SDD-001-knowledge-service.md` — blob `c7b43d4d` · v1.1.0 ACCEPTED
- `docs/ddr/DDR-004-inherited-confidence-derivation.md` — blob `cc33cda3` · v1.0.0 ACCEPTED-WITH-CONDITIONS
- `agent-loop/runs/run-011-sdd-001/disposition.md` (Items 3/4/5 verified verbatim) · `run-010-sdd-001/audit.md` + `run-011-sdd-001/audit.md` (finding IDs 708bcb75 · 7b9a0f8b · 0d3b0fe3 · 8d9f62da · 55ba066a all verified at their recorded verdicts)
- bedrock 1.3.0 cache template hashes (session-verified): adr `1540825b…` · ddr `59068b3a…` · sdd `ba21f228…`
- Linear: RBT-54 (description + all six comments) · RBT-46 · RBT-53 · SOF-154 · HEB-52

Not fetched (not on the ticket's pre-author list; version-chain question resolved from the landed Change Log): the triage-001 record.

## Item A — Version chain + batch sequencing (RATIFIED)

DDR-002 v1.2.0 is landed and ACCEPTED on develop (2026-07-03, triage-001 batch); no pending tail on the document. RBT-46 shows open but re-scoped — moved to Backlog and retitled to a DDR-003-Phase-2 re-evaluation on 2026-07-12; its five touches did not land as their own amendment, and its proposed check numbering has been overtaken by the landed #22–#25. **Ruling:** the batch proceeds now against v1.2.0; RBT-46 imposes no ordering constraint; the lands-before-BUILD gate remains the sole constraint and is currently satisfiable without the 1a/1b fallback. Lineage note (criterion-shift, not blocker): RBT-54's Touch-2 lineage sentence attributes the frozen-content widening to RBT-46 touch 4; the landed vehicle was triage T-20's `PROPOSED_FROM`-closure span, with the routed structuring question living in the landed §4 named-gap text (created v1.1.0/RBT-43). Touch 2's target exists in landed canon either way.

## Item B — Touch 1: the #25 scoping clause (RATIFIED, shape 1)

**Defect:** landed #25's biconditional demands a `RETRACTS` edge on every retraction-kind candidate while #21 (safety-critical) forbids the edge pre-approval — jointly unsatisfiable in any pre-decision retraction window (708bcb75 rider), and permanently violated by every legitimately rejected retraction.

**Ruling — shape 1:** scope #25's forward direction to executed proposals (terminal `status: promoted`), keyed to DDR-002 §5's own execution gloss; reverse direction unscoped. Rejected alternatives: dropping the forward direction (forfeits the audit purpose); keying to the approving verdict (moves the window to approved-but-unmaterialized); writing the edge at proposal (weakens safety-critical #21 to rescue a follow-tier check; 55ba066a's downstream-can't-rescue-upstream ruling stands). Authoring basis text as ratified:

> **25. `proposal_kind` ↔ `RETRACTS`-edge consistency (scoped to executed proposals):** a `CandidatePromotion` with `proposal_kind: retraction` at terminal `status: promoted` carries a `RETRACTS` edge; a `RETRACTS` edge originates only from a `proposal_kind: retraction` node. A retraction proposal before materialization carries no `RETRACTS` edge — the edge's writing is the EA-gated act (#21; §5). *(Follow tier — unchanged.)*

Ratification followed a three-scenario lifecycle walkthrough (happy path · rejected retraction · rogue edge), which stands as the template for the close-time re-check of the 708bcb75 construction. Correlated call-sites (Decision.7, §2.4, §5 retraction paragraph, §7 tier list) fetch-verified at drafting; read this session as needing no substantive touch. Boundary left routed: post-materialization verdict-flip on a retraction stays DDR-003 remedy-boundary territory.

## Item C — Touch 2: ProvenanceSummary structuring (RATIFIED, C1–C3)

Honest floor carried verbatim: no valid finding forced this touch; opened on economy; zero materializations to date (form-fixing pre-traffic, no constants involved).

- **C1 — shape A (RATIFIED):** additive aligned-array realization — add `frozen_evidence_ids` (correlation key) + `frozen_source_node_refs`; declare index-alignment across the four `frozen_*` arrays, keyed by `evidence_id`. Realizes SDD-001 §3.5.3's proposed per-Evidence-entry semantics in the batch's additive grammar; primitives only (audit stays a read, never a parse); #20 completeness becomes set-equality on evidence IDs. Rejected: per-entry child nodes (fights the landed denormalization posture); serialized entry documents (blob-by-another-name). Drafting note: reconcile the §4 gap sentence / Named Gaps entry asymmetry at both sites.
- **C2 — CI-clause pruning (RATIFIED):** adopt SDD-001 §3.3.8's recorded determination — no CI invariant of its own; #20 already guarantees existence, completeness, at-promotion binding; a second invariant would re-verify #20 under another name. The amended gap text drops the clause with that warrant stated.
- **C3 — gap disposition (RATIFIED):** re-scope, not delete — structuring clause closed (C1), CI clause closed (C2), residue explicitly narrowed to the DDR-003 retention-policy dependency (reverse-lookup index/query-pattern optimization).

## Item D — Touch 3: derivation-totality carriers (RATIFIED, D1–D5)

- **D1 — `Evidence.observed_at` verify-intent gate (RATIFIED):** Reading 1 confirmed by the author — the field is the **capture/snapshot instant** (DDR-004's Δt "to" point; "from" recovered via the version pin). Mechanism: the preferred semantic clarification, glossed in §4, **no new field**; DDR-004 Pre-Acceptance Condition 2 discharges by this path. Drafting also disambiguates §4's canonical-definition parenthetical ("decayed by `observed_at`" → the Environment source's field), the one ambiguous anchor. Evidence weighed: parallel field semantics; §1's point-in-time framing; the redundancy test (Reading 2 duplicates pin-recoverable data and loses the to-point entirely); Evidence's surrogate-only posture (no `recorded_at` exists).
- **D2 — `PlaneDefinition` basis declaration (RATIFIED):** new dedicated T2 property `confidence_basis` — per-node-label declaration, named enum (DDR-004 basis numbering glossed once), declared domain freshness operand required iff aging, **no constants in schema**. Declared-totality registration rule: every declared node-label carries exactly one basis (basis 4 is a declaration, never an omission — no "citable" predicate needed); registration fails on any label without a basis or aging label without operand. New **check #26** (follow tier): PlaneDefinition basis-declaration totality. The §2.6 cost-plane exemplar registration gains the declaration field. Commissioned carriage per DDR-004 §4, not mirroring; stated in the Change Log, not contract prose.
- **D3 — core-plane + Cost annotations (RATIFIED):** DDR-004 §4 values carried verbatim, no drift — Catalog/Standards/Governance basis 2; `DeployedService`/`ConfigurationItem` basis 3 (operand `observed_at`); `DeploymentEnvironment` basis 2; `ObservedPattern` basis 1; `CapabilityCostEstimate` basis 1; `RateCard`/`CostFactor` basis 4. Range confirmed §2.1–2.5 (Catalog included, per the addendum-#3 correction). **Carrier form B:** plane-level declaration in the plane-signature idiom + per-label overrides on mixed planes (Environment, Cost); §2 preamble carries the resolution rule, the citable-universe boundary sentence (`SOURCED_FROM` targets KG nodes only — Artifact/Reasoning non-citable by construction; annotations over §2.1–2.6 cover the citable universe exactly), **and the citation-scoped clause** (operator-raised, ratified): *a declared basis governs derivation when a node of that class is cited; it imposes no requirement that such citations exist — evidence completeness is never a derivation concern.* Absence of environment/cost data yields absence of citations, never errors; walked end-to-end for the first-time-solution scenario before ratification. Honest floor carried verbatim (citation reachability for `DeploymentEnvironment` and `RateCard`/`CostFactor` unverified; fail-closed safe regardless).
- **D4 — `DeploymentEnvironment` (RATIFIED):** basis-2 per-label override; correct-by-design body note (structural identity, does not age, no freshness field; "add `observed_at`" stands rejected — kills the run-012 finding class permanently). **Uniform no-values rule** (applied retroactively to D3 drafting): annotations carry basis kind + operand only — not the contested `0.9`, not the invariant `1.0`; one preamble pointer names DDR-004 as the value/semantics authority (document-ID citation). The superseded "Environment base, decay term dropped" phrasing risk dissolves by construction — nothing to phrase means nothing to mis-phrase. Decoupled-tunable facts stay in landed DDR-004 §2/§4.
- **D5 — basis-4 rejection typing (RATIFIED):** new typed rejection, working name **`NON_CITABLE_SOURCE`** (final name fetch-verified against §3.2's vocabulary at drafting). Rejected: reusing `CONFIDENCE_UNDERIVABLE` (re-opens its reachability; conflates system-defect with correct steering) and `SCHEMA_VIOLATION` (the citation is well-formed). Layer split: DDR-002 rules and names the type in the basis contract; SDD-side carriage (the §3.2 vocabulary entry + §3.4.3 refresh) rides the Item-E landing. New **check #27** (follow tier): basis-admissibility — every `SOURCED_FROM` edge terminates at a class declaring basis 1–3; basis-4 labels carry no inbound `SOURCED_FROM`. Deliberate departure from the under-govern default: converts cee27acc's hole-closure from a one-time demonstration into a standing harness property.

## Item E — Riders + packaging (RATIFIED, E1 + E2′)

- **E1 — rider set:** one SDD-001 landing, change-log-carried — (1) §3.4.3 interim-description refresh (D2d; drops the Extension-class heuristic and the "`CONFIDENCE_UNDERIVABLE` as the known reachable case" enumeration; carries the D5 steering type); (2) §2 responsibilities-bullet fold-in (addendum #3); (3) §3.3.8 pin-match refresh → `evidence_id` correlation; (4) §3.2 vocabulary gains the new rejection type; (5) §3.5.3 + §3.5.4 routing notes and §9's proposed-amendments bullet refreshed (status-honesty — "proposed, not opened" becomes false on landing day). DDR-004 same landing: Conditions 1+2 discharged, status → ACCEPTED, change-log row + version bump; body treatment minimal (conditions apparatus records discharge; §3/§6 phrasings that would read false resolve to earned tense). Recorded-not-acted: RBT-48 inherits amended #25 + #26 + #27 + basis vocabulary; RBT-46 Phase 2 sees the amended canon.
- **E2′ — packaging + review breadth (operator-strengthened, RATIFIED):** single PR, one commit per document; merge is the acceptance act; ride-the-landing obligations atomic by construction. **One four-hat review draw** on the amended DDR-002 against a **hash-manifested landing-state substrate (staged rider diffs applied)** — never pre-rider text; coherence brief carries the named seam list (amended #25 ↔ refreshed §3.5.4 ↔ harness ordering; basis annotations ↔ DDR-004 §4 no-drift; #26/#27 ↔ §7 tier criterion + §7.2 set-generic derivation; `observed_at` gloss ↔ DDR-004 §3 ↔ refreshed §3.4.3; ProvenanceSummary structure ↔ #20 ↔ §3.3.8/§3.5.3; Named-Gaps re-scope ↔ §4 asymmetry; DDR-004 discharge tense ↔ conditions apparatus). Rider diffs and the discharge diff each get the **RBT-53-pattern three-hat drafting check + full coherence pass, adjudications ratified per item** — the mechanism that caught the §2.1–2.5 off-by-one both full draws missed. Second-draw escalation only on family-grade findings. Cold-read gate before promotion past PROPOSED.

## Item F — Body-integrity application scope (RATIFIED with operator qualifications)

- **F-i:** new text fully 1.3.0-conformant; the cold-read pass produces an explicit inventory of pre-existing out-of-home ticket-ID occurrences (known: §7 marker paragraphs and the Cross-References conformance bullet carry RBT-33/RBT-48), dispositioned per item at that point — in-batch relocation rider vs. named follow-up. Operator note: expected to hurt; addressed during the review cycle regardless.
- **F-ii — operative ticket-ID rule, BATCH-SCOPED, NAMED EXPIRY:** for this batch's drafting, ticket IDs permitted in Change Log, conditions apparatus, TODO gap-markers, **and Cross-References** (following ratified consumer practice — DDR-004 D1 relocated identifiers *to* Cross-References as the contract-purity fix); never in the normative body. **This rule expires with this landing** — explicitly not sustainable at full corpus; the successor rule is informed by the F-iii promote. It must not become precedent by inertia.
- **F-iii — skill divergence, promote-candidate, SHAPE PENDING:** the `author-decision-record` 1.3.0 ticket-ID-homes rule (three homes, "contract prose never") is inconsistent with its own no-storytelling bullet (which names Cross-References as a sanctioned container) and with its first consumer's ratified practice. Direction ratified as promote (clears no-default-to-neuter honestly — not single-instance); **final shape deliberately deferred to RBT-54 completion evidence** (the cold-read inventory and drafting experience decide between "add the fourth home" and "re-scope the rule to the normative body"). Filed to the HEB-54 ledger at close per Item H.

## Item G — Prep plan (RATIFIED, G1 + G2)

- **G1 — authority re-snapshot:** the review run's substrate re-snapshots from the installed bedrock 1.3.0 plugin cache — never `--from-run` run-015 (pre-1.3.0 snapshot). SKILL.md pin + three template hashes session-verified (see §0); the prep relay re-verifies against the cache at prep time; the run manifest records all four. Manifest prose currency note promoted to structured `verified_against` fields (via G2).
- **G2 — F4 mechanization, IN SCOPE, riding this prep leg:** forward currency check in `agent_loop/prep.py` for bedrock-origin substrate files (carried sha256 vs. installed plugin cache); fail-loud; sanctioned `--accept-stale-authority <id> --reason` override written to the manifest; `verified_against` structured fields; test-first, RBT-56-Item-1-style fixtures. Gates the review run, not the authoring — drafting proceeds immediately. Code implements in pause-point mode behind the repo-identity gate (remote = Haffey-Enterprises/SOFIA, expected file present, branch reported; mismatch is STOP-and-report); git default report-and-STOP; transactions are Tad's.

## Item H — Close obligations (agenda-ratified; execute only on operator go, at close)

Cold-read gate as pass/fail before the amended record leaves PROPOSED · three-layer capture on RBT-54 · SOF-154 leg-B pointer comment (amended DDR-002 version + review reference; resolves SOF-154's proving note and HEB-52's standing note) · HEB-54 ledger entries incl. the F-iii promote-candidate (shape informed by RBT-54 completion), triaged neuter/promote/demote with no default-to-neuter · acceptance items recorded: version chain (Item A) · 708bcb75 construction re-checked against amended text (Item B walkthrough as template) · ProvenanceSummary gap disposition (C3) · sequencing-rule status · DDR-004 discharge · F-ii expiry.

## Execution sequence (consolidated)

1. This record vendored with the batch (Code relay #1).
2. Authoring pass (this surface): amended DDR-002 staged replacement · SDD-001 rider diffs · DDR-004 discharge diff — all drawn from this record.
3. Three-hat drafting check + coherence pass on the rider diffs (adjudications per item).
4. Code relay #1 (pause-point mode): vendor drafts to feature branch · F4 mechanization (test-first) · 1.3.0 re-snapshot + manifest.
5. Review run: one four-hat draw, landing-state substrate, seam-list brief. Cold audit + per-item disposition on this surface. Escalation per E2′.
6. Cold-read gate (pass/fail) + F-i inventory disposition.
7. Code relay #2: single landing PR, one commit per document. Merge (Tad) = acceptance act; DDR-004 discharge and all ride-the-landing obligations discharge atomically.
8. Item H close obligations on operator go.

---

## Addendum — pre-landing drafting-check adjudications (A-1–A-14, each ratified individually by Tad, 2026-07-13)

Per Item E2′, the three-hat drafting check + coherence pass ran over the staged batch (four independent fresh-eyes reviewers: LAA, SA, EA, coherence — the E2′ drafting-check instrument, not the agent-loop; the four-hat review draw remains ahead). Fourteen adjudications, all ratified and folded into the staged artifacts:

- **A-1 (fix):** SDD §3.5.3's stale two-array parenthetical → the keyed `frozen_*` entry-array pointer. (4-hat unanimous.)
- **A-2 (fix):** the "citable node-class" quantifier removed from the DDR-002 §2 preamble and Decision.11 — declared-totality carries no citability predicate (per D2).
- **A-3 (ruling):** `PlaneDefinition` itself declared **`flat_base`** (basis 2 — versioned registry ground truth; staleness supersession). A batch ruling on a disposition DDR-004 §4's table does not yet carry; alignment noted for that record's next touch. `non_citable` rejected — no purpose-built substitute surface exists (basis-4's warrant).
- **A-4 (E1 rider-set extension):** rider 6 — SDD §3.6.2 `register-plane` gains `confidence_basis` declared-totality validation, rejected typed (`SCHEMA_VIOLATION`), #26 by construction; rider 7 — SDD §7.1 enforcement mapping gains #26 (write-time at registration + harness mirror) and #27 (harness-verified; §3.4.3's capture-time rejection as its write-time half). The §4.6 widening is recorded as part of the ratified rider set.
- **A-5 (edit-script extension):** DDR-004 Edits 13 (omission semantics aligned — a label without a declared basis fails registration; non-citability declared, never inferred) and 14 ("fail-closed interim" → "fail-closed backstop").
- **A-6 (fix, mandatory):** honest floors restored verbatim — Touch-3 reachability floor + Touch-2's zero-materializations half, both in their Change Log rows.
- **A-7 (fix):** discharge-script enforcement tense earned — "schema-carried contract (mechanization per §7's follow-tier sequencing)"; "#26/#27 carry the conformance contract"; Edit-4 citation disambiguated to DDR-002 §7 #26.
- **A-8 (fix, five loci):** version-stamp/credit narrative stripped from contract prose (DDR-002 Named Gaps entry, §6, Cross-References DDR-004 bullet; SDD §3.3.8 determination, §3.5.3 structuring line) — the Change Log owns those events.
- **A-9 (ratified-text amendment):** #25's pre-materialization sentence marked normative ("a checked direction of this invariant"); the unratified explanatory tail struck. Closes the out-of-band-edge-on-approved-candidate residual.
- **A-10 (fix):** #26 tightened to the ratified iff (operand present iff `aging`) with the declared-label source named (`property_schema`).
- **A-11 (fix, three loci):** SDD dangling references — §4.6 "documented value" → ruled-value split; §9 amendments bullet de-narrated; "#25 timing note" → "conformance note".
- **A-12 (fix):** `register-plane` operation name removed from DDR-002 body ("at plane registration"); it remains SDD vocabulary.
- **A-13 (no change + gloss):** SDD §3.4.3 keeps the executable `exp(−Δt/τ)` form (a service design states what it implements; DDR-004 authority pointer present); τ glossed "per DDR-004 §2".
- **A-14 (bundle):** Decision.11 glosses `CONFIDENCE_UNDERIVABLE` at first use; #27's "cost-plane hole" allusion dropped; Touch-1 row's "Items 3+4" stands (Item 5 was the no-action bucket); DDR-002 References table stays upstream-only (convention recorded for the cold read); "gateway-clocked" stays (cited).

POSITIVEs of record: the no-values rule held across all four independent checks; the edit script verified mechanically against base blob `cc33cda3` (all spans exact and unique); the landing-set version-reference sweep came back fully consistent.

## Addendum — review-and-verification arc (run-016 → run-017 → cold-read gate → run-018; rulings ratified per item, 2026-07-13)

This addendum records the post-authoring review arc at pointer level; the run folders are the carriers (capture-where-decided).

**Instrument arc.** run-016 (gen-5) produced a false-CONVERGED on an all-hats-null draw — root-caused via six probe rounds to **narrated-completion deference** (conjunctive form: a reviewer emits sanctioned-empty iff any completed-review/ratified narrative is present in context); run-016 preserved as pathology evidence (`run-016-ddr-002/invalid.md`). Remedies: R-C all-hats-null fail-loud guard; gen-7 (semantic countermand) **failed** Arm L; gen-8 (structural two-lever: empty-array-is-protocol-violation floor + recency-positioned review directive) **passed** Arm M and ran both live draws. Operative levers structural, not semantic. Code-relay decisions R-1/R-2 (byte-regression test reframed hermetic), R-A–R-E, R-D1–R-D6 ratified in-session; carriers: the run-016 folder + branch commits.

**run-017 (first draw, gen-8) — 24 findings, 24/24 ruled** (audit + disposition in `run-017-ddr-002/`). Dispositions **P-1–P-8** ratified per item: #10 Condition-half scoped (P-2, latent v1.2.0 defect); §2.4 retraction re-decision named + routed (P-3); #26 key-set equality (P-4); exemplar gloss (P-5); Touch-2 ruled-exception clause (P-6); 7 OVERs (gen-8 cost profile: ruled-decision re-attack). Operator elected a verification draw over the revised text (P-8; run-012 pattern) — the E2′ family-grade trigger did not fire.

**Cold-read gate — PASS with folds.** Adjudications **CR-1–CR-9** ratified per item (disposition record in `run-017-ddr-002/`): §-cite corrections (CR-1/CR-2), routing-pointer fix (CR-3), the re-decided-`GateDecision` governing-verdict gap named (CR-4), #26 only-if warrant (CR-5), §7 ticket-ID relocation — the F-i disposition (CR-6), first-use acronym expansions with corpus sweep → **RBT-60** (CR-7), SDD §4.4 attribution fix (CR-8), DDR-004 Edit 15 (CR-9).

**run-018 (verification draw, gen-8, doc pin `9bb0f9b3`) — 26 findings, 26/26 ruled** (audit + disposition in `run-018-ddr-002/`). Dispositions **P18-1–P18-7** ratified per item. **All run-017 P-closures and cold-read CR-closures held**; CR-6 byte-verified landed. Folds: §2.6 exemplar gloss states the label-set identity (P18-2, resolves a three-hat family on the P-5 gloss); §2.4 clause names the deferred retraction-side **detection** analogue of #15 (P18-3, the CR-4 gap-naming pattern); `WOULD_HAVE_USED` `rebind:pinned` annotation (P18-6, auditor-adjacent). New verdict class recorded: 3 **FALSE-POS** (calibration ledger). No third draw (P18-7).

**Final landing set:** DDR-002 v1.3.0 sha256 `8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16` · SDD-001 v1.2.0 sha256 `a6a9ddaad6a50f76d35768959d18efb7cb15df50eb1185ce294514694c579950` · DDR-004 edit script (15 edits) sha256 `b976cf99d739bbbe78fea7fe08e6a6eeb6bbb7f99a4893e2018c965c4a8509cc`. Merge is the acceptance act (Tad's); DDR-004 discharge rides atomically.

**Routed residues (to RBT-54 close / HEB-54 / next touches):** DDR-004 next touch — §4 table gains `PlaneDefinition` (A-3) + honest-floor sentence names Governance citation-reachability (P18-5); F-ii Cross-References ticket-ID home, batch-scoped with named expiry → HEB-54 seam; narrated-completion-deference finding + code-review-skill rule → HEB backlog ticket at close; F-iii conditional-clause promotion, shape informed by RBT-54 completion → HEB-54.
