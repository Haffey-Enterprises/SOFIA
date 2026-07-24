# File: docs/adr/ADR-NNN-{{slug}}.md
# Author: {{AUTHOR_NAME}} — {{AUTHOR_ROLE}}, {{ORGANIZATION}}
# Created: YYYY-MM-DD
# Description: ADR-NNN — {{short title}}. {{One sentence stating the architectural principle this ADR establishes.}}

# ADR-NNN: {{Title — usually a complete principle statement}}

| Field | Value |
|---|---|
| **Document ID** | ADR-NNN |
| **Status** | PROPOSED |
| **Version** | 0.1.0 |
| **Date** | YYYY-MM-DD |
| **Authors** | {{Author Name}} ({{roles}}) |
| **Supersedes** | {{None — new principle. OR: ADR-NNN v{{X.Y.Z}}}} |

<!-- An ADR records a platform principle: a commitment that holds regardless of which
     services exist. Before authoring, have real deliberation to draw on — if you'd be
     inventing the Rationale or Alternatives, stop and deliberate first. Include only the
     sub-decisions this ADR actually constrains; omit what doesn't apply rather than padding. -->

---

## 1. Context

State two things: the **current state** (what is true about the platform today, present-tense and concrete) and the **forcing function** (what makes deciding *now* necessary — a milestone, an inconsistency services are hitting, a deadline). Don't anticipate the rationale here. Close by naming the indecision this ADR ends.

## 2. Decision

State the decision in one sentence. If you can't, you haven't decided yet — think harder before continuing.

Then expand into testable sub-decisions as numbered subsections (`### 2.1`, `### 2.2`, …). Each should answer "did we conform or not?", in definitive voice. Include only sub-decisions this ADR constrains — common areas are approved stack, component/responsibility mapping, required metadata or audit fields, approval gates, sync/failure behavior, abstraction boundaries, data handling, observability — but use only those that apply.

## 3. Rationale

What becomes true after this decision lands — the affirmative case, in your own voice. Argue from the properties that matter: failure isolation, substitutability, cognitive load, operational scale, auditability. Two paragraphs is often enough; if you're writing five, you're restating §1 or pre-empting §4.

## 4. Alternatives Considered

What other shapes did you consider, and why reject each? One subsection per alternative (`### 4.1 Alternative A: …`). Describe each as its proponents would, *then* give a specific rejection rationale. Two to four is typical — one means it wasn't a real choice; ten means padding.

> If you don't have real deliberation to draw on here, write "TODO — alternatives evaluation pending, tracked at {{ticket}}" and leave the ADR in PROPOSED. A strawman is worse than a gap.

## 5. Consequences

- **5.1 Positive** — concrete capabilities or properties the platform gains (not aspirational benefits).
- **5.2 Constraints imposed** — what this decision prohibits or forecloses; future authors will hit these, so name them upfront.
- **5.3 Risks** — what could go wrong and what signal would say "revisit this." Pair concrete risks with a mitigation or a tracking item; don't claim a mitigation that doesn't exist.

## 6. Compliance

How conformance is verified — what makes this ADR enforceable rather than aspirational. If the mechanism isn't built yet (common for new ADRs), say so honestly and point at a tracking item:

> "Compliance is currently aspirational, tracked at {{ticket}}. Until enforcement lands, conformance is checked at design-review time."

Once built, name the specific mechanism (CI check + path, review checklist + location, runtime assertion + failure behavior).

## 7. Cross-References

Downstream DDRs/SDDs that implement this · sibling or superseded ADRs · engineering standards this depends on or amends · the deliberation artifact that grounds the decision · the review of record (if any). Point to these; don't replay them in the body.

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | {{ticket}} | Initial draft |

<!-- Append new rows at the top. 0.X.0 for PROPOSED-phase revisions; 1.0.0 at first ACCEPTED. -->
