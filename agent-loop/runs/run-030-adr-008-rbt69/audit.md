# Cold Audit — run-030-adr-008-rbt69

| Field | Value |
|---|---|
| **Document** | runs/run-030-adr-008-rbt69/audit.md |
| **Status** | AUTHORED — 2026-07-19 (claude.ai, cold, from the run folder) |
| **Run** | run-030-adr-008-rbt69 (RBT-69 proving run; clean retry of run-029) |
| **Method** | run-supervision.protocol.md §5, scored against run-030's PRE-REGISTRATION criteria 0–4 |
| **Authorities fresh-fetched** | run-supervision.protocol.md, rbt-69-loop-optimization.spec.md, mechanical-gates.md, the run's PRE-REGISTRATION.md + manifest.json, and the raw action-log.jsonl / ledger.json (all recomputed independently — Code's hand-back was not taken as authority) |

---

## 1. Executive result

run-030 **aborted on an external transport ceiling** (the org's self-set $200 monthly API spend cap) mid-pass-5, at `antagonist-EA`, after **4 complete passes + a partial pass 5** (LAA, SA clean). This is a `LlmTransportError` — categorically unlike run-029's `InstrumentCompromisedError`: nothing in the loop misbehaved. Per run-supervision §3e / §4, transport failure aborts itself and is non-diagnostic of the run's merits.

Scorecard against the pre-registered criteria:

| # | Criterion | Result |
|---|---|---|
| 0 | Abort does not recur (RBT-70 proof) | **MET** — path (a). 0 `parse_dropped`, 0 `reviewer_output_preamble_stripped` across passes 2/3/4 coherence (+ pass-5 LAA/SA). The gen-11 forcing function suppressed the preamble at the root; the salvage seam was never needed. |
| 1 | 1h TTL applied | **MET** — total `ephemeral_5m` creation across the entire run = **0**; every actor's creation lands in the 1h bucket. |
| 2 | Cross-pass caching pays | **MET (strong)** — every reviewer writes on pass 1, then reads ~150,900 with 0 re-creation on passes 2–5. Sustained across five passes; run-028 read ≈0 on every pass. |
| 3 | Identity de-inflation (piece 1) | **MET (mechanical)** — 12 `dedup_open` (same-id collapse), 10 `claim_divergence` triaged as reworded-same, 76 findings → 76 distinct `(target,locus,altitude)` keys, zero duplicate-locus collisions. |
| 4 | Honest disposition (piece 3) | **NOT REACHED as a live router event — but determined by the captured state.** Trajectory + the fresh-read gate definition make the imminent disposition unambiguous: **`non-convergence`** (see §5). |

**Single-variable integrity: HELD.** manifest confirms target `24461d3f` (run-029's pristine pre-run pin), the four gen-11 reviewer hashes (`76ce2c8b` LAA, `12361c62` SA, `68fe9c98` EA, `836986a8` coherence), arbiter `3b786d5d` + author `4e435d2c` byte-identical to run-029, HEAD `0370254`. The only changed variable was the RBT-70 work.

**Recommendation:** promote `rbt-69-loop-optimization.spec.md` PROPOSED v0.1.0 → **ACCEPTED v1.0.0**. Criteria 0–3 are met on captured evidence; criterion 4's terminal event is unobserved but its outcome is determined by the captured ledger state and the deterministic gate, and independently proven by unit test S2. The one honest floor: the *live* non-convergence router event was pre-empted by one pass — recorded below, not papered over.

---

## 2. Criterion detail

### Criterion 0 — the RBT-70 proof (MET, path a)

0 parse-drops and 0 reviewer preamble-salvages anywhere in the run. The exact locus that aborted run-029 (pass-2 coherence, then pass-3, pass-4) emitted clean `[`-first JSON every time. RBT-70's root-cause fix (gen-11 silent-re-verification) worked; the defense-in-depth salvage seam correctly never fired. Note the *author* seam did fire 12× (`author_output_preamble_stripped: 12`) — that is the unchanged gen-10 author parser doing its job, outside the RBT-70 variable. RBT-70 is proven on real input.

### Criterion 1 — 1h TTL (MET)

Independent recompute: `sum(ephemeral_5m_input_tokens) = 0` across all 158 `llm_call` events; all cache creation is in `ephemeral_1h_input_tokens`. The structural TTL proof holds.

### Criterion 2 — cross-pass caching (MET, strong)

Per-reviewer, per-pass (independently recomputed from `emission_path` pass tags):

```
pass01  all reviewers   read=0          create_1h≈150,900   (cold write)
pass02  all reviewers   read≈150,900    create=0            (cache hit)
pass03  all reviewers   read≈150,900    create=0
pass04  all reviewers   read≈150,900    create=0
pass05  LAA, SA         read≈150,900    create=0
```

The 1-hour TTL survived every inter-pass gap through pass 5 — the exact inversion of run-028 (hats read ≈0 every pass). This is a *stronger* result than pre-registered (which only required `cache_read>0` on passes 2+): five passes of sustained reuse.

**One nuance, honest.** The **author** cached poorly: cache_read 552,501 vs uncached input 2,069,228 (ratio **0.27**), its 2.07M uncached input the single largest cost line of the run. Mechanism: in dry mode the author mutates its own document input across edits (run-supervision §9), so the document text is not run-stable and cannot cache across the author's own edits. This is **inherent to the author's role, not a caching regression** — but it means the spec's "author stable-input caching" clause (Piece 2) pays materially less than the reviewer clause, and the author is where the caching win is structurally capped. Flagged to the fund-conservation deliberation (task #28).

### Criterion 3 — identity de-inflation (MET, mechanical)

Scored on the pre-registered basis (mechanical key-collapse, **not** raw open_cbm-vs-run-028, which the pre-registration correctly fenced as confounded):

- **12 `dedup_open`** events — 12 re-emissions recognized as existing open findings (same `(target,locus,altitude)` id) rather than minting fresh ids. In run-028 this class was the dominant inflation driver.
- **10 `claim_divergence`** events across ~8 distinct finding-ids — the guard captured reworded re-emissions as `claim_variants` without hiding anything. Triage in §4.
- **76 findings → 76 distinct `(target,locus,altitude)` keys; zero loci carry duplicate findings.** The coarser key collapsed surface-mutation without merging distinct findings.
- **recurrence_count = 0** everywhere — no closed finding reopened.

The directly-analogous run-028 failure (a hat re-emitting one finding under fresh ids each pass) is reproduced-and-collapsed here: e.g. finding `8d8093db` (the RG-capture-exclusion scope claim) was re-emitted 3× and `dedup_open`'d 3× onto one id with variants, instead of becoming 3 separate open findings. Piece 1's safety property — *a live finding is never hidden; distinct findings never silently merge* — holds on this run.

### Criterion 4 — honest disposition (NOT REACHED live; determined by captured state)

The transport abort pre-empted the pass-5 router decision. But criterion 4's outcome is a **pure deterministic function of the captured ledger trajectory**, so it is inferable with high confidence:

- **open_cbm trajectory** (from the `continue` stream, the authoritative source — see §6 on the ledger/log divergence): **19 → 16 → 28 → 37** across passes 1–4.
- **Gate definition** (fresh-read `mechanical-gates.md §2`): `plateau` fires when `open_cbm > 0` AND `len(passes) ≥ plateau_N + 1` AND no strict decrease over the last `plateau_N + 1` passes. Here `plateau_N = 3`, so the window is 4 passes.
  - At pass 4 the 4-pass window is `[19,16,28,37]` — it contains the strict decrease `19→16`, so plateau correctly did **not** fire, and the router correctly issued CONTINUE. ✓
  - At the pass-5 router decision the window would be `[16,28,37, pass5]`. Given the monotonic climb `16→28→37` and pass-5 reviewers still emitting, pass-5 open_cbm ≥ 37 was near-certain → **no strict decrease in the window → `plateau` fires**.
- **recurrence = 0** throughout ⇒ the halt could only be **`non-convergence`**, never `oscillation` (the router splits on which trigger fired; `recurrence` is the sole oscillation trigger).

So run-030 was **inside the very pass that would have produced the run's first live `HALT_DECISION:non-convergence`** — the exact disposition Piece 3 added, on a ledger state (accumulation, zero recurrence) that the *old* pre-Piece-3 code would have mislabeled `oscillation`. The abort robbed us of the router event itself, not of the state that determines it.

**This also falsifies the pre-registration's speculative note** that the identity fix might prevent the plateau and halt `decision-bearing` in 1–2 passes. It did not: ADR-008 genuinely accumulates decisions faster than the dry-mode author drains them, so the run heads to non-convergence *even with de-inflation working*. De-inflation and non-convergence are independent — Piece 1 made the accumulation **honest** (real net-new findings, per §2 criterion 3), and Piece 3 is exactly the disposition that honest accumulation needs. Piece 3 is vindicated on real input, one router event short of the live stamp.

**Empirical floor (stated, not rationalized):** the `non-convergence` router event was not emitted. The conclusion rests on (a) the captured 4-pass trajectory, (b) the deterministic gate definition, (c) recurrence=0, and (d) unit test S2 which already proves the run-028 accumulation replay routes to `non-convergence`. This is n=1 and one-pass-short; it is strong, determined evidence, not a live observation.

---

## 3. Per-hat cost (roster denominator, run-supervision §5.3)

Independently recomputed from `llm_call` (manifest is `finalized: false` — aborted before finalization; the action-log is authoritative):

| site | calls | uncached input | cache_read | 1h create | output |
|---|---|---|---|---|---|
| antagonist-LAA | 5 | 228,102 | 603,604 | 150,901 | 16,466 |
| antagonist-SA | 5 | 228,102 | 603,684 | 150,921 | 17,132 |
| antagonist-EA | 4 | 147,952 | 452,583 | 150,861 | 11,460 |
| coherence | 4 | 147,952 | 452,703 | 150,901 | 12,732 |
| arbiter | 72 | 44,637 | 10,613,790 | 149,490 | 12,938 |
| author | 68 | 2,069,228 | 552,501 | 176,907 | 20,063 |

**Estimated run cost** at Opus 4.8 ($5 in / $25 out / $10 1h-write / $0.50 read per MTok): ≈ **$32–33** (≈$14.3 base input, ≈$9.3 1h writes, ≈$6.6 reads, ≈$2.3 output). The author (2.07M uncached input) is ~44% of the base-input cost — the primary cost lever, and structurally cache-resistant in dry mode.

---

## 4. claim_divergence triage (run-supervision §5.3 duplication axis)

The 10 `claim_divergence` events, hand-triaged reworded-same vs genuinely-distinct:

- **Reworded-same (8+):** `8d8093db` (RG/Reasoning-Graph capture exclusion scope, ×3), `30599cca` (§2.5-vs-§2.2 per-write contradiction, ×2), `f10615f7` (§1 load-bearing-dependency framing), `22874c7b` (ingestion record cited under two subject-names), `15f614f2` (ADR-008-vs-ADR-001 §2.5 silent-override). Each is the same finding at a byte-stable locus, reworded across passes — precisely the run-028 inflation class, now collapsed to one id + variants. The guard behaved as designed.
- **Adjacent-but-distinct, correctly NOT merged:** `a0d4159d` and `875a7ed2` are two §2.1/§6-check-1 accountability findings at *adjacent* loci (Promotion-class vs Environment-class accountability). They carry **separate ids** (different `(target,locus,altitude)` keys) — the machinery kept them distinct, which is correct (cross-altitude / distinct-locus non-merge, spec T3/T2). No dangerous merge occurred.

Net: no live finding hidden; no two genuinely-distinct findings merged into one id. The residual risk Piece 1 routes to this audit (two-as-one under-count) did not materialize on this run.

---

## 5. Stream checks (run-supervision §5)

- **POSITIVE proportionality (§3d):** per-hat POSITIVE share — LAA 6/20 (30%), EA 6/18 (33%), SA 5/19 (26%), coherence 4/19 (21%). EA sits on the ~⅓ soft-alarm line; not a defect, a note. Hats are well-balanced (18–20 findings each) — a healthy independence signal (n=1).
- **SA↔coherence duplication (§3b):** exactly 2 shared loci (§2.1 scope boundary; §2.5 cross-class precedence), each carrying an SA finding and a coherence (cross-set) finding at *distinct altitudes* — preserved as separate records by design (the roster-independence evidence the prior claim-only key destroyed). Low overlap; clean seam.
- **Arbiter (§5, partial):** 72 classifications over the run; the open set resolves to 38 decision-bearing + 0 open resolvables + 21 POSITIVE, consistent with the conservative-bias intent. Per-classification confidence hand-check was **not** performed in this pass — flagged as available depth if wanted; nothing in the stream suggested a false-resolvable.
- **Author seam (§9f/g):** 20 edits, 46 refusals, 12 preamble-strips (gen-10 seam). No anchor-fail storm (no abort trigger). The 46 refusals feed the `_escalate` path (resolvable → decision-bearing), which is the mechanism populating the decision-bearing backlog that drives the (imminent) non-convergence — behaving as designed. edit-then-reopen: 0 (recurrence=0).

---

## 6. Instrument findings (route per §8)

1. **Durable ledger lags the action-log on abort.** `ledger.json` durably holds the pass-3 state (76 findings, open_cbm 25); the `continue` stream shows the run reached open_cbm 37 at pass 4, and `admitted` events (96) exceed durable findings (76). On the transport abort the ledger was not flushed with pass-4/5 admissions, and `manifest.json` is `finalized: false`. **Consequence for audit method:** read the open_cbm trajectory from the action-log `continue` stream, not from the final ledger. **Candidate follow-up:** consider whether ledger flush should be per-admission rather than per-pass so an abort leaves a fully-consistent durable ledger — or document that the action-log is the trajectory-of-record. (Design question, not a run defect.)
2. **Author cache utilization 0.27** — dry-mode document mutation caps the author caching win (§2 criterion 2). Cost + Piece-2-completeness note; routed to task #28.
3. **`calibration.generation: 10`** stamped beside gen-11 reviewer hashes (manifest confirms) — the known metadata gap; task #27 fast-follow stands.
4. **Minor logging gaps:** `claim_divergence` and `continue` events carry `pass: null` / `reason: null`. Harmless here (pass inferable from `emission_path`), but they cost a little audit precision — worth a one-line fix when the runner is next touched.

---

## 7. Disposition

- **Criteria 0–3: MET** on independently-recomputed captured evidence. Criterion 2 exceeds its bar (5-pass sustained reuse).
- **Criterion 4: determined `non-convergence`**, one router event short of a live stamp; independently unit-proven (S2). Honest n=1 floor recorded (§2).
- **Single-variable integrity held; RBT-70 proven (criterion 0).**

**Recommend: promote `rbt-69-loop-optimization.spec.md` → ACCEPTED v1.0.0**, with criterion 4's status recorded honestly as "determined-not-observed (live event pre-empted by external transport abort; S2 unit-proven; a future naturally-non-converging run will stamp it opportunistically)." A dedicated clean rerun on ADR-008 is **not** recommended to chase the live stamp — the same decision density would again drive a long run toward the `max_passes` bound; if a live `non-convergence` stamp is wanted, a lower-`max_passes` bound (e.g. 4–5) on this same target would force the router event cheaply, since the trajectory shows plateau firing at pass 5 regardless.

**n=1 floor.** This is one run on one document (ADR-008). Per run-supervision §7, it produces measurements, not roster/threshold conclusions. The identity zero-collision result and the caching win are consistent with run-028's diagnosis but remain n=1; the cold audit is the watch, and it found no violation.
