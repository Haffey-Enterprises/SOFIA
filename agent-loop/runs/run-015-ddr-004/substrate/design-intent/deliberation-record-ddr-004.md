# Deliberation Record — DDR-004 Inherited-Confidence Derivation Pre-Authoring Session

| Field | Value |
|---|---|
| **Session** | Pre-authoring deliberation + authoring, 2026-07-10 (claude.ai surface) |
| **Doctype gate** | `author-decision-record` skill; **DDR route ruled** — a concrete cross-plane design ruling under DDR-002 §4 (not ADR: the principle is DDR-002's, this fixes its realization; not SDD: the derivation spans the data model and multiple consumers). Allocated **DDR-004** (003 reserved-by-name for the forthcoming promotion-governance record; numbers never reused) |
| **Corpus** | ADR-001 v1.1.0 · ADR-002 v1.1.0 · DDR-001 v1.3.0 · DDR-002 v1.2.0 · SDD-001 v1.0.0 — all fresh-fetched at develop `ed4d944` and version-verified; `DeploymentEnvironment` `observed_at`-absence verified by direct read of DDR-002 §2.2 |
| **Charter** | Linear RBT-53 (D1 election — run-010/011 union disposition Item 1; run-012 dissolution + the two question-set riders); the eight-position agenda harvested from the family riders + audit riders |
| **Rulings** | Eight dispositions ratified per item by Tad, 2026-07-10; this record is the durable design-intent carrier — DDR-004's Cross-References grounding points here |
| **Deliverable** | `docs/ddr/DDR-004-inherited-confidence-derivation.md` PROPOSED v0.1.0, authored from these dispositions; DDR-002 mechanization routed to RBT-54 Touch 3; three-hat review and git transactions are Tad's |
| **Status** | COMPLETE — draft authored; review pending |

**Reviewer's key:** "§N" is DDR-002 unless prefixed; "branch (i)/(ii)" = the two-branch derivation (§1); "the four bases" = native-confidence · non-aging-flat · aging · non-citable (Item 4); finding IDs (`9a21625e`, `cee27acc`, …) index the run-010/011/012 family members.

---

## Gate — substrate assembly + doctype ruling (RATIFIED)

**Substrate (a):** the seven-pointer corpus fresh-fetched at develop `ed4d944` — run-010/011/012 audits, run-011 union disposition Item 1, SDD-001 v1.0.0 (§3.4.3/§4.6/§9), DDR-002 v1.2.0 (§4/§2.2/§2.6/§1), ADR-001 v1.1.0, the `author-decision-record` skill, carrier `loop-dev-state-2026-07-06`. **Substrate (b):** D1 dissolution independently re-verified (run-012: zero valid members where 010/011 held ten). **Substrate (c):** the eight-position design space deliberated to clarity below before any drafting; the pre-authoring gate bound in full — no rationale fabricated.

**Doctype ruling (the gate rules, not the ticket's expectation — though they coincide).** Three altitude tests: not **ADR** (the platform principle "confidence = source authority × freshness" is DDR-002 §4's; this record fixes the concrete realization, not a new cross-service commitment); not **SDD** (SDD-001 *implements* and routes authority *to* the derivation; the derivation itself spans the graph data model and multiple consumers — knowledge-service, the solutioning-agent rollup, the Extension registration contract); therefore **DDR** — a concrete cross-plane design ruling sitting under DDR-002's canon and entailing DDR-002 amendments. Allocated DDR-004.

---

## Item 1 — Function form and constants (RATIFIED)

**Question:** the τ/decay form and its constants are SDD-asserted with no upstream authority (`9a21625e`, the family's form root). What does the record *fix* versus hold open?

**Ruling: split form from constants — fix the form, hold the constants as contested tunables.** The record fixes (a) the two-branch structure — inherit native node `confidence` where present (branch (i)); else class base × freshness (branch (ii)); (b) Environment freshness as **exponential decay** `base × exp(−Δt/τ)`; (c) Catalog/Standards/Governance as flat base, no decay (supersession, not aging, governs staleness). The constants `base = 0.9`, `τ = 90d` remain `*(contested)*` §4.6 tunables, POC-asserted defaults, **not** invariant-ground.

**Deliberation.** DDR-002 §4 mandates that Environment *ages by freshness* — decay is canon, not choice; what is ours to fix is the shape. Exponential is the design-correct monotone decay: constant half-life, asymptotic to but never crossing zero (a stale fact stays weak evidence, never anti-evidence, never needs a clamp), and it reduces calibration to a clean two-parameter fit — the surface §4.6 already assumes. The governing commitment: **form is design (defensible from canon + first principles, testable independent of traffic); constants are empirical.** Honest floor: **n=0 capture traffic** — the constants are unvalidated, and the record says so rather than claiming a calibration it cannot perform. Exponential fixed as *the* form; linear/step not retained as live alternatives.

---

## Item 2 — Δt reference-time anchor (RATIFIED, pending Item 8)

**Question:** §3.4.3 computes Δt "from the cited node's `observed_at`" but supplies the reference "now" only by entailment (run-012 `9c774202`, OVER-close, ruled sufficient-by-entailment; this record is the home to state it).

**Ruling:** the reference "now" is the **capture instant** — the `capture-evidence` transaction moment, which *is* DDR-002 §4's "snapshot time" and the derived-at-creation species' creation instant. `Δt = capture_instant − cited_node.observed_at`. Three properties: **gateway-clocked** (never caller-supplied — the anchor must not be replayable/gameable); **frozen** (computed once, never recomputed at read — the point-in-time fidelity that governs `source_node_version` pinning); **reconstructible** (both endpoints durably recoverable — see Item 8).

**Deliberation.** This codifies an entailed answer, not a new decision. A rider surfaced — Evidence is DDR-002's *sole surrogate-only* type (no `created_at`), so the capture instant is not a durably stored graph field; a frozen confidence is not self-reconstructing across a constant re-tune. Carried to Item 8, where re-tuning lives; **ratification held pending that discharge.**

---

## Item 3 — The 1.0 anchor: contested-flag or invariant-ground? (RATIFIED)

**Question:** `6e21f037`'s rider — the 1.0 is the only constant with *neither* treatment (not `*(contested)*`, not a §4.6 tunable).

**Ruling: invariant-ground — fixed, deliberately not a §4.6 tunable**, with the determination-vs-canon warrant and a non-discrimination note stated in the record.

**Deliberation.** The 1.0 has no free parameter to calibrate: Catalog/Standards/Governance are definitionally authoritative ground truth, staleness handled by supersession not decay, and 1.0 is the top of the `[0,1]` scale — the reference every other confidence is read against; calibrating it is incoherent (fit to what?) and would move the scale's fixed point. This is a **determination on canonical warrant** — DDR-002 §4 fixes inheritance *by authority class* and the ordering, not the literal 1.0 (the `2814cfe0` determination-vs-canon stratum). Pressure-tested live (two co-valid catalog options, e.g. Postgres/CloudSQL): both inherit 1.0 equally, and correctly — **confidence is epistemic (is this true/current), not fitness (is this the better choice)**; equal authority ≠ equal fitness; selection is authored judgment (`ReasoningProgress` conclusion, `RejectedAlternative` `score_delta`, `weight`), never a discrimination the derived scalar makes. Fixing 1.0 as invariant keeps the two axes apart, consistent with the gateway's authors-nothing boundary. Empirical floor cuts the *opposite* way here: 1.0-as-invariant is design-true independent of traffic.

---

## Item 4 — Per-class declared-basis totality (RATIFIED)

**Question:** the Extension-branch totality rule (recommended shape: registration-declared freshness timestamp), generalized by the run-012 rider to per-class totality (the `DeploymentEnvironment` case).

**Ruling: the derivation's totality is a per-class property established at the class-definition/registration boundary.** Every citable node-class declares one of four bases — **1** native node confidence · **2** non-aging flat base (versioned-reference *or* structurally-stable identity; staleness by supersession/lifecycle, no decay) · **3** aging (declared domain freshness operand, Environment-class decay) · **4** non-citable. `CONFIDENCE_UNDERIVABLE` is demoted from primary control to **defense-in-depth** — unreachable for any well-formed plane.

**Deliberation (a finding drove the reframe).** Reading §2.6 fresh: the Cost plane's `RateCard`/`CostFactor` (`cee27acc`'s confirmed hole) are versioned, superseded-only reference data — they **age like Catalog, not like Environment**. Forcing them into a freshness-timestamp→decay mold would be semantically wrong; the disposition's "registration-declared freshness timestamp" shape **under-fit the very plane it was written for**. Root cause: totality belongs at the definition boundary, with a small closed basis-enumeration, not a single freshness assumption. This **supersedes the disposition's shape as an applied learning** (criterion-shift, not contradiction). Honest floor: single Extension plane (n=1) — but this is *structural completion of the already-ratified derive-or-reject invariant*, not a promotion of new scope, so no threshold override needed. The declared-basis carriers are DDR-002 amendments (§2.6 `PlaneDefinition`; core-plane §2.2–2.5), routed to RBT-54 Touch 3.

---

## Item 5 — Cost plane instance disposition (RATIFIED)

**Ruling:** `CapabilityCostEstimate` = **basis 1** (carries `confidence`); `RateCard`/`CostFactor` = **basis 4 (non-citable)**.

**Deliberation.** §2.6 makes `CapabilityCostEstimate` the purpose-built cost-evidence surface (the as-of-decision record carrying `confidence` + `decision_ref`); `RateCard`/`CostFactor` are aggregation *inputs*, not Evidence sources. Non-citable makes `CONFIDENCE_UNDERIVABLE` unreachable on the Cost plane by construction. Honest floor: whether raw references are ever cited is unverified; the permissive alternative (basis 2, versioned-reference flat base) was on the table and declined in favor of matching the plane's designed evidence surface.

---

## Item 6 — `DeploymentEnvironment` instance disposition (RATIFIED)

**Ruling:** **basis 2 (non-aging flat base** — the Environment base `0.9`, contested per Item 3, decay term dropped); the absence of `observed_at` **ratified as correct-by-design**, no field addition.

**Deliberation.** `DeploymentEnvironment` is the Environment plane's structurally-stable member — a realized environment identity (production/staging/dev) that does not age, unlike its re-observed siblings `DeployedService`/`ConfigurationItem`; the schema's omission of `observed_at`/`lifecycle_state`/`status` reflects that. Option "add `observed_at`" (basis 3) explicitly rejected — it would model staleness that doesn't exist, the exact error the general rule prevents. Flat-base chosen over non-citable because **no substitute node** could absorb environment-identity evidence (contrast `RateCard` → `CapabilityCostEstimate`). Resolves the run-012 audit's second reachable `CONFIDENCE_UNDERIVABLE` find. Honest floor: reachability unverified; flat-base is the robust default.

---

## Item 7 — Branch-(i) × #24 interaction (RATIFIED)

**Question:** the #24 ceiling forecloses the routed rollup's access to per-target certainty from evidence-mediated paths (`4ab8d42c`). Intended, tolerated-and-documented, or a defect?

**Ruling: intended (ceiling direction) + tolerated-and-documented (composition routed) — not a defect.** Branch (i) inherits **node authority only**; the `OBSERVED_IN` per-target edge certainty is not inherited into Evidence and is composed downstream in the `ReasoningProgress` rollup (routed to the solutioning-agent SDD, §2.2). The record documents the boundary and cross-references the rollup owner; no amendment.

**Deliberation.** The #24 ceiling (`max` of supporting `Evidence.confidence`) is a **weakest-link bound**: a claim citing a distilled pattern is no more reliable than that pattern's own lesson reliability. The foreclosure bites only *upward* — and upward is exactly what should be foreclosed (per-instance certainty must not launder into higher authority for the general lesson; cite the specific observation directly if a stronger claim is wanted). The meaningful *downward* direction remains available below the ceiling via `weight`/aggregation. The pivotal weakest-link assumption was surfaced explicitly and ruled; had the intent been upward composition, the ceiling would flip to a defect requiring a richer citation model.

---

## Item 8 — Calibration path + Item-2 discharge (RATIFIED)

**Ruling.** Calibrated: Environment `base`/`τ` only (1.0 invariant; form fixed; native bases inherit). Evidence: `τ` fit to Environment-fact staleness via **re-observation**, `base` to fresh-fact reliability against outcomes (estimate-vs-actual variance). **Governance is two-tier:** config tuning (§4.6) is the operational, reversible experiment; a tuned value becomes the ratified default only by the **amendment act** (re-ratified into the record + §4.6 default, evidence presented and ruled). Historical treatment on re-tune: **grandfather** (frozen values never recomputed; re-tuning forward-only). **Item-2 discharge:** calibratability *requires* reconstructing each capture's Δt, so the **capture instant must be durably recoverable** — preferred mechanism clarifies that `Evidence.observed_at` *is* the capture instant (cited node's `observed_at` recovered via the version pin), persisting it with no new field; verify-intent gate against DDR-002's meaning; derived-at field fallback. Routed to RBT-54 Touch 3.

**Deliberation.** Honest floor: **n=0 capture traffic and n=0 re-observations** — no calibration is possible until the platform runs; the record defines the process, not a result. The insight that closed Item 2: *calibration forces persistence* — the decision to tune later imposes a data-retention obligation now, reaching back into the schema; the first re-tune is when a missing input bites.

---

## Authoring notes

- **DDR-002 mechanization not authored here.** Items 4/5/6/8 entail four additive DDR-002 edits — `PlaneDefinition` per-node-label basis declaration; Cost-plane basis annotations; `DeploymentEnvironment` basis-2 annotation; `Evidence.observed_at` semantic clarification — routed to RBT-54 Touch 3, downstream of this record. Adjacent-ticket writes were per-item authorized.
- **Routing satisfaction.** SDD-001 §3.4.3 + §9 route the derivation's authority by subject-name; DDR-004 satisfies the by-name route (no SDD content amendment for correctness). At acceptance the two pointer sites resolve to "DDR-004" (change-log-carried); a §9 scope-enumeration refresh (non-exhaustive vs DDR-004's six components) rides that edit.
- **Known finding, held for the review cycle.** DDR-004 v0.1.0 tripped the docs-structure validator (check D, contract-purity): six instantiated ticket/run identifiers in normative body (Rationale, Pre-Acceptance, Reconciliation) rather than confined to Change Log / Cross-References — an authoring-convention miss, rulings unaffected. Held for the review to formally flag; the revision moves them to Cross-References / subject-name-only and clears the gate before push. (This deliberation record keeps refs in its provenance/metadata rows per the established convention — check D scopes only `docs/adr|ddr|sdd/`, not `agent-loop/deliberation/`.)
- **Out-of-scope discipline:** RBT-54 DDR-002 amendment *authoring* (its own session); SDD-001 §8 evidence-less-conclusion dwell (a §4.6 tunable, not the derivation); the layering-invariant ADR (services-as-tools / agency-as-caller) — **rhyme, not merger**, separate record, neither gates the other.
- **Conventions honored:** no-story-telling — the DDR-004 body is contract-only; this record carries the deliberation. Two-surface: deliberation/authoring/review claude.ai-side; Code mechanizes; git is Tad's.
