---
doctype: kg-seed
plane: Governance
load_order: 50
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Governance — Haffey Enterprises decision/audit ground truth

The decision/audit graph (immutable append-only; references, not records). Basis:
**`flat_base` (basis 2)**. Contents: an EA `Actor` + `Role`, a produced `Solution`
(Artifact family), and a mirrored SDLC `GateDecision` that approved it.

Provenance postures (per §2.4 entry-path rule):
- `Actor` / `Role` — `origin_mechanism: authored` (SOFIA-registered identities); **no
  `source_record_ref`**.
- `GateDecision` — `origin_mechanism: ingested` (mirrored external SDLC gate) + required
  `source_record_ref` (§7 #17); exactly one subtype label on the `Decision` (§7 #16).
- `Solution` (Artifact) — `origin_mechanism: authored`; carries `content_hash` (§7 #12).

`DECIDED_ON {outcome: approved}` on the Solution is the selection-constituting act (§5).

## Graph payload

```yaml
nodes:
  - labels: [Governance, Actor]
    properties:
      actor_id: ACT-001
      actor_type: human
      name: Haffey Enterprises Executive Architect
      origin_mechanism: authored
      recorded_at: "2026-07-14T00:00:00Z"

  - labels: [Governance, Role]
    properties:
      role_id: ROLE-001
      name: Executive Architect
      origin_mechanism: authored
      recorded_at: "2026-07-14T00:00:00Z"

  - labels: [Artifact, Solution]
    properties:
      artifact_id: SOL-001
      artifact_type: solution
      version: "1.0.0"
      lifecycle_state: approved
      content_hash: "sha256:PLACEHOLDER_recomputed_by_loader_over_snapshot"
      snapshot_ref: "firestore://he-solutions/SOL-001/1.0.0"
      target_environment: production
      created_at: "2026-07-10T00:00:00Z"
      origin_mechanism: authored
      recorded_at: "2026-07-14T00:00:00Z"

  - labels: [Governance, Decision, GateDecision]
    properties:
      decision_id: GATE-001
      gate: gate_2
      decided_at: "2026-07-12T00:00:00Z"
      approval_token_id: HE-APPROVAL-0001
      all_hard_constraints_passed: true
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_sdlc_gate, record_id: "HE-GATE-0001" }

edges:
  - type: HAS_ROLE
    from: { actor_id: ACT-001 }
    to: { role_id: ROLE-001 }
    properties: { effective_from: "2026-01-01T00:00:00Z" }

  - type: APPROVED
    from: { actor_id: ACT-001 }
    to: { decision_id: GATE-001 }
    properties: { role: "Executive Architect", approved_at: "2026-07-12T00:00:00Z" }

  - type: DECIDED_ON
    from: { decision_id: GATE-001 }
    to: { artifact_id: SOL-001 }
    properties: { outcome: approved }

  - type: REVIEWED
    from: { decision_id: GATE-001 }
    to: { artifact_id: SOL-001 }
    properties: { hash: "sha256:PLACEHOLDER_recomputed_by_loader_over_snapshot" }

  - type: USES
    from: { artifact_id: SOL-001 }
    to: { technology_id: TECH-001 }
    properties: {}

  - type: FOLLOWS
    from: { artifact_id: SOL-001 }
    to: { pattern_id: PAT-001 }
    properties: {}
```
