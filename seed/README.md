# RBT-58 — KG seed dataset (Batch C)

The Haffey Enterprises ground-truth seed, in the ratified **`.md`-source → loader → graph**
model (DP-2). Each file under `seed/` is a human-readable definition of one plane's
ground truth **plus** a machine-loadable graph payload — the same shape a future
`.md` "define a pattern → load it" update takes, so the bootstrap rehearses the
SDD-001 §3.6 `ingest` path rather than being throwaway Cypher.

All content is fictitious Haffey Enterprises material, scrubbed of the operator's
denylisted proper noun per the standing data-hygiene rule (the term is kept off-repo,
in the operator's profile). Any instance found in source is rewritten to "Haffey
Enterprises" before load.

## The source-file contract (what the Batch-D loader consumes)

Each `seed/NN-<plane>.md` has:

1. **YAML frontmatter** — `doctype: kg-seed`, `plane`, `load_order`, `authority`
   (the DDR-002 pin the payload conforms to).
2. **Prose narrative** — what this plane's seed is and why (human source of truth).
3. **A single fenced ` ```yaml ` block** under `## Graph payload` — the authoritative
   `nodes:` + `edges:` the loader MERGEs. `nodes[].labels` carry the plane label +
   entity label; `properties` are DDR-002 §2 fields. `edges[].from/.to` reference a
   node by its PK. `confidence_basis` / `property_schema` on `PlaneDefinition` are
   authored as objects and **serialized to JSON strings on write** (DDR-002 §2.6 fixes
   them as declarations-not-edges; conformance `extension.py` parses them as JSON).

The prose is documentation; the fenced block is the contract. Load order is the file
number prefix (Catalog first — later planes reference its nodes).

## Basis coverage (DDR-004 v1.2.0 §4) — every declared basis has ≥1 citable node

| Basis | Node(s) in this seed | File |
|---|---|---|
| **1 native_confidence** | `ObservedPattern` OBS-001; `CapabilityCostEstimate` EST-001 | 40, 60 |
| **2 flat_base** | Catalog (all); Standards (all); Governance (Actor/GateDecision); `DeploymentEnvironment` ENV-PROD/STG (own tunable); `PlaneDefinition` PLANE-COST (by construction) | 10,20,50,30,60 |
| **3 aging** | `DeployedService` ×3, `ConfigurationItem` CI-001 (`observed_at`) | 30 |
| **4 non_citable** | Cost `RateCard` RATE-001, `CostFactor` COST-001 (declared by PLANE-COST) | 60 |

**The cost registration is the linchpin (one act, three bases):** PLANE-COST establishes
basis-4 for RATE-001/COST-001, is itself a basis-2 `PlaneDefinition`, and enables the
basis-1 EST-001.

## 1a checks the seed is authored to green (against the seeded instance)

`#11` provenance validity · `#17` ingested/distilled ⇒ `source_record_ref` (OBS-001 is
distilled; Catalog/Standards/Environment/GateDecision/RateCard/CostFactor are ingested)
· `#16` one-subtype-per-Decision (GATE-001) · `#26` cost basis-declaration totality
(`confidence_basis` authored as per-label declaration objects, the form `extension.py`
#26 requires) · DDR-001 #5. Checks with no applicable data
(`#1/#14/#15/#20/#21/#22/#23/#24/#25/#27`) pass vacuously — no
Evidence/promotions/retractions/ReasoningProgress in a static ground-truth seed.

*Satisfied but NOT harness-checked at 1a:* `#18` `attaches_to` targets exist (Capability +
Technology are present in Catalog) — `#18` is Increment-2 / CI-only per DDR-002 §7 with no
`conformance/assertions` function, so the seed meets the condition without the harness
verifying it here.

The fiction is yours to reshape (names, portfolio, which patterns) at the end-of-batch review.
