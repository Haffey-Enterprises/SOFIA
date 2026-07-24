# Disposition Record — run-017-ddr-002 (DDR-002 v1.3.0 review) + cold-read gate

| Field | Value |
|---|---|
| **Session** | RBT-54 authoring session, 2026-07-13 (claude.ai surface) |
| **Basis** | run-017 audit (this folder), 24/24 findings ruled; cold-read gate (stranger test per the governing skill, fresh-context reader, artifact set as sole authority) |
| **Rulings** | P-1–P-8 and CR-1–CR-9, each ratified individually by Tad, 2026-07-13 |
| **Status** | RATIFIED — revisions folded into the staged landing set; run-018 verification draw sequenced |

## Review dispositions (P-set)

- **P-1 — verdict table (RATIFIED):** the 24 verdicts per the audit §2.
- **P-2 — #10 Condition-half scoped (RATIFIED, revision):** edge-backing confined to `PolicyRule` manifests (the case §3's grammar defines); a `Condition`'s manifest is declared-introspectable, consumed at retrieval evaluation (#19), no edge obligation. §2.4/§3 mirrors aligned. Resolves finding 9 — a latent defect in #10's v1.2.0 extension. Rejected alternative: defining Condition-side edges (structure nothing traverses).
- **P-3 — retraction re-decision routed (RATIFIED, revision):** §2.4 names the post-materialization re-decision of an executed retraction (the #15-flip analogue) and routes it to the DDR-003 remedy boundary. Resolves finding 7.
- **P-4 — #26 key-set equality (RATIFIED, revision):** `confidence_basis` declares the same label set as `property_schema`; registration-rule mirror aligned. Resolves finding 20.
- **P-5 — exemplar gloss (RATIFIED, revision):** the §2.6 cost-plane literal glossed (`property_schema` elided in illustration). Resolves finding 10.
- **P-6 — Touch-2 ruled-exception clause (RATIFIED, revision):** the Change Log row names the departure from the Rationale's empirical-warrant discipline as a ratified economy exception with the SDD-001 §3.3.8 correlation contract as the concrete consumer. Resolves finding 15's tension honestly.
- **P-7 — findings 11 + 17 → cold-read gate** per the pre-ratified F-i and A-14 (executed below as CR-6 and the F17 ruling).
- **P-8 — OVERs (findings 1, 2, 4, 8, 14, 16, 22):** no action; authorities per the audit.
- **Escalation:** operator-elected verification draw over the revised text (run-018); the E2′ family-grade trigger did not fire.

## Cold-read gate dispositions (CR-set) — gate verdict: PASS with folds

Stranger-test findings over the landing set (DDR-002, SDD-001, DDR-004 + upstream canon as resolution targets):

- **CR-1 (RATIFIED):** unqualified "§3.3.8" → "SDD-001 §3.3.8" (a defect introduced by the P-6 fold itself; caught same-gate).
- **CR-2 (RATIFIED):** §7 #13's "§2.5" mis-resolved to DDR-002's own Standards section → corrected to **ADR-002 §2.5** (fetch-verified §-cite discipline).
- **CR-3 (RATIFIED):** §2.3's "(a Named Gaps species)" → boundary-routing-map pointer (the item lives in the routing map).
- **CR-4 (RATIFIED, gap-naming):** the **governing-verdict rule for re-decided `GateDecision`s** — the set's one closed-looking unruled surface (verdict precedence ruled only for `PromotionDecision`; SDD-001 §3.6.3 declines widening as upstream) — named and joined to the *gate-decision origin evolution* Named Gap. Nothing decided; the hole converted to a named gap.
- **CR-5 (RATIFIED):** #26's only-if arm gains its warrant (a stray operand is a malformed declaration).
- **CR-6 (RATIFIED — the F-i disposition):** the single §7 body occurrence of ticket identifiers relocated — prose subject-named, identifiers remaining in their sanctioned *Cross-References* home. SDD-001 body verified clean.
- **CR-7 (RATIFIED):** first-use acronym expansions folded — DDR-002 (EA, ASA, AOE, CMDB, FSM, SoR, SDLC, POC, DTO, FK, ASD, PHI, GKE, the **CI/`ConfigurationItem` disambiguation**, the Tier-1/2 vs T1–T3 gloss) and SDD-001 (EA, AOE, CI). **Corpus-wide sweep → named Reboot follow-up ticket** (ADR-001/ADR-002/DDR-001/DDR-004 all failed the acronym signature; ticket drafted at this disposition, filed on the Reboot backlog).
- **CR-8 (RATIFIED):** SDD-001 §4.4 safe-interim attribution corrected to DDR-002 (the forthcoming DDR-003 will own the governance); the fail-closed posture subject-named (triage token retired from body).
- **CR-9 (RATIFIED):** DDR-004 edit script gains Edit 15 — the layering-invariant ADR reference marked forthcoming/unauthored (the set's one unmarked dangler). The DDR-004 §4-table/`PlaneDefinition` alignment stays the ratified next-touch obligation (A-3), deliberately not folded.
- **F17 ruling:** the References metadata table stays upstream-only per adjudication A-14; convention recorded.

## Post-fold landing set

- `docs/ddr/DDR-002-graph-schema.md` — content sha256 `9bb0f9b3d9c9b08e44d5ca5a8fa807d67869f15fa18e285c963750232848e6a3`
- `docs/sdd/SDD-001-knowledge-service.md` — content sha256 `a6a9ddaad6a50f76d35768959d18efb7cb15df50eb1185ce294514694c579950`
- DDR-004 edit script (15 edits) — sha256 `b976cf99d739bbbe78fea7fe08e6a6eeb6bbb7f99a4893e2018c965c4a8509cc`

## Execution sequence

1. Revisions vendored to the branch (per-document commits; Edit 15 applied to the working DDR-004).
2. run-017 outputs + this audit/disposition pair committed to the run folder.
3. run-018 verification draw (gen-8, landing-state substrate at the revised tree, coherence addendum) — tests that the P/CR closures hold and introduced nothing; one draw, run-012 pattern.
4. On a clean run-018 disposition: landing PR (relay #2) — merge is the acceptance act.
