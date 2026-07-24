---
name: author-decision-record
description: Author — or decide whether to author — an Architecture Decision Record (ADR), Design Decision Record (DDR), or Service Design Document (SDD). Routes to the right doctype, supplies its template, enforces the pre-authoring deliberation gate that keeps rationale from being fabricated, and gives the placement, naming, and metadata conventions — plus the body-integrity discipline that keeps a record honest over its life (contract-only prose, pointer-not-mirror, verified citations, earned tense). Use this whenever starting a decision record, capturing an architecture or design decision, writing up why a technical choice was made, documenting a service's design, or asking which decision-record type fits — even when the request is just "write up this decision" or "document this architecture choice" without naming a doctype. Also fires when amending, cleaning up, or de-drifting an existing record.
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
- **Under an empirical floor, fix the form and hold the constants.** A record written before real data exists can still fix a design's *form* — defensible from first principles, testable without data — while explicitly holding its *constants* as contested and unvalidated. Say in the document which is which. Pretending to calibrate at n=0 is the failure mode; separating what design authority settles now from what only traffic settles later is the fix.

## Body integrity (what keeps the record honest)

The body carries the contract and only the contract. Everything else has a dated container built for it.

- **No storytelling in the body.** Process narrative, review history, deliberation prose, and forward-speculation live in the Change Log, Cross-References, the conditions apparatus, or your tracker — never threaded through contract sections. Provenance language decays in body text: a lineage sentence that's load-bearing today is noise in three months. The test for any body sentence: *would a stranger reading this in a year need it — or just need to not be confused by it?* And know your tooling's limit: contract-purity is a **semantic** property, and any validator enforces a **syntactic** proxy — a green check clears the regex, never the convention. The gap between them is owned by review.
- **Point, don't mirror.** When the record needs an authority's enumerated content — a vocabulary, a taxonomy, a mapping owned elsewhere — point to the authority; don't restate it inline. An inline restatement is a standing drift surface: it goes stale the next time the authority moves, and "fixing" it by re-copying just re-plants it.
- **Ticket identifiers have exactly three sanctioned homes:** the Change Log, the conditions apparatus (pre-acceptance / migration conditions), and explicit TODO gap-markers. Contract prose never carries them. A forward reference in the body is subject-named only — genus plus what's unsettled — and the navigability lives in the opposite direction: the ticket's definition-of-done carries the obligation to come back and resolve the document's pointer. The record stays standalone-buildable; the administrative layer references the canonical layer, never the reverse.
- **Tense is earned by enforcement.** A property whose enforcing mechanism is forthcoming is stated in the conditional — "holds once Condition N lands" — with the conditions apparatus carrying the present truth. Present-voice claims about future enforcement read as false statements to every reviewer, and they cost whole finding families; nothing needs to be hidden, only phrased in the tense the facts support.
- **Status claims are earned by the trail.** "Reviewed," "ratified," "enforced," "built" — assert these only when the trail substantiates them. A posture claim the repo has overtaken (or hasn't caught up to) makes every reader and reviewer faithfully report a world that doesn't exist. Review-proposed-and-folded is not operator-ratified; keep the provenance distinct.
- **Section citations are facts — fetch-verify them.** A "§2.3" typed from memory is a distinct error class: the substance right, the pointer off — and it survives review because reviewers verify the claim, not the address. Treat every §-cite as a fetch-verified fact at write time.
- **Remove, don't annotate, zero-load claims.** Annotation is the second-best tool, reserved for unreliable claims that must remain because something rests on them. Once a commitment is re-grounded on a verifiable present dependency, the historical justification is deletable, not flag-able.

## The cold read (before a record is promoted)

Before promoting past PROPOSED, run the stranger test as an actual pass/fail gate, not a sentiment: *a reader with no access to your tracker, your chat history, or your memory of intent can build from this record.* Read the record cold — fresh eyes, the artifact set as the only authority. The two failure signatures to hunt: a **dangling hinge** (a cross-reference that resolves to nothing in the artifact set) and an **unsupported normative claim** (a rule stated without the reasoning that justifies it). Expand every acronym at first use — an unexpanded acronym is an open invitation for any future consumer, human or model, to invent its meaning. A sentence that reads as diary in one document may be the load-bearing hinge another leans on; only the cold, cross-document read surfaces that.
