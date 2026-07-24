# run-supervision.protocol.md §2 — Spend-discipline insert (ratified 2026-07-19)

**Placement:** Insert into §2 — Pre-run checklist, **before** the existing cost-envelope item (spend discipline precedes envelope acknowledgment: first decide whether the run should exist, then acknowledge its cost). Voice matches the protocol.

---

**Spend discipline — does this run need to exist?** A live proving run is the last resort, not the default; clear these four before acknowledging the envelope.

1. **Units before dollars.** Spend a live run only on what a unit test cannot answer. Mechanical behavior — routing, disposition, identity collapse, gate logic — proves out in the S-/T-suites for free; a determined-not-observed disposition (a deterministic gate over captured state) needs no live event at all. Reserve live runs for genuinely emergent, real-input questions: caching under real inter-pass gaps, reviewer output discipline, emergent finding volume and false-positive rate.
2. **Bound to the minimum passes.** Set `max_passes` from what the target criterion needs, not a high ceiling. Most criteria prove out in 1–3 passes; a low bound also forces a disposition cheaply where a natural halt would otherwise run long.
3. **Match the target to the question.** Decision-dense records (e.g. ADR-008) never exhaust and run long by nature — use them only when you need that behavior. Keep a small near-convergeable target on hand for CONVERGED / decision-bearing / disposition proofs.
4. **Mine captured fixtures before spending.** A finalized run folder is a rich, free fixture; most what-happened / why questions — cold audits, defect triage, cost profiling — answer from captured artifacts at $0. Spend a new run only when no captured run can answer it.

The Batch API (50%) and per-actor model-mix are architectural cost levers, tracked separately (RBT-72) — they change what a run costs; these four govern whether it runs.

**Provenance.** Ratified by Tad 2026-07-19 at the close of the RBT-69/70 session, from the run-030 cost profile (~$32–33/run, five passes where the proof was banked by pass 2–3 and the disposition was unit-provable). Companion architectural work: RBT-72.
