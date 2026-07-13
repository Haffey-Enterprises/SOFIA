# Disposition Record — run-018-ddr-002 (DDR-002 v1.3.0 verification draw)

| Field | Value |
|---|---|
| **Session** | RBT-54 authoring session, 2026-07-13 (claude.ai surface) |
| **Basis** | run-018 audit (this folder), 26/26 findings ruled against pinned bytes (DDR-002 `9bb0f9b3`, SDD-001 `a6a9ddaa`, DDR-004 `fbab79ce`) |
| **Rulings** | P18-1–P18-7, each ratified individually by Tad, 2026-07-13 |
| **Status** | RATIFIED — folds applied; landing set final; landing PR (relay #2) sequenced |

## Dispositions (P18-set)

- **P18-1 — verdict table (RATIFIED):** the 26 verdicts per the audit §2. 4 TRUE- · 8 POSITIVE-TRUE · 11 OVER · 3 FALSE-POS.
- **P18-2 — family F-A gloss strengthening (RATIFIED, fold):** the §2.6 cost-plane exemplar gloss states the label-set identity explicitly — the elision hides the property *detail*, not the label *set*; #26's key-set equality readable from the illustration. Resolves findings 3/12/21 (three-hat family on the run-017 P-5 gloss). Decision-free.
- **P18-3 — retraction-side detection asymmetry named (RATIFIED, fold):** the §2.4 retraction re-decision clause extended — the un-retraction remedy **and a standing detection analogue of #15 for executed retractions** (#21 traces to *an* approving decision, not the *governing* one) are both unauthored here, riding the existing DDR-003 routing. The CR-4 pattern: a closed-looking surface converted to a named one. Extending #21 itself to governing-edge keying was considered and declined (decision-bearing on a safety-critical check, out of batch scope, zero instances). Resolves finding 10.
- **P18-4 — FALSE-POS set (findings 4, 9, 23): no action.** New verdict class for this instrument; recorded on the calibration ledger (wrong-reading of §7 ticket-ID state, retention semantics, §2.4 scope placement — refuted by the reviewed bytes).
- **P18-5 — OVER set (findings 1, 2, 7, 8, 11, 15, 16, 17, 18, 22, 24): no action.** Gen-8 cost profile confirmed (ruled-decision re-attack, absorbed by disposition layer). One residue routed: finding 8's observation — DDR-004's honest-floor sentence omits Governance citation-reachability — joins the A-3 alignment obligation as a **DDR-004 next-touch note** (captured at RBT-54 close, not folded now).
- **P18-6 — auditor-adjacent clarity fold (RATIFIED, fold):** `WOULD_HAVE_USED` gains its explicit `rebind:pinned` annotation in §5's Evidence-edges line (the §3 point-in-time principle already forced the resolution; the annotation removes the asymmetry with `SOURCED_FROM`'s explicit marking). Honest floor: auditor observation surfaced while refuting finding 9, not a hat finding.
- **P18-7 — escalation ruling (RATIFIED):** no third draw. All run-017 P-closures and cold-read CR-closures held; the folds are cold-read-class. Fold, re-pin, write run records, proceed to the landing PR (relay #2).

## Post-fold landing set (FINAL)

- `docs/ddr/DDR-002-graph-schema.md` — content sha256 `8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16` (supersedes `9bb0f9b3`; three P18 folds + one Change Log row)
- `docs/sdd/SDD-001-knowledge-service.md` — content sha256 `a6a9ddaad6a50f76d35768959d18efb7cb15df50eb1185ce294514694c579950` (unchanged by run-018)
- DDR-004 edit script (15 edits) — sha256 `b976cf99d739bbbe78fea7fe08e6a6eeb6bbb7f99a4893e2018c965c4a8509cc` (unchanged by run-018)

## Execution sequence

1. P18 folds vendored to the branch (single commit; Change Log row carries the event).
2. run-018 outputs + this audit/disposition pair committed to the run folder.
3. Landing PR (relay #2) — push + PR; **merge is the acceptance act (Tad's)**; DDR-004 discharge rides atomically.
4. RBT-54 close obligations (Item H) on Tad's go.
