---
name: author-decision-record
description: Author — or decide whether to author — an Architecture Decision Record (ADR), Design Decision Record (DDR), or Service Design Document (SDD). Routes to the right doctype, supplies its template, enforces the pre-authoring deliberation gate that keeps rationale from being fabricated, and gives the placement, naming, and metadata conventions. Use this whenever starting a decision record, capturing an architecture or design decision, writing up why a technical choice was made, documenting a service's design, or asking which decision-record type fits — even when the request is just "write up this decision" or "document this architecture choice" without naming a doctype.
---

# Author a Decision Record

Three doctypes capture decisions at three altitudes. This skill routes to the right one, supplies its template, and enforces the one discipline that determines whether the record is worth anything: real deliberation behind it.

## The deliberation gate (read before authoring anything)

A decision record's authority comes from the thinking behind it, not the template around it. **The template gives shape; it does not give substance.** Before authoring, you need deliberation substrate to draw on — a real comparison of options, an investigation, a spike, a scoping discussion, an operator conversation that weighed the trade-offs.

If you reach the section where the *why* goes — an ADR's Rationale and Alternatives, a DDR's Rationale, an SDD's Responsibilities — and find you'd be **inventing** it from a thin prompt, **stop.** Produce the deliberation first, or mark the section as an explicit TODO with a tracking pointer and leave the record in draft. Do not fabricate.

Fabricated rationale and strawman alternatives age worse than missing ones: a future reader who discovers them stops trusting the whole document, and if a later decision reverses the call, the strawman becomes the new decision and the rejection reads as foolish. Honest "TODO — alternatives pending, tracked at X" beats a confident invention every time.

Each doctype names the specific substrate it needs in its routing entry below. That substrate requirement is the gate.

## Which doctype

Pick by altitude. The discriminating tests:

- **ADR — a platform principle.** A commitment that constrains the architecture across services. *Test: if you deleted every service tomorrow and started over, would this still apply?* Yes → ADR. (e.g., "the graph is the system of record for all architecture state.")
- **DDR — a design ruling.** A specific data-shape, system-shape, or coordination decision, usually technology-specific. *Test: is this a technology-independent pattern (→ lean ADR) or a design specific to a chosen technology (→ DDR)? Does it constrain multiple services or the platform data model (→ DDR) or just one service's internals (→ SDD)?* (e.g., "the knowledge graph and reasoning graph share one database instance behind a gateway.")
- **SDD — a service design.** The concrete design of one service. *Test: would this design exist if you deleted this service? No → SDD.* (e.g., "knowledge-service module structure, API contract, data flows, migration path.")

**None of these?** Some decisions are too small for a record — a library choice inside one service, a config default, a retry-logic trade-off. If the decision clears none of the three bars above, it probably doesn't need a separate record at all; capture it in a code comment or the commit narrative instead. Don't reach for the nearest doctype just because this skill is open — over-documenting a small decision is its own failure mode.

When more than one *does* fit, author at the highest altitude the decision actually reaches, and let the lower-altitude records reference it.

## Routing

### ADR — `templates/adr-template.md`
- **Deliberation substrate required:** a real evaluation of alternatives — a scoping discussion with documented options, an investigation note with at least one rejected alternative and why, or a captured operator deliberation. An ADR with one alternative wasn't a real choice; go think harder.
- **Shape:** Context (current state + forcing function) → Decision (testable sub-decisions) → Rationale (the affirmative case) → Alternatives Considered → Consequences (gains / constraints / risks) → Compliance → Cross-References → Change Log.

### DDR — `templates/ddr-template.md`
- **Deliberation substrate required:** *either* a spike with empirical findings that motivate the ruling, *or* a scoping output documenting the design space and the chosen path. A DDR without empirical or deliberative grounding produces a ruling that gets amended every time reality intrudes.
- **Shape:** Decision → Rationale (empirical- or deliberation-grounded) → the substantive design sections the ruling needs (multi-store contract, spike findings, gateway/boundary pattern, schema, operational mechanics — variable) → Pre-Acceptance/Migration Conditions → Migration Path → Cross-References → Change Log.

### SDD — `templates/sdd-template.md`
- **Deliberation substrate required:** *all of* — (1) the upstream ADRs/DDRs this service implements, identified; (2) confirmation those are ACCEPTED, not still PROPOSED (designing against a moving principle produces rework); (3) either a working prior service to compare against, or a deliberation artifact establishing why this service exists as a separate concern.
- **Shape:** Purpose (sole-authority responsibilities) → What Changes from prior (if a migration) → Responsibilities (owned / not-owned) → API Contract → Internal Architecture → Data Flows → Migration (if any) → Testing Requirements → Upstream Compliance Checklist → Observability Contract → Cross-References → Change Log.

## Placement, naming, metadata

- **Location:** `docs/adr/`, `docs/ddr/`, `docs/sdd/` respectively.
- **Filename:** `ADR-NNN-kebab-slug.md` (prefix uppercase, number zero-padded to 3 digits, slug lowercase-kebab). Same form for `DDR-` and `SDD-`.
- **Number allocation:** next unused number in the target directory; verify uniqueness first. Numbers are never reused — a superseded record keeps its number, and the supersession is recorded in the superseding record's metadata.
- **File header + metadata table + Change Log** come pre-shaped in each template. Fill the header (`# File:` / `# Author:` / `# Created:` / `# Description:`) and the metadata table; append Change Log rows most-recent-first.

## Status and version

- **Status lifecycle:** `PROPOSED → ACCEPTED → SUPERSEDED`, with `REJECTED` and `DEFERRED` as terminal branches from PROPOSED. DDRs and SDDs also use `ACCEPTED-WITH-CONDITIONS` when the design is sound but blocked on prerequisites (the conditions are enumerated and tracked). Stay in PROPOSED until review clears blocking findings — don't promote to make a document "feel done."
- **Version:** `0.1.0` initial draft; `0.X.0` substantive revisions while PROPOSED; `1.0.0` first ACCEPTED; `1.X.0` material post-acceptance amendments; `2.0.0` breaking changes. Typo/format fixes within a drafting session don't bump.

## Authoring discipline (applies to all three)

- **Only include sections and sub-decisions the record actually constrains.** The template categories are illustrative, not a checklist. Omit what doesn't apply — don't write "N/A" filler. A focused 3-section record beats a padded 8-section one.
- **Be specific.** "Doesn't scale" is not a rejection rationale; "the per-record audit query exceeds 100ms p95 above 10M rows for lack of a secondary index" is. If a rejection is on preference grounds, say so honestly.
- **State decisions testably.** "Did this conform or not?" should have an answer. Definitive voice ("the platform uses X for Y"), not aspirational ("we recommend considering X").
- **Keep the record's body to the contract.** Process narrative, ticket IDs, and review history belong in the Change Log, Cross-References, or your tracker — not threaded through the body. A stranger with no access to your tracker should be able to build from the record.
