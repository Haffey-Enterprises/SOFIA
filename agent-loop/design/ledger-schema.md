# Ledger Schema

The ledger is the durable spine. It is the single source of continuity: every agent
fetches it fresh, no agent inherits another's context. It must support convergence
counting, oscillation detection, arbiter classification, and routing — all as
functions over its state.

## Finding record

| field | type | set by | notes |
|---|---|---|---|
| `id` | string | admission | **Stable identity across passes.** See §Identity. |
| `source` | enum | reviewer | `coherence` \| `antagonist-LAA` \| `antagonist-SA` \| `antagonist-EA` \| `antagonist-stub` \| `coherence-stub` |
| `altitude` | enum | reviewer | `LAA` \| `SA` \| `EA` \| `cross-set` (coherence) |
| `severity` | enum | reviewer | the house `code-review` ladder: `BLOCKING` \| `MATERIAL` \| `COSMETIC` \| `POSITIVE`. Counted set = §Severity. |
| `target` | string[] | reviewer | document id(s) the finding is against |
| `locus` | string | reviewer | section / decision within target |
| `claim` | string | reviewer | the finding statement |
| `cited_authority` | object \| null | reviewer | **Mandatory.** See §Admission gate. |
| `classification` | enum | arbiter | `unclassified` \| `resolvable` \| `decision-bearing` |
| `authority_locus` | string \| null | arbiter | if `resolvable`, the authority+locus that determines the fix |
| `status` | enum | author / router | `open` \| `closed` \| `escalated` |
| `pass_raised` | int | admission | pass number first admitted |
| `pass_closed` | int \| null | author | pass number closed |
| `recurrence_count` | int | admission | increments when a previously-`closed` `id` is re-admitted `open` |
| `resolution_note` | string \| null | author | in dry mode: *proposed* only, not applied. Variants: `conformed to <authority>` (edit) \| `satisfied: already conforms to <authority>` (satisfied-close, RBT-71 — see §Satisfied-close disposition) |

`cited_authority` shape:
```
{ kind: "canonical" | "design-intent" | "coherence" | "soundness",
  ref:  "<named artifact + locus>" | "<quoted design-intent>" | "<target+locus in conflict>" | "<named defect>" }
```

### Satisfied-close disposition (RBT-71)

The author's third action, `close_satisfied` (`author.py`; `author.prompt.md`),
closes a finding whose demand the current document text *already* meets. It adds
**no schema field and no status value** — a satisfied-close is an ordinary close
(`status = "closed"`, `pass_closed` stamped), so `open_cbm`, plateau, and the
router are arithmetically untouched (a satisfied-closed finding counts exactly as
an edit-closed one). It is distinguished only by its `resolution_note` variant
and its action-log events:

- `resolution_note = "satisfied: already conforms to <authority_satisfied>"` — the
  satisfied variant, parallel to the edit's `"conformed to <authority>"`.
- Action-log event **`author_satisfied`** (`finding_id`, `evidence` — the kind(s)
  checked, `["present"]` / `["absent"]` / both, `authority_satisfied`,
  `confidence`) — emitted when the mechanical evidence check passes and the
  finding closes.
- Action-log event **`author_satisfied_evidence_fail`** (`finding_id`, `failed` —
  which check(s) did not hold, `evidence_present_count`, `evidence_absent_count`)
  — emitted when the evidence does not verify; the finding is **escalated**, never
  closed. A malformed or unverified satisfied-close can never close a finding.

Safety: a *wrong* satisfied-close is caught by the existing recurrence trigger — a
reviewer re-raising the same identity next pass reopens the closed `id`,
increments `recurrence_count`, and halts loudly as `oscillation` (§Identity;
`mechanical-gates.md` §2).

## Pass record

| field | type | notes |
|---|---|---|
| `pass_number` | int | monotonic |
| `open_cbm_count` | int | snapshot of open counted-severity findings taken **at routing time** (post-admission, post-arbiter, pre-author). This is the identical value the router reads for its convergence check — one value, no drift. It is the plateau signal. |
| `agents_run` | string[] | which agents executed this pass |
| `timestamp` | iso8601 | |

## Doc-change record

The author-stub contract requires that a fix's document-state change be recorded
**in the ledger**. In dry mode nothing is applied to a real document, so the
coherence sweep has no filesystem change to observe and must read the change from
the ledger instead. The finding / pass / header records above do not carry this, so
the ledger also holds an explicit doc-change log alongside `findings` and `passes`.

| field | type | set by | notes |
|---|---|---|---|
| `doc` | string | author | the document id the (proposed) fix changed |
| `pass_number` | int | author | the pass in which the change was recorded |

`doc_changes` is a list on the ledger, parallel to `findings` and `passes`, and is
**deliberately not folded into the pass record.** The pass record is snapshotted at
routing time (pre-author); doc-changes are written by the author *after* routing, on
a CONTINUE. Folding them together would entangle the pre-author snapshot with
post-author mutation and put the single-value routing-time snapshot at risk. The
separateness is load-bearing, not incidental.

Firing semantics: a coherence / trading finding emits when its target document was
recorded changed in the **immediately preceding pass** (the fire-on-trigger half of
the emission discipline — see `antagonist-stub.prompt.md`). This is what lets
"closing one finding opens another" and "coherence re-runs whenever any document in
the set changes" work without real document mutation.

**Deployment-time enrichment (not in the skeleton).** When real authoring mutates
real documents, add `caused_by_finding_id` — the resolution that changed the doc —
so the log becomes a genuine audit trail of what changed and why. A document
version / content-hash ref may also be wanted so coherence can distinguish a real
edit from a no-op close. Neither is needed while the author is a dry stub.

## Ledger header

| field | type | notes |
|---|---|---|
| `set` | string[] | documents under review, e.g. `[ADR-001, ADR-002, DDR-001, DDR-002]` |
| `counted_severities` | enum[] | `[BLOCKING, MATERIAL]` (parameter) |
| `plateau_N` | int | passes-without-strict-decrease that trip plateau. Default `3`. |
| `mode` | enum | `dry` \| `live` |

## Identity (`id`) — the load-bearing subtlety

Oscillation detection is only possible if a finding keeps the **same `id`** when it
recurs. The naive implementation — minting a fresh `id` every pass — silently
disables recurrence detection, because a reopened finding looks brand-new. That is a
root-cause trap, not a cosmetic one.

Rule (amended RBT-69): `id` is derived deterministically at first emission from
`hash(sorted(target) + normalize_locus(locus) + altitude)` and **preserved**
thereafter. **`altitude` is in the key; `claim` is not.** When a reviewer emits a
finding whose derived `id` already exists in the ledger:
- if that `id` is currently `open` → it's the same standing finding, no new record
  (the claim-divergence guard below still fires on a materially-different claim);
- if that `id` was `closed` → re-admit as `open` and increment `recurrence_count`
  (this is a reopen — a signal for the oscillation detector).

**Why altitude replaced claim (RBT-69, empirical driver run-028).** The prior key
`hash(target + locus + normalize_claim(claim))` was too fine along the claim axis: a
hat re-emitting substantively the same finding with the claim reworded each pass
minted a fresh `id` every time and was admitted as net-new, inflating `open_cbm`
(run-028: 18 → 24 → 41 → 55 with zero recurrences — identity-failure inflation, not
coverage). Keying on locus alone is forbidden — one locus legitimately carries
several *distinct* findings (LAA claim-fidelity, SA conformance, EA reversibility,
coherence cross-reference), and merging them by locus would hide real findings.
Adding **altitude** threads the needle: a hat's re-emission of its own finding is
stable under wording drift (same target+locus+altitude), while two distinct-stance
findings at one locus stay separate (different altitude). The discriminator moves
from the brittle claim sentence to the stable stance-at-locus.

`normalize_locus` is a deterministic normalizer analogous to `normalize_claim`:
lowercase, strip markdown/punctuation/quoting noise, collapse whitespace. It
**absorbs formatting drift only** — it does not semantically alter the locus (quoted
section anchors are preserved). Kept conservative because over-normalizing a locus
risks merging distinct loci. `normalize_claim` is **retained** (now used only by the
claim-divergence guard below), never identity-bearing.

**Counting-semantics note (ratified as a feature).** Because altitude is in the key,
two hats raising the *identical* claim at one locus no longer dedup to one record —
they are two records at two altitudes. This preserves cross-hat overlap as the
roster-independence evidence the run protocol measures (run-supervision §5.3, §7),
which the prior claim-only key destroyed by deduping. A defect independently found by
two altitudes counts twice toward `open_cbm`; that is intended and is **not**
double-counting of the *same* finding (distinct altitude = distinct instrument's
finding). Do not "fix" this back to a single record.

### Claim-divergence guard (RBT-69)

The one residual risk of the coarser key is two genuinely-distinct findings sharing a
single `(target, locus, altitude)`. The guard is the safety net: on the `dedup_open`
path, if `normalize_claim(incoming) != normalize_claim(existing)`, the finding stays
**open** (nothing hidden), the incoming claim is preserved in a new `claim_variants:
list[str]` field on the existing record, and a `claim_divergence` action-log event is
emitted (`finding_id`, `existing_claim`, `incoming_claim`). No new record is created;
no claim is discarded. This guarantees the loop's safety property exactly — *a live
finding is never hidden; it stays open, surfaces, and carries every divergent claim
variant* — and routes the sole residual risk (under-counting two-as-one) to the cold
hand-audit (run-supervision §5), which is equipped to split it. Under-govern until it
hurts: no similarity apparatus, just never throw the variant away.

`claim` remains a mandatory record field, now purely descriptive. `claim_variants`
defaults to an empty list and round-trips through persistence.

**`source` / `altitude` — "set by: reviewer," satisfied at the port boundary
(ratified 2026-07-01).** For real LLM reviewers, the runner stamps both fields
from the invoked reviewer's identity, ignoring any value in the model's emitted
text — hardcode over trust; a hat cannot mislabel its own altitude, accidentally
or otherwise. See `runner-real-hats.contract.md` §7.

## Admission gate (mechanical — scope enforcement)

Before a finding enters the ledger it must pass a **structural** check:
`cited_authority` is present and well-formed (one of the four kinds above, with a
non-empty `ref`). A finding with `cited_authority == null`, or a `ref` that is a
bare preference ("I'd have designed it differently", "I'd prefer X"), is **dropped
and never counted**. This enforces the reviewer scope rule mechanically.

Honest seam: the gate can enforce that a citation of the required *shape* is
present. It cannot verify the citation is *honest* — a reviewer could dress a
preference as a fake authority ref. That discipline lives in the reviewer prompts,
not in this gate. Flagged, not solved.

## Severity — the house ladder (ratified 2026-07-01)

Severity is the `code-review` skill's ladder — `BLOCKING / MATERIAL / COSMETIC /
POSITIVE` — adopted as the single house vocabulary across every Haffey
tool/agent/system; no tool defines its own severity set. This replaces the
skeleton's earlier private `{critical, blocking, major}` set (which mapped
critical/blocking → `BLOCKING`, major → `MATERIAL`).

The convergence-counted set is `counted_severities = {BLOCKING, MATERIAL}` —
`BLOCKING` and `MATERIAL` are the two tiers that hold a change from landing;
`COSMETIC` and `POSITIVE` never count toward convergence and never block. This
preserves the original "no critical/blocking/major" strictness (major → `MATERIAL`,
still counted) under the single ladder.

Severity is orthogonal to the resolvable-vs-decision-bearing axis: a
`decision-bearing` finding halts regardless of its severity, so a `COSMETIC`
decision-bearing finding still halts even though it counts zero toward `open_cbm`
(see `mechanical-gates.md`).
