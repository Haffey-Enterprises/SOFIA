# RBT-59 — ADR-008 Pre-Authoring Deliberation Record

| Field | Value |
|---|---|
| **Session** | RBT-59 authoring leg, 2026-07-17 (claude.ai authoring surface) |
| **Artifact** | ADR-008 — Ground-Truth Mutation Governance (`docs/adr/ADR-008-ground-truth-mutation-governance.md`) |
| **Status** | Deliberation COMPLETE — six items ratified per item by Tad. ADR drafted PROPOSED v0.1.0. Next: design-review-loop. |
| **Substrate (fresh-fetched, not recalled)** | ADR-001, ADR-002, DDR-001 (Decision.5), DDR-002 (§2.2/§2.3/§2.4/§5/§6/§7 #8/#15/#21/#22), DDR-004 (§1/§4/§6), SDD-001 (§3.4.3/§3.5/§3.5.2/§3.6/§4.4/§9), triage-001 Appendix A charter, RBT-59 ticket, Reboot Decision Ledger R30 (verbatim), `adr-template` + `author-decision-record` SKILLs |

**Note on ignored inputs (per Tad, 2026-07-17):** the two "carried-forward rulings" in the kickoff and the RBT-59 run-019 comment were test-generation / sandbox exercises — *not* load-bearing. All run-* ledgers and the `adr-003-*` / `adr-004-*` sandbox fixtures are mock agent-loop exercises. None influenced this deliberation; both source-class postures (Environment, distillation) were deliberated fresh.

---

## Item 1 — Doctype & number (RATIFIED)

New standalone **ADR-008**, slug `ground-truth-mutation-governance`. Doctype ruled ADR (platform principle: survives deleting all services; cited by DDR-003, the ingestion ADR, multiple SDDs). Number: the ADR ladder ADR-003–007 is fully reserved by standing RBT tickets (RBT-9 Platform Patterns, RBT-10 ingestion, RBT-11 Directives Bridge, RBT-28 Encoding, RBT-29 Operational Feedback); this record is triage-created and was never in that ladder, so it takes the next free number, ADR-008. Slug `ground-truth-mutation-governance` chosen over `kg-entry-governance` — covers un-promotion (not just entry), scopes to ground truth (excludes RG capture), matches the RBT-59 title. **Consequence tracked:** the "KG-entry-governance ADR" subject-name pointers in DDR-002/SDD-001/DDR-001/charter resolve to ADR-008 at the pointer-resolution pass (RBT-59 acceptance criterion).

## Item 2 — Warrant & core-decision frame (RATIFIED)

**Warrant:** ADR-001 §2.5 authorizes only promotion of SOFIA's own reasoning (EA-gated); it reaches neither the broader ground-truth-mutation class nor un-promotion. Four accepted records carry interim un-homed postures routed here (DDR-001 Decision.5, DDR-002 §2.3, §2.4/§5, SDD-001 §3.5.2); DDR-003 is blocked on this record.

**Frame (ratified):** the invariant is **human accountability over enterprise ground-truth mutation**; the **form of the control** is calibrated per source class. Accountability is per-write for gated/reviewed classes, **per-policy** for the observational class. Umbrella term **"accountability control"** (not "checkpoint" — which wrongly presumes a per-write gate). **Altitude line:** ADR fixes invariant + accountability + control-*type* per class; downstream fixes control *form* + mechanics.

## Item 3 — Per-source-class calibration (RATIFIED, four classes + lifecycle sharpening)

- **Promotion** → existing EA per-write gate (built: DDR-002 §5, §7 #15). ADR homes the general authority; §2.5 cited for its narrow sub-case.
- **Authoritative-source ingestion (Catalog/Standards)** → pre-entry human **fidelity** verification of the captured representation, gating official entry. Affordable (deliberate, low-volume — off R30's bottleneck). Institutionalizes the capture-fidelity failure mode (R30/R3/R23). New commitment; mechanics → ingestion ADR-004 / SDD-001 §3.6. Boundary: mirrored `GateDecision` (external authority) is out of scope.
- **Operational distillation** → substantive, **evidence-visible** human review of the **distinct distilled judgment**, distinctness-bounded (per distinct lesson, not per observation → off R30's bottleneck; raw signal stays in external SoR). Distillation ≠ Environment: a distilled *judgment* is an inference whose self-assigned confidence can't gate its own pollution (circularity). Supersedes R30's "staging tier / non-gated" inference (criterion-shift; R30's derive/promote seam and declined-gate-all constraint survive). Realized via candidate-`ObservedPattern` (routed → DDR-003 + future DDR-002 amendment). Reviewer role → DDR-003.
- **Environment (CMDB)** → per-policy reliability-**weighting** at retrieval, **no** per-write gate. Grounds: volume (R30 bottleneck), plane already ages (DDR-004 aging basis, ACCEPTED), not authoritative selection knowledge (R30 surviving distinction). Accountability per-policy (human owns the weighting posture, DDR-004 §6). Control-*type* rests on the design-fixed form; constants held contested (n=0).

**Lifecycle sharpening (ratified):** the per-class control governs the full mutation lifecycle — **entry + transition + withdrawal** — not just first entry (broadens the item-2 scope). Surfaced by Tad's expiry/revalidation question.

**Distillation additions (ratified, from Tad's question):**
- **Resolve/supersede/re-activate of a distilled lesson** = a distillation judgment → same class-4 review.
- **Revalidation obligation:** a distilled lesson may not persist authoritative indefinitely without re-grounding (Operational is `native_confidence`, non-aging — unlike Environment it doesn't self-correct); a mechanism must surface stale lessons (trigger: `last_observed_at` cold while `active`) for governed transition. Cadence/trigger → DDR-003.
- **Expire-not-delete:** resolution is read-exclusion + retention-demotion (`archived`), never hard-delete — retained, fully traceable.
- **Provenance-survives-mutation:** verified against DDR-002 §4 — `Evidence` freezes `fact_summary` + `source_node_version`, `SOURCED_FROM` is `rebind:pinned` (not re-pointed on supersession), cited `ObservedPattern` never deleted. Capture is sound and plane-uniform. **Caveat (finding):** the frozen-provenance survival guarantee (`ProvenanceSummary`, §7 #20) is **promotion-scoped**; a design that *consumed* a pattern without promoting it relies on RG Evidence under bounded retention (DDR-001 Versioning; DDR-003 windows) and could age out the graph-native trace. ADR commits the survival *requirement*; extending the mechanism → named DDR-002 + DDR-003 follow-up.

## Item 4 — Un-promotion authority (RATIFIED)

Un-promotion = withdrawal-leg of the promotion class → same per-write EA gate. ADR homes the upstream authority (ADR-001 §2.5 reaches promotion only; DDR-002 §7 #21 routes un-promotion authority here). Instance: built retraction shape (DDR-002 §5 / §7 #21; SDD-001 §3.5.4). Never a bare delete (retained, traceable — consistent with the provenance-survival principle). Remedy-boundary held for item 5. Known edge: #21 traces to *an* approving decision not the *governing* one — named schema/detection gap, ADR sits above it.

## Item 5 — ADR ↔ DDR-003 boundary (RATIFIED)

ADR owns invariant + accountability + control-type + lifecycle/never-delete. **Remedy-boundary (supersede vs. retract) and all governance policy** (criteria, thresholds, cadence, retention, roles, multi-condition composition) → DDR-003. ADR does **not** rule the remedy-boundary (accountability holds identically whichever remedy applies; DDR-002 §2.4 already routes it to DDR-003). **Citation direction:** DDR-003 is a downstream consumer citing this ADR as authority; the ADR never lists DDR-003 as an upstream it depends on (forward, subject-named).

## Item 6 — Cross-class precedence (RATIFIED)

Cross-class conflict → **withhold-and-escalate to human resolution**; a lighter-control class's mutation never silently overrides a heavier-control class's human-accountable decision. Observational/ingested reality never silently overrides an EA-set governance scope. Fail-safe = withhold, not admit. Interim instance: SDD-001 §3.5.2 `SCOPE_CONFLICT` block (n=0 — costless now). Richer disposition → DDR-003.

---

## Standing to-dos

1. **RBT-59 three-layer capture at landing** — record ADR-008 allocation + resolve the DDR-002/SDD-001/DDR-001/charter "KG-entry-governance ADR" subject-name pointers to the concrete ADR-008 ID. (This surface's Linear capture; git is Tad's.)
2. **Named follow-ups to route** (never silent): (a) provenance-survival extension to decision-consumed Evidence → DDR-002 §4/§6 + DDR-003 retention classes; (b) executed-retraction governing-verdict detection analogue → DDR-002 §7 / DDR-003; (c) revalidation cadence/trigger → DDR-003; (d) candidate-`ObservedPattern` shape → future DDR-002 amendment + DDR-003.
3. **Deliberation record** — durable placement `agent-loop/deliberation/adr-008-ground-truth-mutation-governance/record.md` is a git transaction (Tad's); this project doc is the interim carrier.

*Next: design-review-loop (three-hat + coherence) on ADR-008 PROPOSED v0.1.0 → decision-bearing findings → Tad rules remainder → converge → land; pointers resolve to the concrete document ID.*
