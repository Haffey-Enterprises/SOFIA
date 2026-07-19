# File: docs/reviews/2026-06-22-rbt-14-ddr-003-antagonistic-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-22
# Description: Antagonistic review (DIRECTIVE-032) of the DDR-003 Feedback Loop Governance draft (0.1.0 PROPOSED) — pressure-tests every assumption and design decision in the ratified substrate, and checks coherence with the parent ADRs (ADR-001/002) and sister DDRs (DDR-001 v1.1.0 / DDR-002 v1.1.0).

# Antagonistic Review — DDR-003 Feedback Loop Governance (RBT-14) — 2026-06-22

| Field | Value |
|---|---|
| **Review Date** | 2026-06-22 |
| **Reviewer** | claude.ai (architecture leadership team) — antagonistic / fresh-eyes pass under DIRECTIVE-032 |
| **Scope** | Pressure-test the DDR-003 draft (`docs/ddr/DDR-003-feedback-loop-governance.md`, 0.1.0 PROPOSED) and its ratified substrate against the parent ADRs, sister DDRs, and prior ruling rationale (Reboot Decision Ledger). |
| **Authority** | DIRECTIVE-032 (antagonistic review / continuity check); operator-invoked. Severity vocabulary per DIRECTIVE-007 §7.2 (BLOCKING / MATERIAL / COSMETIC / POSITIVE). |
| **Outcome** | **FAIL (this pass) — 2 BLOCKING + 12 MATERIAL + 4 COSMETIC, against a large POSITIVE no-drift set.** The draft faithfully realizes the ratified substrate; the findings are where the substrate itself left cross-document seams unreconciled, plus internal under-specification. Convergence is reached when a pass surfaces zero new and zero unresolved findings (DIRECTIVE-032 §32.4). |

---

## §0 Method and stance

This is a deliberately adversarial pass. It does three things, in order of increasing aggression:

1. **Fidelity check** — does the draft realize what was ratified across the seven forks (clusters B/A/D/E/F/G + the framing cut) and the ledger elevations R29/R30/R31? *(Mostly yes — see POSITIVE set, §2.4.)*
2. **Coherence check** — does the draft contradict, dangle against, or under-cite the parent ADRs (ADR-001 §2.5 / §5.3; ADR-002 §2.4 / §2.6 / §6) and the sister DDRs (DDR-001 v1.1.0; DDR-002 v1.1.0 as landed by RBT-43)?
3. **Substrate challenge** — attack the design decisions themselves on their merits, not the fold-confirmations. Where the *substrate* (not just the draft) carries an unstated assumption, that is fair game.

**Sources fresh-fetched for this review:** CLAUDE.md; CLAUDE_SESSION_DIRECTIVES.md (DIRECTIVE-007/031/032/034); ADR-001 v1.0.0; ADR-002 v1.0.0; DDR-001 v1.1.0; DDR-002 v1.0.0 (project knowledge) reconciled against the RBT-43 v1.1.0 landing record; the DDR template and review template; Linear RBT-14 (with relations + full comment trail, incl. the substrate-complete comment); the Reboot Decision Ledger (R1–R31); the DDR-003 draft and the `~/Downloads/ddr-003-substrate-handover.md` substrate.

**Residual blind spots (DIRECTIVE-032 §32.4.1), held explicitly:** (a) cross-block internal consistency is checked but not exhaustively; (b) *runtime* behavior — whether the gateway actually enforces the read-disciplines this DDR asserts — is deferred-to-runtime-verification at RBT-15, not certified here. Several findings below (B-2, M-3) are precisely at that seam.

---

## §1 Scope

### 1.1 In-scope
- `docs/ddr/DDR-003-feedback-loop-governance.md` (0.1.0 PROPOSED) — every ruling component (Decision.1–.7) and substantive section.
- The ratified substrate (RBT-14 substrate-complete comment) — challenged on its merits.
- Coherence with ADR-001, ADR-002, DDR-001 v1.1.0, DDR-002 v1.1.0, and ledger R22/R24/R25/R26/R27/R29/R30/R31.

### 1.2 Out of scope (deliberately)
- The DDR-002 v1.1.0 amendment itself (RBT-43, landed) — reviewed at its own gate; cited here only where DDR-003 leans on it.
- Service realization (gateway API, detection-job lifecycle, review portal, write sequences) — DDR-003 correctly routes these to the SDDs; this review does **not** fault the draft for deferring them, only where a *deferral is mis-scoped or an exposure is unnamed*.
- Calibration *values* — correctly deferred per R29; not faulted.

---

## §2 Findings

### 2.1 BLOCKING — must resolve before the three-hat acceptance gate proceeds

#### Finding B-1: Write-authority for `CandidatePromotion` and the materialized KG node is unhomed against ADR-002 §2.6

**Location:** §The EA Gate → "Authorship & gate completion" ("The `CandidatePromotion` is **system-authored** by the out-of-band feedback process…"); cross-check ADR-002 §2.6, §6 check #5; DDR-001 §Reasoning-Graph RG-invariants.

**Description:** ADR-002 §2.6 fixes reasoning-state write authority as **component-scoped, not diffuse**, and names exactly two writers: ASA authors `ReasoningProgress`; AOE owns the `ReasoningSession` lifecycle. `CandidatePromotion` is a `:Reasoning:`-labelled node, and the materialized promotion is an authoritative KG write — yet **no document (ADR-002, DDR-001, DDR-002) assigns write authority for either.** The draft fills the void by asserting the feedback process as the author, but does not reconcile that against §2.6's closed two-writer model, nor route the *authority assignment* (as distinct from the write *path*, which legitimately → SDD) to an owner.

**Why blocking:** This is the same class of defect that surfaced as DDR-001's own Pass-3 **B-1** (RG write-authority reconciled to ADR-002 §2.6 / R7). ADR-002 §6 **check #5** (write-authority) is a mandatory three-hat check for every DDR that writes reasoning state; a design that introduces a third de-facto RG writer without reconciling it will fail that check. It is also the single most sensitive write on the platform — the one that mutates authoritative ground truth.

**Risk if not addressed:** A latent authority hole at the highest-stakes write. Downstream SDDs (RBT-15/16/17) will each make a local assumption about which component authors `CandidatePromotion` and performs materialization, producing inconsistent realizations and a write boundary with no single authority of record — exactly the diffuse-write failure ADR-002 §2.6 and §2.5 exist to prevent. Discovered late (at SDD authoring or build), it forces a cross-document amendment under blast radius.

**Disposition:** Reconcile the feedback-process writer against ADR-002 §2.6 — name the authorized component and route it through the sole-owner gateway. Likely outcome is a **DDR-001 (architecture) or ADR-002 reconciliation**, not a DDR-003-only edit; DDR-003 should at minimum state the authority explicitly and cite its home, rather than asserting it as settled.

#### Finding B-2: Retracted-node read-exclusion is asserted as "gateway-enforced" but has no enforcing invariant and no structural guarantee

**Location:** §Conditional Governance & Retraction → "Retraction governance" ("The retracted node is **retained and read-excluded** (gateway-enforced read-discipline keyed on the EA-approved `RETRACTS` edge)…"); cross-check DDR-002 v1.1.0 §7 #21 (retraction-gated) and the RBT-43 landing note ("**no `applicability_state: retracted` marker, edge-only shape**").

**Description:** Under the *edge-only* retraction shape RBT-43 landed, a retracted node **keeps its KG plane label and its `applicability_state` (`unconditional`/`conditional`)**. DDR-002's read-disciplines exclude only (a) `CandidatePromotion` (no KG plane label → structurally skipped, #9) and (b) `conditional` nodes failing their `Condition` (#19). A retracted node is **neither** — so it is admitted to ground-truth synthesis traversals **unless** the gateway specifically excludes nodes carrying an inbound `RETRACTS` edge. Invariant **#21 governs the legitimacy of the retraction act** (it must be EA-approved — the #15 mirror); it does **not** enforce read-exclusion of the retracted node. There is **no #9/#19-analog invariant** for retracted-node exclusion, and the draft names none.

**Why blocking:** Retraction is the remedy for knowledge that *should never have been promoted* (a data-defect promotion, a spurious pattern). If the retracted node remains consumable in synthesis, the remedy does not remedy — the "should-never-have-been" fact stays live in authoritative reasoning. The draft asserts the exclusion as settled gateway behavior with no conformance invariant guarding it and no structural skip backing it.

**Risk if not addressed:** A retracted node continues to be read as ground truth (a silent integrity failure that is hard to detect — there is no CI check), defeating the retraction governance R31 establishes. The exposure rides entirely on un-conformance-checked RBT-15 gateway code. This is the safety-critical tier per R27/R28's own classification (wrong-consumption of non-ground-truth as ground truth).

**Disposition:** Either (a) name a retracted-node read-exclusion **invariant** parallel to #19 and route it to DDR-002 amendment + RBT-33 (safety-critical tier), or (b) explicitly name it as a **gap with an exposure window** (R27 pattern). The current "asserted as settled" posture is the defect. Recommend (a) given the safety-criticality.

### 2.2 MATERIAL — should be resolved in scope of the acceptance cycle

#### Finding M-1: The loop's own reason-to-exist risk (ADR-001 §5.3 "encoding density never grows") and the single-EA liveness bottleneck are unaddressed

**Location:** Whole-document; cross-check ADR-001 §2.5, §5.3 (risk: "Encoding density never grows … promotion-cycle exercise is a signal to monitor once the loop exists"), and Alternative E ("Position 5 forever").

**Description:** ADR-001 §2.5 says the promotion mechanism *is the engine of the Position-4 trajectory*, and §5.3 names the **specific platform risk** that the loop is never exercised → the trajectory becomes rhetorical. DDR-003 is the governance home for that loop, yet it (i) does not name a **liveness/exercise health signal** (is the loop firing? are promotions happening? is encoding density actually growing?), and (ii) **concentrates every gate function on a single human EA** — diagnosis, calibration ownership, conditional scope-setting, retraction approval — with no governance for EA unavailability, delegation, queue backpressure, or escalation. The routed "judgment-consolidation health/weighting → RBT-27 (parked)" is about *weighting promoted-vs-ingested facts*, not about loop liveness.

**Why material:** The draft governs the loop richly on *correctness* (no leak, audit-first, never-self-modify) but is silent on *liveness* — the dimension ADR-001 §5.3 flags as the trajectory-defeating risk. The single-EA design is the very "consultation bottleneck" SOFIA exists to remove (ADR-001 §4.2, Position 2 rejection), re-imported at the gate.

**Risk if not addressed:** The loop is structurally sound but never runs at volume because the sole EA is the bottleneck; encoding density flatlines; the platform sits at Position 5 forever (Alternative E) — and nothing in the governance surfaces it, because no liveness signal was ruled. The R17 precedent ("solo-operator phase, expands when team scales") shows the right move: name the single-EA concentration as a deferred-with-reversal-path concern, not leave it implicit.

**Disposition:** Add a named (deferrable) **loop-liveness/exercise health concern** routed to operational onboarding + RBT-27, and a named **EA-concentration / delegation-backpressure gap** with an R17-style "expands when the team scales" reversal path.

#### Finding M-2: R30 derive/promote seam contradicts DDR-002 v1.1.0 §2.3's own wording ("entry into the KG is EA-gated")

**Location:** §Signals & Detection → "Distillation governance — the derive/promote authority seam (R30)"; cross-check **DDR-002 v1.1.0 §2.3** verbatim: *"Weakness/strength entry into the KG is **EA-gated** via the feedback loop (§5), not auto-ingested."*

**Description:** DDR-003 / R30 assert that the distillation write of an `ObservedPattern` into the Operational plane is a **non-EA-gated** `derived` write, and that *only* promotion into Catalog/Standards is EA-gated — the Operational plane being a "non-authoritative staging tier." But the Operational plane **is a KG plane** (DDR-001 Decision.2), and the landed DDR-002 v1.1.0 §2.3 states in its own voice that *weakness/strength entry into the KG is EA-gated*. A reader of DDR-002 + DDR-003 gets **two different answers** to "is the `ObservedPattern` write EA-gated?" R30's rationale openly concedes the tension ("the apparent self-modification tension … was never made explicit") and resolves it conceptually — but the DDR-002 **text was not updated** (RBT-43 added `archived`/`ProvenanceSummary`/`RETRACTS` only), and DDR-003 does not flag or reconcile the residual wording.

**Why material:** This is a live cross-document inconsistency on the exact axis ADR-001 cares about most (SOFIA-never-self-modifies). The seam (Operational = staging) is doing heavy lifting on the word "selection" — yet the Operational plane's whole purpose is to *inform selection* (a weakness track-record should steer selection), so the line between "informs selection" and "is selection knowledge" is not crisp, and synthesis can traverse Operational as ground truth.

**Risk if not addressed:** Either the contradiction stands (DDR-002 says gated, DDR-003 says not) and a future reader/implementer enforces the wrong one; or, if Operational *is* read during synthesis, a non-EA-gated derived write *does* influence authoritative reasoning outputs without an EA gate — the precise self-modification the seam claims to resolve. An antagonistic reviewer (or RBT-15) will re-litigate this.

**Disposition:** Reconcile explicitly. Either route a **DDR-002 §2.3 wording clarification** (replace "entry into the KG is EA-gated" with the staging-tier/authoritative-tier seam language) as an additive amendment, or carry a crisp reconciliation note in DDR-003 establishing that Operational is excluded from *authoritative selection* reads, with the exclusion mechanism named.

#### Finding M-3: The retention framework smuggles a binding inter-parameter constraint (`signal retention ≥ detection lookback`) as rationale prose

**Location:** §Retention → "Bounded / non-uniform … `RejectedAlternative` longest-lived … **must outlive the detection windows that might promote it**."

**Description:** The framework claims to rule only **relative ordering** among RG roles and to defer **absolute windows** as calibration values. But "`RejectedAlternative` must outlive the detection windows" is not an ordering — it is a **cross-parameter constraint** binding two deferred values (`RejectedAlternative` retention ≥ override-recurrence lookback). It generalizes: **every promotion-eligible signal's retention window must be ≥ its detection lookback**, else the signal expires before it can be counted. The draft states this only for one role, only as prose, and never names it as a binding rule the calibration must satisfy.

**Why material:** R29's mandate is to rule the *mechanism* now — and the *constraints among parameters* are part of the mechanism, not a value. Leaving this as prose means a calibration at onboarding can set `lookback > retention` and **silently under-detect** (the primary feedback signal expires before the window that would promote it). This is a loophole that surfaces exactly when R29 says it should already be closed.

**Risk if not addressed:** Silent loss of promotion signal at calibration time — the loop quietly under-promotes with no error, undermining the encoding-density growth the whole DDR exists to govern (compounds M-1).

**Disposition:** Promote the constraint to a **named binding calibration invariant** ("for every promotion-eligible signal class, retention window ≥ its detection lookback window") in the parameter-mechanism section, alongside the deferred values.

#### Finding M-4: The audit-first invariant is ambiguous and unsatisfiable-as-stated across two stores

**Location:** §Retention → "Audit policy — the two-record model" (audit-first invariant) + Decision.5 ("two-record audit model (Neo4j `PromotionDecision` + PostgreSQL operational trail)").

**Description:** The two-record model places the **accountable decision** in Neo4j (`PromotionDecision`) and the **operational trail** in PostgreSQL. The audit-first invariant says *"no KG promotion materializes without its audit record committed first."* It does not say **which** record must precede. If it is the Neo4j `PromotionDecision`, then `PromotionDecision` + `PROMOTES_TO_KNOWLEDGE` + materialized node are co-resident and can be one atomic transaction — but then "audit-first" is just the already-stated approval-precedes-materialization rule. If it is the **PostgreSQL** trail, the invariant is a genuine **cross-store ordering constraint** with a failure window (PostgreSQL committed, Neo4j mutation fails → a "materialized" audit record for a promotion that didn't happen).

**Why material:** As literally stated, the invariant conflates the two records and is either redundant (Neo4j reading) or unsatisfiable without cross-store failure semantics (PostgreSQL reading). The draft's event list does include a "failed" terminal event, which *anticipates* the failure window — but the invariant text doesn't connect to it.

**Risk if not addressed:** Implementers pick a reading; under the PostgreSQL reading they ship a two-phase write whose failure window produces phantom-audit records (audit says materialized, KG empty) or unaudited mutations, both of which the recoverability requirement then cannot honor.

**Disposition:** Specify **which** audit record bears the precedence, and if it is cross-store, state the reconciliation rule (the "failed" event closes the window) as part of the invariant — or scope the precedence to the in-store `PromotionDecision` and demote the PostgreSQL trail to eventually-consistent secondary.

#### Finding M-5: Provenance-survival is specified around `Evidence` expiry but the chain also runs through `PROPOSED_FROM` sources that expire

**Location:** §Retention → "Provenance-survival snapshot" (ProvenanceSummary carries `frozen_fact_summaries` + `frozen_source_version_pins` + chain to `PromotionDecision`); cross-check DDR-002 §5 provenance chain (`promoted → CandidatePromotion → PROPOSED_FROM → ReasoningProgress|Evidence|RejectedAlternative → SOURCED_FROM → facts`) and §Retention bounded-class (`RejectedAlternative`/`ReasoningProgress` are **bounded**, not durable).

**Description:** The promoted node's full provenance chain passes through its **`PROPOSED_FROM` source** (`ReasoningProgress` / `RejectedAlternative` / `ObservedPattern`), then through `Evidence`. The `ProvenanceSummary` freezes the **`Evidence`** layer (fact summaries + version pins). But `RejectedAlternative` and `ReasoningProgress` are in the **bounded** retention class (only `CandidatePromotion`-terminal, cost, and audit-trail are durable). When a promotion is sourced *from* a now-expired `RejectedAlternative`, the chain breaks at the `PROPOSED_FROM` link — and the `ProvenanceSummary`, being `Evidence`-scoped, does not obviously preserve the `RejectedAlternative`'s content (its `rejection_reason`, the override chain that *was* the promotion's basis).

**Why material:** The recoverability requirement (§5.2) promises the audit can answer "the full provenance chain to source" for **any** promoted fact, **forever** (promoted nodes are durable). But the chain's intermediate `PROPOSED_FROM` source is bounded, and the survival snapshot is `Evidence`-scoped. The guarantee and the mechanism don't match at the `PROPOSED_FROM` layer.

**Risk if not addressed:** Post-expiry, a durable promoted fact has a chain that dead-ends at an expired `PROPOSED_FROM` source — the "why this became knowledge" (especially for override-sourced promotions, the *primary* feedback input) is lost despite the ProvenanceSummary existing. The audit's recoverability promise is broken for the highest-leverage promotions.

**Disposition:** Either rule that the `ProvenanceSummary` freezes the `PROPOSED_FROM`-source content too (widening DDR-002's ProvenanceSummary content — a coordination item with RBT-15), or rule that any `PROPOSED_FROM` source of a durable promotion is itself promoted to durable/never-expire. State which.

#### Finding M-6: Cross-source signal correlation is undefined — Operational and RG-override can double-count the same latent fact

**Location:** §Signals & Detection → "Signal taxonomy" (two independent promotion-path sources: RG override-recurrence and Operational `ObservedPattern`); de-dup is stated only as "KG as ground-truth-checked-against."

**Description:** The same underlying reality (e.g., "technology X is weak in environment Y") can surface **simultaneously** as an Operational weakness-`ObservedPattern` **and** as RG override-recurrence (architects override X *because* it's weak). The taxonomy keys signals "by `PROPOSED_FROM` source," treating the two sources as independent, and the threshold mechanism counts them independently. The only de-dup ruled is against **already-promoted** knowledge — not against **concurrent multi-source signals for the same not-yet-promoted fact**.

**Why material:** Two correlated weak signals can jointly cross a threshold calibrated for one strong signal, causing **premature promotion** of a fact neither source independently justified — and the audit would show two "independent" sources lending false corroboration.

**Risk if not addressed:** The gate promotes on manufactured corroboration; the EA's diagnosis (which weighs "recurrence strength") is fed double-counted recurrence. This is a correctness hole in the detection layer that no calibration value fixes (it's structural).

**Disposition:** Rule whether cross-source signals for the same target are **correlated/de-duped** before threshold evaluation, or **deliberately additive** (and if additive, that the EA diagnosis must be told the corroboration is from correlated sources). At minimum, name it as a gap with a reversal path rather than leaving the taxonomy's independence assumption silent.

#### Finding M-7: "Rejected verdict is terminal and won't re-surface" lacks a de-dup-against-rejected mechanism and forecloses changed-circumstances re-proposal

**Location:** §The EA Gate → "Authorship & gate completion" ("a **rejected verdict is terminal and durably explained** so the same gap doesn't re-surface and re-burn EA attention").

**Description:** Detection counts recurring signals. A rejected gap that *keeps recurring* will keep being detected — yet the draft asserts it "doesn't re-surface." The only de-dup ruled is against already-**promoted** knowledge; there is **no de-dup-against-rejected** mechanism stated. Separately, "terminal" forecloses re-proposal even when circumstances change (the EA's "not genuine" call was wrong, or the world moved) — but a gap recurring at 10× the original rate is arguably *new* evidence that warrants re-evaluation.

**Why material:** The claimed property ("won't re-surface") has no stated mechanism, and the absolute-terminal posture has no escape for legitimately changed circumstances — two opposite failure modes from one under-specified rule.

**Risk if not addressed:** Either detection re-surfaces rejected gaps and re-burns EA attention (the failure the rule claims to prevent), or a genuinely-now-promotable recurring gap is permanently suppressed by a stale rejection. Both degrade the loop.

**Disposition:** Rule the de-dup-against-rejected mechanism (mirror the against-promoted de-dup) **and** rule whether/when a rejected candidate may re-open (e.g., a much-higher recurrence threshold or an EA-initiated re-open), or name the re-open question as an explicit gap.

#### Finding M-8: PostgreSQL placement of EA-owned calibration config is asserted by analogy, not grounded in ADR-002 §2.4

**Location:** §Signals & Detection → "Calibration-parameter mechanism" ("Config store: **PostgreSQL** (DDR-001's existing workflow/staging assignment)"); cross-check ADR-002 §2.4 (PostgreSQL = **workflow, audit, and staging** state) and §6 check #3 (store-authority).

**Description:** ADR-002 §2.4 names exactly three PostgreSQL state classes: workflow, audit, staging. EA-owned promotion-governing **calibration config** is none of these cleanly — it is operational/governance configuration. The draft places it in PostgreSQL "by analogy" to workflow/staging without naming which class it falls under or that it is a slight extension.

**Why material:** Store-authority is a mandatory ADR-002 §6 check (#3). Asserting a store placement that isn't crisply within the §2.4 division invites a conformance flag, and "config" arguably has governance significance (it controls what enters authoritative KG) that could argue for a different owner (e.g., governance-state-manager, RBT-22).

**Risk if not addressed:** A §6 check-#3 flag at three-hat; or a later realization that promotion-governing config should be a first-class governance-state concern, forcing a move.

**Disposition:** Name the §2.4 class the config falls under (most defensibly "workflow/staging" with a one-line justification) **or** route config ownership to governance-state-manager (RBT-22) and confirm the store. A sentence closes it.

#### Finding M-9: Interim enforcement is unnamed for invariants whose mechanism is routed downstream — no exposure window (contrast R27)

**Location:** Multiple: config "EA-owned" (RBAC mechanism = routed gap); conditional carry-forward (mechanism + CI-invariant → RBT-15/RBT-33); (and B-2's retracted read-exclusion). Cross-check DDR-002/R27, which names its acceptance→RBT-33 **exposure window** explicitly.

**Description:** DDR-003 rules several **invariants** (EA-only config changes; no-silent-default-to-unconditional on supersession) but routes their **enforcement mechanism** to RBT-15/RBT-33/RBAC. DDR-002 set the corpus precedent (R27): when an invariant is ruled but not yet mechanized, the **exposure window is named as a tracked risk**. DDR-003 names the *values* as deferred but does **not** name the *interim un-enforcement of these invariants* as an exposure.

**Why material:** "EA-owned config" with no enforcement until the routed RBAC gap closes is governance-by-assertion over the parameters that directly control promotion behavior (an actor with store access could drop the detection threshold to 1 and flood the gate). Conditional carry-forward un-enforced re-opens the silent-default-to-`unconditional` failure DDR-002 says check #19 *cannot* catch.

**Risk if not addressed:** Un-named interim exposures on safety-relevant invariants; the project loses the honest "named gap, tracked" discipline R27 established, and the exposures surface as surprises rather than tracked debt.

**Disposition:** Add a brief **exposure-window** subsection (R27 pattern) naming the asserted-but-not-yet-enforced invariants and their mechanization owners/timelines.

#### Finding M-10: Audit-trail integrity (tamper-evidence) is unaddressed for the PostgreSQL operational trail

**Location:** §Retention → "Audit policy" (PostgreSQL trail "append-only"); cross-check DDR-002 §7 CI-only set (which includes **tamper-detection** per R27) and DDR-001 governance-decision immutability (Neo4j append-only).

**Description:** The Neo4j `PromotionDecision` rides DDR-001's append-only governance immutability. The **PostgreSQL operational trail** — the second audit record, and the carrier of the calibration-config change log — is described as "append-only" with **no integrity/tamper-evidence requirement**. For the record that underwrites the platform's accountability thesis, append-only-by-convention (vs. enforced/tamper-evident) is a gap.

**Why material:** The recoverability requirement makes this trail load-bearing for "who approved what, when, on what basis." If it can be silently altered, the accountability guarantee is only as strong as PostgreSQL access control — which is the routed-RBAC gap.

**Risk if not addressed:** The governance audit trail is mutable in practice; a disputed or erroneous promotion's record cannot be trusted; the auditability moat (ADR-001) is weaker than claimed.

**Disposition:** Rule an integrity posture for the PostgreSQL trail (append-only enforced / tamper-evident / hash-chained as appropriate) or route it explicitly to the SDD **with** a named requirement, not silence.

#### Finding M-11: Diagnosis-basis auditability — the five-dimension *inputs* are captured, but the EA's per-dimension *assessment* is not ruled to be

**Location:** §The EA Gate → "Diagnosis policy" ("Weights and decision rules are EA judgment … not ruled") + "carries the diagnosis substrate (… the five-dimension inputs)" + §Retention recoverability ("on what diagnosis basis").

**Description:** The draft rules *which* five dimensions a decision must weigh and that the `CandidatePromotion` carries the dimension **inputs**. But it leaves the EA's **per-dimension assessment / verdict** as unstructured judgment, while simultaneously promising the audit can answer "on what diagnosis basis." So the diagnosis basis recoverable from the audit is the *inputs* plus free-text EA rationale — not a reproducible, queryable per-dimension assessment.

**Why material:** For a platform whose moat is *auditable, queryable reasoning*, the highest-stakes decision (what becomes authoritative encoded knowledge) is recorded with weaker structure than the reasoning the platform captures everywhere else. It is a soft spot against ADR-001's own thesis.

**Risk if not addressed:** "Why was this promoted?" is answerable only by reading EA prose, not by traversal — the platform under-delivers its auditability promise at precisely the gate that matters most; promotion-quality analysis over time (R27→RBT-27 consolidation health) has no structured substrate to work from.

**Disposition:** Rule whether the EA's per-dimension assessment is captured **structurally** (e.g., a per-dimension verdict recorded on the `PromotionDecision`/audit) vs. free-text, even if the *weighting* stays judgment. This need not assert weights (R29-safe); it asserts *capture*.

#### Finding M-12: Internal cross-reference integrity — the draft references numbered sections (§3.2, §5.3, §6.1 …) that do not exist

**Location:** Throughout — Decision.1–.6 cite "(§3)…(§6)"; body prose cites "§3.2", "§3.3", "§4.2", "§5.2", "§5.3", "§6.1" — but the body section headings are **unnumbered prose titles** ("The EA Gate (the spine)", "Signals & Detection", "Retention, Audit, Provenance-Survival", "Conditional Governance & Retraction").

**Description:** The substrate handover used its own §3/§4/§5/§6 numbering; the draft inherited the §-references but rendered the sections as unnumbered titles, so every numbered cross-reference **dangles** (no numbered anchor resolves). A reader must reconstruct the mapping by section order.

**Why material:** This is the **exact** defect class DDR-002 caught as its acceptance-review **M-A** ("dangling §8 cross-references, a substrate→template restructure artifact"). Cross-reference integrity is load-bearing for a governance document that other DDRs/SDDs will cite by section.

**Risk if not addressed:** Every internal pointer is unresolvable; downstream citations to "DDR-003 §5.3" have no target; the navigability the Cross-References section promises is broken.

**Disposition:** Number the substantive sections (e.g., §3 EA Gate, §4 Signals, §5 Retention, §6 Conditional) to match the existing references, or convert all references to named-section form. Numbering is the lower-churn fix and matches the substrate.

#### Finding M-13: Cross-reference mis-attribution — DDR-001 check #4 is listed among "DDR-002 §7 invariants"

**Location:** §Cross-References → "← DDR-002 v1.1.0 … §7 invariants **#4**/#9/#15/#19/#20/#21."

**Description:** **#4 is a DDR-001 conformance check** (proposal-visibility / SOFIA-never-self-modifies), not a DDR-002 §7 invariant. DDR-002's proposal-visibility is **#9**, which *defers to* DDR-001 #4. The draft itself elsewhere correctly attributes "proposal-visibility / check #4" to DDR-001 — so the Cross-References lumping of #4 under "DDR-002 §7 invariants" is an internal contradiction.

**Why material:** Precise invariant attribution is exactly what a governance cross-reference exists to get right; the error will propagate into SDD citations.

**Risk if not addressed:** Downstream readers look for a non-existent "DDR-002 §7 #4" or mis-route the proposal-visibility dependency.

**Disposition:** Move #4 to the DDR-001 citation line; keep #9/#15/#19/#20/#21 under DDR-002 §7.

### 2.3 COSMETIC — noted, no-action (or trivial)

- **C-1 — Durable-class double-listing.** §Retention "Durable / never-expire" lists "terminal-`promoted` `CandidatePromotion`" *and* "all terminal `CandidatePromotion`s (rejected included)"; the latter superset already contains the former. Trim to one entry. *(Substance is correct — both promoted and rejected terminals are durable.)*
- **C-2 — Invariant-taxonomy overlap.** "approval precedes materialization," the "audit-first invariant," and DDR-002 check #15 are presented as distinct but substantially overlap (M-4 touches this). A one-line note clarifying their relationship would prevent apparent redundancy.
- **C-3 — "the promotion audit trail" is ambiguous** in the durable class (Neo4j `PromotionDecision` vs. PostgreSQL trail vs. both). Both are durable; name both.
- **C-4 — "Seven forks" vs six labelled clusters.** The substrate-complete comment labels clusters B/A/D/E/F/G (six); "seven" presumably counts the framing/empirical-warrant cut. Confirm no "Cluster C" concern was dropped between session and draft. *(No evidence of a dropped cluster — the draft realizes all six labelled clusters; recorded for completeness.)*

### 2.4 No-drift confirmations (POSITIVE — required per DIRECTIVE-007 §7.2)

- **P-1 — Substrate fidelity (complete).** The draft faithfully realizes **all six ratified clusters** — B (EA gate: authority/diagnosis/no-leak/batch/authorship), A (signals/taxonomy/calibration mechanism/derive-promote seam), D (retention classes/invariants), E (two-record audit/audit-first/ProvenanceSummary), F (conditional carry-forward/multi-condition interim posture), G (retraction remedy boundary) — and the framing cut line. No ratified item was dropped.
- **P-2 — R29 realized in full.** The parameter-mechanism-now/values-deferred ruling is realized on all six R29 facets (what / who / stored / changed / audited / read). **No DDR-038 values (10 / daily / 90) asserted** — the R29 decline is honored.
- **P-3 — R30 and R31 realized.** The derive/promote seam (§4.3) and the supersession-vs-retraction remedy boundary (§6.3) match their ledger rulings. *(M-2 flags a residual DDR-002-text reconciliation, not a draft-vs-R30 drift.)*
- **P-4 — Correct schema-evolution tracking.** The draft cites the **final edge-only** retraction shape (no stale `applicability_state: retracted`), the `archived` status, the `ProvenanceSummary` + `MATERIALIZES_PROVENANCE_OF`, and §7 #15/#20/#21 — all as landed by RBT-43 (DDR-002 v1.1.0). It did **not** inherit the stale earlier-comment vocabulary.
- **P-5 — One-way reference discipline (R8) honored.** DDR-003 references DDR-001/DDR-002, never the reverse; the boundary map cleanly routes architecture → DDR-001, schema → DDR-002, service → SDD.
- **P-6 — DIRECTIVE-034 substrate gate satisfied.** The DDR is deliberation-grounded (the ratified RBT-14 design session); the Rationale states it; no fabricated alternatives.
- **P-7 — R18 form discipline.** 0.1.0 PROPOSED, single-artifact authoring, no premature version trail, Platform-Version row correctly omitted for the pre-release project.
- **P-8 — Proposal-visibility / never-self-modify correctly cited.** The draft correctly attributes the proposal-visibility invariant to DDR-001 check #4 and grounds the gate in ADR-001 §2.5 — the spine reading is accurate. *(M-13 is a single mis-placement in the Cross-References list, not a conceptual drift.)*
- **P-9 — Operational track-record signal source retained.** The reboot's advance over the prior-SOFIA RG-only model (DDR-038) is deliberately carried — consistent with DDR-001's feedback-loop data-path and DDR-002's `PROPOSED_FROM` targets.

---

## §3 Forward-Pointer Triage

Items surfaced that may warrant tracking beyond the DDR-003 acceptance cycle. **No tickets minted** (DIRECTIVE-025); proposals only, for operator disposition.

| Source finding | Candidate | Summary | Proposed disposition |
|---|---|---|---|
| B-1 | (existing) RBT-15/RBT-16/RBT-17 + possible ADR-002/DDR-001 touch | `CandidatePromotion` + materialized-KG-node write-authority assignment | Reconcile in DDR-003 acceptance cycle; if it requires an ADR-002/DDR-001 statement, route there — do **not** absorb silently into an SDD. |
| B-2 | DDR-002 amendment + RBT-33 | Retracted-node read-exclusion invariant (parallel to #19), safety-critical tier | Add invariant on first acceptance pass; mechanize at RBT-33. |
| M-1 | RBT-27 (parked) + operational onboarding | Loop-liveness/exercise health signal + EA-concentration/delegation backpressure | Name as deferred concerns with R17-style reversal path in DDR-003; health metric → RBT-27/onboarding. |
| M-2 | DDR-002 amendment (wording) | §2.3 "entry into the KG is EA-gated" → staging/authoritative-tier seam language | Additive MINOR clarification, or DDR-003 reconciliation note. |
| M-5 | RBT-15 (with DDR-002) | `ProvenanceSummary` content coverage of `PROPOSED_FROM`-source layer | Resolve during RBT-15; may widen ProvenanceSummary content. |
| M-6 | RBT-16/RBT-17 (detection) | Cross-source signal correlation/de-dup policy | Rule or name-as-gap in DDR-003; mechanics → detection SDD. |
| M-9 | (DDR-003 §) | Named exposure-window subsection for asserted-but-unenforced invariants | Add to DDR-003 on acceptance pass. |

---

## §4 Audit Outcome

> **FAIL (this antagonistic pass).** **2 BLOCKING** (B-1 write-authority unhomed vs ADR-002 §2.6; B-2 retracted-node read-exclusion asserted without an enforcing invariant), **12 MATERIAL**, and **4 COSMETIC**, against a strong POSITIVE no-drift set (9 confirmations). The draft is a **high-fidelity realization of the ratified substrate** — the failures are concentrated where the substrate itself left cross-document seams unreconciled (B-1, M-2), where ruled invariants are asserted without enforcement or exposure-naming (B-2, M-9), and where the retention/detection/audit machinery is under-specified at its edges (M-3 through M-7, M-10, M-11). Two findings are pure document hygiene with direct DDR-002 precedent (M-12 dangling §-refs ≈ DDR-002 M-A; M-13 invariant mis-attribution).

The three-hat acceptance gate is **not satisfied** until at least the two BLOCKING findings are dispositioned. Per DIRECTIVE-032 §32.4, convergence requires a subsequent pass surfacing zero new and zero unresolved findings; the corrective authoring returns to the primary (DDR-003) session — this review is verification-only and authors no fixes.

**Honest scoping note (DIRECTIVE-032 §32.4.1):** the runtime behaviors B-2 and M-4 turn on (does the gateway actually exclude retracted nodes; does the two-store write order hold) are **deferred-to-runtime-verification** at RBT-15 — zero-findings convergence here would still not be zero-defect certification of those seams.

---

## §5 Cross-References

- **Authority for this review:** DIRECTIVE-032 (antagonistic review / continuity check); DIRECTIVE-007 §7.2 (severity vocabulary).
- **Document reviewed:** `docs/ddr/DDR-003-feedback-loop-governance.md` v0.1.0 PROPOSED + `~/Downloads/ddr-003-substrate-handover.md`.
- **Coherence anchors:** ADR-001 v1.0.0 (§2.5, §5.3); ADR-002 v1.0.0 (§2.4, §2.6, §6); DDR-001 v1.1.0; DDR-002 v1.1.0 (RBT-43 landing); Reboot Decision Ledger R22/R24/R25/R26/R27/R29/R30/R31.
- **Tracking surfaces (for the corrective session):** RBT-14 (this), RBT-43 (landed), RBT-15/RBT-16/RBT-17/RBT-22/RBT-25/RBT-27/RBT-33.
- **Disposition tracking:** to be recorded against the DDR-003 corrective authoring + the eventual three-hat review of record (DIRECTIVE-007).

---

*End of antagonistic review — DDR-003 Feedback Loop Governance (RBT-14), 2026-06-22.*
