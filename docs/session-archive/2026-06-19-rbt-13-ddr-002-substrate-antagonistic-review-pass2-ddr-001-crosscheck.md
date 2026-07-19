# File: docs/reviews/2026-06-19-rbt-13-ddr-002-substrate-antagonistic-review-pass2-ddr-001-crosscheck.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-19
# Description: Pass-2 addendum to the DDR-002 substrate antagonistic review — cross-verification against DDR-001's ACCEPTED body (now available). Discharges the M-14 alignment limitation, adds one verified BLOCKING contradiction, corrects one prior blocker, and reinforces prior findings with direct DDR-001 citations.

# Antagonistic Review — DDR-002 Substrate — Pass 2 (DDR-001 Cross-Verification) — 2026-06-19

| Field | Value |
|---|---|
| **Review Date** | 2026-06-19 |
| **Reviewer** | claude.ai antagonistic reviewer (LAA / SA / EA hats), DIRECTIVE-032 — verification-only |
| **Scope** | Cross-verification of Pass-1 findings against `DDR-001-data-architecture.md` v1.0.0 ACCEPTED (`develop`@`15ff20f`), now supplied. Updates dispositions; surfaces findings revealed by the new substrate (DIRECTIVE-032 §32.4). |
| **Authority** | DIRECTIVE-032 §32.4 (review-until-zero-findings cadence — subsequent passes verify prior findings AND surface new ones revealed by new substrate) |
| **Outcome** | **STILL PASS WITH FINDINGS — BLOCKING present.** Net BLOCKING count unchanged at 3, but the *composition* changed: B-2 corrected down to MATERIAL; **B-4 (DDR-001 Operational-plane contradiction) added** — a verified, black-and-white conflict between the substrate and its ACCEPTED parent. **Do not author until B-1, B-3, B-4 clear.** |

> This addendum supersedes the Pass-1 disposition of each finding it names; unnamed Pass-1 findings stand as written. Read with the Pass-1 review.

---

## §0 Headline: the cross-check earned its keep

Pass-1's M-14 flagged that DDR-002's alignment with DDR-001 was *asserted, not verified* (DDR-001 was unfetchable). With DDR-001 now in hand, the verdict splits cleanly:

- **The bulk of the alignment is real and verified (M-14 largely discharged).** The feedback-loop and RG vocabulary the substrate leans on matches DDR-001 verbatim or near-verbatim: `CandidatePromotion`, `PROMOTES_TO_KNOWLEDGE`, `SOURCED_FROM` (with `DREW_FROM` correctly deferred — DDR-001 lists it only illustratively), the `ReasoningProgress` (ASA) / `ReasoningSession`-lifecycle (AOE) split, the six typed-conclusion kinds, the Solution dual-home (graph node + Firestore snapshot), the five-plane+Extension model, the sole-owner gateway, and the substitution-contract capability bar (DDR-002 §2.6 correctly defers the bar to DDR-001, which establishes it). On its dominant surface, the substrate faithfully implements DDR-001.

- **One contradiction the substrate alone concealed (new BLOCKING, B-4).** The Operational plane. This is exactly the class of defect M-14 existed to catch: a schema-session ruling (R24) silently re-characterizing a DDR-001-owned plane definition, producing a live conflict with the ACCEPTED parent.

The net is *more* confidence in the substrate's craftsmanship and a *sharper, verified* blocker — which is the point of fresh-fetch over recall.

---

## §1 NEW BLOCKING

### Finding B-4: The substrate's R24-grounded Operational plane directly contradicts DDR-001's ACCEPTED Operational plane

**Location:** Substrate §2.3 (Operational — "durable distillation, not telemetry"; `ObservedPattern`; "**No TTL**"; "does not mirror transient SoR telemetry"). DDR-001 *Two-Graph Model → KG plane table* (Operational row) + *cross-cutting KG invariants* + *Versioning table*.

**The contradiction, verbatim from each side:**

| Axis | DDR-001 v1.0.0 ACCEPTED | DDR-002 substrate (R24) |
|---|---|---|
| Plane role / nature | "live operational signal"; source-class "observability / AIOps telemetry" | "the track-record graph … durable distillation, **not telemetry**" |
| Retention | cadence "near-real-time, **TTL-bounded**"; cross-cutting invariant "operational data **TTL-governed**"; versioning row "Operational data expiry \| **TTL-governed**" | "**No TTL**" |
| Illustrative content | "incident patterns, **performance profiles, SLO violations, capacity signals**" | `ObservedPattern` only (dual-polarity strength/weakness); raw telemetry excluded by R24 |

The two are not reconcilable as written. DDR-001 names a TTL-governed, near-real-time telemetry plane carrying SLO violations and capacity signals; the substrate names a no-TTL durable-distillation plane that explicitly excludes telemetry and carries only `ObservedPattern`. ("incident patterns" ≈ `ObservedPattern` is the one overlapping item; everything else, and the TTL axis outright, conflicts.)

**Why this is a contradiction, not a refinement-in-bounds.** R24 was ratified **2026-06-19 in the RBT-13 (DDR-002) session — after DDR-001 had already landed ACCEPTED** — and its ledger text scopes it to "govern plane **content** across the schema." But *plane definition and nature* is a DDR-001-owned concern: DDR-001's Appendix assigns "Plane definitions … " to **DDR-001**, and DDR-001 §"Pre-Acceptance Conditions" states "**Ruling stands as authored.**" R8 makes the reference one-way (architecture → schema; "DDR-001 not re-opened"). So R24, a schema-session ruling, has re-characterized a DDR-001 plane definition without re-opening DDR-001 — and the substrate now carries a schema (no-TTL `ObservedPattern`) that does **not implement** its accepted parent's Operational plane (TTL-governed telemetry). DDR-002 would *contradict*, not *implement*, DDR-001.

**Why blocking.** A schema that contradicts a named invariant of its ACCEPTED parent ("operational data TTL-governed") fails the R8 / ADR-002 §6 conformance bar at three-hat. It also strands DDR-001 in an inconsistent state: its Operational row and its TTL invariant are now stale relative to the platform's actual intent, but it reads ACCEPTED and unconditioned.

**Risk if not addressed.** Either (a) the schema ships and DDR-001's Operational plane definition is silently wrong-in-the-record (the exact drift the Reboot exists to prevent), or (b) an implementer builds to DDR-001 (TTL telemetry) while another builds to DDR-002 (durable `ObservedPattern`), splitting the platform's most behaviorally-loaded plane.

**Disposition (returns to primary session — this is a governance decision, not an authoring tweak).** Resolve the contradiction *before* authoring DDR-002. The honest options:
1. **Coordinated DDR-001 amendment.** Treat R24 as the architecture-level refinement it actually is, and amend DDR-001's Operational plane (role, cadence, TTL invariant, versioning row) to the durable-distillation model — a MINOR amendment to an ACCEPTED DDR, with its own three-hat pass. This accepts a bounded re-open of DDR-001, which R8/R23's "don't re-open" guidance discourages but does not forbid when the architecture itself moved.
2. **Re-scope R24.** If R24 was only ever meant to constrain *how* Operational content is written (distill, don't dump) *within* DDR-001's TTL-governed telemetry frame, reconcile the substrate's "No TTL / not telemetry" language back toward DDR-001 — i.e., `ObservedPattern` is a TTL-governed distillation, not a TTL-free durable record. (This reading is hard to square with the substrate's explicit "No TTL," so option 1 looks more honest.)

Either way, this is a **criterion-shift** (Operational's nature was re-decided during the schema session) that must be surfaced and ratified as such — not absorbed silently into DDR-002.

---

## §2 Corrected dispositions (DDR-001 changes the Pass-1 call)

### B-2 → corrected to **MATERIAL** (DDR-001 supplies the architecture Pass-1 found missing)

Pass-1 called the proposal→fact write path "no owner" and rated it BLOCKING. DDR-001 supplies the architecture-level coverage I lacked the source to see:

- DDR-001 §Feedback-Loop fixes a "**mandatory, non-bypassable EA gate** (the loop proposes, a human materializes)," with materialization = "real KG node + `PROMOTES_TO_KNOWLEDGE` edge, provenance-stamped," and a **proposal-visibility invariant** (`CandidatePromotion` excluded from ground-truth traversal until EA-approved).
- DDR-001 conformance check #4: "`CandidatePromotion` proposals are excluded … until EA-approved; **SOFIA never self-modifies the KG**."
- ADR-002 §2.5 makes knowledge-service the **sole writer** — so the materialization *executor* is fixed (knowledge-service), and DDR-001 legitimately routes the `CandidatePromotion` *author* (the scheduled job + EA-review portal) → SDD.
- The namespace question resolves: DDR-001 scopes "ASA is **sole author of reasoning content** (`ReasoningProgress`)" — so `CandidatePromotion`, a feedback-loop *proposal* produced by the scheduled job, is **not** ASA reasoning content and does not need §2.6-style authorship fixing. It is a `:Reasoning:`-namespaced proposal, not ground truth and not `ReasoningProgress`.

**Corrected finding (MATERIAL).** The path is architecturally covered, but two residuals remain: (a) the substrate should *cite* DDR-001's non-bypassable EA gate + ADR-002 §2.5 sole-writer as the explicit controls on the `CandidatePromotion`→`PROMOTES_TO_KNOWLEDGE` write, rather than leaving the writer implicit; and (b) the guarantee is **architecturally stated but not mechanically enforced** — DDR-001 itself marks conformance check #4 "aspirational … not CI-enforced at authoring" (RBT-33). So the non-bypassable gate is a design commitment riding the same unmechanized-enforcement exposure as M-11. *(Note: this residual ties B-2 directly into M-11 and M-9 — the gate is only as non-bypassable as the unbuilt check that enforces it and the read-discipline that hides proposals.)*

### M-2 → corrected to **COSMETIC / routed-to-DDR-001** (Environment is DDR-001-sanctioned; the real R24 conflict is Operational)

Pass-1's M-2 pointed at the Environment plane as a "latent CMDB mirror in tension with R24." DDR-001 *sanctions* Environment as CMDB-sourced (source-class "CMDB / service registry"; node types "deployed services, environments, configuration items"), and the substrate's Environment plane aligns with it. So the substrate is faithful here, not overreaching. The residual R24-vs-Environment question (does a full CI inventory honor "distillation/reference, not mirror"?) is a tension **DDR-001 owns**, not a DDR-002 defect. **Corrected:** Environment alignment with DDR-001 is a POSITIVE; the residual R24/Environment question is routed to DDR-001/DDR-003, not charged against the schema. The *verified* R24 conflict is Operational (B-4), where Pass-1's instinct was right but aimed one plane over.

### M-16 → reframed (DDR-001's "no conditions" precedent does **not** transfer to DDR-002)

DDR-001 landed at plain ACCEPTED with "**No pre-acceptance conditions. Ruling stands as authored.**", treating its forward items as forward *dependencies*. Pass-1 noted DDR-002 should likely carry conditions; DDR-001 establishes that the project *can* land a DDR clean. **Reframed:** that precedent applies only to a DDR with a clean substrate. DDR-002 carries an open design call (B-1) **and** a parent contradiction (B-4) — both genuine acceptance-blockers, unlike anything DDR-001 faced. So DDR-002 cannot inherit DDR-001's "no conditions" posture; it must land PROPOSED (or ACCEPTED-WITH-CONDITIONS) until B-1/B-3/B-4 discharge, then may go clean like DDR-001.

---

## §3 Reinforced findings (DDR-001 supplies the citation Pass-1 lacked)

### M-1 (provenance group must cover origin classes) — **reinforced, now with a named DDR-001 requirement**
DDR-001 conformance check #6: "Every KG node carries provenance; **promoted knowledge is distinguishable from ingested**." The substrate's ingestion-shaped group (`source_class` + `ingested_at`) cannot cleanly express *promoted* vs *ingested* (a node arriving via `PROMOTES_TO_KNOWLEDGE` is not "ingested"). So M-1 is no longer just a coherence concern — it is a **DDR-001 conformance obligation** the current provenance group fails to satisfy. Promotion-provenance is also named in DDR-001's versioning table ("`PROMOTES_TO_KNOWLEDGE` + lineage; **promoted ≠ ingested**"). Severity holds MATERIAL but it is now a verified gap against an explicit parent check.

### B-1 (RG provenance open design call) — **confirmed, framing softened**
DDR-001's "provenance on every node" is a **KG** cross-cutting invariant; for the RG it requires only that Evidence pin its source ("confidence inherited from its source plane," check #5 point-in-time resolution) — it does **not** mandate a provenance group on `Evidence`/`RejectedAlternative`. So the substrate's narrower existence-constraint scope is **consistent with DDR-001** (not a parent violation). B-1 therefore loses its "violates DDR-001" edge but **keeps its BLOCKING status on the original basis**: it is the substrate's own *flagged-for-confirmation open design call* on the capture invariant's auditability, and the structural surrogate rides the same unmechanized enforcement (M-11). An open design call still blocks ACCEPTED.

### M-6 (taxonomy reconciliation) — **reinforced; one of the three lists now confirmed aligned, two still unreconciled**
The `conclusion_type` enum **matches** DDR-001's typed-conclusion kinds ("pattern selection, technology resolution, gap, override, risk, compliance evaluation") — confirmed aligned. But the cross-check now exposes **three** related-but-distinct enumerations to reconcile: `conclusion_type` (6, aligned), DDR-001's feedback **signal classes** ("override-recurrence, gap-recurrence, evidence-quality") and **action classes** ("knowledge promotion … source-quality feedback"), and the substrate's §5 **correction surfaces** (7 items: technology/pattern/capability/integration/risk/compliance/cost). The substrate's "every conclusion_type is a correction surface" claim still doesn't map, and now there is a third axis (DDR-001 signal/action classes) to align against. Reinforced.

### M-7 (Artifact/Solution) — **reinforced with a verified placement conflict**
New sub-finding: DDR-001's Catalog plane illustrative node types include "**solution documents**," but the substrate §2.1 explicitly rules "The ASD/solution is **not** a Catalog node (it is the `(:Artifact:Solution)` keystone)." Reconcile: is the produced ASD a Catalog node (DDR-001 illustrative list) or a standalone non-plane Artifact (substrate)? If DDR-001's "solution documents" means *reference/template* solutions in the catalog (distinct from the *produced* ASD), the two reconcile — but that distinction must be made explicit, because as written they read as conflicting placements of "solution." (DDR-001 *does* confirm the Solution dual-home, which aligns — POSITIVE.)

### M-8 (supersession re-pointing) — **reinforced with an R8-boundary concern**
The substrate's "structural edges track current — **gateway re-points** on supersession" invokes the gateway, whose *pattern* DDR-001 owns. DDR-001's gateway roles (KG read / RG write+read / ingestion) do **not** include supersession-driven structural-edge re-pointing. So the substrate is specifying **new gateway behavior** that is arguably DDR-001's to own under R8's one-way rule. Reinforced: in addition to the atomicity + structural-vs-pinned-classification gaps (Pass-1), verify that "re-point on supersession" belongs in DDR-001's gateway pattern (or is consistent with it) rather than being introduced unilaterally in the schema.

### M-11 (aspirational enforcement) — **strongly reinforced; DDR-001 says so in its own voice**
DDR-001 §Conformance: "**Aspirational checkpoints — enforcement-mechanization is tracked at RBT-33 … not CI-enforced at authoring.**" Both parent and schema now confirm that the integrity invariants are honor-system until RBT-33. The aggregate-exposure finding stands at the top of the risk agenda, now double-sourced. RBT-33 is already broadened ("ADR-002 §6 + DDR-001 conformance checks: 1–3 ADR-002 §6, 4–6 DDR-001-native") — the substrate's DDR-002-native checks add a third tranche to the same unbuilt mechanization, which should be folded into RBT-33's scope and sequenced against the first writing SDD (RBT-15).

### M-5, M-3, M-10, M-12 — **confirmed unchanged**
- **M-5** (ReasoningSession lifecycle domain): DDR-001 also leaves it unspecified ("Lifecycle owned by AOE"; retention/read-scoping deferred to DDR-003/SDD). Confirmed.
- **M-3** (GateDecision `ea_promotion` enum/posture): DDR-001 names the EA gate only abstractly ("non-bypassable EA gate"); the GateDecision-reuse + `gate` enum mismatch + "external-always-SoR" strain are DDR-002 schema concerns, unresolved by DDR-001. Confirmed.
- **M-10** (graph-native retrieval affordance): DDR-001 also asserts "semantic retrieval is graph-traversal-native" without specifying the affordance. Confirmed — the R6 substitute is unrealized in *both* docs.
- **M-12** (`rule_definition` opacity): DDR-001 Standards plane is neutral on it; the option-C opacity / change-impact concern is DDR-002's alone. Confirmed.

---

## §4 New POSITIVE confirmations from the cross-check

- **Feedback-loop + RG vocabulary aligned** (`CandidatePromotion`, `PROMOTES_TO_KNOWLEDGE`, `SOURCED_FROM`, ReasoningProgress/ReasoningSession split, six conclusion-kinds) — verified against DDR-001, not asserted.
- **Solution dual-home aligned** — substrate's `snapshot_ref` + `content_hash` (graph node + Firestore body) matches DDR-001's "dual-homed — graph node in Neo4j + immutable per-version snapshot in Firestore."
- **Substitution-contract bar correctly deferred** — substrate §2.6 ("the precise capability bar is the one DDR-001 establishes") matches DDR-001's dedicated Capability-Bar section (ADR-002 §2.2 → DDR-001).
- **Evidence version-pinning aligned** — substrate's `Evidence.source_node_version` + `fact_summary` matches DDR-001's "version-pinned evidence" + point-in-time check #5.
- **Environment plane aligned with DDR-001** (corrected M-2).
- **Substrate-stability discipline modeled by DDR-001** — DDR-001 carries an explicit Substrate-Stability section naming DDR-002 as its consumer; DDR-002 should mirror this (it gates all 12 SDDs). Confirms Pass-1 C-3.

---

## §5 Refreshed tally and outcome

| Severity | Pass-1 | Pass-2 (this addendum) | Delta |
|---|---|---|---|
| BLOCKING | 3 (B-1, B-2, B-3) | **3 (B-1, B-3, B-4)** | B-2 → MATERIAL; **B-4 added** |
| MATERIAL | 17 | **17** | +B-2; −M-2 (→ COSMETIC) |
| COSMETIC | 6 | **7** | +M-2 |
| POSITIVE | (substantial) | (substantial, +6 verified) | reinforced |

> **STILL PASS WITH FINDINGS — BLOCKING present; authoring gate NOT satisfied.** The three blockers to clear before DDR-002 is authored: **B-1** (resolve the RG-provenance design call), **B-3** (the `Process` dangling-edge defect), and the new **B-4** (resolve the DDR-001 Operational-plane contradiction — a governance decision, likely a coordinated DDR-001 amendment). The MATERIAL agenda is unchanged in substance but now better-sourced; its center of gravity is **provenance coverage** (M-1, B-1, reinforced by DDR-001 check #6), **promotion-path integrity-under-aspirational-enforcement** (B-2, M-9, M-11, M-13), and **taxonomy/placement reconciliation against DDR-001** (M-6, M-7).

**On convergence (DIRECTIVE-032 §32.4).** This pass surfaced one new BLOCKING revealed only by the new substrate (B-4) and corrected one prior call (B-2) — so the surface is still moving; convergence is not reached. The next pass should verify B-1/B-3/B-4 dispositions and the MATERIAL agenda, and — per §32.4.1 — explicitly carry the RBT-33 mechanization window (M-11) and the B-4 governance decision as residual, deferred-to-ratification items rather than treating their resolution-in-prose as closure.

**The meta-point worth keeping.** B-4 existed in the substrate from the moment R24 was ratified, but was invisible until DDR-001 was placed beside it — the substrate cites R24 as settled and self-consistent. This is the verification value of fresh-fetch over recall, and the reason M-14 was worth raising even before it could be answered.

---

## §6 Cross-references
- **Pass-1 review:** `2026-06-19-rbt-13-ddr-002-substrate-antagonistic-review.md` (this addendum updates its dispositions).
- **Newly verified against:** `DDR-001-data-architecture.md` v1.0.0 ACCEPTED (`develop`@`15ff20f`, PR #12).
- **Governing rulings re-touched:** R8 (one-way architecture→schema), R22 (feedback split), R24 (durable-knowledge — the source of B-4), R23 (don't re-open DDR-001).
- **Tickets implicated:** RBT-13 (this DDR), RBT-12 (DDR-001 — candidate for a coordinated MINOR amendment per B-4), RBT-14 (DDR-003 governance), RBT-33 (conformance mechanization — fold DDR-002-native checks in).
