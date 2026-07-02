# Run-007 Audit — Calibration-2 Retest + Intra-Generation Variance Study

| Field | Value |
|---|---|
| **Run** | run-007-distilled-set — HALT_DECISION, pass 1 |
| **Audited** | 2026-07-02, cold (protocol §5); rulings ratified by Tad |
| **Corpus** | Unchanged distilled four-doc set; repo HEAD 0cfcf5e (calibration-2 generation) |
| **Companion evidence** | run-006-distilled-set (aborted mid-gather on credit exhaustion; three completed antagonist emissions, same generation, same input bytes — the intra-generation comparison sample, per ratified disposition) |

## 1. Pre-registered scorecard

| Target | Result |
|---|---|
| B1 via the procedural form | **MISSED — third consecutive. Documented-limitation close executed per the ratified two-track.** Nuance that matters: the procedure demonstrably improved the *class* — coherence produced two B1-class property/vocabulary-level cross-document finds this run (df072a4b: ADR-002's Firestore "workflow snapshots" narrowed downstream to solution-body snapshots with no upstream reconciliation; 64319dce: ProvenanceSummary + Artifact family asserted under an ADR-001 deferral that doesn't gesture at them) versus zero in runs 004–005. The class detector works; the instance evades. Mechanism hypothesis from four draws of evidence: B1 lives in a three-word prose bullet in DDR-001, and attention across every draw anchors on DDR-002's schema side of the confidence surface (da89dc21 type-set orbit ×2; run-006 SA's rollup-bound-unenforced orbit) without reading the DDR-001 bullet against it. Single-pass limitation documented; multi-run union is the mitigation; no further prompt-chasing. B1 itself dies at triage. |
| Zero borderline-credit recurrences | **PASS in the admitted set.** SA's 7779a6a9 is the narrow §2.3-non-contradiction credit, consistent with the prior TRUE ruling of the same scope (5ef4b0fe); the substantiation chain itself was reported as a defect (784d7a9e, ddefe9fb), not credited. Evidence note from the unadmitted sample: run-006 LAA credited the feedback-loop write-authority extension as held, while run-005 and run-007 LAA both report the same surface as MATERIAL — tie-goes-to-the-defect damps but does not eliminate borderline flips (unadmitted, so no formal ruling; recorded as calibration evidence). |
| Zero self-refuting emissions | **PASS.** b1863ae1's concede-then-pivot presents a coherent distinct defect (mutual authoring dependency), not a self-rebuttal. |
| Caps / arbiter regression | **PASS.** 28 findings: 15 M, 5 C, 8 P (29%); 2 POSITIVEs per hat; zero mis-severitied held-checks; arbiter 20 calls = non-POSITIVE count, all well-formed; ≈416k input total. |
| Tie-to-defect over-correction watch | **CLEAR.** No weak/hedgy defects on surfaces previously credited as solid survivals; solid credits either persisted (no-CMEK, ×2 hats) or dropped out cleanly. |

## 2. Intra-generation variance (run-006 vs run-007 — same prompts, same bytes)

Per-hat defect-finding overlap between two independent draws under identical
conditions:

- **EA: ~75%** — its core three (cost-plane-without-upstream-need,
  governance-shape-ahead-of-DDR-003, Enterprise-commitment-vs-unrecorded-
  blocker) reproduced near-verbatim. Most stable hat; fewest, biggest targets.
- **LAA: ~50%** — spike substantiation, the Directives-Context-Envelope
  Bridge dangling reference, and the capture-invariant POSITIVE reproduced;
  the rest diverged. One direct intra-hat contradiction (feedback-loop
  extension: POSITIVE in 006, MATERIAL in 007; run-005 also MATERIAL — the
  006 credit is the outlier draw).
- **SA: ~35%** — least stable; its fine-grained soundness surface is the
  largest search space. 006-only gems no completed run holds: the
  confidence-rollup upper bound has no §7 enforcement check; the reserved
  authored-GateDecision has no write-authority home; decided_at
  verdict-precedence has no tie-break where the schema permits ties.
  006-LAA also uniquely holds: the GKE runtime commitment never surfaces in
  ADR-002's Decision statement.

Conclusion at n=4 draws: run-to-run variance is intrinsic (no sampling
control exists on this model family), inversely related to finding
granularity, and the union across draws strictly dominates any single draw —
even an aborted run's emissions contributed unique true findings. Cross-hat
migration also confirmed across runs (authored-reserved: LAA/EA→EA→coherence;
gateway-as-author: SA→coherence; IAM drift: SA→coherence; 6→7 mapping:
coherence→SA) — defects are not hat-locked. All recorded as roster/operating-
mode data; no conclusions drawn here.

## 3. Findings notes (full four-axis table waived this cycle by comparison-audit format)

Stable core defect set, now reproduced in every draw that touched it: spike
substantiation (4/4), DDR-003 timing family (4/4), GateDecision
authored-reserved posture (4/4, three different hats), Decision-statement
completeness family (4/4), cost-plane-without-upstream-need (2/2 EA draws).
Notable new-in-007 true finds: 5840457e (approved_conditional has no defined
semantics for GateDecision→Solution and no Condition path), b94454b7 +
ede8ad3e (PromotionDecision's origin_mechanism unspecified — a genuine
provenance-matrix gap), f59dd120 (§7 authority-split exceeds Decision.6's
schema-only scope), e7b94bac (authored-reserved gate vs ADR-001's reasoner
taxonomy supplying no system-authored approval category — sharpest form yet).
One finding deferred can't-rule: **cae82b89** (was the derive/promote seam
introduced at distillation despite "no decision change"?) — verification
requires the pre-distillation staging copy
(~/Downloads/DDR-002-graph-schema-v1.1.0-staging.md); routed to triage.
Cumulative precision across three completed runs: 88/91 rulings TRUE or
TRUE-with-caveat.

## 4. Dispositions

- **B1:** documented single-pass limitation (instance); class improvement
  credited to the procedural charter; B1 the defect goes to triage for fix.
- **Operating-mode question — formally queued as a design deliberation:**
  at n=4 draws the union-over-runs result graduates from observation to
  design question — should the loop's high-recall mode be union-of-k runs,
  and what do convergence and unattended trust mean under that mode? Queued,
  not designed; explicitly fenced from restructuring-on-intuition.
- **Frontier triage is next and overdue:** three completed runs of
  decision-bearing escalations, dup-collapsed, + B1 + S1 + cae82b89
  verification + run-006's unique unadmitted finds (GKE-in-Decision,
  rollup-bound check, decided_at tie-break, authored-gate authority home) as
  triage-eligible evidence.
- **run-006 + run-007 commit together** per ratified disposition, this audit
  in the run-007 folder.
