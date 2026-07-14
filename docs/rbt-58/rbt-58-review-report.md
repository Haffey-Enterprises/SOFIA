# RBT-58 Deliverables Review Report — Batches A–D

## Overall Verdict

**Not ready to hand to Claude Code as-is: one BLOCKING defect must be fixed first.** The Batch-C cost seed authors `PlaneDefinition.confidence_basis` as a flat `{label: basis-string}` map, but the operative conformance assertion (`extension.py` #26, basis-declaration totality) requires each value to be a nested `{basis: …}` object. As delivered, the seed loads and produces three "malformed" #26 violations, so `run_conformance_1a.py` reports **RESULT: NOT GREEN** — directly failing RBT-58's stated acceptance leg ("1a green against the seeded instance") and falsifying the seed README's "authored to green" claim. Everything else is sound: the remaining findings are MATERIAL (real, should-fix, non-blocking) and COSMETIC. The underlying schema, IaC, and tooling are well-built and heavily verified-correct — but the deliverable cannot pass its own acceptance gate until #26 is reconciled. Fix the BLOCKING item (Tad's call: enrich the seed to the nested shape the harness demands, or reconcile `extension.py`/DDR-002 §2.6, whose line-156 illustration uses the flat form the author copied), then proceed.

---

## BLOCKING

### B1 — Cost seed fails conformance #26 (confidence_basis value-shape)
- **File / location:** `/home/claude/rbt-58-seed/seed/60-cost-extension.md`, `confidence_basis` block, lines 44–47.
- **Defect:** `confidence_basis` is authored label→string (`CapabilityCostEstimate: native_confidence`, `RateCard: non_citable`, `CostFactor: non_citable`). `loader.py._serialize` (lines 34–41) `json.dumps` it verbatim, storing string leaf values. The #26 assertion `basis_declaration_totality` (`conformance/assertions/extension.py` lines 123–133) iterates `confidence_basis.items()` and flags any value that is `not isinstance(declaration, dict)` as malformed, then reads `declaration.get("basis")`. All three cost labels yield strings → **3 malformed violations** → `run_conformance_1a.py` returns 1 / NOT GREEN. Contradicts `rbt-58-seed/README.md` lines 44–49 ("#26 … authored to green") and the prose at 60-cost lines 20–22.
- **Canon:** DDR-002 §7 #26 as mechanized in `conformance/assertions/extension.py` (each `confidence_basis` value must be a `{basis, freshness_operand?}` object; freshness operand iff aging — a bare string structurally cannot carry it). The harness is the operative 1a authority; DDR-002 §2.6 line 156's flat illustration is the likely source of the author's error.
- **Fix:** Author each value as a nested map — `CapabilityCostEstimate: { basis: native_confidence }`, `RateCard: { basis: non_citable }`, `CostFactor: { basis: non_citable }` — or (Tad's call) reconcile `extension.py`/DDR-002 §2.6 to the flat form. Either way, seed + loader + harness must agree before 1a can be green.

*(This is the same underlying issue independently surfaced by the seed, coherence, and antagonistic lenses; consolidated here.)*

---

## MATERIAL

### M1 — Section 6 verification counts overstate the applied constraint set
- **File / location:** `/home/claude/01-constraints.cypher`, Section 6 verification block, lines 253–255.
- **Defect:** The self-declared "and verified" acceptance target states **110** constraints (28 PK-uniqueness + 9 bk/ver + 26 provenance-existence + 47 T1-existence). The file actually creates **106** (27 + 9 + 24 + 46). Off by +1 PK, +2 provenance, +1 T1, +4 total — traceable to counting 28 rather than 27 entity labels and to a stale tally after CandidatePromotion provenance-existence was (correctly) dropped. The individual constraint statements are all correct; only the verification target is wrong. Section 6 instructs the operator to compare `SHOW CONSTRAINTS` (which returns 106) against the stated 110, producing a phantom acceptance failure.
- **Canon:** DDR-002 §7 "DB-enforced (Neo4j Enterprise)" — uniqueness on every PK + (business_key,version); provenance-existence = 12 label-scopes × 2 = 24.
- **Fix:** Correct the Section 6 tally to 27 / 9 / 24 / 46 = 106 (and 23 indexes).

*(Reported by both the constraints and antagonistic lenses; consolidated.)*

### M2 — Three flagged T2 index properties dropped, not deferred (Cost plane)
- **File / location:** `/home/claude/01-constraints.cypher`, Section 5 index set, lines 221–243 (23 indexes).
- **Defect:** DDR-002 §2.6 flags `RateCard.status`, `CostFactor.factor_scope`, and `CostFactor.factor_type` each as "(T2, indexed)", but no index exists on `:RateCard` or `:CostFactor`, and Section 5's deferred list (lines 213–219) does not mention them — so they are silently dropped, contradicting the file's own "flagged T2 traversal/filter props only" scope claim. (Reviewer note: `RejectedAlternative.candidate_type`, §4, is a fourth flagged property also dropped-not-deferred; the true gap is 4, not 3 — understating, not overstating.) Bounded impact: no conformance assertion checks indexes, so it does not fail acceptance.
- **Canon:** DDR-002 §2.6 lines 157–158; §7 "Indexes on the flagged T2 traversal/filter properties only."
- **Fix:** Add the missing indexes, or explicitly add them to Section 5's deferred list with rationale.

### M3 — `APPROVED_OPTION_FOR` edges omit required provenance + temporal fields
- **File / location:** `/home/claude/rbt-58-seed/seed/10-catalog.md`, lines 116–124 (both edges).
- **Defect:** Edge properties are only `{ conditional, justification }`. DDR-002 §3 names `APPROVED_OPTION_FOR` explicitly as the ingested asserted-fact edge that must carry `origin_mechanism` (§1) and marks it *(temporal)* — requiring `effective_from`/`status`. The sibling temporal edge `HAS_ROLE` (`50-governance.md:70`) correctly carries `effective_from`, showing inconsistent application. These are T1/T2 fields, so the reversibility-tiered completeness posture does not defer them. No 1a assertion inspects edge properties, so it does not block — but it is genuine §3 edge-grammar drift on ground-truth data.
- **Canon:** DDR-002 §3 edge grammar (asserted-fact edges carry provenance; temporal edges carry `effective_from/effective_to + status`).
- **Fix:** Add `origin_mechanism`, `effective_from`, and `status` to both `APPROVED_OPTION_FOR` edges.

### M4 — Regional cluster triples the always-on node floor the scheduler exists to eliminate
- **File / location:** `/home/claude/rbt-58-infra/terraform/modules/neo4j_graph/cluster.tf`, L16–18 (cluster `location = var.region`), L74–98 (system pool `node_count = 1`), L104–113 (graph pool autoscaling max=1).
- **Defect:** The cluster is REGIONAL (`location = var.region`, dev = `us-east4`) with no `node_locations` pin anywhere in the module. In GKE, node-pool `node_count` and autoscaling min/max are **per-zone**, so the "small always-on" system pool (`node_count=1`) is actually **3** e2-small nodes running 24/7 — 3× the intended floor, directly undercutting the scale-to-zero scheduler's cost lever. Comments (cluster.tf L8–9, README L19) assert a single-node count the regional topology does not deliver. The single-replica StatefulSet self-limits the graph pool, so the system pool is the real cost defect; the cluster still functions and 1a is unaffected (not BLOCKING).
- **Canon:** infrastructure-code reference/02 §3 (non-prod trades protection for cost; prod ? REGIONAL : ZONAL pattern).
- **Fix:** Make the cluster zonal for dev (`location = <zone>`) or pin `node_locations` to a single zone.

### M5 — 1a acceptance runner can report GREEN while silently skipping an entire assertion module
- **File / location:** `/home/claude/rbt-58-tools/tools/run_conformance_1a.py`, lines 66–71 (`except ModuleNotFoundError: continue`) and 79–84 (GREEN/exit).
- **Defect:** Each assertion module is imported in a `try/except ModuleNotFoundError` that prints a skip note and continues, with no bookkeeping that the module ran. `main()` gates solely on `total_violations`; nothing compares `ran` against an expected count. Reachable path: the `conformance` package is a separate install from `tools`, so if it is not importable, **all six** `import_module` calls raise `ModuleNotFoundError`, all are skipped, and the runner prints **RESULT: GREEN** / exit 0 having executed **zero** assertions — a false green on the designated acceptance gate. Partial mitigations (stderr skip lines, printed `ran` count, prompt step-6 human confirmation) rely on a human overriding a GREEN/exit-0 signal.
- **Canon:** Acceptance gate per the Code prompt ("RESULT must be GREEN (zero violations)"); the fail-loud discipline `conformance/README` asserts for 1a.
- **Fix:** Compare `ran` against the expected module/assertion count (or make a skipped module fatal); exit non-zero if any expected module failed to import.

---

## COSMETIC

### C1 — Execution prompt step 6 gives no import setup for the `conformance` package
- **File / location:** `/home/claude/rbt-58-tools/RBT-58-code-execution-prompt.md`, execution step 6, line 59 (and `tools/README.md` line 42).
- **Defect:** Step 5 sets `PYTHONPATH=.` for the tools package, but step 6 runs `python run_conformance_1a.py` with no PYTHONPATH/install for the separate `conformance` package. Run naively from `tools/`, the `conformance.assertions.*` imports all raise `ModuleNotFoundError` — which (per M5) the runner swallows into a spurious GREEN. Scoped narrowly to the missing import note; the spurious-green consequence is M5.
- **Canon:** Operational completeness of the acceptance leg; `conformance/README` install (`pip install -e .`).
- **Fix:** Add an explicit step to `pip install -e .` (or set PYTHONPATH to the repo root) for `conformance` before step 6. *(Fixing this also removes M5's most likely trigger — do both.)*

### C2 — Edge MERGE silently drops edges with unmatched endpoints but still counts them
- **File / location:** `/home/claude/rbt-58-tools/tools/seed_loader/loader.py`, `_merge_edge` lines 84–94; count bump `load_docs` lines 107–110.
- **Defect:** `MATCH (a {…}),(b {…}) MERGE (a)-[r]->(b)`: if either endpoint MATCH returns zero rows (PK typo, missing/mis-ordered node), MERGE binds nothing, creates no edge, and raises no error, yet `counts['edges'] += 1` runs unconditionally. The reported edge count cannot prove edges landed. Current Batch-C seed is clean (24 nodes / 25 edges, 0 dangling), so it does not bite today; nodes load first and pass DB constraints, and 1a does not consume the loader's self-count — bounding impact to a defensive-guard / reporting-honesty gap (a missing edge is incompleteness, not corruption).
- **Canon:** DDR-002 §5 cross-graph linkage (edges resolve to real endpoints); the loader header's "MERGE by matching endpoints on their PK" presumes but does not verify endpoint existence.
- **Fix:** Assert `summary.counters.relationships_created` (or a post-load endpoint-resolution check) and fail loud on a dropped edge.

### C3 — Seed README lists a non-existent `#18` assertion as an "authored-to-green" 1a check
- **File / location:** `/home/claude/rbt-58-seed/README.md`, line 48 ("#18 attaches_to targets exist").
- **Defect:** `run_conformance_1a.py` runs only provenance/decision/reasoning/supersession/retraction/extension; no `#18` assertion function exists (`#18` is Increment-2, CI-only per DDR-002 §7). The seed satisfies the underlying condition (`attaches_to: [Capability, Technology]`, both present in Catalog), so this is documentation drift, not a load/conformance failure. (One supporting citation in the source finding — that `01-constraints.cypher` L22–24 lists #18 — is inaccurate; #18's CI-only status is confirmed elsewhere and the core defect stands.)
- **Canon:** `conformance/README.md` scope list (#18 not built); DDR-002 §7 line 154 (#18 CI-only).
- **Fix:** Remove `#18` from the "authored to green" list, or move it to a "satisfied but not harness-checked" note.

### C4 — Module declares an unused `kubernetes` provider requirement
- **File / location:** `/home/claude/rbt-58-infra/terraform/modules/neo4j_graph/versions.tf`, L20–23.
- **Defect:** Pins `hashicorp/kubernetes ~> 2.30`, but the module defines zero `kubernetes_*` resources, no `provider "kubernetes"` block, and no `configuration_aliases`; `providers.tf` L7–11 delegates the kubernetes provider to the caller (manifests applied out-of-band). The dev root omits `kubernetes` entirely, so the requirement is dead and inconsistent — exactly the `terraform_unused_required_providers` lint case. `terraform init/plan` does not error on it.
- **Canon:** infrastructure-code reference/01 §1 (versions.tf required_providers; TFLint unused-provider rule).
- **Fix:** Drop the `kubernetes` entry from the module's `required_providers`.

---

## Verified-Correct (notable POSITIVE findings)

The review independently confirmed the following as sound, canon-grounded decisions:

**Batch A — schema bootstrap (`01-constraints.cypher`)**
- **Composite-uniqueness scope is exactly §6's versioned-ground-truth set** — the 9 types (Catalog 4 + Standard + PolicyRule + RateCard + CostFactor + PlaneDefinition), correctly excluding ComplianceControl (no version), CapabilityCostEstimate (immutable as-of record), and Solution (dual-home, not versioned-ground-truth).
- **Enterprise-vs-both-editions split is correct** — uniqueness on both editions, node-property existence Enterprise-only, with failure-to-create-on-Community used as the live Enterprise proof (matches Neo4j semantics and ADR-002 §2.2/§4.1).
- **Surrogate/scope edge-cases handled per the literal §7 contract, not by invention** — Evidence excluded from provenance-existence; CandidatePromotion given only PK-existence with the genuine §5-vs-§7 ambiguity flagged for DDR resolution rather than resolved by an unlisted constraint; separate `exist_*_bk`/`exist_*_ver` constraints correctly back the composite (which Neo4j does not enforce for presence).

**Batch B — infrastructure**
- **Secret handling is exemplary** — container-only Secret Manager secret with the version added out-of-band (never in Terraform state), projected to the pod via the Secret Manager CSI driver under Workload Identity, no credential in any Kubernetes Secret (invariant #5; SDD-001 §4.6).
- **IAM is least-privilege, keyless, and additive** — two purpose-scoped SAs, only `_iam_member` bindings, complete Workload Identity wiring, no `google_service_account_key` anywhere (invariants #7/#8).
- **Stateful-database pattern is correct end to end** — StatefulSet with Guaranteed QoS, regional-SSD `volumeClaimTemplates` (WaitForFirstConsumer + Retain), headless service, all three probes; scale-to-0 preserves the Retain PVC (invariant #10; 04 §3/§4).
- **Stack-independent disciplines hold** — everything pinned, remote-locked GCS state, plan-before-apply, env-specific values carry no defaults (invariants #2/#3/#4/#6).
- **No IaC footgun on the hunted vectors** — graph-pool taint ↔ StatefulSet toleration match, and scale CronJobs land on the always-on system pool so scale-up is always schedulable.

**Batch C — seed content**
- **DeploymentEnvironment correctly omits `observed_at`** (per-label flat_base override), with basis-3 aging classes (DeployedService, ConfigurationItem) correctly carrying it — the freshness axis applied precisely where the plane signature demands (DDR-002 §2.2; DDR-004 §4).
- **`source_record_ref` discipline and DDR-004 §4 basis coverage are complete and correctly assigned** — every ingested node and the sole distilled node carry a ref; authored/aggregated nodes correctly omit it; all four bases have ≥1 correctly-assigned node (the basis-4 *intent* is right even though its encoding rides the #26-broken value-shape).

**Batch D — tools**
- **`VERSIONED_GROUND_TRUTH` in `schema.py` matches §6 and Batch-A Section 2 verbatim** (9 types), correctly excluding ComplianceControl and CapabilityCostEstimate despite plane membership.
- **Dict/nested-list property serialization round-trips exactly** with `extension.py`'s parser (`json.dumps` sort_keys ↔ `json.loads` with duplicate-key rejection), and primitive arrays stay native for Cypher set-equality.
- **Supersession marks the correct §6 fields and faithfully defers the gateway-owned `rebind:current` re-point** — `superseded_by=<successor version>` is wire-compatible with the #22 conformance assertion.
- **Assertion discovery by introspection is sound** — selects exactly the 16 public `(driver)`-signature functions across the six 1a modules, correctly excluding `base.py` helpers and re-imported symbols.
- **Content-addressed manifest genuinely detects drift** across source bytes, canonical payload, and file add/remove; 6/6 unit tests pass (a prose-only edit moves `source_sha256` but not `payload_sha256`).
- **The Code execution prompt honors the two-surface model** (report-and-STOP, no commit) and carries a concrete fresh-fetch guard with the `schema_constants.py` sha256 authority pin.

**Cross-batch coherence**
- **Setting aside #26, the seed loads cleanly against every Batch-A constraint** — no missing required prop, no versioned node lacking business_key/version; `loader.py`'s PK map agrees exactly with the constraint labels and `schema_constants` enums; RG-dependent assertions pass vacuously as designed for a static ground-truth seed.