# Run-004 Audit — Supervised First Dry Run (Distilled Set)

| Field | Value |
|---|---|
| **Run** | run-004-distilled-set — HALT_DECISION, pass 1 |
| **Audited** | 2026-07-02, cold, same-day (protocol §5) |
| **Auditor** | Authored on claude.ai; rulings ratified by Tad |
| **Corpus** | ADR-001 v1.0.0 · ADR-002 v1.0.0 · DDR-001 v1.2.0 · DDR-002 v1.1.0 at repo HEAD e7a6e51 |
| **Baseline** | COLD-REVIEW-2-Findings.md (primary; ran against a mid-distillation snapshot — every item re-verified against the landed corpus before scoring); COLD-REVIEW-Findings.md (round 1, superseded by round 2); the 11 in-cycle three-hat records in docs/reviews/ were scoped out (findings resolved before acceptance, not still-live) |

**Still-live baseline set** (COLD-2 items surviving in the landed corpus, verified by fresh fetch): B1 (ReasoningSession aggregate confidence), S1 (self-modify invariant object drift + §2.5 cross-category citation), S4 ("specific Enterprise capability" overclaim), N6 (DDR-003 forward-reference dead ends), N8 (distillation rows reuse version numbers). COLD-2's S2/S3/S5/S6/N1/N2/N3/N4/N7 and most of N5 were fixed by the final distillation (verified in current text).

---

## 1. Pre-registered marker — RULING: outcome (d), not fully fixed and MISSED

DDR-001 §Reasoning Graph still asserts the session root "carries aggregate
confidence"; DDR-002 §4 gives `ReasoningSession` no confidence property and
places the roll-up on `ReasoningProgress`. The conflict (= baseline B1, the
persistent BLOCKING) is live in the landed corpus. No run-004 finding touches
it — and coherence was demonstrably active in the adjacent neighborhood
(5f103fc4 flags ADR-001's illustrative-kinds omission of `ReasoningSession`).

**Instrument characterization this yields:** the coherence sweep verified
vocabulary-level (type sets) and reference-level (version pins, §-pointers)
consistency but not **property-level assertions** across documents. Recall on
the registered defect: 0/1. B1 routes to the frontier queue as a live defect.

## 2. Per-finding rulings

Validity: TRUE / TRUE- (true with caveat) / OVER (overreach) / FALSE-POS.
Stance: ON / OFF / AMB. Dup: cluster id or UNIQ. Baseline: MATCH / NOVEL / —.

### antagonist-LAA (9 findings: 3M, 2C, 3P + 1M multi)
| id | sev | validity | stance | dup | baseline | ruling note |
|---|---|---|---|---|---|---|
| d69da3e8 | M | TRUE | ON | D3 | NOVEL | §2.4 forward-compat posture rides schema un-enumerated; genuine record-discipline catch |
| 0b6e871a | M | TRUE | ON | UNIQ | NOVEL | RBT-43 additions absent from Decision block; template discipline correctly cited |
| e1bb7e0c | M | TRUE | AMB | D1 | MATCH S4 | True and matches baseline; substantiation-vs-cited-authority is closer to SA's axis than LAA's — mild stance blur |
| f4738b7b | C | TRUE | ON | UNIQ | NOVEL | adr-template requires tracking pointer on aspirational compliance; correct |
| 7686768d | M | TRUE- | ON | UNIQ | NOVEL | "asserting upstream silence as license" is real, though DDR-001 declares it openly; MATERIAL defensible |
| d6053ce6 | C | TRUE | ON | D2 | MATCH N6 | DDR-003 status undeclared |
| f84ac10b | P | TRUE | ON | UNIQ | — | Genuine survived-attack framing |
| 2e6d7605 | P | TRUE | ON | UNIQ | — | Genuine; correctly grounded in design-intent substrate |
| 2363f516 | P | TRUE | ON | UNIQ | — | Genuine; scope-fidelity attack held |

### antagonist-SA (11 findings: 5M+1M multi, 3C, 3P)
| id | sev | validity | stance | dup | baseline | ruling note |
|---|---|---|---|---|---|---|
| 1f683374 | M | TRUE | ON | UNIQ | NOVEL | §3 edge catalog omits GateDecision→Solution DECIDED_ON that §2.4/§5 depend on — sharp, real, humans missed it |
| 6f145a17 | M | TRUE- | ON | UNIQ | NOVEL | The doc names the #19 supersession gap itself and routes the mechanism to SDD; finding correctly notes the "blocking safety control" claim is unsubstantiated for that case. True; severity defensible |
| 2fd87588 | C | TRUE- | ON | UNIQ | NOVEL | Real but thin — a cross-link absence, correctly COSMETIC |
| 986612a3 | M | TRUE | ON | D1 | MATCH S4 | The spike-substantiation overclaim; duplicate of e1bb7e0c, SA's is the on-stance twin |
| 958411d3 | C | TRUE | ON | UNIQ | NOVEL | Vocabulary non-unification ('derived-from-external' vs 'distilled'); real, minor |
| f789ddb8 | M | TRUE- | ON | UNIQ | NOVEL | Sharp conformance reading of ADR-001 §2.2 per-artifact attribution vs Evidence surrogate-only posture; DDR-002 argues its exemption explicitly (§4 RG-provenance posture), so this is a genuine unreconciled-conformance question, not an oversight — MATERIAL defensible |
| c288829a | M | TRUE | ON | UNIQ | NOVEL | no-PHI simultaneously "gateway-enforced" (§1) and CI-only-review-enforced-until-mechanization (§7) — genuine contradiction on the surface ADR-002 §2.7's no-CMEK soundness depends on. Best novel finding of the run |
| d7364887 | C | TRUE | ON | D2 | MATCH N6 | DDR-003 absent |
| cf062ba0 | P | TRUE | ON | UNIQ | — | Promotion-provenance chain attack; genuine |
| 7a4e02d0 | P | TRUE | ON | D4 | — | No-vector conformance held; redundant with EA/coherence |
| 18eaa453 | P | TRUE | ON | D5 | — | Write-authority propagation held; redundant with coherence |

### antagonist-EA (7 findings: 3M, 1C, 3P)
| id | sev | validity | stance | dup | baseline | ruling note |
|---|---|---|---|---|---|---|
| 563b4d5a | P | TRUE | ON | UNIQ | — | Trajectory over-commitment attack; textbook EA altitude |
| e1e97a39 | P | TRUE | ON | UNIQ | — | Reversibility-proportionality attack held |
| 66a041a2 | M | TRUE | ON | D2 | MATCH N6+ | Escalates the DDR-003 gap to its enterprise consequence: downstream schema committed against unratified governance. The strongest framing of the cluster; targeting nonexistent DDR-003 in `target` is a schema quirk to note |
| 01b84a95 | M | TRUE | ON | UNIQ | NOVEL | Safety-critical invariant tier unmechanized across an ACCEPTED schema gating twelve SDDs; the "explicit gating decision" ask is EA-correct |
| 912767ff | M | TRUE- | ON | D3 | NOVEL | The authored-reserved Position-4 surface as unratified posture commitment; pairs with d69da3e8 at a genuinely different altitude |
| 653c1afa | P | TRUE | ON | D4 | — | No-vector reversibility held; redundant |
| 23c28708 | C | TRUE | ON | D2 | MATCH N6 | DDR-003 timing question |

### coherence (9 findings: 2C, 7P — one mis-severitied)
| id | sev | validity | stance | dup | baseline | ruling note |
|---|---|---|---|---|---|---|
| 6bc83308 | P | TRUE | ON | D5 | — | Write-authority no-drift; redundant |
| 1b25ae0a | P | TRUE | ON | D4 | — | No-vector consistent; redundant |
| d677da64 | P | **FALSE-POS** | ON | UNIQ | **MISS of S1** | Credited the never-self-modifies surface as held via DDR-002's derive/promote seam. Baseline S1 (verified live in current text): DDR-001 Decision.5 is unqualified ("never self-modifies the KG"), Operational is a KG plane, and the staging-tier carve-out exists only in DDR-002 — a downstream document rescuing an upstream invariant with a qualifier the upstream does not carry. The sweep accepted the self-rescue. Worst single miss of the run: an actual defect converted into a survived-attack credit |
| 5f103fc4 | C | TRUE | ON | UNIQ | NOVEL | ADR-001 illustrative kinds omit ReasoningSession vs DDR-002 type set; adjacent to B1 but not it |
| b22ce0b0 | P | TRUE | ON | UNIQ | — | Substitution-bar routing held |
| 5ef4b0fe | P | TRUE | ON | UNIQ | — | Spike-home narrative/substrate alignment held (correct as scoped; the overclaim lives in ADR-002's wording, found separately as D1) |
| e8cdf1c0 | C | TRUE | ON | UNIQ | NOVEL | "twelve SDDs" unsupported magnitude; real, minor |
| 5eb0b1f3 | P | TRUE | ON | D5 | — | Feedback-loop extension consistency held; redundant |
| 8ed91773 | C | TRUE | ON | UNIQ | — | **Mis-severitied:** reports a check that HOLDS (version pins) tagged COSMETIC — a POSITIVE wearing a defect label. Drove calibration item (ii) |

## 3. Duplication clusters (hand-matched)

- **D1 — spike substantiation** (e1bb7e0c LAA ↔ 986612a3 SA): near-identical claim, same loci. True duplicate; SA's is on-stance, LAA's is the drift twin. = baseline S4.
- **D2 — DDR-003 absence family** (d6053ce6 LAA, d7364887 SA, 23c28708 EA, 66a041a2 EA): one underlying gap, four findings — but genuinely stratified by altitude (record-discipline / cross-reference resolution / enterprise timing / enterprise consequence). Partial duplication; EA's MATERIAL framing is the keeper. = baseline N6, escalated.
- **D3 — GateDecision authored-reserved** (d69da3e8 LAA ↔ 912767ff EA): same surface, complementary altitudes (un-enumerated scope-riding vs unratified posture). Legitimate stratification, not waste.
- **D4 — no-vector POSITIVE** (7a4e02d0 SA, 653c1afa EA, 1b25ae0a coherence): triple survived-attack credit on one surface.
- **D5 — write-authority POSITIVE** (18eaa453 SA, 6bc83308 + 5eb0b1f3 coherence): triple credit.
- **SA↔coherence seam:** cleaner than feared. SA's "soundness"-kind findings (1f683374, 6f145a17, c288829a) are intra-document consistency — SA's charter, not the sweep's cross-set axis. No defect-level SA↔coherence collision occurred; the seam blur in this run is POSITIVE-side only (D4/D5).

## 4. Baseline comparison (still-live set, n=5)

| Baseline item | Run-004 outcome |
|---|---|
| B1 ReasoningSession confidence (BLOCKING) | **MISSED** (pre-registered marker, outcome d) |
| S1 self-modify invariant drift | **MISSED + FALSE-CREDITED** (d677da64 reported the surface as held) |
| S4 spike-capability overclaim | **FOUND** ×2 (e1bb7e0c, 986612a3) |
| N6 DDR-003 dead ends | **FOUND** ×4, escalated to MATERIAL enterprise framing (66a041a2) |
| N8 version-number reuse on distillation rows | MISSED (NIT-grade) |

Recall on still-live baseline: 2/5 overall; 0/1 on BLOCKING. **Novel true
findings: 12** — including c288829a (no-PHI enforcement contradiction),
1f683374 (edge-catalog omission), 01b84a95 (unmechanized safety tier), none of
which either human cold pass surfaced. Precision: 35/36 rulings TRUE or
TRUE-with-caveat; 1 FALSE-POS (d677da64); 0 fabrications; every cited
authority checked resolves.

**Instrument profile from this run:** strong at intra-document structural and
conformance analysis (edge catalogs, invariant cross-checks, template
discipline, enforcement-posture contradictions) — measurably beyond the human
baseline there. Weak at property-level cross-document reconciliation (B1
miss) and vulnerable to accepting a downstream document's self-rescue of an
upstream invariant (S1 false-credit). Both weaknesses are coherence-charter
surfaces; both are prompt-addressable.

## 5. Stream-level checks

**Arbiter.** 36 classifications, 35 high / 1 medium confidence, zero
malformed, zero fabrications. The mandatory medium-confidence hand-check
(2fd87588 → decision-bearing): RULED OVER-TRIGGERED — a missing cross-link is
a resolvable doc fix; the arbiter's own hesitation (medium) was the correct
instinct. Of six COSMETIC→decision-bearing calls: three defensible (the
DDR-003 family — timing/authority genuinely needs Tad), three over-triggered
(2fd87588, 958411d3 vocabulary unification, e8cdf1c0 count clarification —
all resolvable). Conservative bias confirmed working and running hot on
COSMETICs; no false-resolvable found among decision-bearing candidates
(the serious failure direction is clean).

**POSITIVE stream.** 15/36 (42%), soft alarm confirmed. Framing quality
healthy (all survived-attack framed, no praise-padding); bloat driven by
cross-hat redundancy on strong surfaces (D4/D5 — roster-question data, not a
defect) and coherence's 6/9 rate (held checks are its modal outcome). One
mis-severitied held-check (8ed91773). Calibration items (i)–(iii) ratified
2026-07-02: per-reviewer POSITIVE cap of 2 (strongest survived attacks only);
severity-discipline line (held = POSITIVE, never a defect severity); arbiter
skips POSITIVEs.

**Cost per hat (manifest/log).** Reviewers: LAA 63,552 in / 3,067 out · SA
63,649 / 4,263 · EA 63,589 / 2,570 · coherence 63,318 / 2,547. Arbiter: 36
calls, ≈287k in / ≈7.2k out (~120k of it classifying POSITIVEs — removed by
item iii). Run total ≈541k in / ≈19.6k out. Unique-true-finding yield per
hat: LAA 4 · SA 8 · EA 3(+1 escalation) · coherence 2. Recorded per §7 —
no roster conclusion at n=1.

## 6. Dispositions out of this audit

- **Findings-about-documents → frontier queue (Notion):** B1 (live BLOCKING,
  missed), S1 (live, false-credited), the 17-finding halt payload as the
  loop's proposed escalations — subject to Tad's triage; D1/D2/D3 clusters
  collapse to one frontier item each.
- **Findings-about-instrument → next refinement cycle:** calibration items
  (i)–(iii) ratified; proposed item (iv): coherence-prompt charter extension
  to property-level cross-document assertion checking + a
  downstream-cannot-rescue-upstream rule (targets both B1-class and S1-class
  misses). Also noted: EA finding targeting nonexistent doc-id DDR-003 in
  `target` (schema tolerance question, minor); terminal-abort/no-run_aborted
  and probe gates landed in prior cycles.
- **Spec-authoring pattern (from the road here):** three contract errata in
  one authoring cycle, all cross-references written without re-derivation —
  recorded as an instrument finding about the claude.ai side.
