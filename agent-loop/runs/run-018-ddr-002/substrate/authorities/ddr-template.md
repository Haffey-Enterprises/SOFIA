# File: docs/ddr/DDR-NNN-{{slug}}.md
# Author: {{AUTHOR_NAME}} — {{AUTHOR_ROLE}}, {{ORGANIZATION}}
# Created: YYYY-MM-DD
# Description: DDR-NNN — {{short title}}. {{One sentence stating the design ruling and the principle it implements.}}

# DDR-NNN — {{Title — usually a complete design statement}}

| Field | Value |
|---|---|
| **Document ID** | DDR-NNN |
| **Version** | 0.1.0 |
| **Status** | PROPOSED |
| **Date** | YYYY-MM-DD |
| **Authors** | {{Author Name}} ({{roles}}) |
| **Supersedes** | {{None — new ruling. OR: DDR-NNN v{{X.Y.Z}}}} |
| **References** | {{upstream ADR(s)/DDR(s) this implements}} |

<!-- A DDR records a specific design ruling — narrower than an ADR, deeper in technical
     detail. It needs either spike findings or a scoping output behind it; a DDR without
     empirical or deliberative grounding gets amended every time reality intrudes. DDRs are
     shape-flexible: include the substantive design sections this ruling needs, skip the rest.
     DDRs frequently land at ACCEPTED-WITH-CONDITIONS when prerequisite work must precede migration. -->

---

## Decision

State the ruling in one or two testable sentences — "did the design conform or not?", not aspirational. Then expand the ruling's components as numbered subsections if needed. Keep this section to *what* is decided; the *why* is below.

## Rationale

Why this design and not another. Two flavors:

- **Empirical-grounded** — reference the spike, summarize what it found, state the design implication ("the spike showed technology A can't register the schema due to X; the ruling adopts B").
- **Deliberation-grounded** — reference the scoping output, name the shapes considered, say why the chosen one won (less detail per shape than an ADR's alternatives — DDRs are more focused).

Two paragraphs is often enough.

## {{Substantive design sections — variable count and shape}}

This is where most of a DDR's content lives, and the shape varies by ruling. Use the sections the ruling actually needs:

- **Multi-store / multi-component contract** — if the ruling splits responsibility across stores or components, codify the split (often a table: concern × component).
- **Spike findings** — if the ruling rests on empirical results, record what was tested, what failed or succeeded, and what was learned, so a future reader understands the rejection without re-running the spike.
- **Gateway / boundary pattern** — if the ruling establishes a boundary, say which component owns it, what's exposed across it, what's prohibited.
- **Schema / data shape** — if the ruling is about data shape, document it (link schema files if they exist; inline if small).
- **Operational mechanics** — backup, restore, scaling, failure modes; DDRs that skip these generate downstream churn when operations turn out to be load-bearing.

Add or drop sections freely. Don't pad; don't omit substance.

## Pre-Acceptance / Migration Conditions

If the ruling is conditional — sound design, blocked on prerequisites — enumerate each condition as a discrete, buildable prerequisite with a tracking pointer. Conditions without tracking are wishes. If unconditional, replace this section with: **"No pre-acceptance conditions. Ruling stands as authored."**

## Migration Path

If the ruling supersedes a prior design: phasing, cutover strategy, data-migration mechanics, rollback strategy, decommissioning timeline. Delete this section if greenfield.

## Cross-References

Upstream ADRs this implements · sibling DDRs it coordinates with · SDDs that implement it · engineering standards it depends on or amends · the spike/scoping artifact that grounds it · the review of record (if any). Point to these; don't replay them.

## Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | {{ticket}} | Initial draft |

<!-- Append new rows at the top. 0.X.0 for PROPOSED-phase revisions; 1.0.0 at first ACCEPTED. -->
