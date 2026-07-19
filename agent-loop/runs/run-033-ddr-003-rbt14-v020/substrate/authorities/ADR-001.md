# File: docs/adr/ADR-001-reasoning-architecture.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-03
# Description: ADR-001 — Reasoning Architecture (SOFIA as Reasoner). Establishes SOFIA's reasoning-capture invariant and its Position 5 operating regime on a committed trajectory toward Position 4, binding the discipline across the enterprise SDLC.

# ADR-001: Reasoning Architecture — SOFIA as Reasoner

| Field | Value |
|---|---|
| **Document ID** | ADR-001 |
| **Status** | ACCEPTED |
| **Version** | 1.2.0 |
| **Date** | 2026-07-17 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — establishes new platform principle |

---

## 1. Context

**SOFIA — Semantic Orchestration for Intelligent Architecture / Applications** — is the reasoning-capture layer for the enterprise SDLC. Its durable value is not any single agent, service, or model. It is two things no off-the-shelf model can replicate: the **Knowledge Graph (KG)**, the enterprise's unified ground-truth context, and the **Reasoning Graph (RG)**, the platform's persistent institutional memory — every inference, its supporting evidence, and every rejected alternative recorded as a traversable asset. The platform's reason to exist is the consistent and automatic application of enterprise context at every lifecycle stage, with the reasoning behind every decision captured durably and queryably.

SOFIA is at initial design: no service is yet deployed and no per-phase design is yet accepted. This decision must be stated before the platform's data and service architecture are committed, because every one of those decisions depends on whether SOFIA reasons over the enterprise graph or merely wraps a model. That dependency is the forcing function. Absent an explicit reasoning-architecture commitment, the architecture drifts by default toward an LLM-wrapping pattern — prompt plus graph context plus standards, with the model doing the choosing (Position 1; see §4). In that pattern the reasoning is opaque, living transiently in model weights; the enterprise context is bounded by the prompt's token budget rather than by enterprise scale; reasoning quality varies with model version; and "why these choices were made in this enterprise's context" is lost because the model is choosing. That pattern is fast to build, and it is the specific regression this platform exists to prevent: any architect with model access reproduces it, and SOFIA's existence as a platform would be unjustified.

This Architecture Decision Record (ADR) ends that default. It states the reasoning-architecture commitment on which the platform's data and service architecture depend.

---

## 2. Decision

SOFIA is the reasoning-capture layer for the enterprise SDLC: whoever does the reasoning — encoded SOFIA logic, a specialized agent, an LLM, or a human — SOFIA captures that reasoning in the Reasoning Graph alongside the Knowledge Graph, operating at **Position 5** (hybrid reasoning within encoded boundaries) on a committed trajectory toward **Position 4** (SOFIA-as-reasoner, LLM-as-tool).

### 2.1 Position taxonomy and trajectory commitment

Two positions anchor the commitment (the full five-position taxonomy, including the two binary-commitment framings, is set out in §4):

- **Position 4 — SOFIA-as-Reasoner.** All architectural reasoning is encoded in SOFIA. The LLM is invoked only for narrow text-generation tasks — narrative, advisory, diagram rendering. Reasoning loops, decision-making, evidence weighing, and hypothesis generation are SOFIA-owned. This is the audacious end-state.
- **Position 5 — Hybrid with Reasoning-Capture Discipline.** SOFIA encodes deterministic reasoning where it can; the LLM produces probabilistic content where deterministic encoding is not yet feasible. All reasoning chains and rejected alternatives are captured in the RG with evidence linkage back to the KG, regardless of which reasoner produced them. This is the operating regime.

SOFIA commits to a **trajectory away from the Position-1 default toward Position 4, with Position 5 as the operating regime for the foreseeable future.** Position 4 may never be strictly reached in practice — Position 5 may deliver enough value that it is never strictly necessary — but it remains the north star that pulls every implementation decision toward more SOFIA-encoded reasoning over time. **The capture discipline is invariant; the encoding density grows.** This is a deliberate choice over a binary commitment: a binary Position 4 over-commits to encoding density that is impractical in some domains, while a binary Position 5 lets Position 1 reassert itself silently under the banner of "we said hybrid, so any model use is fine."

### 2.2 The reasoning-capture invariant

Whoever does the reasoning, SOFIA captures it:

- **Encoded SOFIA logic decides** → recorded as ReasoningProgress artifacts with evidence linkage to the KG nodes consulted; source category *encoded reasoning*, authoritative.
- **A specialized agent decides** → recorded as ReasoningProgress artifacts with evidence linkage to the KG nodes the agent consulted; source category *specialized agent* (attributed to the specific agent), authoritative.
- **An LLM generates probabilistic content** → recorded on the relevant SOFIA-authored artifact as content properties; source category *LLM advisory*, non-authoritative.
- **A human reviewer overrides** → recorded as approval-authored artifacts with override linkage to the artifact superseded; source category *human override*, authoritative.

The capture discipline is invariant across all reasoners. What varies is the **locus of reasoning** (encoded SOFIA logic, specialized agent, LLM, human) and the **authoritative flag**. Rejected alternatives are first-class: where a reasoner weighed and discarded an option, the discarded option is captured as a RejectedAlternative artifact, not silently dropped.

This ADR commits the *conceptual capture contract* — that each reasoner's output is recorded with evidence linkage, source attribution by category, and an authoritative flag, and that rejected alternatives are retained. It commits the **categories** of captured reasoning — conclusion, evidence, and rejected alternative (named above as ReasoningProgress, Evidence, RejectedAlternative); their canonical labels, property names, the source-attribution vocabulary, relationship types, and constraints are owned by and ratified in the Graph Schema document (DDR-002 §4), cited here rather than fixed. Structural containers (ReasoningSession), retention-mechanism nodes (ProvenanceSummary), and the produced-deliverable Artifact family are not part of this capture contract's category set — they take their authority from the data architecture (DDR-001) and its schema realization (DDR-002 §4–§5), not from this contract.

### 2.3 Deterministic / probabilistic output framing

SOFIA produces **deterministic outputs** from SOFIA-encoded reasoning over the enterprise context graph wherever deterministic encoding is feasible, and **probabilistic outputs** from LLM generation where deterministic encoding is not feasible — narrative architecture documents, advisory text for capability gaps, rendered diagrams, generated code. All reasoning, deterministic and probabilistic, is captured in the RG. The LLM does not select technologies, detect gaps, evaluate compliance, or make architectural decisions; those are SOFIA-encoded reasoning steps with auditable graph artifacts.

The canonical shape of every LLM use under this ADR is: **SOFIA decides the components, relationships, and structural choices; the LLM renders them** — in prose, advisory text, diagram form, or code. The framing places the burden of proof on probabilistic output: a design must justify why deterministic encoding is not feasible for a given output. Deterministic output is the default and carries no such burden.

### 2.4 Lifecycle scope and design-maturity honesty

The reasoning-capture invariant binds across the full enterprise SDLC — from idea capture through solutioning to operational onboarding — plus an always-on operational feedback substrate that ingests production reality and surfaces recommendations re-entering the lifecycle. The invariant is lifecycle-spanning so that later-stage work inherits the commitment without requiring a new ADR per stage.

This ADR is honest about design maturity. No service is yet deployed and no per-phase design is yet accepted, so every stage is **architecturally committed, design forthcoming** — the per-stage reasoning-capture mechanics (which decisions are SOFIA-encoded, which are delegated to specialized agents with reasoning captured, which are LLM-rendered probabilistic content, and which are human-reasoned over SOFIA-prepared context) are specified in the service and data designs as they are authored, not pre-encoded here. The later lifecycle stages — such as environment instantiation, code generation, test generation, and operational onboarding — and the operational feedback substrate carry **provisional** reasoning-capture shapes: their probabilistic decision shapes are flagged as forward commitments, to be confirmed at each stage's detail design, not settled by this ADR.

### 2.5 Encoding-density growth mechanism

The trajectory toward Position 4 is made real by a promotion mechanism: recurring reasoning patterns consolidate, over time, from LLM-rendered narrative or human override into encoded SOFIA logic. Every promotion into encoded knowledge passes a human (EA) approval gate — **SOFIA does not self-modify its encoded reasoning without EA approval.** This mechanism is what distinguishes the committed trajectory from a static Position 5: without it, recurring reasoning never consolidates and the platform is Position 5 today and Position 5 forever. The governance of the promotion mechanism is designed in the forthcoming Feedback Loop Governance design (DDR-003); this ADR commits the principle that the mechanism exists, is EA-gated, and is the engine of the Position 4 trajectory.

---

## 3. Rationale

Once this decision is in place, the *why* behind every architectural decision becomes a durable, queryable asset rather than transient prompt content. Every decision the platform produces carries a graph-resident provenance record — the inference, the evidence it drew on, and the alternatives it rejected — so audit and explainability are structural properties of the system, answerable by traversal, not reconstructed after the fact. This is the affirmative case for the platform's existence: enterprise context applied consistently and automatically, at a scale that exceeds any prompt's token budget and any individual architect's working memory (large application portfolios, hundreds of standards, accumulated incident and remediation history). That consistent-and-automatic application is the moat — the thing that distinguishes SOFIA from any architect with model access.

The decision is also what makes the platform drift-resistant and value-compounding. The explicit Position 5 commitment, together with the burden-of-proof-on-probabilistic-output rule (§2.3), means no downstream artifact can quietly regress into an LLM-wrapper without failing the compliance checks in §6 — the regression that would erase the platform's reason to exist is structurally surfaced rather than left to vigilance. And because encoding density grows over time (§2.5), the platform's reasoning gets richer with use rather than depending on model version; value compounds as recurring patterns consolidate into encoded logic, without retraining.

---

## 4. Alternatives Considered

The alternatives are the five positions of the reasoning taxonomy. They are not a flat 1→5 ladder: Positions 1–3 are distinct reasoning models (Alternatives A–C), while Positions 4 and 5 each admit a *binary-commitment* framing (Alternatives D–E). The decision — Position 5 as the operating regime on a trajectory toward Position 4 — is the synthesis that rejects the lower positions and both binary commitments.

### 4.1 Alternative A — Position 1: LLM-as-Reasoner

*Description:* The LLM receives a prompt plus graph context plus standards and produces the architecture decisions and their rationale. SOFIA's role is context assembly, output validation, and audit logging. This is the implicit default a build drifts toward absent an explicit commitment.

*Rejection rationale:* Position 1 cannot deliver the platform's explainability and auditability commitments — the reasoning lives in model weights and is opaque. Reasoning quality varies with model version, so the platform's value would compound *negatively* under a model regression. Enterprise context is bounded by whatever fits the prompt rather than by enterprise scale. And "why these choices were made in this enterprise's context" is lost because the model is doing the choosing. Decisively: any architect with model access reproduces equivalent output, so SOFIA's existence as a platform is unjustified. This is the specific failure mode the platform's anti-simplification commitment names.

### 4.2 Alternative B — Position 2: LLM-as-Drafter, Human-as-Reasoner

*Description:* The LLM produces a draft; humans do the actual reasoning at structured review gates, accepting, modifying, or rejecting the draft.

*Rejection rationale:* Position 2 is only as scalable as the humans available — it recreates the consultation bottleneck SOFIA exists to remove. The reasoning stays in human heads and never accumulates in the RG over time, so the platform builds no institutional memory. Net cycle time is worse than Position 4–5: it trades model speed for human review burden without the compounding capture.

### 4.3 Alternative C — Position 3: Constrained LLM with Decision-Tree Backbone

*Description:* SOFIA owns deliberate decision-tree structures encoding prior reasoning; the LLM is constrained to traverse the tree and produce rationale-supported choices within branches.

*Rejection rationale:* Decision trees become brittle at enterprise scale (large portfolios, hundreds of standards), novel situations do not fit existing branches, and tree authoring becomes a perpetual lift. Graph-native encoded traversal over the KG is a richer expressive substrate that handles the same governance constraint more flexibly. Position 3 is in fact a special case of Position 4–5 with the encoding constrained to tree form; the general case is preferable.

### 4.4 Alternative D — Position 4 as a binary commitment

*Description:* All architectural reasoning is encoded in SOFIA, the LLM is relegated entirely to narrow text generation, and no probabilistic outputs appear in the architectural-decision path.

*Rejection rationale (for now):* A binary Position 4 over-commits to encoding density that may prove impractical in some domains — novel cross-domain reasoning and edge cases where deterministic encoding adds little value. It forecloses Position 5's pragmatic flexibility and creates a "purity" pressure that slows practical progress. Position 4 remains the audacious end-state and the direction of travel; the ADR commits to the trajectory toward it without a binary commitment to arriving.

### 4.5 Alternative E — Position 5 as a binary commitment (no Position 4 trajectory)

*Description:* Hybrid LLM/SOFIA reasoning with capture discipline, but with no commitment to growing encoding density over time.

*Rejection rationale:* Without the Position 4 trajectory pull, "hybrid" becomes a license for whatever model use build pressure favors, and Position 1 reasserts itself silently. The encoding-density-grows-over-time commitment is what makes the platform's value compound; without it there is no mechanism to consolidate recurring reasoning into encoded logic, and the EA-gated promotion mechanism (§2.5) is left unmotivated. Position 5 without the trajectory is Position 5 forever.

---

## 5. Consequences

### 5.1 Positive Consequences

- **Architectural clarity.** Downstream work has an explicit position to anchor against; the "is this Position 1 or Position 4–5" ambiguity cannot recur, because §6 forces every design to state its answer.
- **Drift-resistance.** Implementation pressure to ship a quick model call is constrained by the Position 5 commitment and the burden of proof on probabilistic output. No subsystem can accidentally become "the platform" — narrow LLM use stays structurally narrow.
- **Auditability is structural, not aspirational.** Every architectural decision has a graph-resident provenance record (inference, evidence, rejected hypotheses), answerable by traversal.
- **Value compounds.** The encoding-density growth mechanism motivates the feedback loop; the platform's reasoning gets richer over time without model retraining.
- **Specialized-agent compatibility.** As specialized agents proliferate, SOFIA's identity as the reasoning-capture and coordination layer is preserved. SOFIA is not in competition with specialized agents; it makes them more powerful by capturing the reasoning that connects them.

### 5.2 Constraints Imposed

- **More upfront design.** Reasoning machinery — encoded matching, evidence weighting, hypothesis enumeration, gap detection — must be designed before implementation. The "wrap a model in graph context" shortcut is unavailable.
- **A standing burden of proof.** Every proposed LLM use must clear the Position 5 burden: why is deterministic encoding not feasible here, and what would shift it to deterministic over time? This is ongoing design-discipline overhead.
- **Authoritative-state reads bypass probabilistic content.** Probabilistic outputs are recorded as non-authoritative on their graph artifacts; any consumer needing authoritative state reads encoded or human-approved artifacts, not LLM-rendered content.
- **SOFIA must implement encoded reasoning.** The encoded reasoning patterns are platform code to design, build, and test — not delegated to the model.

### 5.3 Risks

- **Encoding density never grows.** If the promotion mechanism (§2.5) is never built or exercised, the platform stalls at Position 5 with no compounding and the trajectory becomes rhetorical. *Mitigation:* the EA-gated promotion mechanism and its governance are designed in the forthcoming Feedback Loop Governance work (DDR-003); promotion-cycle exercise is a signal to monitor once the loop exists.
- **Position-1 reassertion under build pressure.** Implementation pressure can favor a quick model call that quietly assumes Position 1. *Mitigation:* the §6 compliance checks are enforced at three-hat architecture review, which surfaces Position-1 drift before a design lands; the burden of proof on probabilistic output (§2.3) makes the regression explicit rather than silent.
- **Provisional later-stage capture hardens without design.** The later lifecycle stages carry provisional reasoning-capture shapes (§2.4); the risk is that a provisional shape is treated as settled. *Mitigation:* each stage's detail design re-confirms its capture mechanics; the provisional shapes are flagged as not pre-encoded by this ADR.

---

## 6. Compliance

Conformance with this ADR is verified at architecture review. The following checks are mandatory for every new SDD (Service Design Document), DDR (Design Decision Record), and design pass:

1. **Position commitment statement.** The design states how it honors the Position 5 operating regime and contributes to the Position 4 trajectory. Designs that quietly assume Position 1 without the §2.3 burden of proof are flagged.
2. **Reasoning-capture invariant.** Every architectural decision the design produces has a captured RG artifact in the conclusion category (§2.2; verified against the canonical vocabulary per DDR-002 §4 — currently `ReasoningProgress`) with source attribution by category and an authoritative flag, evidence linkage to the KG nodes consulted, and a rejected-alternative artifact (currently `RejectedAlternative`) for each option weighed and discarded.
3. **Deterministic / probabilistic classification.** Every output the design produces is classified as deterministic (SOFIA-encoded) or probabilistic (LLM-rendered); probabilistic outputs are recorded as non-authoritative.
4. **Burden of proof on probabilistic output.** Each probabilistic output justifies why deterministic encoding is not feasible and what would be required to shift it to deterministic over time (its Position 4 trajectory contribution).
5. **LLM-as-renderer language.** Design documents describing model use employ language consistent with §2.3 — the LLM renders SOFIA-decided components and does not select, decide, evaluate, or detect. Position-1-leaning verbs (the model "synthesizes," "selects," "decides," "reasons over") are flagged and reframed.
6. **Specialized-agent integration check.** Designs introducing a specialized agent specify how the agent honors the invariant: conclusion-category artifacts (canonical vocabulary per DDR-002 §4 — currently `ReasoningProgress`) attributed to the specific agent (source category *specialized agent*), evidence linkage to KG nodes consulted, rejected-alternative artifacts for rejected alternatives.
7. **Lifecycle-stage scope statement.** Designs touching a lifecycle stage state which decisions are SOFIA-encoded, which are delegated to specialized agents with reasoning captured, which are LLM-rendered probabilistic content, and which are human-reasoned over SOFIA-prepared context.

**Enforcement.** These checks are enforced at three-hat (LAA / SA / EA — Lead Application Architect / Solution Architect / Enterprise Architect) review — the operational gate every SDD and DDR passes through — at design time. This three-hat design review is **platform-development governance** — a gate on SOFIA's own design work — **not a graph-captured gate** on produced Solutions; the latter is the enterprise SDLC gate mirrored as a `GateDecision` (DDR-002 §2.4), a separate mechanism this review neither is nor pre-empts.

**Propagation.** Propagation of this commitment across reasoning-architecture design work is carried by the compliance checks above, enforced at three-hat review; no dedicated propagation directive is required. This is distinct from the runtime Directives-Context-Envelope Bridge, which §6 neither requires nor pre-empts.

---

## 7. Cross-References

- **Graph Schema document (DDR-002)** — owns the canonical artifact vocabulary (labels, property names, source-attribution categories, relationship types, constraints) that §2.2 defers to.
- **Feedback Loop Governance design** (DDR-003, forthcoming) — designs the EA-gated encoding-density promotion mechanism whose existence §2.5 commits.
- **Directives-Context-Envelope Bridge** — runtime directive-propagation mechanism (forthcoming, unauthored); §6 neither requires nor pre-empts it.
- Downstream DDRs and SDDs implement this ADR and are checked against it at three-hat review per §6.

---

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.2.0 | 2026-07-17 | RBT-59 | Forward-note (no decision change). ADR-008 (Ground-Truth Mutation Governance), ACCEPTED v1.0.0, generalizes and homes §2.5's EA-gated-promotion authority as the general ground-truth-mutation authority; §2.5 remains valid as the reasoning-consolidation sub-case. No change to this record's decision. Pin cascade (records still pinning the pre-bump versions) routed to a follow-up ticket. |
| 1.1.0 | 2026-07-03 | — | Triage-001 amendment batch (record: `agent-loop/triage/triage-001-distilled-set/record.md`). §2.2 retires the "illustrative" hedge — commits the reasoning-capture *categories* (conclusion / evidence / rejected alternative) and cites DDR-002 §4's now-ratified canonical vocabulary rather than deferring it (T-11); §2.2 altitude parenthetical signposts that structural containers, retention-mechanism nodes, and the Artifact family route their authority through DDR-001/DDR-002 §4–§5, not this capture contract (T-24); §6 checks 2 and 6 bind category-first, rename-safe against DDR-002 §4 (T-11); §7 Cross-References gains the Directives-Context-Envelope Bridge status marker (forthcoming, unauthored) (T-14); §6 Enforcement adds the three-hat-review fencing clause — platform-development governance, not a graph-captured gate (T-19). Clarification / reconciliation — no decision change. |
| 1.0.0 | 2026-07-01 | — | Distilled to standalone contract form; ledger coupling and review-diary scaffolding removed; documentation-purity pass folded in (acronym expansions, downstream doc-IDs back-filled, illustrative RG-vocabulary refreshed to the canonical DDR-002 set, Date/organization normalized); no decision change. |
| 1.0.0 | 2026-06-03 | — | Original authoring; ACCEPTED. |
