# Run-005 Audit — Calibration-1 Retest

| Field | Value |
|---|---|
| **Run** | run-005-distilled-set — HALT_DECISION, pass 1 |
| **Audited** | 2026-07-02, cold (protocol §5); rulings ratified by Tad |
| **Corpus** | Same distilled four-doc set, docs unchanged; repo HEAD 001c701 (calibration-1 generation — four reviewer prompt hashes changed vs run-004, arbiter hash identical) |
| **Purpose** | Retest against the pre-registered targets recorded at calibration-1 ratification; comparison audit vs run-004, not a full re-derivation |

## 1. Pre-registered targets — scorecard

| Target | Result |
|---|---|
| B1 found (property-level charter) | **FAIL — missed again.** No finding touches the ReasoningSession confidence conflict; coherence again orbited it (da89dc21 flags ReasoningSession in the type-set context) without landing. The abstract charter principle did not convert to the concrete check. |
| S1 found (upstream-authority rule) | **PASS (attribution murky).** SA 7f610b6c (MATERIAL, decision-bearing) states it in the baseline's own terms — the staging-tier carve-out "is asserted in DDR-002 but is not established" upstream, "a substantiation gap against the upstream authorities it cites for cover." The run-004 false-credit (d677da64) did not recur. Attribution caveat: the rule was added to coherence's prompt; the find came from SA. Fix vs freed attention vs nondeterminism — not separable at n=1. |
| POSITIVEs ≤ 8 total, ≤ 2/hat | **PASS exactly.** 8/27 (30%); 2 per hat; survived-attack framing intact. |
| Zero mis-severitied held-checks | **PASS.** |
| Arbiter calls ≈ non-POSITIVE count | **PASS.** 19 calls = 12 MATERIAL + 7 COSMETIC; all 8 POSITIVEs unclassified; arbiter input 152k vs 287k (−47%); run total ≈407k in vs ≈541k (−25%). |
| Broad reproduction of run-004 finds | **PARTIAL — see §3, the run's most important result.** |

## 2. Findings summary (27: 12 M, 7 C, 8 P)

Per hat: LAA 9 (4M/3C/2P) · SA 8 (4M/2C/2P) · EA 6 (3M/1C/2P) ·
coherence 4 (1M/1C/2P). 14 decision-bearing → HALT_DECISION pass 1;
open_cbm 12.

**Ruled FALSE-POSITIVE (ratified 2026-07-02):**
- **20f73ce0 (SA):** credited the spike-substantiation chain as held —
  against still-live baseline S4, against LAA 498012b8 in the same run,
  and against SA's own run-004 verdict (986612a3). Root cause: a
  genuinely borderline surface + no sampling control ⇒ threshold flip;
  contributing: the required-POSITIVE floor makes borderline attacks the
  marginal credit supply. Corrective: tie-goes-to-the-defect prompt rule
  (calibration 2).
- **1c827a44 (EA):** claims ADR-001's doc-ID references need
  role-vs-ID reconciliation; the references are correct and the claim
  concedes its own consistency mid-sentence. Root cause: a real faint
  signal (ADR-001's cross-refs never mention DDR-001 at all) articulated
  as the wrong defect; no self-check caught the self-refuting emission.
  Corrective: self-refutation check prompt rule (calibration 2).

All other rulings: TRUE or TRUE-with-caveat; notable novel true finds
this run — ed1fa7d2 (gateway-as-author vs ADR-002 §2.5
gateway-as-access-boundary), aea9a913 (ProvenanceSummary frozen-set
completeness: §7 #20 checks existence, not completeness), 64e28d99
(GateDecision origin ingested vs the platform's own three-hat gate being
SOFIA-internal), e01ddee2 (six conclusion_types vs seven
correction-surfaces — capability has no home), 22b3ac4a (= baseline N8,
which run-004 missed). Cumulative precision across both runs: 60/63.

## 3. Stability result (unregistered, most significant)

Run-004's two strongest novel finds — c288829a (no-PHI enforcement
contradiction) and 1f683374 (DECIDED_ON edge-catalog omission) — did NOT
reproduce. Run-005 produced equally sharp novels run-004 missed (above)
and recovered a baseline item run-004 dropped (N8). Reproduced across
both runs: the spike-substantiation defect, the DDR-003 family
(consolidated 4→2 findings), the GateDecision authored-reserved posture,
the safety-tier/sequencing concern, Decision-block completeness, and the
ReasoningSession type-set adjacency.

Stated at n=2: single-pass recall is unstable on this model family (no
sampling control exists); the union of runs is substantially richer than
any single run. Implication held, not concluded: the loop's operating
mode for high-recall review may be multi-run union rather than
single-run trust, which reframes the unattended-trust criterion. Roster
measurements recorded (unique-true per hat this run: LAA 5 · SA 4 · EA 3
· coherence 2); no roster conclusion.

## 4. Arbiter check

19/19 well-formed, zero retries, all high confidence. COSMETIC →
decision-bearing: 3 of 7 (cb282dff, 40aef0f8, 4271a56b) — running hot on
COSMETICs at a rate consistent with run-004; trend noted, no action
ratified (conservatism in the safe direction; zero false-resolvables
again).

## 5. Dispositions

- **B1 two-track close (ratified):** (i) B1 itself goes to the frontier
  triage to be FIXED — its bait value is spent after two runs of data;
  (ii) one operational sharpening of the property-level instruction
  (procedure, not principle) ships in calibration 2, and if a B1-class
  defect is missed again the limitation is documented and multi-run
  union is the mitigation — no further prompt-chasing of this defect
  class.
- **Calibration 2 (this cycle):** operational property-level procedure
  (coherence); tie-goes-to-the-defect rule (four reviewers);
  self-refutation check (four reviewers).
- **Frontier triage (next):** two runs' decision-bearing escalations,
  dup-collapsed, + B1 + S1 — the session where loop output becomes
  document fixes.
