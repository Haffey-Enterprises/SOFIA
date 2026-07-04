# Deliberation Record — SDD-001 knowledge-service Pre-Authoring Session

| Field | Value |
|---|---|
| **Session** | Pre-authoring deliberation + authoring, 2026-07-03 (claude.ai surface) |
| **Doctype gate** | `author-decision-record` skill; SDD route; routing test run and confirmed (one service's concrete design — no referent if the service is deleted) |
| **Corpus** | ADR-001 v1.1.0 · ADR-002 v1.1.0 · DDR-001 v1.3.0 · DDR-002 v1.2.0 — all fresh-fetched and ACCEPTED-verified at these versions |
| **Charter** | Linear RBT-15 (reworked 2026-07-03; gate cleared at PR #8 / `c935c68`); triage-001 record §T-15/T-17/T-27 + Item-4 charter notes + Addendum; Notion SOFIA page (SDD-001 = Now) |
| **Rulings** | Eleven dispositions ratified per item by Tad (Gate resolutions · Item 1 · Items 2a–2h · Item 3); this record is the durable carrier — the SDD's Cross-References deliberation citation points here |
| **Deliverable** | `docs/sdd/SDD-001-knowledge-service.md` PROPOSED v0.1.0, authored from these dispositions; three-hat + antagonistic review and commit are Tad's |
| **Status** | COMPLETE — draft authored; reviews in flight |

**Reviewer's key:** every §7/§N citation below is DDR-002 unless prefixed; "the four ports" = KG retrieval · RG capture · promotion boundary · ingestion (Item 1); "Species 1/2" = the two-species write-authority convention (Item 1, as corrected).

---

## Gate — substrate assembly + two session rulings (RATIFIED)

**Substrate (a):** four upstream records fetched at HEAD and verified `Status: ACCEPTED` at the exact charter versions. **Substrate (b):** prior SDD-001 (SOFIA-legacy, read-only) fetched. **Substrate (c):** the design space deliberated to clarity across Items 1–3 below before any drafting.

**Ruling — fresh-fetch source (session incident, dissolved).** The local Filesystem MCP server hung mid-orientation (parallel-session collision); the GitHub remote (`Haffey-Enterprises/SOFIA`, main) was substituted as the fresh-fetch source. After server restart, local ≡ remote verified: all four corpus files byte-identical to the remote blobs (24,544 / 27,259 / 24,346 / 99,228); triage-record Addendum present locally verbatim. No divergence existed; the close reads stand on identical bytes.

**Ruling — legacy SDD-001 (Tad, this session): context-only, greenfield.** The prior SDD-001 informs operational texture only; it is **not a prior version** — no "What Changes from prior," no migration section, `Supersedes: None — new service`, zero references to it in the SDD body. Comparison hazard noted and neutralized: the legacy document cites legacy-corpus ADR/DDR numbers (e.g., its CMEK-required posture is the exact reversal of current ADR-002 §2.7; its 3-node cluster is the now-deferred topology) — legacy section cites treated as radioactive; nothing cited.

---

## Item 1 — Gateway API shape (RATIFIED, as corrected)

**Ruling: operation-shaped (intent-based) API — no generic node/relationship CRUD.** DDR-002's writes are transactional shapes with invariants living *between* nodes (atomic capture-unit #14; atomic supersession §6/#8; materialization closure #20; retraction gating #21; `DECIDED_ON` monotonicity #15; carry-forward #22). Generic CRUD structurally cannot enforce these — the gateway would police after the fact what the operation shape can make unexpressible. Each write endpoint = one schema-defined transactional shape with its invariants native. The 1b harness contracts are behavioral contracts against a `GraphGateway` seam; behaviors need operations to attach to.

**Structure:** four domain operation groups — KG retrieval (read-discipline structural, no bypassing read) · RG capture · promotion/governance boundary · ingestion — plus health. **Promotion boundary is its own port** (writer classes differ from ASA/AOE; port-per-writer-class keeps §2.6 enforcement at the seam). DDR-001's three roles are pattern, not exhaustive port count; adding the promotion seam realizes, not amends.

**Two-species write-authority convention (corrected in-session on Tad's authority-structure challenge; the correction is the ruling):**
- **Species 1 — component-scoped authors:** request carries the authoring component's identity, validated against the upstream-fixed assignments (ASA → reasoning content + `Solution` creation; AOE → session lifecycle; feedback-loop job → `CandidatePromotion`).
- **Species 2 — decision-authorized materializations:** authority = the governing approving `PromotionDecision`, verified in-transaction; request carries `decision_id`, **no author field exists** — authorship-by-gateway unexpressible; caller is transport.
- Corollaries: the gateway authors nothing (supersession re-point and closure computation are execution mechanics of authority held elsewhere); unfixed assignments (PromotionDecision transport, Attestation/Actor/Role, ingestion sources, Solution lifecycle transitions) are **routed by name, never invented** — assigning them here would be the §2.6 violation dressed as thoroughness.

---

## Item 2a — Write-endpoint enumeration (RATIFIED, incl. four sub-calls)

Thirteen operations: RG capture — `open-session`/`advance-session` (AOE), `capture-conclusion` (ASA; #23 + `reasoner_ref` at write), `capture-evidence`, `capture-rejected-alternative`, `create-artifact`, `advance-artifact-lifecycle` (authority routed; unassigned transitions rejected). Promotion boundary — `propose-candidate`, `record-promotion-decision` (#15 monotonicity, #16, `HAS_CONDITION`), `materialize-promotion` (Species 2), `materialize-retraction` (Species 2). Ingestion — `ingest`, `register-plane` (#18), `mirror-gate-decision` (monotonicity **not** extended to the GateDecision edge — DDR-002 scopes it to `CandidatePromotion`; widening is upstream's question).

- **(i) Capture-unit tightening:** `capture-evidence` requires `SUPPORTED_BY` in the #14 transaction. #1 mandates `SOURCED_FROM` but is silent on a `SUPPORTED_BY` parent — unlinked Evidence is schema-legal; this is the "SDDs may tighten" species (§4), grounded in ADR-001 §2.2 (evidence supporting nothing has no capture semantics).
- **(ii) `RETRACTS` timing — at materialization, not proposal.** §5's own terminal-`promoted` gloss for retractions ("the `RETRACTS` edge written and the target read-excluded") nearly decides it; #21 then holds by construction. **Residue:** #25's biconditional is unsatisfied during a retraction proposal's pre-decision window — harness implementation nuance (scope to executed proposals or status-guard), flagged toward the catch-up work, not resolved here.
- **(iii) Supersession is a transactional mode, not an endpoint.** Nobody "calls supersede": versioned ground truth supersedes via `ingest` at an existing business key; promoted facts via `materialize-promotion` at an existing business key. Keeps supersession authority with the superseding write's author; a standalone endpoint would create a write authored by nobody.
- **(iv) Enumerate-now vs route:** no operations for `Attestation`/`Actor`/`Role` — no upstream-assigned author exists; additive amendments land with the governance-state-manager SDD. Inventing a registration op = inventing its author.

---

## Item 2b — Invariant-enforcement mapping (RATIFIED)

Four enforcement modes stating the gateway's **runtime relationship** to each §7 obligation (harness mechanization bucketing deliberately not restated — the SDD says what the gateway does; the harness independently verifies):

- **By construction:** #1, #14 · #4, #8, #22 · #15 · #20 · #21 · **#2** (operation contracts make vector properties unexpressible through the gateway; harness assertion = defense-in-depth).
- **Write-time rejected:** #6, #18 · #7 · #13 · #16 · #17 · #23 · #11's stamping half.
- **Read-discipline:** #9 · #19 · retracted-node exclusion (§5).
- **Harness/routed:** #3, #5 (attach to future cost ops) · #10 (constraint-validator) · #12's verification half · #24 · #25.

Charter bindings carried into the SDD verbatim in substance: no safety-critical downgrade / none slip the gateway gate; 1b required-flip **set-generic** per RBT-15 ("the harness's 1b set at build time"), binding the BUILD leg.

- **(i) #24 harness-only, no gateway recheck:** matches the ruled tier (follow), and the ceiling is not computable at conclusion-write time under non-blocking capture ordering (evidence attaches after the conclusion). Honest floor: a transient unvalidated-confidence window exists — acceptable because #24 guards reasoning-quality, not ground-truth entry (exactly why it was tiered follow).
- **(ii) #12 split — presence enforced at write; hash-vs-snapshot verification routed to snapshot-service.** knowledge-service holds no Firestore client; ADR-002 §2.5 makes it sole owner of the *Neo4j* driver, not a cross-store octopus. Extending it would quietly widen §2.4's authority lines.

---

## Item 2c — Graph-native retrieval affordance (RATIFIED)

- **(i) Typed, intent-shaped operations; no Cypher passthrough** — passthrough would bypass the read-discipline trio, leak the store through the substitution seam, and violate DDR-001 uniform access.
- **(ii) Operation set derived from named upstream consumers, declared provisional** — pattern selection, technology resolution, track-record composition, obligation-context (graph half only; closure is validator logic per §3), precedent retrieval, as-of reads, citation lookup, provenance retrieval, session trace. **Empirical floor stated: zero synthesis runs exist** — derived from named consumers, not observed traffic; additive evolution + DDR-002's provisional-index revisit ride along.
- **(iii) Uniform attribution envelope** (DDR-001's source-plane + confidence + version-pin, elevated to one contract, + `applicability_state`); design payoff: retrieval output is `capture-evidence` input — one contract, no second lookup.
- **(iv) The gateway retrieves; it never recommends.** The legacy service's `recommended` field is, under the current corpus, a violation: choosing is reasoning, reasoning is ASA's and must be captured (ADR-001 §2.2). Mechanically computed structural facts are data (deterministic, documented — ADR-001 §2.3); picking a winner would be authorship of a conclusion. Stated in §1 Purpose's not-owned list.
- **(v) `SIMILAR_TO` declined** — no consumer-demonstrated pattern the named substrates can't serve (empirical-warrant discipline); deterministic similarity is computable at read (materializing = premature denormalization needing its own sync-check). Two escalation paths, deliberately distinct: latency-driven derived edge → **DDR-002 additive amendment**; anything embedding-based → **ADR-002 §4.3's new-ADR path**, never a local addition.

---

## Item 2d — #19 conditional read-discipline mechanics (RATIFIED)

- **(i) Evaluation hosted in-gateway behind a predicate-evaluation port; semantics single-sourced from the constraint-validator SDD's shared component.** Rejected: synchronous call-out (second service on the hot path of a safety-critical control; enforcement loses its single home) and gateway-local reimplementation (forks the predicate grammar §2.5 deliberately pattern-aligned across `Condition` and `rule_definition`). One grammar, one implementation, two hosts; named cross-SDD coordination point.
- **(ii) Consuming-context contract** on ground-truth retrieval; required fields determined **introspectably** from `Condition.dependency_manifest` — mechanical, never judgment.
- **(iii) Fail-closed, with disclosure.** Unevaluable ⇒ not admitted, always (T-21's pinned never-auto-admit interim; #19 is the blocking safety control). Envelope discloses **existence, not content**: `{node_id, reason}`, no payload — exclusion auditable; scoped-knowledge existence remains a legitimate `GapConclusion` input without the content admission #19 prevents.
- **(iv) Multi-condition interim adopted verbatim from the Named Gap:** excluded + surfaced as scope-conflict; no composition rule invented.
- **(v) DDR-003 vocabulary dependency:** mechanism designed against the predicate *shape* DDR-002 fixed; concrete grammar = TODO-with-pointer. Not blocking **by construction**: conditional promotions arise only from the feedback loop, whose governance DDR-003 itself gates — the ratified-grammar-less window is empty; (iii) backstops regardless. Floor: zero promotions have ever run.

---

## Item 2e — #22 carry-forward + cross-origin case (RATIFIED)

- **(i) Same-origin (promotion path): explicit scope disposition required** — `carry_conditional` (linked `Condition` verified) or `rescope_unconditional` (approving decision verified condition-free); absence rejected. The design insight: #22's target failure is the *silent* default, so the mechanism makes silence **unexpressible rather than detectable** — the operation contract has no default to fall into. Residue named: whether the EA *deliberated* the re-scope is not schema-verifiable (no scope field on `PromotionDecision`; inventing one = DDR-002 amendment, not this SDD's); presence + structural consistency enforced here, deliberation guarantee routed to EA-review workflow / DDR-003.
- **(ii) Cross-origin (ingestion arrives at a `conditional` promoted predecessor): block-and-surface.** Structural ground: an ingested successor cannot satisfy #22 (not promoted; no `applicability_state`; no re-scoping decision) — admitting would be the SDD carving a pass-through exception to a safety-critical check, forbidden by the charter binding. The tempting "ingested reality outranks promoted judgment" alternative fails on the T-02 axis: an ingestion event silently discharging an EA-set scope with no human in the loop. Ruled: gateway blocks, surfaces `SCOPE_CONFLICT` (same disposition species as multi-condition — surface-to-EA, never silent auto-resolution); remediation via the promotion boundary (retract or re-scope, then retry clean); richer cross-origin disposition = KG-entry-governance ADR / DDR-003 territory, cited as escalation path. **Floor: zero promotions, zero ingestion runs — collision frequency unknown; block forfeits nothing and is fully disclosed.**
- **(iii) Predecessor-keyed per #22, evaluated inside both atomic supersession transactions** — one cheap read at the sole chokepoint (#15/#13 species). #22 lands in the by-construction column for mediated writes; harness contract = independent verification; scope-conflict blocks emit governance-significant events.

---

## Item 2f — Two-surface applicability composition (RATIFIED)

- **(i) Deliberately asymmetric enforcement.** Promoted-conditional = **admission control** (#19, safety-critical, fail-closed). Catalog eligibility = **annotation** (verdict + failing fields disclosed; never excludes). Grounds: #19 guards an EA-set scope (a §7 safety check); eligibility fields are Catalog metadata whose violation is a compliance gap in the reasoning path — not a §7 check; the corpus tiers them differently. Clincher: silent eligibility filtering would erase the gap-vs-ineligible distinction the capture invariant depends on — "no resolving technology" (`GapConclusion`, DDR-001's gap definition) vs "exists but ineligible here" (`RejectedAlternative`) must remain distinguishable to ASA.
- **(ii) One consuming-context contract serves both surfaces** (the 2d-ii payload; no second payload, no drift).
- **(iii) Envelope gains a per-result applicability block; annotate-only.** No gateway-side eligibility filter parameter now — filtering is the caller's move over disclosed verdicts (keeps the retrieves-never-recommends line); a convenience filter is a legitimate additive later on demonstrated need. Floor: zero synthesis runs.
- **(iv) The composition judgment (what ASA does on conflict/failure) is routed** to the solutioning SDD — selection reasoning, not gateway behavior. Net decomposition: gateway answers "here is everything, every applicability fact evaluated"; ASA answers "therefore I choose."

---

## Item 2g — ProvenanceSummary reverse-lookup affordance + determination (RATIFIED)

- **(i) The affordance is an operation, not an index.** The traversal path (promoted node ← `PROMOTES_TO_KNOWLEDGE` — `CandidatePromotion` ← `MATERIALIZES_PROVENANCE_OF` — `ProvenanceSummary`; governing `PromotionDecision` one hop) is durable append-only structure; entry by uniqueness-indexed PK; Neo4j traverses bidirectionally. No new index.
- **(ii) Read contract: frozen-always, live-enriched, retention-agnostic.** Frozen layer returned always (at-promotion materialization guarantees existence for the node's whole life); live `Evidence` chain where it survives; entries marked live vs frozen-only. Property worth the ink: the contract is **independent of whatever retention policy DDR-003 sets** — the flagged DDR-003 coupling dissolves by construction, not by TODO.
- **(iii) Snapshot internal structuring (gateway-authored payload, SDD-owned shape): per-Evidence entries keyed by `evidence_id`** (fact_summary + version pin + source ref) — §4's traversal-not-parse requirement met; keying enables mechanical live/frozen correlation.
- **(iv) Determination (the Named Gap's open question, answered): NO CI invariant.** An affordance invariant would check frozen-layer reachability — exactly what **#20 already guarantees** (existence + completeness + at-promotion binding), atop the atomic materialization transaction. A second invariant = re-verifying #20 under another name — the same redundancy-as-divergence-surface logic that declined the `selected` flag. Read-operation correctness = service test discipline (§8), not a schema invariant. Determination **recorded in the SDD** (§3.3.8); pruning the Named Gap text is a future DDR-002 amendment, not performed by the SDD.

---

## Item 2h — Reverse cross-graph lookup (RATIFIED)

- **(i) `citation-lookup` operation, version-aware, two modes:** per-version (precise audit) and business-key-wide (change-impact across the version chain — both readings have chartered consumers: feedback-loop detect pass, supersession change-impact, explainability audit; all out-of-band/advisory).
- **(ii) No index now.** Entry by uniqueness-indexed PK; `SOURCED_FROM` natively bidirectional (direction is readability, not access — §3's own grammar). Real concern is **fan-out**, answered in contract: pagination mandatory both modes; live set bounded by the DDR-003 retention window. Filtered reverse patterns native traversal can't serve → DDR-002's provisional-index revisit (named escalation, no present need). Floor: zero observed traffic.
- **(iii) Completeness horizon stated honestly:** complete within the RG retention window; beyond it, frozen `ProvenanceSummary` entries preserve citations as **per-promotion keyed properties, structurally unreachable from the cited node's side** — by design (the frozen layer answers 2g's direction, not "what cited this fact, ever?"). Reverse reach into frozen summaries: retention-coupled, zero consumers, would require a DDR-002 schema amendment (frozen properties aren't traversable) — doubly routed.

---

## Item 3 — Write-authority assignments + gateway's own state (RATIFIED, with rider)

- **(i) Consolidated §2.6 realization table** (Species 1 assignments · Species 2 decision-authority · routed-not-assigned list) — consolidation, nothing new decided; one surface for the check-#7 review.
- **(ii) The gateway authors nothing; its operational events are not graph citizens.** ADR-002 §5.2 bounds local state to operational/cache/staging; DDR-001's Governance plane excludes per-action disposition events by name. A gateway journaling its own enforcement into the graph would author authoritative-adjacent state with no assigned authority — §2.6's subtlest violation. **Single store client:** Neo4j only; no PostgreSQL (nothing chartered needs workflow/staging state; change = additive amendment with the state-class named); Firestore already disclaimed. **Ratification rider (Tad):** the gateway's operational state is addressed entirely through observability tooling (monitoring/logging) — carried verbatim into SDD §4.7/§8: those surfaces are the *only* home of the operational record.
- **(iii) Caching: no ground-truth result caching** (#19/#21/#22 are read-time controls; a cached admission could serve retracted/re-scoped knowledge). **Metadata caching permitted** (PlaneDefinition, predicate parse artifacts): sole-writer makes write-through invalidation complete by construction — no external-writer invalidation race exists.
- **(iv) Ingestion authorship boundary:** enforced-at-port here (schema-on-write, #13, #17 regardless of caller); assigned-at-source in the architecture-ingestion SDD (adapter decomposition per DDR-001 routing).

---

## Authoring notes

- **Template deviations:** "What Changes from prior" + "Migration" sections deleted — per Tad's greenfield ruling (Gate), coinciding with the template's own greenfield instruction.
- **TODO-with-pointer set carried in the SDD** (none blocking): `lifecycle_state` value-set enforcement → AOE SDD · condition-predicate grammar → DDR-003 (empty-window-by-construction + fail-closed backstop) · Solution lifecycle-transition authority instantiation → approval/governance-state-manager SDDs (unassigned = unexecutable, not defaulted) · #25 timing coordination note → harness catch-up work.
- **Out-of-scope discipline:** DDR-003-routed policy cited, never answered; KG-entry-governance ADR questions routed, never resolved; AOE `lifecycle_state` value-set untouched; no `conformance/` or service code; Linear/Notion writes: none (this record was ratified in-session).
- **Conventions honored:** no-story-telling (record §D.1) — the SDD body is contract-only; this record carries the deliberation.
