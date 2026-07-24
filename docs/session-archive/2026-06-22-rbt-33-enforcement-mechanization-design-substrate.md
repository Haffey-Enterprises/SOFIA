# RBT-33 — Enforcement-Mechanization Design Substrate

> **Artifact class.** Pre-authoring deliberation / design substrate (DIRECTIVE-034 working
> artifact) — *not* a governed DMS doctype. Same class as the v0.3 / v0.6 substrates Code
> authored DDR-001 / DDR-002 from. No `doctype:` frontmatter; carries no normative authority
> of its own. The invariant *specifications* remain owned by their accepted homes
> (ADR-002 §6, DDR-001 § Conformance-checks, DDR-002 §7); this substrate designs only the
> *mechanization* and is the input from which Code builds the validators/CI.

| Field | Value |
|---|---|
| **Work item** | RBT-33 — S8, Enforcement-mechanization for ADR-002 §6 + DDR-001 + DDR-002 conformance checks |
| **Leg** | claude.ai design/deliberation leg (DIRECTIVE-026); Code builds validators/CI in a later BUILD leg |
| **Date** | 2026-06-22 |
| **Baseline** | `develop` @ `ca48b7d` (RBT-13 / DDR-002 landing) |
| **Source authorities (fresh-fetched)** | ADR-002 v1.0.0 §6 / §2.5 / §2.6 / §2.4 · DDR-001 v1.1.0 § Conformance-checks · DDR-002 v1.0.0 §7 + § Risks · Notion ledger R27 (orig + 2026-06-20 amendment + 2026-06-21 refinement) |
| **Status** | Ratified spine (Forks 1–5 below); per-invariant mechanization authored herein for review |
| **Revision** | **v0.2** — Pass-1 three-hat fold-in (B-1, B-2, M-1, M-2, M-3, C-1, C-2 of the 2026-06-22 substrate review). v0.1 was the pre-review draft. |

---

## 0. Ratified decision spine (Forks 1–5)

These were deliberated and ratified one at a time this session; they are the fixed frame the
mechanization realizes. Recorded here so the substrate is self-contained for the Code handoff.

1. **Artifact intent.** This leg produces a design substrate (this document); the Code-facing
   vehicle is a **BUILD execution** (DIRECTIVE-030), *not* an ENG-STD-003 apply-prompt — RBT-33
   authors net-new TDD validator tooling, not prepared-edit application.
2. **Formal home.** No new governed doctype. Invariant specs stay in their accepted homes
   (ADR-002 §6 / DDR-001 / DDR-002 §7); the gateway-behavioral subset's *design* rides into
   RBT-15's knowledge-service SDD where the gateway is designed; RBT-33's mechanization design is
   captured as this substrate + a ledger ruling (R28 candidate, drafted at session close).
3. **Decomposition.** Two increments at the DDR-002-bound tier boundary —
   **Increment 1 = safety-critical tier (10)**, gated ahead of RBT-15, internally split
   **1a (graph-state checks, enforcing now) / 1b (gateway-behavioral contract tests, `xfail`-pending
   against the seam until RBT-15)**; **Increment 2 = follow tier (9)**, uniform timeline, no RBT-15 gate.
4. **Mechanism.** Four mechanism classes (static schema-lint · graph-state Cypher assertion ·
   gateway-behavioral contract test · native-constraint backstop); per-invariant assignment §3;
   graph-state checks run against **seeded ephemeral-Neo4j fixtures**; delivered as a single
   **conformance-assertion + contract-test library** RBT-15 builds against.
5. **`applicability_state` carry-forward.** **Named gap, not a 20th invariant** — the over-admission
   exposure is latent-contingent on un-built promotion machinery (R25 empirical-warrant lever);
   reversal path recorded (§6). No DDR-002 amendment — closes the routing on the RBT-33 side.

---

## 1. Enforcement surface (de-duplicated union)

RBT-33's charter is the union across three sources. De-duplicated so we mechanize one map, not
three overlapping ones:

- **ADR-002 §6** — six *design-review* checks against SDDs/DDRs (system-of-record,
  graph-access-authority, store-authority, traversal-locality, write-authority, data-protection).
  §6 itself names store-authority (#3) and write-authority (#5) as the mechanizable pair; the rest
  are judgment-based review checks.
- **DDR-001 § Conformance-checks** — six checks; **1–3 are the ADR-002 §6 surfaces**
  (gateway-only access / no-local-authoritative-state / RG write-authority), only **4–6 are
  DDR-001-native** (no-self-modify + proposal-exclusion; Evidence→pinned-KG-version; provenance +
  promoted-vs-ingested).
- **DDR-002 §7** — the **19 CI-only integrity invariants** (the load-bearing set; the others are
  DB-enforced natively and out of RBT-33 scope). DDR-002 **binds** the safety-critical
  classification and the precede-gateway rule; **RBT-33 finalizes the mechanization** subject to
  that binding.

**Scope note — two enforcement venues.** The ADR-002 §6 / DDR-001 1–3 checks are *design-review*
checks (do SDDs/DDRs conform). The DDR-002 §7 invariants + DDR-001 4–6 are *graph-state / gateway*
checks (does the schema/graph/gateway conform). RBT-33 mechanizes the **graph/gateway venue** as
its core (the 19 + DDR-001 4–6); the design-review venue (ADR-002 §6 store/write-authority against
design docs) is a thinner, lint-against-design-text concern addressed in §3.4. The two are not the
same artifact and should not be conflated.

---

## 2. The 19 invariants and the two tiers (fresh from DDR-002 §7)

**Safety-critical tier (10) — ahead of RBT-15:** #1, #7, #9, #11, #13, #14, #15, #16, #17, #19.
RG-provenance (#1 / #14) is the **highest-priority member within** the tier — *not* a smaller
increment. The precede-RBT-15 gate binds all ten.

**Follow tier (9) — uniform RBT-33 timeline, no RBT-15 gate:** #2, #3, #4, #5, #6, #8, #10, #12, #18.

The safety-critical tier splits cleanly **5 graph-state / 5 gateway-behavioral** — and that split
*is* the mechanical meaning of "enforceable before RBT-15":

| | Safety-critical (Increment 1) |
|---|---|
| **1a — graph-state, enforcing on landing** | #1, #11, #15, #16, #17 |
| **1b — gateway-behavioral, `xfail`-pending against the seam until RBT-15** | #7, #9, #13, #14, #19 |

---

## 3. Per-invariant mechanism assignment

Four classes. None of the 19 is a *pure* native constraint (by §7's definition), but the
existence/uniqueness constraints **backstop** several — DB guarantees presence; CI does the
semantic half.

> **Cypher predicate sketches below are illustrative — they show shape and prove buildability.**
> Build-time authoring MUST fresh-fetch the exact label/property constants from DDR-002 §2–§7 (per
> the no-guessing-on-domain-signatures principle); the labels here are representative, not pinned.

### 3.1 Increment 1 — safety-critical (10)

| # | Invariant | Class | Check shape |
|---|---|---|---|
| **1** | RG-provenance edges | graph-state (1a) | `MATCH (e:Reasoning:Evidence) WHERE NOT (e)-[:SOURCED_FROM]->(:KGNode) RETURN e` (mandatory source) **+** `MATCH (r:Reasoning:RejectedAlternative) WHERE size([()-[x:REJECTED]->(r)|x]) <> 1 RETURN r` (exactly-one parent) |
| **11** | provenance distinguishability | graph-state (1a), constraint-backed | presence of `origin_mechanism` is DB-enforced; CI checks valid-value ∈ {ingested, authored, promoted, derived} and that `promoted` is distinguishable from `ingested` |
| **15** | promoted → governing approving decision | graph-state (1a) | trace `(:KGNode {origin_mechanism:'promoted'})←[:PROMOTES_TO_KNOWLEDGE]-(:CandidatePromotion)` to the **governing** `DECIDED_ON` edge (max `decided_at`) → `PromotionDecision{outcome ∈ {approved, approved_conditional}}`; fail nodes whose governing verdict is not approving |
| **16** | exactly-one-subtype-per-Decision | graph-state (1a) | `MATCH (d:Decision) WHERE size([l IN labels(d) WHERE l IN ['GateDecision','PromotionDecision']]) <> 1 RETURN d` |
| **17** | ingested/distilled ⇒ source_record_ref | graph-state (1a) | `WHERE n.origin_mechanism='ingested' AND n.source_record_ref IS NULL` **+** `WHERE n.derivation_class='distilled' AND n.source_record_ref IS NULL` |
| **7** | ADR-002 §2.6 write-authority | gateway-behavioral (1b) | contract test: gateway *rejects* a `ReasoningProgress` write not attributed to ASA; AOE confined to `ReasoningSession` lifecycle |
| **9** | proposal-visibility read-discipline | gateway-behavioral (1b) | contract test: ground-truth synthesis traversal *excludes* `CandidatePromotion` until EA-approved (gateway-scoped read; structural label-skip is an aid, not the guarantee) |
| **13** | no-PHI classification | gateway-behavioral (1b) | contract test: gateway *rejects* a write whose classification flags PHI (classification at the write boundary, R10) |
| **14** | atomic capture-unit | gateway-behavioral (1b) | contract test: `Evidence` node + its `SOURCED_FROM` edge commit in a **single** gateway transaction (atomicity is invisible in final state — verifiable only at the txn boundary) |
| **19** | conditional-consumption read-discipline | gateway-behavioral (1b) | contract test: an `applicability_state:conditional` node is admitted to a consuming context *only* where that context satisfies its `Condition` predicate |

### 3.1a The 1b interface seam (resolves B-1 — what the gateway-behavioral contract artifact concretely *is*)

The five 1b contracts test *gateway behavior*, but the gateway's API is **RBT-15's to design** (DDR-002 §5 routes the write-endpoint / API contract → knowledge-service SDD). To author the contracts *now* (the precede-RBT-15 gate) without RBT-33 designing RBT-15's API, the 1b artifact is defined precisely as follows:

1. **RBT-33 defines a minimal abstract gateway seam** — a Python `Protocol` (structural; no inheritance coupling), call it `GraphGateway`, exposing only the *behavioral surface the safety-critical contracts must exercise*: a write path carrying author identity + classification, a ground-truth read path taking an optional consuming-context, and an evidence-write path carrying its source. This is the **contract seam, not the gateway API** — RBT-15's real API is a *superset* that satisfies the Protocol. The seam stays minimal and behavioral precisely so it does not pre-empt RBT-15's API design (the reverse DIRECTIVE-026 role-boundary risk): RBT-33 owns the contract surface, RBT-15 owns the API that conforms to it.
2. **The 1b contracts are authored as expected-failure (`xfail`) tests against the seam** — each imports `GraphGateway`, asserts the required behavior (e.g. #7: a non-ASA `ReasoningProgress` write raises), and is marked `xfail(reason="awaiting RBT-15 gateway implementation of GraphGateway seam")` per the DIRECTIVE-009 §9.2.1 xfail/skip lifecycle. Against the bare seam (no implementation) they fail-as-expected (`xfail`); when RBT-15 implements the seam they pass (`xpass`), which is the signal the gateway was built to the contract.
3. **RBT-15's obligation is to implement the seam and convert the contracts to required-green** — un-mark the `xfail`, make the 1b job a required status check, and demonstrate all-green. This is the M-3 carry-forward (§9), captured as an RBT-15 acceptance addition.

This makes "enforced before RBT-15" operational: the contract is a **real, executable, tracked artifact** in RBT-33 (not a prose spec), and the gateway is demonstrably built against it. #14's atomicity — invisible in final graph state — is expressible only this way: an `xfail` contract asserting the seam's evidence-write is single-transaction, which RBT-15's implementation must satisfy.

> **CI-state precision (B-1 secondary).** In the Increment-1 PR the 1b job runs **`skip`/`xfail` (non-blocking)** so the PR merges green — **not** `red` (which blocks). "Red until RBT-15" elsewhere in this substrate is shorthand for *xfail-pending*, never *failing-the-build*; §5 is corrected to this precise wording.

### 3.2 Increment 2 — follow tier (9)

| # | Invariant | Class | Check shape |
|---|---|---|---|
| **2** | no vector properties | static schema-lint | scan property declarations / constraint DDL for vector/embedding-typed props; fail any |
| **18** | attaches_to-exists | static schema-lint | every `PlaneDefinition.attaches_to` label ∈ declared core-label set |
| **3** | relationship cardinality | graph-state | e.g. `FOR_CAPABILITY` cardinality 1 — `MATCH (n)-[:FOR_CAPABILITY]->(m) WITH n, count(m) AS c WHERE c <> 1` |
| **4** | one active version per business_key | graph-state (PK-backed) | PK uniqueness is DB-enforced; CI adds the *active-version* semantic the PK can't express: ≤1 `status:active` per `business_key` |
| **5** | aggregate-derivation | graph-state | recompute `CapabilityCostEstimate.aggregate_cost` from components; fail if stored ≠ derived (catches hand-set divergence; equal-by-derivation passes harmlessly) |
| **6** | schema-on-write bounding | static (declarations) + graph-state (instances) | extension nodes validate vs their `PlaneDefinition`; instance-edges bounded to `attaches_to`. *On-write rejection itself is RBT-15 gateway behavior; CI checks resident conformance.* |
| **10** | `rule_definition`↔edge sync | graph-state | every `dependency_manifest` entry of a `PolicyRule`/`Condition` appears as a `GOVERNED_BY`/`MANDATES` target. **Enforces declared-but-wired, not declared-complete** — the completeness check is RBT-22's. |
| **12** | tamper-detection | graph-state | `Artifact.content_hash` matches the referenced snapshot hash |
| **8** | never-delete | graph-state + gateway | graph-state: version chains intact, no orphaned supersession; gateway: reject hard-delete on versioned types. *The one follow-tier member with gateway-behavioral character — "follow" is about timeline, not mechanism; its contract test lands on the uniform timeline, not the gated one.* |

### 3.3 Split-mechanism members (named so they don't fall through a single-class assumption)

- **#6** — static (declaration rules) + graph-state (resident extension nodes/edges); on-write
  rejection is RBT-15's.
- **#8** — graph-state (chain integrity) + gateway (delete-rejection).
- **#11** — native existence-constraint (presence) + CI (valid-value / distinguishability).

### 3.4 ADR-002 §6 design-review checks (the thinner second venue)

ADR-002 §6 is six checks against *design documents* (and eventually service code), distinct from
the graph/gateway venue. The original RBT-33 charter anchor (ADR-002 three-hat Pass-1, B-1) is this
venue's mechanizable subset. Enumerated 1:1 to avoid mis-mapping a check to its source:

| §6 check | What it asserts | ADR-002 / DDR-001 surface | Mechanization |
|---|---|---|---|
| **#1 system-of-record** | design holds no *authoritative* architecture/reasoning state in a local store; reads it from the graph | §2.1 / DDR-001 #2 | design-review lint (mechanizable) |
| **#2 graph-access-authority** | no service other than knowledge-service holds a direct Neo4j driver | §2.5 / DDR-001 #1 | design-review lint (grep for Neo4j-driver imports outside knowledge-service) |
| **#3 store-authority** | state placed in the correct store per §2.4; no vector store introduced | §2.4 | design-review lint (mechanizable) |
| **#4 traversal-locality** | KG/RG / cross-plane access uses first-class traversal, not app-layer joins | §2.3 | **judgment-only** — stays three-hat review (not cleanly lint-able) |
| **#5 write-authority** | designs writing reasoning state honor §2.6 (ASA authors `ReasoningProgress`; AOE owns `ReasoningSession` lifecycle) | §2.6 / DDR-001 #3 | design-review lint; **overlaps graph/gateway #7** (different venue: design-text vs gateway-runtime) |
| **#6 data-protection** | designs enforce no-PHI-by-design classification (§2.7) | §2.7 | design-review lint; **overlaps graph/gateway #13** (≈ no-PHI) |

So #1, #2, #3, #5 are the design-review-lint subset; #6 overlaps #13 and #5 overlaps #7 (same
control, different venue — design-text vs graph/gateway-runtime); #4 stays judgment-only. The
no-vector half of #3 also overlaps graph/gateway #2.

**Sequencing:** implement the design-review lint subset as a **later, lower-priority slice** within
RBT-33 — it doesn't gate RBT-15, and greenfield has no service code/designs to scan yet, so the
highest-value enforcement is the graph/gateway venue (Increments 1–2). Tracked within RBT-33; not
part of either graph/gateway increment.

### 3.5 DDR-001-native checks 4–6 (charter includes DDR-001 checks 1–6; 1–3 = ADR-002 §6 surfaces)

The RBT-33 charter union explicitly carries DDR-001's six conformance checks. Checks **1–3** are
the ADR-002 §6 surfaces (§3.4 / #7). Checks **4–6** map as:

| DDR-001 check | Maps to | Class / increment |
|---|---|---|
| **4** — `CandidatePromotion` excluded from synthesis ground-truth until EA-approved; SOFIA never self-modifies KG | **absorbed → DDR-002 #9** (proposal-visibility; #9 defers to DDR-001 #4) | gateway-behavioral, 1b |
| **5** — RG `Evidence` resolves to its **pinned KG version** (point-in-time explainability) | **distinct check — NOT among the 19** (see below) | graph-state, Increment 1 (1a-class) |
| **6** — every KG node carries provenance; promoted distinguishable from ingested | **absorbed → DDR-002 #11** (provenance distinguishability) | graph-state, 1a |

**Check 5 is a straggler my cold read surfaced — it is real charter scope but not one of the
DDR-002 §7 nineteen.** It mechanizes as a graph-state referential-integrity assertion: the version
`Evidence` pinned must resolve to a **retained** version of the cited lineage (the as-of pin is not
dangling). The KG node is reached via the `SOURCED_FROM` edge (DDR-002 §5), **not** a denormalized
business-key on `Evidence` — `(:Reasoning:Evidence)` carries `{evidence_id, fact_summary,
confidence, weight, source_node_version, observed_at}` (§4); there is no `source_business_key`
property. Corrected sketch, anchored on the §6 never-delete / version-retention model:

```cypher
MATCH (e:Reasoning:Evidence)-[:SOURCED_FROM]->(k)
WHERE e.source_node_version IS NOT NULL
  AND NOT EXISTS {
        MATCH (kv) WHERE kv.business_key = k.business_key
                     AND kv.version      = e.source_node_version
      }
RETURN e AS dangling_version_pin
```

i.e. fail any `Evidence` whose pinned `source_node_version` does not resolve to a retained version
node of the lineage its `SOURCED_FROM` target belongs to — exactly the point-in-time-explainability
guarantee, which §6 retention is what keeps satisfiable. **Tier:** DDR-002's binding does not cover
it (it is DDR-001-native, outside the 19), so the classification is **RBT-33's call** — placed
conservatively in **Increment 1 (1a graph-state)** as a member of the provenance-soundness /
point-in-time-audit cluster alongside #1, #11, #15. Library home: `assertions/provenance.py`.

This brings the enforced graph/gateway set to **the 19 + DDR-001 check 5** (= 20 graph/gateway
checks total), with DDR-001 checks 4 and 6 absorbed into #9 and #11.

---

## 4. Deliverable: the conformance-assertion + contract-test library

One library, two usage modes — this is what collapses 1a and 1b into a single artifact RBT-15
builds against.

### 4.1 Structure (proposed; repo-placement to confirm at build)

```
conformance/                      # the library (Python; ENG-STD-001 §2 layout, TDD per DIRECTIVE-008/009)
├── assertions/                   # graph-state checks (1a + follow-tier graph-state)
│   ├── provenance.py             #   #1, #11, #15, #17, + DDR-001 #5 (Evidence version-pin integrity)
│   ├── decision.py               #   #16
│   ├── versioning.py             #   #4, #8(chain)
│   ├── governance_sync.py        #   #10
│   ├── cost.py                   #   #5
│   └── integrity.py              #   #3, #6(instances), #12
├── lint/                         # static schema-lint (no graph)
│   └── schema_lint.py            #   #2, #18, #6(declarations)
├── contracts/                    # gateway-behavioral xfail contract tests against the seam (1b + #8 delete-reject)
│   ├── gateway_seam.py           #   the minimal abstract GraphGateway Protocol (§3.1a) — RBT-15 implements
│   ├── write_authority.py        #   #7
│   ├── read_discipline.py        #   #9, #19
│   ├── classification.py         #   #13
│   ├── atomic_capture.py         #   #14
│   └── never_delete.py           #   #8(delete-reject)
├── fixtures/                     # seeded conformant + violation graphs (per assertion)
└── tests/                        # validator-correctness tests (each assertion vs its fixtures)
```

### 4.2 Two usage modes

- **Graph-state members (1a + follow graph-state):** run standalone in CI against
  **seeded ephemeral-Neo4j fixtures** (testcontainers / Docker-Compose — the substrate already
  ratified for autonomous build). Each assertion ships a *conformant* fixture (must pass) and one
  or more *violation* fixtures (must be caught). This proves **validator correctness now**,
  independent of any gateway.
- **Gateway-behavioral members (1b + #8 delete-reject):** authored as **`xfail` contract tests
  against the `GraphGateway` seam** (§3.1a) the library defines. Against the bare seam they
  fail-as-expected (`xfail`); RBT-15 implements the seam and the contracts pass (`xpass`), then
  RBT-15 un-marks them and makes the job required-green (M-3 carry-forward, §9). They are "enforced
  before RBT-15" because the executable contract artifact + its seam exist in RBT-33 and gate the
  gateway build — not because they run green against a gateway that does not yet exist.

#### 4.2.1 Fixture-seeding convention (resolves M-2)

Graph-state fixtures are **raw Cypher `CREATE` statements** that construct the conformant and
violation graph patterns directly (label + property shapes per DDR-002 §2–§7, constants
fresh-fetched at build). Raw `CREATE`s are **sufficient for assertion-correctness testing** — the
question each fixture answers is "does the assertion flag this violation / pass this clean case,"
which needs only the graph shape, not an installed schema.

The **native-constraint backstop** (the existence/uniqueness constraints that DB-enforce the
*presence* half of #4 and #11) is **not installed in the assertion-correctness fixtures** — those
fixtures exercise the **CI-half** (the semantic check the constraint cannot express). Installing the
native constraints to exercise the **DB-half** is the real schema's job, stood up where the
schema/gateway lands (RBT-15-adjacent / deploy-time); scoping it there is explicit, not an omission.
**Schema-consistency** between fixtures and the eventual real schema is an **RBT-15-coupled
concern** — named here, not solved in RBT-33; a light mitigation is to source fixture label/property
names from a single shared schema-constants module so a future real-schema definition can share
them (build-detail, not a fork).

### 4.3 Honest enforcement floor

What CI enforces *today* for the graph-state class is **validator correctness against fixtures** —
no graph is deployed yet, so there is no live-graph sweep. Wiring the same assertions against a
deployed/staging graph as a pipeline or scheduled stage is **downstream deploy-time work**
(post-RBT-15, post-deploy), not built in RBT-33. This is named so the acceptance ("validators run
in CI and fail non-conformant designs/code") is read correctly: in RBT-33 it means *the validators
exist, are correct, and gate the gateway build*; live-graph conformance scanning is a later wiring.

---

## 5. CI topology

- New CI job(s) on `ci.yml` alongside the existing `validate-docs-structure`. The current `ci.yml`
  ships only `validate-docs-structure`; full ENG-STD-001 §13.1 app gates were deferred until
  `app/` + `tests/` exist (build-leg note, RBT-3). The `conformance/` package + its tests are the
  first body of app/tooling code, so this leg also stands up the app-test CI surface for it
  (lint / typecheck / test / coverage ≥90% per ENG-STD-001 §10.1).
- **Increment 1 PR** adds: a `conformance-graph-state` job (ephemeral Neo4j service container +
  fixtures + the 1a assertions running green) and the **1b contract tests committed as `xfail`
  (non-blocking)** against the `GraphGateway` seam (§3.1a), each carrying an `xfail` reason tying it
  to RBT-15. `xfail` keeps the Increment-1 PR **green** (the contracts are *expected* to fail
  against the bare seam) while making the contracts visible, executable, and tracked — **not** `red`
  (which would block the merge).
- **Increment 2 PR** adds the follow-tier assertions onto the same job/fixtures (additive; low
  marginal overhead) + the static-lint job (#2, #18, #6-declarations).
- Branch-protection: the graph-state + lint jobs become required status checks once green. The 1b
  contract job is **`xfail`-non-blocking at RBT-33** and becomes a **required status check at RBT-15
  merge time** — RBT-15 implements the seam, the contracts flip `xfail → xpass`, RBT-15 un-marks
  them and requires the green job (the M-3 carry-forward, §9). It is never a build-blocking `red`
  state; "red until RBT-15" elsewhere is shorthand for this `xfail`-pending lifecycle.

---

## 6. `applicability_state` carry-forward — named-gap record (Fork 5)

**The exposure.** Check #19 enforces "a `conditional` node is consumed only where its `Condition`
is satisfied." On **supersession**, a successor that silently defaults to `unconditional` escapes
#19 (it is no longer marked `conditional`, so never enters the filter) — over-admitting past an
EA-set `Condition`. DDR-002 §5 names the blind spot and commits the integrity *expectation*, then
routes the *invariant-or-not* question to RBT-33.

**Candidate 20th invariant (recorded, not adopted).** Graph-state-checkable: *every successor of a
`conditional` node either carries `conditional` + a `Condition`, or traces to an explicit
re-scoping `PromotionDecision`.*

**Determination: named gap, additive-on-instance.** The exposure is **latent-contingent on
un-built machinery** — minting a promoted `conditional` node requires the promotion / feedback-loop
machinery (DDR-003 / RBT-14 governance + the gateway + reasoning machinery), none of which exists;
there is no path to create an exploitable instance today. Adopting a 20th enforced invariant for a
confluence that cannot occur yet is the over-specification the R25 empirical-warrant lever — and
the v0.4–v0.6 subtraction pass (F-9, which demoted retraction / multi-condition disjunction /
ProvenanceSummary-form / `decision_origin` to named gaps) — exist to prevent.

**Reversal path.** Re-instate the candidate invariant as an additive graph-state check (and/or a
gateway carry-forward contract) when the promotion + conditional + supersession confluence first
becomes real — DDR-003 / RBT-14 + RBT-15 territory. The carry-forward *mechanism* stays RBT-15's
gateway responsibility per DDR-002; RBT-33 answers only the invariant-question, and the answer is
"not yet." **No DDR-002 amendment** — DDR-002 already names the routing open; this closes it on the
RBT-33 side.

---

## 7. Within-increment-1 build order (settled consequence)

The 1a/1b split + RG-provenance priority determine the order; recorded, not a fresh fork:

1. **1a graph-state first** — they are standalone-fixture-testable, so they stand up the
   ephemeral-Neo4j fixture harness + the assertion library scaffold and prove the CI job green.
   **RG-provenance #1 leads** (highest-priority member).
2. **1b gateway-contracts second** — layered onto the proven scaffold as `xfail` contracts against
   the `GraphGateway` seam (§3.1a), awaiting RBT-15. **#14** (atomic-capture, the gateway half of
   RG-provenance) is the priority within 1b.

RG-provenance therefore spans both strata (#1 in 1a, #14 in 1b) — consistent with it being the
tier's highest-priority member rather than a separable increment.

---

## 8. Acceptance mapping (RBT-33)

| Acceptance criterion | How this design satisfies it |
|---|---|
| Validators run in CI and fail non-conformant designs/code | §4–§5: graph-state assertions on seeded fixtures (now) + gateway contract tests (at RBT-15) + design-review lint (§3.4, later slice) |
| ADR-002 §6, DDR-001 § Conformance-checks, DDR-002 § Integrity-invariants / Risks all cite this item | Already cite RBT-33 aspirationally (DIRECTIVE-024 §24.1). **Build-completion follow-item:** on landing, update each from "tracked at RBT-33" to "enforced by RBT-33's validators." A light doc-touch at build close, not this leg. |
| RG-provenance invariants implemented before RBT-15 authoring begins | §3.1 + §7: #1 (1a) enforcing on Increment-1 landing; #14 (1b) `xfail` contract against the seam, flipped required at RBT-15. Increment 1 is the precede-RBT-15 gate. |

> **Disambiguation (C-1 / C-2).** Two "20th" usages, intentionally different frames: DDR-001 check 5
> is the **20th *enforced* check** (adopted — the 19 + DDR-001 #5, §3.5); the `applicability_state`
> candidate (§6) is a **20th *invariant* that is *not* adopted** (named gap). And two "#5"s: write
> **"DDR-002 §7 #5"** for aggregate-derivation (`cost.py`) vs **"DDR-001 check 5"** for the Evidence
> version-pin (`provenance.py`) — always qualified, never bare "#5".

---

## 9. Items routed onward / open at build

- **Repo placement** of `conformance/` — proposed §4.1; confirm against ENG-STD-001 §2 at build.
- **Exact label/property constants** — fresh-fetched from DDR-002 §2–§7 at build (no recall).
- **Design-review lint pair** (§3.4) — later, lower-priority RBT-33 slice; doesn't gate RBT-15.
- **Live-graph conformance sweep** (§4.3) — downstream deploy-time wiring; out of RBT-33.
- **Carry-forward mechanism** (§6) — RBT-15 gateway design; invariant re-instatement is additive-on-instance.
- **1b → required flip (M-3; integrity hinge of the precede-RBT-15 gate).** The `xfail` 1b contracts
  only deliver the "built against an enforced contract" guarantee if RBT-15 un-marks them and makes
  the 1b job a required green check. Captured as a **tracked RBT-15 acceptance addition** — *"un-skip
  RBT-33's 1b gateway-behavioral contract job, make it a required status check, all green"* — written
  to existing RBT-15 at ratification (three-layer; no new ticket, DIRECTIVE-025). Without this, the
  contracts stay `xfail` indefinitely and the gate silently lapses (the DIRECTIVE-024 §24.1
  compounding-debt failure mode). **Pending operator ratification before the Linear write.**
- **Source-citation updates** (§8) — build-completion doc-touch across the three sources.
- **Handoff form** — substrate-direct (à la DDR cycle) vs. thin DIRECTIVE-030 BUILD-prompt wrapper;
  decide at handoff.

---

## 10. Pass-1 three-hat fold-in log (v0.1 → v0.2)

Disposition of every 2026-06-22 substrate-review finding, for the Pass-2 re-confirm:

| Finding | Disposition | Where |
|---|---|---|
| **B-1** — 1b deliverable form under-specified / RBT-15 seam collision | Added §3.1a: RBT-33 defines a minimal abstract `GraphGateway` Protocol seam (contract surface, not the gateway API); 1b contracts authored `xfail`-against-seam (DIRECTIVE-009 §9.2.1 lifecycle); RBT-15 implements seam + flips to required. CI-state precision corrected (xfail-non-blocking, not red). | §3.1a, §4.1, §4.2, §5, §7 |
| **B-2** — check-5 sketch references non-existent `source_business_key` | Sketch rewritten to traverse `SOURCED_FROM` and verify the pinned `source_node_version` resolves to a retained version of the cited lineage, anchored on §6 never-delete/retention. Placement (Inc-1 / 1a / `provenance.py`) unchanged. | §3.5 |
| **M-1** — ADR-002 §6 venue loosely enumerated | §3.4 rewritten as a 1:1 table over §6's six: #1/#2/#3/#5 design-review-lint; #6≈#13 and #5≈#7 overlaps named; #4 judgment-only. | §3.4 |
| **M-2** — fixture-seeding source unspecified | Added §4.2.1: raw-`CREATE` fixtures sufficient for assertion-correctness; native-constraint DB-half scoped to real-schema/deploy; schema-consistency named as RBT-15-coupled. | §4.2.1 |
| **M-3** — 1b→required flip untracked | Added as tracked carry-forward: RBT-15 acceptance addition (un-skip + require 1b job green), written to existing RBT-15 at ratification (no new ticket). Pending operator ratification. | §9 |
| **C-1** — "20th" overloaded | Disambiguation note added (20th *enforced check* vs 20th *invariant, not adopted*). | §8 |
| **C-2** — dual `#5` | Qualifier convention added ("DDR-002 §7 #5" vs "DDR-001 check 5", never bare). | §8 |

**Gate:** resolves the 2 BLOCKING + 3 MATERIAL; C-1/C-2 readability folded. Ready for the Pass-2
re-confirm. One disposition (M-3) carries a **pending Linear write to RBT-15** awaiting operator
ratification — flagged, not yet executed.

---

*End of substrate.*
