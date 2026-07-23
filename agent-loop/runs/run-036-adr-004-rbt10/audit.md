# run-036-adr-004-rbt10 — Cold Audit

Auditor: claude.ai design surface, 2026-07-22. Substrate: fetched from
origin/develop @ b9e6f6d (run folder as merged, PR #48); as-reviewed document
reconstructed by reverse-applying sandbox-vs-canonical.diff to the committed
sandbox copy — sha256 verifies byte-exact to the manifest pin (cac9d8e2...),
and the pushed authoring-branch tip (54c9702) carries the identical bytes.
Chain of custody closes on remote artifacts alone.

## 1. Mechanical recompute (ledger, independent)
85 findings: 56 MATERIAL / 13 COSMETIC / 16 POSITIVE. Status: 75 open / 10
closed. Altitude: LAA 18, SA 22, EA 19, cross-set 26. Classification: 59
decision-bearing / 10 resolvable / 16 unclassified POSITIVE. Open set: 50 M /
9 C / 16 P; all 59 open classified items decision-bearing, 0 resolvable open.
Closed 10 = 5 author edits (conformed, authorities cited) + 5 satisfied-closes
(all with mechanical evidence anchors; 0 evidence-fails). Author events: 5
edit / 5 satisfied / 13 refused / 3 unresolved. Corrections to the executor
GATE-2 report: satisfied-closes 5 (reported 4), refusals 13 (reported 14) —
cosmetic, recompute-justified. Confidence stream (classified events): 54 high
/ 15 medium / 0 low.

## 2. Exit legitimacy
LoopBoundExceeded at the operator-set 3-pass budget backstop. open_cbm 15 →
36 → 55, net-new loci each pass (carry-forward active; growth is real, not
identity-inflation). Dense-record signature; per decisions-not-findings
doctrine the 59-item decision-bearing backlog coalesces to SIX distinct
decisions (rulings file, this date). Honest non-exhaustion; the docket is the
product.

## 3. claim_divergence (15 events) — RESOLVED BENIGN
All divergence ids are dedup_open ids (14 unique; one twice). Sampled pairs
differ by stochastic re-wording only (e.g. "driver-less loader" vs
"driver-less loader utility"); substance identical. Verdict: the cross-pass
finding-identity coverage-preservation guard operating as designed — logged
rather than silently suppressed; zero lost findings, zero judgment errors.
Five divergence ids are POSITIVEs: credits reproduce across passes,
consistent with prior-run stability.

## 4. Entailment verification
12/12 load-bearing quotes from the six decision clusters verified verbatim
against the as-reviewed text. Locus-entailment inflation in sampled set: 0.
(One false ABSENT during audit traced to markdown emphasis inside the quoted
phrase — "ingestion-mechanics *authority*" — resolved PRESENT.)

## 5. Watch-item verdicts
- Reviewer empties / re-draw: no reviewer re-draws (each hat exactly 1
  call/pass). No installment to the run-correlated-empties stream.
- RELIT class: 0. The gen-13 close rule's trigger did NOT fire; stays shelved.
- Retries: 11, ALL arbiter-side content retries ("malformed classification
  output"), 11/80 calls = 13.75% malformation. Parse/salvage recovered all;
  zero aborts. NEW WATCH: arbiter output-malformation rate (n=1 at this
  volume).
- Cross-doc author_unresolved: 3, all "target not in document set"
  (ADR-008/DDR-002 co-targets). Known single-doc-set behavior; second
  occurrence of the owed skill note.

## 6. Instrument findings (routed)
I1 arbiter malformation 13.75% -> loop-machinery ticket family, watch-grade.
I2 pass_number absent on dedup_open + claim_divergence events; doc_changes
rows carry only doc+pass fields — the named pass-null logging gap, SECOND
firing; rides the next runner-touching ticket. I3 classification confidence
present in events, None in all 85 ledger rows — ledger-persistence gap, same
family as I2. I4 = §5 cross-doc note. I5 executor report off-by-ones (§1).

## 7. Cost (independent recompute, action-log usage fields)
115 calls. Uncached in 911,893 / out 65,316 / cache-write 844,728 /
cache-read 13,824,267. Four-line-item at claude-opus-4-8 list: $21.55
($4.56 / $1.63 / $8.45 / $6.91). Reconciles with executor figures. Structure
notes for the cost line: cache-WRITE is now the largest item (five per-actor
prefix writes ~157k each); author uncached input (523k) is the largest
uncached block. Routed to the standing cost-architecture ticket; no design
here.

## 8. Docket
Six decisions, 59 members, all ruled per item 2026-07-22 — see
agent-loop/deliberation/adr-004-graph-fresh-schema-file-driven-ingestion/
run-036-docket-rulings.md. POSITIVE set (16) affirmed as survived-attack
credits; 5 reproduce across passes.

## 9. Predecessor run — run-035 provenance (ruled 2026-07-22)
run-035-adr-004-rbt10 launched against the pre-fold draft (head_sha 4f1b5ef,
the initial-PROPOSED commit) and terminated mid-pass-2 by a network/system
failure (operator-reported); manifest never finalized. Its partial tape (52
llm_calls, 47 admitted, 1 author edit, 7 refusals — two verbatim refusals
anticipate the D3/D4 docket questions a run early) informed the fold commit
(54c9702) that produced the run-036 target bytes. Disposition: committed
as-is as evidence alongside this audit — an aborted run's output is evidence,
not waste. Cross-run behavioral note: the 035 author refused the Decision-
enumeration surfacing as beyond-amendment-scope; the 036 author edited it;
variance mooted by the D3 ratification of the edit.
