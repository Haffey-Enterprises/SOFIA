# File: docs/ddr/DDR-004-inherited-confidence-derivation.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-10
# Description: DDR-004 — inherited-confidence derivation. Fixes the concrete confidence-derivation function knowledge-service computes on Evidence capture, realizing DDR-002 §4's inheritance rule ("Evidence.confidence inherits from the SOURCED_FROM KG node's authority class at snapshot time") as a total-by-construction, derived-at-creation determination.

# DDR-004 — Inherited-Confidence Derivation

| Field | Value |
|---|---|
| **Document ID** | DDR-004 |
| **Version** | 1.1.0 |
| **Status** | ACCEPTED |
| **Date** | 2026-07-13 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — new ruling |
| **References** | DDR-002 v1.3.0 (§4 canonical confidence definition + inheritance rule + #24 ceiling + `Evidence.observed_at` capture-instant semantic, §1 contested-T2 convention, §2.1–2.5 + §2.6 plane schemas incl. the declared-basis carriers); DDR-001 v1.3.0; ADR-001 v1.1.0 (§2.2 source-attribution intent, §5.2 read discipline); ADR-002 v1.1.0; SDD-001 v1.2.0 (§3.4.3 derivation execution, §4.6 config surface, §9 cross-reference) |

---

## Decision

`knowledge-service` computes an inherited confidence on every `Evidence` capture, realizing DDR-002 §4's inheritance rule — *"`Evidence.confidence` inherits from the `SOURCED_FROM` KG node's authority class at snapshot time."* DDR-002 fixes that inheritance happens, by authority class, at snapshot time, and that the rollup is ceilinged; it fixes no concrete function. **This record fixes the function, its constant treatment, its totality contract, its composition boundary, and its calibration governance.** The derivation is **total by construction** — derive or reject, never default — and **derived-at-creation** — computed once at capture, then frozen.

The ruling has six testable components:

1. **Function form** — a two-branch derivation; Environment freshness is exponential decay. (§1)
2. **Constant treatment** — the `1.0` class base is invariant-ground; the Environment `base` and `τ`, and the `DeploymentEnvironment` flat base, are contested tunables. (§2)
3. **Δt reference anchor** — the capture instant, gateway-clocked, frozen. (§3)
4. **Per-class declared-basis totality** — every citable node-class declares one of four bases at its definition boundary; `CONFIDENCE_UNDERIVABLE` is defense-in-depth. (§4)
5. **Composition boundary** — branch (i) inherits node authority only; per-target edge certainty composes downstream in the `ReasoningProgress` rollup, under the #24 ceiling. (§5)
6. **Calibration governance** — how the contested constants are tuned and what ratifies a tuned value. (§6)

## Rationale

This derivation was the last Declared determination in SDD-001 with no deliberation lineage. It entered the corpus through the first SDD-001 review cycle as an explicitly-unruled inclination ("a v0.2.0 question, not ruled here") and was carried as interim executable behavior; the SDD-001 deliberation record contains no derivation item. Across two independent cold-audit draws it surfaced as a ten-member family spanning all four review hats and eight strata — every member ruled valid and decision-bearing, zero survivals of the underlying question, the signature of a real open decision rather than review noise. It was elected for its own record by ratified union disposition; the subsequent verification draw confirmed the election dissolved the family (zero valid members) and left only question-set refinements. The rulings in §§1–6 are the product of the charter design session, ratified per item. (The election substrate and design-session pointers live in Cross-References.)

Two commitments shape every ruling. **Form is design; constants are empirical.** The derivation's *shape* — two branches, exponential freshness decay, total-by-construction — is fixed here on design and canonical grounds and is testable independent of traffic. The derivation's *constants* (`base`, `τ`, and the `DeploymentEnvironment` flat base, §2) are POC-asserted and, with **zero capture traffic to date**, empirically unvalidated; the record fixes the form and holds the constants as contested, config-surfaced tunables rather than claiming a calibration it cannot yet perform. **Derive or reject, never default.** The gateway has no authority to invent a confidence it cannot derive; totality is achieved by giving every citable node-class a declared derivation basis at its definition boundary, not by defaulting a value at capture.

## 1. The derivation function

On `capture-evidence`, the gateway derives `Evidence.confidence ∈ [0.0, 1.0]` from the `SOURCED_FROM` KG node, by two branches.

**Branch (i) — native node confidence.** Where the cited node carries its own node `confidence` — Operational `ObservedPattern` (lesson reliability), Cost `CapabilityCostEstimate` (estimate reliability) — the inherited value **is that node confidence**. The node's plane has already expressed its authority measure natively; the Evidence inherits it unchanged.

**Branch (ii) — class base × freshness.** Otherwise, the inherited value is a class base multiplied by a freshness factor:

- **Catalog / Standards / Governance — base `1.0`, no decay.** These planes are versioned or append-only authoritative ground truth; staleness is governed by supersession (a superseded version is read-excluded), not by decay. There is no freshness term.
- **Environment (aging) — `base × exp(−Δt/τ)`**, with `base = 0.9`, `τ = 90 days`, and `Δt` the age of the cited fact at capture (§3).

**Freshness form — exponential decay.** DDR-002 §4 mandates that Environment ages by freshness; the *shape* is fixed here as exponential: monotone decreasing, asymptotic to but never crossing zero (a stale fact remains weak evidence — never anti-evidence, never requiring a clamp), constant half-life. Exponential also reduces calibration to a clean two-parameter (`base`, `τ`) fit, the surface SDD-001 §4.6 already assumes. The form is fixed; linear and step decays are not retained as live alternatives.

**Totality.** For every citable node-class exactly one branch yields a value, because every citable class carries a declared basis (§4). A citation that reaches no branch is **rejected, typed `CONFIDENCE_UNDERIVABLE`, fail-closed** — a defense-in-depth backstop, not the primary control (§4).

## 2. Constant treatment — the invariant / contested split

**The `1.0` class base is invariant-ground, fixed, and deliberately not a §4.6 tunable.** Unlike `base`/`τ`, it has no free parameter to calibrate: Catalog/Standards/Governance are definitionally authoritative ground truth, their staleness is handled by supersession rather than decay, and `1.0` is the top of the `[0,1]` scale — the reference against which every other confidence is read. Calibrating it would be incoherent (fit to what?) and would move the scale's own fixed point. This is a **determination this record makes on canonical warrant**, not a value DDR-002 carries: DDR-002 §4 fixes inheritance *by authority class* and the ordering (authoritative Catalog above aging Environment), but not the literal `1.0`.

**The `1.0` is intentionally non-discriminating across co-valid options.** Where several ground-truth options satisfy a need — two catalog technologies that each meet a requirement — each citation inherits `1.0`, and equally so. Confidence is an epistemic measure (is this fact true and current), not a fitness measure (is this the better choice). Equal authority is not equal fitness; selection among co-valid options is *authored judgment* — the ASA's `ReasoningProgress` conclusion, the `RejectedAlternative` and its `score_delta`, and `weight` — never a discrimination the derived confidence is asked to make. Fixing `1.0` as invariant keeps epistemic reliability and decision fitness on separate axes, consistent with the gateway's "executes everything, authors nothing" boundary.

**The Environment `base` (`0.9`) and `τ` (`90 days`) are `*(contested)*` tunables** under DDR-002 §1's convention — POC-asserted defaults pending calibration on real capture traffic, config-surfaced per SDD-001 §4.6 with the documented values as defaults. **The `DeploymentEnvironment` flat base is its own `*(contested)*` tunable** — initialized `0.9`, equal to but decoupled from the aging `base`: §6's calibration evidence is aging-fact evidence (re-observation; fresh-fact variance), which never measures the non-aging use, and a shared tunable would let a re-tune silently move a class its calibration never covered. **Empirical floor: zero capture traffic to date; these values are unvalidated.** Their governance is §6.

## 3. The Δt reference anchor

`Δt = capture_instant − cited_node.observed_at`.

The **reference "now" is the capture instant** — the `capture-evidence` transaction moment at which the `Evidence` node is created. This is DDR-002 §4's "snapshot time" and the derived-at-creation species' creation instant, stated here explicitly rather than left to entailment. Three properties hold:

- **Gateway-clocked.** The reference instant is the gateway's own transaction time, never a caller-supplied timestamp — the anchor must not be caller-influenceable, or confidence becomes replayable.
- **Frozen.** Confidence is computed once at capture and frozen onto `Evidence.confidence`; it is never recomputed at read. This is the point-in-time fidelity that also governs `source_node_version` pinning — `Evidence.confidence` records staleness-as-of-capture, immune to later KG drift.
- **Reconstructible.** Both Δt endpoints are durably recoverable: the cited node's `observed_at` via the `SOURCED_FROM` + `source_node_version` pin, and the capture instant persisted as `Evidence.observed_at` — DDR-002 §4's ratified semantic, the capture/snapshot instant (Condition 2 discharged by the clarification path, no new field; required for calibration).

## 4. Per-class declared-basis totality

Totality is a property established at each citable node-class's **definition boundary** — schema for core planes, registration for Extension planes — not rescued at capture. Every citable node-class declares exactly one confidence-derivation basis:

| Basis | Treatment | Staleness |
|---|---|---|
| **1 — native confidence** | inherit the node's own `confidence` (branch (i)) | as encoded in the node's confidence |
| **2 — non-aging flat base** | class base, no decay | supersession / lifecycle (not decay) |
| **3 — aging** | `base × exp(−Δt/τ)` on a declared domain freshness operand (branch (ii), Environment) | continuous decay |
| **4 — non-citable** | not a valid `Evidence` source; citation rejected, knowable at the definition boundary | — |

Basis 2 covers both *versioned-reference* data (the Catalog/Standards/Governance posture) and *structurally-stable identity* (a node whose fact does not age); in both, staleness is governed by supersession or lifecycle rather than decay.

A label without a declared basis fails registration (DDR-002 §2.6); non-citability is itself a declaration (basis 4), never an omission. `CONFIDENCE_UNDERIVABLE` is thereby unreachable for any well-formed plane, retained only as a fail-closed backstop against a malformed or legacy definition — **defense-in-depth, not the primary control.**

**Per-class dispositions (current planes):**

- **Catalog / Standards / Governance** — basis 2, flat base `1.0` (§2, invariant).
- **Environment `DeployedService`, `ConfigurationItem`** — basis 3 (aging; freshness operand `observed_at`).
- **Environment `DeploymentEnvironment`** — **basis 2** (non-aging flat base: its own contested tunable per §2, initialized `0.9`, no decay term). `DeploymentEnvironment` is the plane's structurally-stable member — a realized environment identity that does not age — so its **absence of `observed_at` is correct by design, not a schema gap**; no freshness field is added. The discriminator: **the authority class sets the base; the staleness mode sets only the decay term** (DDR-002 §4's canon ordering — authoritative Catalog above aging Environment). Dropping the decay term therefore does not promote the class to the authoritative planes' `1.0`; the base stays Environment-class.
- **Operational `ObservedPattern`** — basis 1 (native lesson-reliability confidence).
- **Cost `CapabilityCostEstimate`** — basis 1 (native estimate-reliability confidence).
- **Cost `RateCard`, `CostFactor`** — **basis 4 (non-citable).** The cost-evidence surface is `CapabilityCostEstimate` (the confidence-bearing as-of-decision record); `RateCard`/`CostFactor` are aggregation inputs, not `Evidence` sources.

**Honest floor:** whether reasoners cite `DeploymentEnvironment`, `RateCard`, or `CostFactor` is unverified. The fail-closed backstop keeps behavior safe regardless; the dispositions above resolve the permanent rule per class.

The declared basis is carried in the schema — for core planes in DDR-002 §2.1–2.5, for Extension planes in the `PlaneDefinition` registration contract (§2.6, `confidence_basis`) — so a plane declaring a node-label with no basis fails registration (DDR-002 §2.6's declared-totality rule; DDR-002 §7 #26). The carriers landed at DDR-002 v1.3.0 (Pre-Acceptance Condition 1, discharged); the declarations above bind as ratified, schema-carried contract (mechanization per DDR-002 §7's follow-tier sequencing).

## 5. Composition boundary — branch (i) × the #24 ceiling

Branch (i) inherits **node authority only.** The Operational plane carries a second confidence surface — the `OBSERVED_IN` edge's per-target observation certainty — distinct from the node's lesson reliability. That edge certainty is **not** inherited into `Evidence.confidence`, and its composition with node reliability is **the `ReasoningProgress` rollup's responsibility, routed to the solutioning-agent SDD** (SDD-001 §2.2), not this derivation's.

This is intended, not a loss. DDR-002 §4's #24 ceiling bounds a conclusion at `max` of its supporting `Evidence.confidence` — a weakest-link bound: a claim citing a distilled pattern is no more reliable than that pattern's own lesson reliability. Per-target certainty may pull a rollup *below* the ceiling (where `weight` and aggregation operate) but may not raise a conclusion above the reliability of the lesson it cites. A reasoner needing a claim stronger than the generalization should cite the specific observation as its own evidence, not the distilled pattern. The only residue is indirection — a rollup wanting per-target certainty reads it from the graph edge, not from the Evidence node. This boundary is documented, not amended.

## 6. Calibration and constant governance

**Scope.** The Environment aging `base` and `τ` are calibrated by the process below. The `DeploymentEnvironment` flat base (§2) is contested, but its **calibration basis is explicitly deferred**: this section's evidence streams measure aging facts and do not cover a non-aging identity class; a basis is named by amendment when a real evidence stream for it exists, and until then any config override of it is a live experiment under the same two-tier governance. `1.0` is invariant (§2); the form is fixed (§1); native-confidence bases inherit values. (SDD-001 §8's evidence-less-conclusion dwell is a separate §4.6 tunable, out of this record's scope.)

**Evidence that feeds calibration.** `τ` is fit to the empirical staleness timescale of Environment facts, measured by **re-observation** (a fact re-checked later: still true → decay too fast; changed → decay apt). `base` is fit to the baseline reliability of *fresh* Environment facts against outcomes — the estimate-vs-actual-variance logic DDR-002 §2.6 already invokes for cost. **Empirical floor: n=0 capture traffic and n=0 re-observations; no calibration is possible until the platform runs.** This section defines the process, not a result.

**Two-tier governance.** Config tuning (SDD-001 §4.6) is the operational, reversible experiment surface. A tuned value becomes the **ratified default only by the amendment act** — re-ratified into this record (and the SDD-001 §4.6 default) with the calibration evidence presented and ruled. Until amended, the documented default is the last-ratified value and any config override is a live experiment.

**Historical treatment on re-tune — grandfather.** Frozen `Evidence.confidence` values are never recomputed; re-tuning is forward-only, consistent with the derived-at-creation freezing (§3).

**Reconstructibility.** Because fitting `base`/`τ` requires reconstructing each capture's `Δt`, the **capture instant must be durably recoverable.** The mechanism is ratified: `Evidence.observed_at` *is* the capture instant (the Δt "to" point; the cited node's `observed_at` — the "from" point — recovered via the version pin), persisted with no new field — the semantic is glossed at DDR-002 §4 (Pre-Acceptance Condition 2, discharged by the clarification path; the derived-at-field fallback was not needed).

## Pre-Acceptance / Migration Conditions

The ruling was sound as authored; its full mechanization depended on two DDR-002 amendments (this record's acceptance conditions). Both are **discharged** — the DDR-002 v1.3.0 additive amendment batch landed their carriers, and the status change to ACCEPTED rode that landing (change-log-carried), per the ratified close ruling.

1. **DDR-002 declared-basis carriers — DISCHARGED at DDR-002 v1.3.0.** `PlaneDefinition` (§2.6) gained the per-node-label `confidence_basis` declaration with the declared-totality registration rule; core-plane bases are annotated in §2.1–2.5 (including `DeploymentEnvironment` = basis 2, `observed_at`-absence ratified correct-by-design); DDR-002 §7 checks #26/#27 carry the conformance contract.
2. **`Evidence.observed_at` semantic — DISCHARGED at DDR-002 v1.3.0.** DDR-002's intended meaning author-confirmed as the capture instant; the clarification adopted at DDR-002 §4 (no new field; the derived-at fallback not needed) (§6).

**Discharged at acceptance — three-hat review.** The originally-enumerated review condition (three-hat review of this record) is discharged by the two-draw review union and cold audit whose ratified dispositions this revision applies (carriers in the Change Log); the acceptance act is its discharge.

**Standing (non-blocking) condition — constants.** `base`/`τ` remain contested, unvalidated interim defaults until capture traffic and re-observation data exist (§6). Their contested status is honest at acceptance and is not a bar to it; calibration is ongoing governance, not a pre-acceptance prerequisite.

## Reconciliation with the SDD-001 interim

SDD-001 §3.4.3 carried this derivation as interim implemented behavior, with authority routed by name to this record (§3.4.3 body, §9). At this record's acceptance:

- **Confirmed unchanged:** the two-branch form, the Environment `base × exp(−Δt/τ)` shape, the `1.0` flat base, the total-by-construction property, and the fail-closed `CONFIDENCE_UNDERIVABLE` **rejection behavior** — a citation that reaches no branch still rejects, typed, fail-closed.
- **Fixed / extended by this record:** the `1.0`-as-invariant treatment; the explicit Δt capture-instant anchor; the per-class declared-basis totality; the `CONFIDENCE_UNDERIVABLE` control's **role and enumeration** — its interim primary-control position and single-named-reachable-case enumeration are superseded (demoted to defense-in-depth, unreachable for well-formed planes, §4); the branch-(i)×#24 composition boundary; the calibration governance and capture-instant persistence.
- **Routing resolves:** SDD-001's §3.4.3 / §9 subject-name pointers resolve to `DDR-004`. The routing was by subject-name, which this record now satisfies; the SDD needs no content change **for this record's acceptance** — the pointer resolution is a change-log-carried amendment on the SDD side (the ratified anchor-capture; see Cross-References). The §3.4.3 interim derivation *description* was superseded in substance by §4's declared-basis totality and was refreshed with the declared-basis carriers' landing (SDD-001 v1.2.0), not with this acceptance.

## Cross-References

- **Implements:** DDR-002 v1.3.0 §4 (canonical confidence definition, inheritance rule, #24 ceiling), §1 (contested-T2 convention), §2.1–2.5 + §2.6 (core-plane and Extension plane schemas, carrying this record's basis declarations); ADR-001 v1.1.0 §2.2 (source-attribution intent).
- **Implemented by:** SDD-001 v1.2.0 (`knowledge-service` — the gateway that computes the derivation) §3.4.3, §4.6, §9; the forthcoming solutioning-agent SDD (the `ReasoningProgress` rollup and per-target composition, §5).
- **Coordinates with:** RBT-54 (Touch 3) — the DDR-002 additive amendments this record entailed (declared-basis carriers; `Evidence.observed_at` semantic), landed at DDR-002 v1.3.0 and discharging Pre-Acceptance Conditions 1–2 (deliberation record: `agent-loop/deliberation/ddr-002-amendment-batch/record.md`).
- **Review of record:** the run-014 ∪ run-015 two-draw review union and cold audit — `agent-loop/runs/run-014-ddr-004/audit.md` (primary) · `agent-loop/runs/run-015-ddr-004/audit.md` (companion + union) · `agent-loop/runs/run-015-ddr-004/disposition.md` (dispositions D1–D7 + close rulings R1–R6, ratified per item, 2026-07-11/12).
- **Grounding:** the D1 election substrate — the run-009 audit's R6 inclination entry (the derivation's corpus entry point, explicitly unruled there), the run-010 / run-011 / run-012 audits, and the run-011 union disposition (Item 1); the RBT-53 design session (per-item ratifications, 2026-07-10).
- **Rhyme, not merger:** the layering-invariant ADR (services-as-deterministic-tools / agency-as-caller-layer) — separate record, loose coupling; neither gates the other.

## Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.1.0 | 2026-07-13 | RBT-54 | Conditions discharge — Pre-Acceptance Conditions 1–2 discharged by the DDR-002 v1.3.0 additive amendment batch (Condition 1: declared-basis carriers, §2 preamble + §2.1–2.5 annotations + §2.6 `confidence_basis` + checks #26/#27; Condition 2: the `Evidence.observed_at` capture-instant clarification at DDR-002 §4 — the preferred path, no new field). Status change rides the same landing per RBT-53 close ruling R1: **ACCEPTED-WITH-CONDITIONS → ACCEPTED.** §3/§4/§6/Pre-Acceptance/Reconciliation conditional phrasings resolved to earned tense; §4 omission semantics aligned to the landed carriers (a label without a declared basis fails registration; non-citability declared, never inferred — drafting-check adjudication A-5); References refreshed (DDR-002 v1.3.0; SDD-001 v1.2.0). The constants standing condition is unchanged — non-blocking, ongoing §6 governance. |
| 1.0.0 | 2026-07-12 | RBT-53 | First ACCEPTED-WITH-CONDITIONS — two-draw review union (run-014 ∪ run-015, gen-5, cold audit; union validity 39/44; 44/44 rulings, disposition D1–D7, and close rulings R1–R6 ratified per item, 2026-07-11/12; acceptance carriers: `agent-loop/runs/run-014-ddr-004/audit.md` + `agent-loop/runs/run-015-ddr-004/audit.md` + `agent-loop/runs/run-015-ddr-004/disposition.md`). Conditions = the two DDR-002 amendment prerequisites (Pre-Acceptance Conditions 1–2, tracked on RBT-54 Touch 3); the constants standing condition stays non-blocking as authored; the three-hat-review condition is discharged by this review. Merge of this revision is the acceptance act; the ACCEPTED-WITH-CONDITIONS → ACCEPTED status change rides the RBT-54 Touch 3 landing. PROPOSED → ACCEPTED-WITH-CONDITIONS. |
| 0.2.0 | 2026-07-12 | RBT-53 | Review-driven revision from the same union (revision carriers: both run audits + the ratified disposition, above; landed in the same commit as 1.0.0 — single landing per close ruling R1). Contract-purity sweep of the normative body: operational identifiers relocated to Cross-References / reduced to subject-name-only (D1). §3 Reconstructible conditioned on Pre-Acceptance Condition 2 (D2a). §4 declared-basis carrier restated forthcoming-amendment-conditional — resolves the carrier-tense family (D2b). §4 DeploymentEnvironment authority-class/staleness-mode discriminator stated (D2c). Reconciliation acceptance-scope qualification (D2d) and `CONFIDENCE_UNDERIVABLE` behavior-vs-role double-listing split (D2e). References + Cross-References DDR-002 citation widened to §2.2–2.5 + §2.6 (D2f). Decision rider: the `DeploymentEnvironment` flat base decoupled into its own contested tunable, initialized 0.9, calibration basis explicitly deferred (D3; §2/§4/§6). Verification-pass corrections (three-hat drafting check, ratified per item 2026-07-12): DDR-002 core-plane citation range corrected §2.2–2.5 → §2.1–2.5 at all four sites (Catalog is §2.1 — off-by-one present in the reviewed text); SDD-001 citation updated to the co-landing v1.1.0 with the §9 gloss reworded; §6 condition pointer made precise (Condition 2); Rationale contested-constants gloss widened to the D3 tunable set. |
| 0.1.0 | 2026-07-10 | RBT-53 | Initial draft. The inherited-confidence derivation, elected for its own record from the run-010/011 cold-audit union (D1, disposition Item 1) and confirmed dissolved by run-012; authored from the RBT-53 design session's per-item ratifications (2026-07-10). Six-component ruling: function form · constant treatment · Δt anchor · per-class declared-basis totality · composition boundary · calibration governance. Entails DDR-002 additive amendments (RBT-54 Touch 3). PROPOSED. |
