# File: docs/sdd/SDD-NNN-{{service-slug}}.md
# Author: {{AUTHOR_NAME}} — {{AUTHOR_ROLE}}, {{ORGANIZATION}}
# Created: YYYY-MM-DD
# Description: SDD-NNN — {{service-name}} design. {{One sentence stating what the service does and what makes its design distinctive.}}

# {{service_name}} — Service Design Document

| Field | Value |
|---|---|
| **Document ID** | SDD-NNN |
| **Service** | `{{service_name}}` |
| **Version** | 0.1.0 |
| **Status** | PROPOSED |
| **Date** | YYYY-MM-DD |
| **Authors** | {{Author Name}} ({{roles}}) |
| **Supersedes** | {{None — new service. OR: prior-service-name (retired). OR: SDD-NNN v{{X.Y.Z}}}} |
| **References** | {{upstream ADR-NNN / DDR-NNN this service implements}} |

<!-- An SDD records how one service is built. Before authoring, identify the upstream
     ADRs/DDRs it implements and confirm they're ACCEPTED (not PROPOSED) — designing against a
     moving principle produces rework. Include only the sections this service needs; delete the
     migration sections for a greenfield service. -->

---

## 1. Purpose

What the service does, in two or three sentences — specific about what makes it distinct from other services. Then enumerate the responsibilities it is the **sole** authority for ("{{service}} is the sole service authorised to: …"); shared responsibilities are a design smell worth resolving first. Close with what the service explicitly does **not** do — this sentence is load-bearing for future boundary enforcement.

## 2. What Changes from {{prior-service}}

*Migration only — delete for a greenfield service.* A comparison table, one discrete factual statement per row (primary store, status model, data classification, port, etc.). Skip "same" rows; include only where the change matters.

## 3. Responsibilities

- **3.1 Owned** — the specific responsibilities this service owns, concrete enough that a reviewer can answer "is this code in the right service?" from the list.
- **3.2 Not owned** — what it explicitly doesn't do, and which service does. This is the boundary doc: a future PR proposing one of these must either argue the boundary is wrong or be rejected.

## 4. API Contract

- **4.1 Health and readiness** — `/healthz` and `/readyz` contracts; be specific about what readiness actually checks for *this* service.
- **4.2+ Domain operation groups** — per endpoint group: path + verb, request/response shape (link schema or inline if small), auth requirements, error semantics (what each 4xx/5xx means specifically), idempotency behavior.

## 5. Internal Architecture

- **5.1 Module structure** — the service's filesystem tree; annotate non-obvious choices.
- **5.2 Adapter pattern** — the port (what domain code depends on), the production adapter, the test double; ~10 lines each, link to source for the rest.
- **5.3 Pipeline / state machine** — if there's a significant internal workflow: stages, transitions, failure handling, where stage-state is persisted.
- **5.4 Secrets / 5.5 Config / 5.6 Readiness logic** — which secrets and how they're sourced/rotated; the config shape; the ordered readiness checks and what each failure does.

## 6. Data Flows

The principal flows, one subsection each, traced entry → persistence with side effects noted (events emitted, downstream calls, cache invalidations). Separate inbound and outbound.

## 7. Migration from {{prior-service}}

*Migration only — delete for greenfield.* Phasing, data-migration approach, rollback strategy, verification gates between phases, decommissioning timeline. A clean design with no migration plan is a paper design.

## 8. Testing Requirements

Service-specific test discipline *beyond* the platform default — integration against a real backend, contract tests for a particular sync, etc. Reference the platform testing standard rather than restating it; name the coverage threshold (or "platform default").

## 9. Upstream Compliance Checklist

For each upstream ADR/DDR this service implements, a row stating how this design conforms — or honest non-conformance with a tracking pointer. Cite the upstream requirement; don't reproduce its full text.

| Upstream | Requirement | This SDD's conformance |
|---|---|---|
| ADR-NNN §X | {{summary}} | {{how it conforms, or "not yet — tracked at {{ticket}}"}} |

## 10. Observability Contract

Structured log events (name, trigger, required fields, severity) · metrics (distinguish platform-default from service-specific) · trace propagation · retention if the service handles sensitive data. Reference the platform observability standard for the wire format rather than restating it.

## 11. Cross-References

Upstream ADRs/DDRs · sibling/superseded SDDs · engineering standards this depends on · the deliberation artifact that grounds it · the review of record (if any).

## 12. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | {{ticket}} | Initial draft |

<!-- Append new rows at the top. 0.X.0 for PROPOSED-phase revisions; 1.0.0 at first ACCEPTED. -->
