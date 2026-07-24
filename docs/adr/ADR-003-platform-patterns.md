# File: docs/adr/ADR-003-platform-patterns.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-20
# Description: ADR-003 — Platform Patterns. Commits the agentic orchestration model: work performed in orchestrated runs of specialized, reasoning-bearing agents that collaborate on any route, governed by invariants anchored to the graph rather than the topology, on a committed trajectory of decreasing coordination density at the orchestrator.

# ADR-003: Platform Patterns — Orchestrated Runs of Specialized Agents under Graph-Anchored Governance

| Field | Value |
|---|---|
| **Document ID** | ADR-003 |
| **Status** | ACCEPTED |
| **Version** | 1.0.0 |
| **Date** | 2026-07-20 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — establishes new platform principle |

---

## 1. Context

The platform's foundations are committed: the reasoning-capture invariant and the Position 5 → Position 4 trajectory (ADR-001), the graph as system of record with a sole-owner gateway and named write authority (ADR-002), human-accountable governance over every mutation of enterprise ground truth (ADR-008), and the data architecture and schema that realize them (DDR-001, DDR-002). One substrate service is fully designed (SDD-001). What no record yet states is the platform's **orchestration model**: how work is composed across the specialized agents the platform exists to coordinate, how those agents may interact, and what makes their interaction governable.

That absence is now load-bearing in two directions. Forward: the agent service designs — the orchestration engine and the solutioning agent at their head — cannot be authored without an orchestration model to design against. Backward: a prior platform cycle demonstrated the failure mode of answering this question wrongly. That cycle committed static structure at architecture altitude — a fixed hub-and-spoke call graph, enumerated message topics, named transport products, a frozen service roster — and those commitments accumulated inertia far past their evidential warrant, constraining later design work that had outgrown them. The lesson is not that orchestration decisions don't belong in an ADR; it is that an ADR must commit the *invariants* of orchestration and leave its *structure* free to evolve.

This Architecture Decision Record ends the indecision. It commits the orchestration model — orchestrated runs, specialized agents, graph-anchored governance, and a coordination trajectory — and deliberately defers the structural choices whose premature durability the prior cycle demonstrated.

---

## 2. Decision

**Work on the platform is performed in orchestrated runs composed by the Agent Orchestration Engine (AOE) over specialized, reasoning-bearing agents that collaborate on any route — under governance anchored to the graph rather than the topology, with coordination density at the orchestrator on a committed decreasing trajectory as the platform learns.**

### 2.1 Orchestrated runs

The unit of platform work is the **orchestrated run**: the AOE composes a loop of specialized agents over a shared, mediated substrate to produce a solution outcome. Run composition is **non-deterministic by design** — every solution defined and delivered through the platform differs, and the run is composed for the work at hand, not instantiated from a fixed process template. The platform is explicitly not deterministic process automation.

Runs are **multi-origin**: a run may be initiated by a human brief (through a platform surface, §2.6), by schedule, or by an agent-observed signal. Whatever the origin, the run is a first-class recorded object — a run corresponds to a `ReasoningSession`, whose lifecycle the AOE owns (ADR-002 §2.6).

### 2.2 Specialized agents and collaboration

**Specialized agents are the platform's units of work.** Agents collaborate semantically within runs — one agent's output is another's input, agents consult one another mid-work, and an agent's observation may initiate work for another. **Agent-to-agent communication is a first-class platform capability: no platform design may preclude it, and no architectural mechanism may exist whose function depends on preventing it.** Direct interaction between agents is permitted on the same terms as orchestrator-mediated interaction, because the invariants that make interaction governable (§2.3) are independent of its route.

### 2.3 Governance anchors to the graph, not the topology

An agent interaction is governable on **any** route because the platform's controls are **route-agnostic invariants**, all committed upstream and cited here:

- **Capture** — reasoning produced in any interaction is captured to the Reasoning Graph with source attribution and evidence linkage (ADR-001 §2.2), whoever initiated the interaction.
- **Constraint-binding** — enterprise constraints bind the agent from the Knowledge Graph (§2.4), regardless of who invoked it.
- **Graph access** — every read or write of graph state routes through the sole-owner gateway under named write authority (ADR-002 §2.5, §2.6); no interaction route creates a second path to the graph.
- **Checkpoint gates** — human-accountable controls (the ADR-008 family) anchor to **authoritative-state transitions**: checkpoints in the run and the graph, not positions in a call graph. Because every authoritative transition executes at the sole-owner gateway (ADR-002 §2.1, §2.5), no routing choice can carry a gated state transition past its gate; an interaction that touches no authoritative state passes no gate — nothing of record occurred, and its reasoning-bearing outcome still enters the record through capture.

Because these invariants hold identically on every route, the routing topology carries no governance load — which is precisely what frees it to evolve (§2.7).

### 2.4 Constraints from the graph

For work performed through the platform, enterprise constraints — standards, directives, policy — **bind agents from the Knowledge Graph** once the Standards-plane ingestion path lands (§5.3): they are graph-resident (the Standards plane, DDR-001), consulted through the sole-owner gateway, **version-pinned at consultation** (an agent's conformance traces to the constraint version it actually read, per DDR-001's version-pinning model), and **evidence-linked in the Reasoning Graph** (a conformance claim is traversable to the constraint nodes consulted). Constraint binding is **invocation-agnostic**: the same constraints bind an agent whether a human brief, a schedule, another agent, or the orchestrator invoked it. Constraint *evaluation* is deterministic encoded reasoning (ADR-001 §2.3) — the model renders; it does not decide what complies.

The discriminating rule is testable: **if it binds, it is in the graph; if it is only in a prompt, it does not bind.** Prompt-carried material — briefs, task context, working substrate — is legitimate working input and is not constraint. This section commits the binding pattern only: the constraint schema and vocabulary are the graph schema's (DDR-002), predicate-evaluation semantics are routed to the forthcoming constraint-validator service design (per DDR-002 §3's obligation-closure assignment; SDD-001 §4.2 names the constraint-validator design as the single source of predicate-evaluation semantics), and which constraints exist is corpus content, not architecture.

### 2.5 Run anatomy

Four properties hold for every run, at every composition level (§2.6):

1. **Durable record.** Every run leaves a durable, traversable record — the platform run's `ReasoningSession` and its captured reasoning (ADR-001 §2.2; ADR-002 §2.6); a sub-run's record is carried within its enclosing run's session (§2.6). No run is unrecorded.
2. **Human-accountable gates.** Corporate checkpoints — approval, review, ground-truth mutation — are discharged by the human-accountable controls committed in the ADR-008 family, surfaced to humans through platform surfaces (§2.6), and are route-agnostic per §2.3.
3. **Versioned substrate.** Agents work against version-pinned substrate — the context an agent consulted is resolvable as it stood at consultation time (DDR-001's version-pinning and temporal model).
4. **Isolation is expressible.** An agent's stance may be deliberately isolated from other agents' outputs where the work benefits — adversarial review being the proven case — and orchestration must keep isolation expressible: no orchestration design may assume that all agents in a run share full context.

**Non-convergence is an honest outcome.** A run that halts with open decisions surfaced to a human is a product, not a failure. Accumulated tuning, data, and incorporated learning raise the likelihood of convergence over time, but each new technology, pattern, data source, or solution reintroduces variability no tuning forecloses — non-convergence is the signal of that variability, and a platform that treats the halt as failure will suppress its own signal.

### 2.6 Component taxonomy

Platform components fall into four classes, discriminated by **what they author** — the platform's existing authorship discipline (ADR-001 §2.2; ADR-002 §2.6) applied as taxonomy:

- **The orchestrator** — the AOE: composes and coordinates runs and owns run lifecycle (ADR-002 §2.6).
- **Specialized agents** — reasoning-bearing components. The test for agenthood: the component makes judgments, and those judgments are captured to the Reasoning Graph as attributed reasoning (source category *specialized agent*, ADR-001 §2.2). The Architecture Solutioning Agent (ASA) is the canon-named instance.
- **Substrate services** — components that execute, enforce, store, or mediate without authoring. The knowledge-service gateway is the canonical instance (sole executor of graph writes, author of none).
- **Surfaces** — where humans brief, ratify, and observe: the voice-first orchestration surface, review surfaces, portals. Surface experience design is owned outside this record (§7).

**What earns a new agent** is a distinct specialization with its own named reasoning authority. **Adding an agent is additive**: it is wired into orchestration and its authority named; no peer agent changes. **This record enumerates no agent roster** — the roster is a consequence of the platform's design work, owned by the service-design layer, and listing it here would recreate the frozen-roster failure this record exists to avoid. Components are named above only where existing canon already names them.

**Composition is recursive.** A specialized agent may discharge its specialization by composing sub-agents — the orchestration model applied at smaller scope, with the composing agent orchestrating its sub-run. A sub-run is a run: the §2.5 anatomy invariants apply at every level, and a sub-run's durable record is carried **within its enclosing platform run's `ReasoningSession`**, whose lifecycle remains the AOE's (ADR-002 §2.6) — unchanged by this clause. Attribution is preserved at depth — every reasoning sub-agent's judgment is captured attributed to that sub-agent, inside the enclosing session — while the **output of record belongs to the composing agent**, which is the named, answerable author of the result (ADR-002 §2.6). Accountability concentrates; provenance stays fully deep. A first-class sub-session shape, should composition depth ever warrant one, is a named trajectory item arriving under §2.7's amendment rule — not committed here. No registration, permission, or depth machinery governs sub-agent composition; the standing invariants are the control.

Whether the orchestrator's own composition decisions constitute captured reasoning, and in what shape, is specified in the forthcoming agent-orchestration-engine service design — routed, not ruled here.

### 2.7 Coordination trajectory

The platform commits a **coordination trajectory**, in the same regime-plus-trajectory form as ADR-001 §2.1: the **operating regime** is AOE-coordinated — the orchestrator composes runs and mediates most inter-agent interaction — and the **committed trajectory** is toward increasing direct agent-to-agent interaction as the platform, and its operators, accumulate learning. The governance invariants (§2.3) hold identically at every point on the trajectory; what decreases is coordination density at the orchestrator, not governability.

The trajectory advances **through** the upstream authority structure, never around it: where the far end of the trajectory would widen a coordination authority that upstream canon assigns — for example, run-lifecycle authorship beyond the AOE (ADR-002 §2.6) — that widening arrives as a named, additive authority assignment under the owning record's own amendment process. This record acknowledges those future widenings as trajectory items and neither blocks nor pre-empts them. As with ADR-001's Position 4, the trajectory's far end is directional, not scheduled.

### 2.8 Deliberate deferrals

The following are **deferred by decision**, each with its resolution locus, so that structure follows evidence rather than preceding it:

- **Transport and protocol** for any given interaction (synchronous call, message bus, in-process, agent protocol) — decided per interaction at the service-design layer, against real dispatch needs.
- **Bus or messaging product** — no platform-wide commitment; a design that needs one selects and records it at its own layer, and a platform-wide commitment, if ever warranted, is an amendment to this record.
- **Static call-graph** — no enumeration of who-may-call-whom exists at platform level, and no downstream design may commit one as platform structure.
- **Direct-route permission machinery** — opening a direct agent-to-agent route requires no ratification act; the §2.3 invariants are the entire control. Permission machinery is added only on demonstrated harm, as an amendment here.

### 2.9 Boundary — what this ADR does not rule

Deployment runtime is ADR-002 §2.2's. Graph access and write authority are ADR-002 §2.5/§2.6's. Ground-truth mutation governance and its policy are ADR-008's and DDR-003's; gates in runs instantiate those controls and never re-author them. Data architecture and schema are DDR-001's and DDR-002's. Port/adapter code conventions — layout, naming, test doubles — are the house application-code standard's; this record commits only the principle that every external seam is a substitutable port (the substitution seams DDR-001's port-substitutability and SDD-001 §4.2 already realize). Per-stage capture mechanics and probabilistic-output burdens are ADR-001 §2.3/§2.4's, discharged per agent design. Surface experience design is owned by its own design authority (§7). Which agents exist is the service-design layer's.

---

## 3. Rationale

Once this decision lands, the platform can compose work the way the work actually arrives — differently every time — without choosing between governability and freedom of interaction. The load-bearing move is §2.3: because capture, constraint-binding, gateway access, and gates anchor to the graph substrate, they hold on every route an interaction could take, so the platform gets auditability and accountability as structural properties *of the substrate* rather than as side effects of a routing diagram. That is what makes §2.2's non-preclusion commitment safe, and it is the same architectural instinct as ADR-001's capture invariant: fix what must always be true, and leave who-does-what-when free to evolve.

The trajectory form is chosen over both binary alternatives for the same reason ADR-001 §2.1 chose it. A permanent everything-through-the-orchestrator regime re-creates the structural inertia the prior cycle demonstrated, and hard-commits a bottleneck the platform is expected to outgrow. Unmediated peer choreography from day one commits past the evidence — the orchestrated-loop model is proven in one domain, and its platform runtime has not yet run. The regime-plus-trajectory synthesis states honestly where the platform operates now, commits the direction, and lets accumulated learning — not assertion — move the boundary. Committing invariants at this altitude and deferring structure (§2.8) is the anti-inertia discipline applied to this record itself: the decisions here are the ones that should be hard to change; everything else is left where evidence can still reach it.

---

## 4. Alternatives Considered

### 4.1 Alternative A — Hub-and-spoke with prohibited agent-to-agent communication

*Description:* A single orchestrator hub initiates all work and mediates all inter-agent flow; direct agent-to-agent communication is architecturally prohibited; the call graph and its transport classifications are enumerated at platform level. This is the prior platform cycle's committed pattern.

*Rejection rationale:* The prohibition conflates two different rules. As a transport-era control it was rational: when governance lives in the topology, the hub is the only place to put it, so every hand-off must pass through the hub or governance leaks. But this platform's governance no longer lives in the topology — it anchors to the graph (§2.3) — so the prohibition's protective function is discharged by route-agnostic invariants, and what remains of it is pure cost: real collaboration shapes (an agent routing an observed signal to a peer; an agent consulting a peer mid-work) become architecturally inexpressible, and the enumerated structure accumulates inertia past its evidential warrant, which is the prior cycle's demonstrated failure. The one durable clause of the prior pattern — adding an agent must not modify its peers — survives in generalized form as §2.6's additive-extensibility rule.

### 4.2 Alternative B — Unmediated peer choreography from day one

*Description:* No orchestrator; agents discover and invoke one another freely; runs are emergent from peer interaction rather than composed.

*Rejection rationale:* This commits past the evidence in exactly the direction the trajectory device exists to avoid. The platform's empirical base for multi-agent work is orchestrated: composed loops with mediated hand-offs and mechanical gates, proven in one domain. Emergent choreography has no platform evidence, and it surrenders the composition point where non-deterministic runs are assembled, observed, and honestly halted (§2.5) — with no orchestrator, there is no locus for the honest-halt surface, and session state disperses across peers where no single durable record naturally forms. The trajectory (§2.7) preserves this alternative's insight — coordination density should fall over time — without adopting its timing.

### 4.3 Alternative C — Transport-carried directive propagation

*Description:* Constraints and directives travel with the work: an LLM-facing ordered directive list paired with a checksummed, immutable transport envelope, a bridge layer translating between them, canonical key ordering, replay protection, and correlation-chain preservation across agent hops. This is the prior platform cycle's directive-bridge pattern, re-evaluated here as the propagation alternative to §2.4.

*Rejection rationale:* Every mechanism in the pattern — checksums, envelope immutability, deterministic key ordering, replay caches — is integrity machinery compensating for constraint authority *residing in the transport*. When directives are payload, every hop is a corruption surface, and the machinery is how you cope. Under §2.4 the authority relocates to the graph: an agent does not receive its constraints from its caller at all; it reads them, version-pinned, from the system of record through the sole-owner gateway. There is no envelope to protect because there is no envelope. The pattern's genuine residues route to their owning layers: run-identity and correlation propagation to the orchestration and observability designs; rendering graph-fetched constraints into model calls to each agent's design under ADR-001 §2.3; surfaced-constraint audit to §2.4's evidence linkage.

### 4.4 Alternative D — Commit the transport and bus at platform level now

*Description:* Fix the inter-agent transport (a managed publish/subscribe bus for asynchronous flow, synchronous HTTP for request-response) as a platform commitment in this record, as the prior cycle's platform-patterns record did.

*Rejection rationale:* No present design fact discriminates among transports — the agent designs that would exercise them are unauthored, and the one built service is a synchronous gateway whose transport needs are settled at its own layer. A platform-level transport commitment made now would be made on zero platform traffic, and it is precisely the class of structural commitment whose premature durability the prior cycle demonstrated: cheap to write down, expensive to walk back once services encode it. Deferral is not indecision here; §2.8 names each deferred choice's resolution locus, and a genuine platform-wide transport need, should one emerge, is an explicit amendment trigger rather than a silent accretion.

---

## 5. Consequences

### 5.1 Positive Consequences

- **The agent service designs are unblocked** — the orchestration-engine and solutioning-agent designs, and the further agent and substrate designs behind them, have a committed orchestration model to design against.
- **Route freedom without governance loss.** Agent collaboration shapes — signal routing, mid-work consults, sub-team composition — are expressible from day one, governed by standing invariants rather than topology.
- **Anti-inertia by construction.** The structural choices most likely to be invalidated by learning (transport, call-graph, roster) are deferred with named resolution loci, so evolving them never requires amending a platform principle.
- **Scale-free composition.** One model covers the platform run, the agent-composed sub-run, and future depths — with attribution preserved and accountability concentrated at each composing agent.
- **The constraint pattern makes context application testable.** "If it binds, it is in the graph" gives design review a mechanical question where "applies enterprise context consistently" was previously aspirational prose.

### 5.2 Constraints Imposed

- **No design may preclude agent-to-agent communication** or introduce a mechanism whose function depends on preventing it (§2.2).
- **Binding constraints may not be prompt-carried or configuration-carried** — a design whose conformance depends on constraint material outside the graph is non-conforming (§2.4).
- **Every reasoning-bearing component pays the capture cost** — agenthood *is* captured, attributed reasoning; a component that reasons without capture is not a permissible component class (§2.6).
- **No downstream design may commit platform-level static structure** — call-graph enumerations, platform-wide transport, or roster freezes — absent this record's amendment (§2.8).
- **Orchestration designs must keep isolation expressible** — full-context sharing may be a run's choice, never an architectural assumption (§2.5).
- **Sub-agent composition carries the full anatomy** — a design that spawns sub-agents owes them the run invariants: record, gates, versioned substrate, expressible isolation (§2.6).

### 5.3 Risks

- **Empirical floor.** The orchestrated-loop model is proven in one domain (design-document review); no platform runtime run has occurred, and the constraint-binding and multi-origin-initiation patterns have zero traffic. *Mitigation:* this record commits form, not calibration; the first platform runs are the named evidence source, and the §2.8 deferrals keep the evidence-sensitive choices open until they arrive.
- **The trajectory never advances.** Coordination density at the orchestrator could remain total indefinitely, making the trajectory rhetorical — the coordination analogue of ADR-001 §5.3's stalled-encoding risk. *Signal:* direct-route use cases arriving and being routed through the orchestrator by habit rather than by need. *Mitigation:* the trajectory is reviewed against real interaction patterns as agent designs land; no machinery is added prospectively.
- **Constraints-from-graph is committed ahead of its enforcement.** The Standards plane has no ingestion path until the forthcoming file-driven ingestion decision record and its port land, and predicate evaluation awaits the forthcoming constraint-validator service design — until then, §2.4 is enforceable only at design review. *Mitigation:* stated in earned tense here; the enforcement trail is those two records' and follows the platform's aspirational-until-mechanized compliance posture (ADR-002 §6).
- **The orchestrator concentrates operational criticality** during the operating regime — a run cannot start without it. *Mitigation:* this is a deployment-scaling concern at the service layer (the orchestrator holds no authoritative state locally, ADR-002 §5.2, so it scales as a stateless coordinator), and the trajectory reduces the concentration over time.

---

## 6. Compliance

Conformance with this ADR is verified at three-hat (LAA / SA / EA — Lead Application Architect / Solution Architect / Enterprise Architect) architecture review. The following are checked for every new SDD (Service Design Document) and DDR (Design Decision Record), and at each design pass touching orchestration, agent interaction, or constraint consumption:

1. **Orchestration-model check.** The design states how its work participates in orchestrated runs — origin, composition, and the durable run record (§2.1, §2.5).
2. **Route-agnostic governance check.** Every inter-agent interaction the design introduces satisfies the four §2.3 invariants identically on every route it can take; a design whose governance depends on a specific routing is flagged.
3. **Constraint-source check.** Everything that binds the design's agents traces to graph-resident constraints, version-pinned at consultation and evidence-linked; binding material found only in prompts or configuration is flagged (§2.4).
4. **Taxonomy check.** Each component the design introduces is classed by the authorship discriminator (§2.6); reasoning-bearing components carry named authority and capture; agent additions are additive with no peer modification.
5. **Recursion check.** Designs composing sub-agents apply the run anatomy at depth, preserve attribution, and name the composing agent as author of the output of record (§2.5, §2.6).
6. **Deferral-respect check.** The design commits no platform-level transport, bus, call-graph, or roster structure; per-interaction transport choices are recorded at the design's own layer (§2.8).
7. **Trajectory check.** A design widening coordination authority routes the widening through the owning upstream record's amendment process as a named additive assignment; silent pre-emption is flagged (§2.7).

**Enforcement.** These checks are enforced at three-hat review at design time — platform-development governance over the platform's own design work. No mechanized enforcement of this record's checks exists yet; conformance is review-verified until the relevant enforcement surfaces land with the designs named in §2.4 and §2.6, consistent with the platform's aspirational-until-mechanized posture (ADR-002 §6).

---

## 7. Cross-References

- **ADR-001 (Reasoning Architecture)** — the capture invariant (§2.2) and renderer discipline (§2.3) this record's governance anchoring cites; the regime-plus-trajectory device (§2.1) this record's coordination trajectory reuses.
- **ADR-002 (Graph as System of Record)** — sole-owner gateway (§2.5) and the write-authority general principle with the AOE/ASA assignments (§2.6) that this record's taxonomy and trajectory build on and never pre-empt.
- **ADR-008 (Ground-Truth Mutation Governance)** — the human-accountable control family that run gates instantiate.
- **DDR-001 (Data Architecture)** — the Standards plane, the version-pinning and temporal model, the graph-gateway pattern, and the port-substitutability seam cited throughout.
- **DDR-002 (Graph Schema)** — the schema authority for constraint vocabulary and the reasoning-capture label set.
- **DDR-003 (Feedback Loop Governance)** — governance policy for the promotion path; the routing of the Condition predicate vocabulary (the predicate grammar for scope conditions) onward to the constraint-validator service design.
- **SDD-001 (knowledge-service)** — the built substrate-service instance: sole executor authoring nothing (§1), the obligation-context retrieval surface this record's constraint pattern rides (§3.3), the port seam (§4.2).
- **The file-driven ingestion decision record** (forthcoming, unauthored) — the Standards-plane entry path on which §2.4's enforcement stages depend.
- **Forthcoming service designs** (all forthcoming, unauthored) — agent-orchestration-engine (run composition, orchestrator capture shape, correlation propagation), architecture-solutioning-agent, ai-gateway-service, constraint-validator (predicate-evaluation semantics), each implementing this record and checked against §6.
- **The voice-first orchestration experience design (HEX repository)** — the binding design authority for the surface class (§2.6); experience intent, cited not ruled.
- **The design-review agent-loop construct** (`agent-loop/`) — the orchestrated-loop model's empirical grounding: composed multi-agent loops with mediated hand-offs, stance isolation, mechanical gates, and honest halts, proven across its run corpus in the document-review domain.
- **Deliberation substrate** — the pre-authoring deliberation record (`agent-loop/deliberation/adr-003-platform-patterns/record.md`; eight items ratified per item, 2026-07-20).

---

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.0.0 | 2026-07-20 | RBT-9 | **PROPOSED → ACCEPTED.** Acceptance on the reviewed-and-ratified basis: one design-review-loop draw (run-034 — oscillation halt at pass 3; 64 findings coalesced to a 7-decision docket, ratified per item 2026-07-20) plus the authoring-session three-hat self-review. Mechanical CONVERGED was not a gate per the dense-record doctrine, and run-034 sharpened that doctrine: the distinct-decision space exhausted by pass 2 (pass 3 added zero new decision loci) even as the finding stream did not. Review of record: `agent-loop/runs/run-034-adr-003-rbt9/` (folder + cold audit) + `agent-loop/deliberation/adr-003-platform-patterns/run-034-docket-rulings.md`. Status promotion; no decision change beyond the 0.2.0 rulings. |
| 0.2.0 | 2026-07-20 | RBT-9 | **Review-driven revision from run-034** (docket rulings D1–D7 ratified per item 2026-07-20; incorporates the run author's conformed closes). D1: §2.2's absolute mechanism clause ratified as a deliberate commitment (no text change; provenance cured by ruling). D2: §2.3's gate invariant derived rather than asserted — unbypassability grounded on the sole-path property (ADR-002 §2.1/§2.5); "no routing choice can bypass a gate" rephrased to the state-transition form. D3: §2.4 predicate-routing re-grounded (DDR-002 §3 obligation-closure; SDD-001 §4.2 single-source designation) and §7's DDR-003 entry aligned to its actual Condition-vocabulary routing. D4: model-access-gateway instance dropped from §1/§2.6/§5.1 — the canon-named-only rule enforced against this record itself; ai-gateway-service remains a forthcoming §7 design decided by its own SDD. D5: recursion clause qualified — a sub-run's record is carried within the enclosing platform run's AOE-owned `ReasoningSession` (attribution at depth inside it); a first-class sub-session shape is a named §2.7 trajectory item; §2.5 property 1 phrasing aligned. D6: orchestrator-capture routing stated plainly (borrowed ADR-001 §2.4 citation struck in §2.6 and §7). D7: §7 forthcoming-dependency status markers applied per corpus convention. Rider: §2.4 lead gains the earned-tense qualifier (run-034 conformed close). |
| 0.1.0 | 2026-07-20 | RBT-9 | Initial draft. Authored from the RBT-9 pre-authoring deliberation (eight items ratified per item, 2026-07-20): doctype and number; the orchestration model (orchestrated runs, agents-as-units with non-precluded agent-to-agent collaboration, graph-anchored governance, coordination trajectory); run anatomy incl. expressible isolation and the honest-halt posture; constraints-from-graph; the four-class component taxonomy with recursive composition; the non-ruling boundary; the directives-bridge fold (transport-carried propagation rejected as Alternative C, superseding the prior-cycle bridge intent); deliberate deferrals with named loci. PROPOSED pending three-hat design-review-loop. |
