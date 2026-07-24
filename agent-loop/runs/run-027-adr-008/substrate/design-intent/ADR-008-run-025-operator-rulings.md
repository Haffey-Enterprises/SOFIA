# RBT-59 / ADR-008 — Design-Review-Loop Operator Rulings (run-025 + run-026 dispositions)

**Ratified per item by Tad (Executive Architect), 2026-07-17.** Rulings A–F dispose of run-025's eight pass-1 decision-bearing findings; Ruling G disposes of the one that flipped decision-bearing in run-026. These are authoritative design intent for the ADR-008 re-run: each ruling names the conformance ADR-008 must meet, converting its finding from decision-bearing to resolvable. The arbiter reads these as authority; the author derives the scoped edit from them.

**Governing principle established this pass (applies to the whole record):** an ADR is **standalone**. Reboot Decision Ledger rulings (e.g., R30) are *substrate* — they inform the review — but are **never durable in-body ADR citations**. Any reconciliation R30 supplies, the ADR states self-containedly or rests on a durable authority (ADR/DDR/SDD).

---

## Ruling A — Distillation control-type; the R30 supersession (finding `01867665`, §2.2/§2.6)

ADR-008's operational-distillation control — substantive, evidence-visible human review of the **distinct distilled judgment** — stands. It supersedes R30's staging-tier / non-gated-distillation inference on the ratified **criterion-shift** (deliberation Item 3): a distilled *judgment* is an inference whose **self-assigned confidence cannot gate its own soundness**, which is distinct from a non-gated Environment observation. R30's surviving parts — the derive/promote seam and the declined gate-all constraint — remain in force.

- **Conformance:** state the distillation control-type and this rationale **self-containedly** in the ADR body; do **not** name or cite R30 in the ADR.
- **Durable follow-up (Tad, governance):** record the supersession in the Reboot Decision Ledger R30 entry.

## Ruling B — Relationship to ADR-001 §2.5 (findings `b55f71f6` + `47aa7054`, metadata/§2.2/§2.3/§7)

ADR-008 establishes the **general** ground-truth-mutation authority, of which ADR-001 §2.5's EA-gated promotion is now the reasoning-consolidation **sub-case**, and homes the **un-promotion** authority §2.5 does not reach. It supersedes nothing — §2.5 remains valid; `Supersedes: None` stands (house norm for a new principle).

- **Conformance:** (1) add an explicit **"Relationship to ADR-001 §2.5"** statement recording the generalization + subsumption + un-promotion extension, so the position is *recorded*, not asserted in passing; (2) fix the Promotion-class authority citation to the **durable chain** — ADR-001 §2.5 (EA-gated-promotion principle) + DDR-002 §5 / §7 #15 (the built `PromotionDecision` gate into Catalog/Standards). R30 not cited.
- **Durable follow-up (Tad, governance):** forward change-log note in ADR-001 at ADR-008 landing (pointer-resolution pass).

## Ruling C — Environment cross-class precedence reconciliation (finding `dc830833`, §2.2 vs §2.5)

"No per-write gate" governs the **routine** Environment observation stream. The §2.5 cross-class withhold is a **mechanical conflict-detection at the graph gateway** (the sole executor, ADR-002 §2.6), firing **only** on a structural collision with an EA-set governance scope, and escalating *that* write to human resolution. It is **not** a per-write human gate on the observation stream; the human is accountable at the **resolution** step. This is the shape of the ratified interim instance (SDD-001 §3.5.2 `SCOPE_CONFLICT`, a mechanical block).

- **Conformance:** clarify §2.2/§2.5 so both hold — the cross-class withhold is gateway-mechanical on structural collision, human accountability at resolution, routine observation ungated.

## Ruling D — Environment control is capture-time-frozen, not "at retrieval" (findings `db343ac9` + `9d7e8220`, §2.2/§2.6)

The Environment reliability control **is** built and DDR-004 supplies it — but its mechanism is **capture-time**, not retrieval-time. The weighting is the DDR-004 aging derivation: freshness-decayed confidence `base × exp(−Δt/τ)` **derived at Evidence capture and frozen** (DDR-004 §1/§3 — "never recomputed at read"), consumed at reasoning time under the DDR-002 §4 #24 ceiling. Per-policy human accountability is **DDR-004 §6's two-tier calibration governance** of the contested constants (a human ratifies `base`/`τ` by amendment). The **form** is built (DDR-004, ACCEPTED); the **constants** are contested/unvalidated at n=0.

- **Conformance:** (1) correct the Environment control description — **drop "reliability-weighting at retrieval"**; state capture-time-frozen aging + §6 governance; (2) relabel the §2.2 "Built" status to **"form built (DDR-004); constants contested/unvalidated (n=0)."**
- **Refinement of prior intent (non-silent):** this also corrects the deliberation Item 3's own "at retrieval" wording. The mechanism was always capture-time-frozen; "at retrieval" was loose in both the deliberation and the draft.

## Ruling E — Distillation candidate-shape is forthcoming, not present (finding `3f8adee8`, §2.2/§5.2)

The candidate-`ObservedPattern` shape does **not** exist in the ratified schema — DDR-002 §2.3 leaves the distillation checkpoint "explicitly un-decided," and the promotion-boundary `CandidatePromotion` class does not cover it. It is the **additive shape the downstream design introduces** (deliberation Item 3: routed → DDR-003 + a future DDR-002 amendment).

- **Conformance:** earned tense — state the candidate-`ObservedPattern` shape as **forthcoming / additive** (introduced downstream), not as a present schema constraint.

## Ruling F — Un-promotion "same control" qualification (finding `ef3f60e2`, §2.3)

The un-promotion **authority principle** holds — same EA-gated, human-accountable class as promotion. But the **built retraction instance** (DDR-002 §7 #21) traces to *an* approving decision, not the *governing* one, so it does not yet supply promotion's governing-verdict guarantee (#15). ADR-008 §5.3 already concedes exactly this.

- **Conformance:** qualify §2.3's "same control" claim to match the §5.3 concession — the authority is homed; the governing-verdict detection analogue for executed retractions is the **named follow-up** (DDR-002 §7 / DDR-003). This is the same fix as the already-resolvable sibling finding `e08de818`.

## Ruling G — Forthcoming-record references are subject-named, not numbered (finding `4c460bf7`, §7; run-026)

Forward references to **unauthored** records — the forthcoming file-driven ingestion decision record, and the forthcoming feedback-loop governance design — are stated by **subject-name only** in the ADR body and cross-references, **never by concrete identifier**. This is the author-decision-record body-integrity forward-reference rule, already the authority for the resolvable sibling findings (`801bdc56`, `93c9253a` in run-026; `c1aa6fef` in run-025). Concrete identifiers bind only at the downstream record's landing (the pointer-resolution pass), and directionally: other records cite ADR-008 by its now-concrete ID; ADR-008 cites forthcoming records by subject-name.

- **Conformance:** in §7 (and anywhere in the body), replace `"ADR-004 (file-driven ingestion, forthcoming)"` and `"DDR-003 (Feedback Loop Governance, forthcoming)"` with subject-name forms — "the forthcoming file-driven ingestion decision record"; "the forthcoming feedback-loop governance design." This removes the ADR-004 / DDR-004 numbering ambiguity entirely and closes the whole forthcoming-reference class.

---

## Carried follow-ups (named, non-silent — already in the deliberation Standing to-dos; unchanged)

- Provenance-survival extension to decision-consumed (unpromoted) Evidence → DDR-002 §4/§6 + DDR-003 retention classes.
- Executed-retraction governing-verdict detection analogue → DDR-002 §7 / DDR-003 (Ruling F's follow-up).
- Revalidation cadence/trigger for stale distilled lessons → DDR-003.
- Candidate-`ObservedPattern` shape → future DDR-002 amendment + DDR-003 (Ruling E's downstream home).

## Governance acts reserved to Tad (durable, outside the ADR)

- R30 Decision Ledger supersession note (Ruling A).
- ADR-001 change-log forward note at ADR-008 landing (Ruling B).

## Note on the already-resolvable findings

Findings the arbiter already classifies resolvable need no ruling — the author fixes them from their existing named authority (citation, tense, and cross-reference conformance). This addendum governs the findings that were classified decision-bearing across run-025 (A–F) and run-026 (G).
