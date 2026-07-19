# File: docs/adr/ADR-004-provenance-invariant.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-17
# Description: ADR-004 — Provenance Invariant. Every knowledge-graph node carries an immutable provenance group, as a platform principle services conform to.

# ADR-004: Every Knowledge-Graph Node Carries an Immutable Provenance Group

| Field | Value |
|---|---|
| **Document ID** | ADR-004 |
| **Status** | DRAFT |
| **Version** | 0.1.0 |
| **Date** | 2026-07-17 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — new principle. |

---

## 1. Context

The knowledge graph (KG) is SOFIA's enterprise system of record, and DDR-002 fixes its schema. The schema layer already requires a provenance group on every KG node. As new services are built against the graph, they need that requirement stated once, at the platform-principle altitude, as a commitment they conform to rather than a schema detail they might overlook. This ADR states the invariant as a principle; it introduces no new schema.

## 2. Decision

**Every knowledge-graph node carries an immutable provenance group — `origin_mechanism` and `recorded_at` — written at node creation and never mutated thereafter.**

### 2.1 The provenance group is mandatory on every KG node

Every node in every KG plane carries `origin_mechanism` and `recorded_at`. This is the existence-constraint requirement fixed at DDR-002 §6; this ADR elevates it to a platform principle. No KG node is exempt.

### 2.2 Provenance is written at the sole write boundary

The provenance group is stamped by the graph gateway — the sole executor of graph writes per the write-authority principle at ADR-002 §2.4 — at node creation. No service writes to the graph outside the gateway, so no node can enter without provenance.

### 2.3 Provenance is immutable

Once written, the provenance group is never mutated; corrections are made by the schema's versioning and never-delete mechanisms, not by overwriting provenance in place.

## 3. Rationale

A provenance group on every node, stamped at the one write boundary and never mutated, is what makes the graph auditable: any fact can be traced to how it entered and when. Stating it as a platform principle means a new service conforms by construction rather than rediscovering the requirement. The graph store is Neo4j Community Edition, whose existence-constraint capability makes the mandatory-property guarantee enforceable at the database layer rather than by convention.

## 4. Alternatives Considered

### 4.1 Alternative A: No platform principle — leave it in the schema

Leave the provenance requirement solely in DDR-002 and trust each service to read the schema. This is obviously wrong and nobody would defend it — a requirement every service must honor should not be buried where a service can miss it.

### 4.2 Alternative B: Provenance stamped by each writing service

Let each service stamp its own provenance rather than the gateway. Its proponents would argue it keeps the gateway thin. Rejected because it multiplies the surface where a node could enter unstamped, and it contradicts the single-write-boundary posture the platform already commits.

## 5. Consequences

- **5.1 Positive** — every node is auditable to its origin; new services conform by construction; the database enforces the guarantee.
- **5.2 Constraints imposed** — no write path may bypass the gateway; no code may mutate a written provenance group.
- **5.3 Risks** — a service attempting a direct write fails closed at the gateway boundary; the signal to watch is rejected-write volume at the gateway.

## 6. Compliance

Compliance is currently aspirational, tracked at RBT-67 (design-review-loop execution). Until enforcement lands, conformance is checked at design-review time against this ADR.

## 7. Cross-References

- ADR-002 (write authority — the sole-writer gateway); DDR-002 (graph schema — the provenance existence constraint); DDR-001 (data architecture).
- No downstream records depend on this ADR yet.

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-17 | design-review-loop | Initial draft |
