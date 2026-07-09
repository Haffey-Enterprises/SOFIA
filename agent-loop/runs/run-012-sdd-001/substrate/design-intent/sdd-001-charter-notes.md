# SDD-001 — Charter Notes (design-intent substrate, run-008)

> Extracted from the triage-001 record (`agent-loop/triage/triage-001-distilled-set/record.md`, §Item-4 / §T-15 / §T-17 / §T-27) and the Notion roadmap entry. Authored for this run at claude.ai prep, 2026-07-03. The record is authoritative; this is the reviewer-facing distillation.

SDD-001 designs the **knowledge-service**: the sole-owner KG/RG graph gateway — the only holder of the Neo4j driver, sole executor of all graph writes as invariant-enforcing transactional operations, and the sole read boundary enforcing the platform's read-discipline controls.

**Charter commitments the design must satisfy (ratified at triage-001):**

1. **Write-authority principle (ADR-002 v1.1.0, §T-09):** every authoritative graph write has a named, component-scoped author; the gateway is the sole *executor* and enforcement boundary and is **never itself the authoring authority**; for EA-gated materializations, authority rests with the approving decision.
2. **Builds against DDR-002 v1.2.0's safety-critical-tier contract.** The gateway must not operate against an unenforced safety-critical tier (§T-15 — a conformance requirement, not a work-ordering rule).
3. **Gateway-behavioral conformance contracts flip to required at this service's build** (the harness's own rule; flip reserved to RBT-15): the built 1b set (#7, #9, #13, #14, #19) plus the triage additions — #22 conditional-scope carry-forward on supersession, #23 authoritative-flag↔reasoner-category consistency, #25 proposal_kind↔RETRACTS sync, and #15's per-candidate strict `decided_at` monotonicity companions (§T-13/T-17/T-27/T-28).
4. **Read discipline is now structurally implementable (§T-17):** `ReasoningProgress.authoritative` (indexed T2) is the ADR-001 §5.2 bypass filter surface; the gateway's read paths enforce it.
5. **Gateway-enforced write invariants introduced at triage:** per-candidate strict `decided_at` monotonicity on `DECIDED_ON` (§T-27); the provenance-survival closure computed in the materialization transaction (§T-20); no-PHI classification co-located with the sole write path — zero pre-enforcement exposure at graph entry (§T-18).
6. **Routed to adjacent SDDs, not this one:** Actor/Role provenance sourcing (governance-state-manager) — though it touches this gateway's surface; conditionally-approved-Solution lifecycle semantics; the carry-forward *implementation* detail is this SDD's to specify (§T-13).

**Gate status:** cleared 2026-07-03 — triage-001 doc-fix PR #8 merged (`c935c68`); the corpus this SDD cites is the amended one (ADR-001 v1.1.0, ADR-002 v1.1.0, DDR-001 v1.3.0, DDR-002 v1.2.0).
