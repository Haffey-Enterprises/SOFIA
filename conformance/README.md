# conformance/ — graph data-layer contract tests

CI-enforced conformance for the ADR-002 §6 / DDR-001 / DDR-002 §7 invariants.
Built TDD-first against seeded ephemeral-Neo4j fixtures. This README doubles as
the build-leg working note; the items flagged **→ RBT-15** are inherited by the
knowledge-service build.

## Scope

### Increment 1 — safety-critical tier (RBT-33)

- **1a — graph-state assertions** (enforce on landing): DDR-002 §7 #1, #11, #15,
  #16, #17, plus **DDR-001 check 5** (Evidence version-pin integrity). Live in
  `assertions/`.
- **1b — gateway-behavioral contracts** (`xfail` against the `GraphGateway` seam
  until RBT-15): #7, #9, #13, #14, #19. Live in `contracts/`.

### Catch-up increment (RBT-48) — v1.3.0 vocabulary + checks #20–#27, #15 companions

Brings the harness to the DDR-002 **v1.3.0** contract (constants refreshed from
v1.0.0 — the full post-v1.0.0 delta). Same 1a/1b discipline: 1a enforces on
landing, 1b stays `xfail` until RBT-15's gateway build.

- **1a — graph-state assertions:** #20 (ProvenanceSummary existence + completeness
  against the §5 span), #21 (retraction-gating trace), #22 (conditional-scope
  carry-forward, predecessor-keyed), #23 (flag↔category), #24 (rollup ceiling),
  #25 (`proposal_kind`↔`RETRACTS`, executed-proposal scope), #26 (basis-declaration
  totality), #27 (basis-admissibility), plus the **#15 companion** (per-candidate
  `decided_at` uniqueness). New modules: `reasoning.py`, `supersession.py`,
  `retraction.py`, `extension.py`; extends `provenance.py`, `decision.py`.
- **1b — gateway-behavioral contracts** (`xfail`): #23 write-time, #22 supersession
  scope-disposition, #20 at-promotion materialization, #21 retracted-node
  read-exclusion, #15 monotonicity, #26 register-plane, #27 capture-time
  `NON_CITABLE_SOURCE`.
- **Tier within this increment:** safety-critical — #21, #22, #23, #15-companion;
  follow-tier — #20, #24, #25, #26, #27 (pulled in early because their ratified
  vocabulary landed; they otherwise sit on Increment 2's schedule).
- **#27 basis resolution** keys off the **active** PlaneDefinition version (§6) and
  fails loud on an unresolvable or conflicting basis. `confidence_basis` /
  `property_schema` are modelled as JSON-string properties (§2.6 fixes them as
  declarations-not-edges; wire format binds at RBT-15).

Increment 2 (remaining follow tier: #2–#6, #8, #10, #12, #18 + static-lint + the
ADR-002 §6 design-review lint slice) is a later BUILD leg — not built here.

## Layout

```
conformance/
├── schema_constants.py   # single source of DDR-002 labels/props/edges/enums (M-2)
├── assertions/           # graph-state Cypher assertions (1a + follow graph-state)
├── contracts/            # GraphGateway Protocol seam + xfail gateway contracts (1b)
├── fixtures/             # raw-CREATE conformant + violation fixtures + seeding helper
└── tests/                # validator-correctness tests + conftest (ephemeral Neo4j)
```

## Test harness

`tests/conftest.py` starts one ephemeral Neo4j per session via testcontainers and
resets the graph before each test. Requires a running Docker daemon.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
pytest conformance   # runs tests/ (graph-state) + contracts/ (1b xfail); 90% cov gate
```

## Build-leg decisions & inherited gaps

- **Neo4j edition: Community, pinned `neo4j:5.26-community`.** The assertion-
  correctness fixtures install **no native constraints** (DDR-002 §4.2.1 — the
  DB-half is the real schema's job), so Community is sufficient and keeps the
  harness license-friction-free. Pinned to the 5.x line for Cypher-dialect parity
  with the Enterprise production graph (Enterprise per DDR-001 / R3).
- **Fixture ↔ real-schema parity gap (→ RBT-15).** Fixtures are raw-`CREATE`
  graph shapes; they do not install the real schema's uniqueness/existence
  constraints. Keeping fixtures and the eventual real schema consistent is an
  RBT-15-coupled concern (DDR-002 §4.2.1). The mitigation in place: fixtures and
  assertions both source label/property names from `schema_constants.py`, so a
  future real-schema definition can share that single source.
- **The 1b → required flip is RBT-15's** (substrate §9, M-3). RBT-33 leaves the
  1b contracts `xfail`-non-blocking; RBT-15 implements the `GraphGateway` seam,
  un-marks the `xfail`s, and makes the job a required green status check. Do not
  un-skip them here.
- **Constants are fresh-fetched from committed DDR-002 v1.3.0** (RBT-48 refresh;
  RBT-33 built against v1.0.0), pinned by the authority sha256 in
  `schema_constants.py`'s header — not from the substrate's representative Cypher
  sketches (which are illustrative only). Re-fetch and re-verify the pin before any
  future refresh (F4 currency discipline).
