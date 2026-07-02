# Mechanical Gates

Three pure functions over ledger state. **No LLM anywhere in this file.** The only
LLM input they consume is the arbiter's per-finding `classification`, which is
computed upstream (see `arbiter-classifier.prompt.md`) and read here as data.

The design intent: the loop must never be able to *decide* it has converged. It can
only *count*. A smart agent that could judge "we're done" would re-import the
anchoring we built the whole system to escape.

## 1. Convergence counter

```
open_cbm(ledger) = count( f in ledger.findings
                          where f.status == "open"
                          and   f.severity in ledger.counted_severities )

converged_by_count(ledger) = (open_cbm(ledger) == 0)
```

Dumb and total. That is the point.

## 2. Oscillation detector

Two independent triggers; either sets the flag.

```
recurrence(ledger) = exists f in ledger.findings
                     where f.status == "open" and f.recurrence_count >= 1
```
A finding that was closed and came back is, by definition, not converging by fixing —
it is trading. Trip.

```
plateau(ledger) =
    open_cbm(ledger) > 0
    and  len(ledger.passes) >= ledger.plateau_N + 1
    and  no strict decrease in open_cbm_count over the last (plateau_N + 1) passes
         (i.e. every consecutive pair in that window is >=, never <)
```
The open counted-severity count has stopped falling for `plateau_N` passes while
still positive. The fixes are chasing their own tail. Trip.

```
oscillating(ledger) = recurrence(ledger) or plateau(ledger)
```

When it trips, this is **not** a convergence failure. It is a decision-bearing
tension wearing a resolvable disguise — two altitudes (or two documents) want
opposite things and no higher authority settles it. It is surfaced to Tad **as a
decision**, carrying the recurring `id` (or the plateaued open set) as the payload.

## 3. Router

Exactly three exits. Precedence matters; evaluate top to bottom, first match wins.

```
route(ledger):
    if oscillating(ledger):
        return HALT_DECISION(reason="oscillation",
                             payload=recurring_or_plateaued_findings(ledger))

    open_decisions = [ f for f in ledger.findings
                       if f.status == "open" and f.classification == "decision-bearing" ]
    if open_decisions:
        return HALT_DECISION(reason="decision-bearing",
                             payload=open_decisions)          # surfaced one at a time, unbundled

    if converged_by_count(ledger):
        return CONVERGED

    return CONTINUE       # open_cbm > 0, all open findings resolvable → back to Author
```

### Why decision-bearing gates convergence regardless of severity

A `decision-bearing` finding halts the loop **even if `open_cbm == 0`** — i.e. even
if it is `COSMETIC` and the counter alone would say "done." Silently
auto-resolving *or* silently dropping a discovered decision, however small, is the
manufactured-alignment failure the whole loop exists to prevent. So the router
surfaces it. Once Tad rules, his ruling is ratified authority: the finding becomes
`resolvable` (or is closed), and the loop proceeds. The counter stays dumb; the
router composes.

### The CONVERGED exit is a mechanical conjunction

```
CONVERGED fires  iff  open_cbm == 0
                 and  no open decision-bearing finding
                 and  not oscillating
```
All three are booleans over ledger state and arbiter labels. **No LLM in the "done"
decision.** This is the ratified guarantee, expressed as code Claude Code implements.

### Instrument-compromised guard

A pass in which any scheduled reviewer produced ≥1 parse-dropped emission and 0
admitted findings is instrument-compromised: the runner raises
`InstrumentCompromisedError` (fail-loud, `run_aborted` emitted first) before
routing — CONVERGED must never be reachable through a fully-dropped reviewer.
Partial drops and legitimately empty emissions (zero findings, zero drops) do
not trip the guard (amended 2026-07-02 after run-003's false CONVERGED).

## Escalation surfacing (dry mode)

On `HALT_DECISION`, the runner emits **one escalation per finding, unbundled** — in
dry mode as a logged, proposed Linear ticket (RBT in `t-bone-haff-sofia`), not an
opened one. Bundling multiple decisions into one escalation is prohibited; it is the
exact opposite of ratify-one-at-a-time.
