### [EA] MATERIAL — decision-bearing
- id: e1413b55d1a05a40
- locus: §2.2 Schema provisioning holds the sole-driver line
- claim: ADR-004 commits knowledge-service to expose a schema-provisioning capability — 'an addition its service design does not yet enumerate, gained as a named obligation of this decision' — but SDD-001 v1.6.0 is ACCEPTED and its §1 states knowledge-service is 'the sole holder of the Neo4j driver' whose ownership is enumerated for the DDR-002 §7 write/read invariant surface only; §3.1 readiness explicitly requires 'schema metadata loaded' as a precondition without any provisioning operation, and §3.6 ingestion port enumerates ingest / register-plane / mirror-gate-decision with no schema-DDL-provisioning operation. A new PROPOSED ADR imposing a new capability obligation on an already-ACCEPTED service design pulls against the settled posture and deserves the SDD amendment to be at least a named forward item there, not asserted solely from this record.
- cited_authority: coherence — ADR-004 §2.2 (schema-provisioning capability obligation) vs SDD-001 §1 / §3.1 / §3.6 (ACCEPTED; no provisioning operation enumerated, schema-present treated as a readiness precondition)

### [EA] MATERIAL — decision-bearing
- id: cae70c9e80ed731e
- locus: §2.7 Authoritative-source fidelity control; §5.3; §6 check 6
- claim: §2.7 states 'read-exclusion of provisional ground truth is committed as a schema-level invariant … That invariant is a forthcoming addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' This commits DDR-002 (an ACCEPTED, downstream schema record) to a new safety-critical read-discipline invariant from a PROPOSED upstream ADR, while DDR-002 §7's read-discipline set (#9, #19, retraction-exclusion) carries no provisional-exclusion invariant and its Named Gaps do not list one. Committing a downstream ACCEPTED record to a forthcoming safety-critical schema invariant is a hard-to-reverse cross-record obligation that deserves confirmation the amendment is homed and tracked, not asserted as a self-discharging forward reference.
- cited_authority: coherence — ADR-004 §2.7 (forthcoming schema read-discipline invariant for provisional read-exclusion) vs DDR-002 §7 read-discipline set + Named Gaps (no such invariant; not enumerated as a gap)

### [EA] MATERIAL — decision-bearing
- id: fbc8883b8c24be72
- locus: §2.7 / §7 Cross-References (ADR-008 relationship)
- claim: §2.7 asserts 'this ADR … is the record the governance record names as the home of the ingestion-mechanics authority' and §7 states 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)' and §2.2's realization route reads 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 routes ingestion *mechanics* to that record; ADR-004 §2.6/§2.7 explicitly disclaims owning port mechanics ('the port-level mechanics … are the knowledge-service design's') and instead claims to own the *authority* only. The self-identification as ADR-008's named home rests on a scope the record simultaneously narrows — a posture-fit question of whether ADR-004 actually discharges the forward reference ADR-008 opened.
- cited_authority: coherence — ADR-004 §2.7 (claims to be ADR-008's named forthcoming ingestion record, authority-only) vs ADR-008 §2.2 / §7 (routes ingestion mechanics, not bare authority, to that record)

### [EA] MATERIAL — decision-bearing
- id: 459c446f017af1d2
- locus: §2 Decision / §2.4 / §5.3 timing against deferred production runtime
- claim: The Decision depends on a runtime posture that is itself unsettled: §2.5 and §5.3 rest RG durability-across-instance-loss on 'instance-level backup and restore,' assigned in dev to the managed provider and for production 'deferred (see §5.3)'; ADR-002 §5.2 and §2.2 leave the production deployment runtime deferred. ADR-004 commits 'the RG is not source-recoverable and must not be presumed so' while its only recovery mechanism (backup/restore) is explicitly unspecified for production. Committing a no-destructive-reset structural guarantee whose sole RG-durability backstop is an as-yet-undecided production backup posture leaves a load-bearing safety property resting on a decision that has not been made — a premature-timing concern the record acknowledges but does not resolve.
- cited_authority: coherence — ADR-004 §2.5 / §5.3 (RG durability rests on backup/restore; production backup posture deferred) vs ADR-002 §2.2 / §5.2 (production deployment runtime deferred)

### [EA] MATERIAL — decision-bearing
- id: 9298a104cef145a6
- locus: §2.7 vs §2 decision sentence — standing read-discipline invariant riding inside an instantiation ADR
- claim: §2 states the decision at instantiation altitude: 'The SOFIA graph is instantiated greenfield from declared source artifacts...' But §2.7 commits a standing steady-state read-discipline invariant: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' Exclusion 'from ground-truth synthesis' governs every synthesis read, not merely instantiation. A commitment that constrains steady-state platform read-discipline deserves its own decision record — or at minimum its own enumerated decision — and here it rides inside a record framed and titled as instantiation architecture without being surfaced at decision altitude.
- cited_authority: coherence — ADR-004 §2 (instantiation-scoped decision sentence) vs §2.7 (standing schema-level read-exclusion invariant governing all ground-truth synthesis)

### [EA] MATERIAL — decision-bearing
- id: 66d4c0b416f29b9d
- locus: §2.7 — dependency of a PROPOSED record on an unauthored downstream schema amendment; reversibility disproportionate to unstated cost
- claim: §2.7 commits an invariant that 'is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' The record thereby makes a load-bearing safety commitment (§6 check 6 presents the fidelity gate as verifiable conformance) whose enforcement locus does not yet exist in DDR-002 §7 — which the record itself cites at §7 as the schema authority. A PROPOSED ADR obligating an already-ACCEPTED downstream schema record to a forthcoming safety-critical read-discipline invariant is a hard-to-reverse cross-record commitment; the posture of accepting this ADR before DDR-002 carries (or at least names as a gap) the amendment is a timing question the record does not resolve — it asserts the obligation as self-discharging rather than gating its own acceptance on the amendment landing.
- cited_authority: coherence — ADR-004 §2.7 / §6 check 6 (fidelity gate committed as schema-enforced conformance) vs DDR-002 §7 read-discipline invariant set (#9/#19/#21) and Named Gaps, which carry no provisional read-exclusion invariant

### [EA] MATERIAL — decision-bearing
- id: 1367ad48d12aef29
- locus: §2.2 — new capability obligation imposed on an already-ratified service design
- claim: §2.2 commits knowledge-service 'to expose a schema-provisioning capability — an addition its service design does not yet enumerate, gained as a named obligation of this decision.' SDD-001 is ACCEPTED (v1.6.0); its §1 enumerates knowledge-service's sole-driver ownership for the DDR-002 §7 write/read surface, §3.6 enumerates the ingestion port (ingest / register-plane / mirror-gate-decision) with no DDL-provisioning operation, and §3.1 treats 'schema metadata loaded' as a readiness precondition. A PROPOSED ADR mandating a new capability into an ACCEPTED service design pulls against the settled posture; the settled record deserves the amendment to be at least a named forward item on the SDD side, not asserted solely from this upstream record. The obligation is stated one-directionally, with no confirmation the receiving ACCEPTED design has a home for it.
- cited_authority: coherence — ADR-004 §2.2 (schema-provisioning capability obligation) vs SDD-001 §1 / §3.1 / §3.6 (ACCEPTED; no provisioning operation enumerated; schema-present treated as readiness precondition)

### [EA] MATERIAL — decision-bearing
- id: 85a52a2bddbb7ece
- locus: §2.2 / §5.3 — constraint-versioning ownership deferred with no located home or firing trigger
- claim: §2.2 defers a live forward question — 'how the provisioning capability evolves a live instance's constraints... its policy not settled here — tracked as a forward item against the schema-provisioning capability's design.' §5.3 restates it as 'a named forward question, not a silent gap.' But the deferral is homed only to an unnamed 'capability's design' with no record, ticket, or event that re-surfaces it. Constraint evolution over a live populated instance is a decision with real blast radius (it can alter what the gateway validates every write against); leaving it deferred without a locatable home and firing trigger is a posture that will calcify — the obligation has nowhere concrete to land.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated, no named home or trigger)

### [EA] MATERIAL — decision-bearing
- id: 4c0c39d9322b3fc1
- locus: §2 Decision / §2.5 / §5.3 — a structural safety guarantee resting on an unsettled production runtime decision
- claim: The Decision's RG-durability posture depends on a decision not yet made. §2.5 rests RG durability-across-instance-loss on 'instance-level backup and restore,' assigned in dev to the managed provider and for production 'deferred (see §5.3),' and commits 'the RG is not source-recoverable and must not be presumed so.' ADR-002 §2.2/§5.2 leave the production deployment runtime — and therefore its backup posture — deferred. The record commits a no-destructive-reset structural guarantee whose sole RG-durability backstop is an as-yet-undecided production backup posture. The instantiation-path guarantee (no path discards the RG) is sound, but the record's own §5.1 positive claim and §2.5 lean on backup/restore as the recovery mechanism, and that mechanism is explicitly unspecified for production — a load-bearing durability property resting on a decision the platform has not yet taken.
- cited_authority: coherence — ADR-004 §2.5 / §5.3 (RG durability rests on backup/restore; production backup posture deferred) vs ADR-002 §2.2 / §5.2 (production deployment runtime deferred; burden 'returns for production... weighed at the production-environment build')

### [EA] MATERIAL — decision-bearing
- id: 17fe572a6ec7e56e
- locus: §2 Decision sentence vs §2.7 schema-level read-exclusion invariant
- claim: The §2 decision sentence scopes the record to greenfield instantiation ('The SOFIA graph is instantiated greenfield from declared source artifacts, and instantiation ... is orchestrated by a driver-less loader'). §2.7 commits a standing steady-state read-discipline invariant that is not surfaced at the decision altitude: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' Exclusion from ALL ground-truth synthesis governs every synthesis read, not merely instantiation — a standing platform-wide consumption rule riding inside a record framed and titled as instantiation architecture. A commitment that constrains steady-state platform read-discipline is a position that deserves its own decision surface, or at minimum its own enumerated sub-decision; here it stands only in a sub-section of an instantiation ADR.
- cited_authority: coherence — ADR-004 §2 (instantiation-scoped decision sentence) vs §2.7 (schema-level read-exclusion invariant governing all ground-truth synthesis)

### [EA] MATERIAL — decision-bearing
- id: 7e440c4a7a696b1c
- locus: §2.7 / §6 check 6 — load-bearing safety commitment resting on an unauthored downstream schema amendment; acceptance timing
- claim: §2.7 commits read-exclusion of provisional ground truth 'as a schema-level invariant' while conceding it 'is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' §6 check 6 presents the fidelity gate as verifiable conformance. A PROPOSED ADR thus commits an ACCEPTED downstream schema record (DDR-002 §7, whose read-discipline set #9/#19/#21 carries no such invariant) to a forthcoming safety-critical invariant that does not yet exist — a hard-to-reverse cross-record obligation the record asserts as self-discharging rather than gating its own acceptance on the amendment landing. Whether this ADR should stand ACCEPTED before DDR-002 carries (or at least names as a gap) the amendment is a timing question left unresolved: the record commits the guarantee in present voice while its enforcement locus is not yet built.
- cited_authority: coherence — ADR-004 §2.7 ('forthcoming addition ... not one the schema already carries') / §6 check 6 vs DDR-002 §7 read-discipline invariant set (#9/#19/#21) and Named Gaps, neither carrying nor tracking the amendment

### [EA] MATERIAL — decision-bearing
- id: 19069fca6a8638e3
- locus: §2.7 — self-identification as ADR-008's named ingestion-mechanics home vs disclaimed mechanics
- claim: §2.7 asserts this ADR 'is the record the governance record names as the home of the ingestion-mechanics authority' and §7 restates 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names that forthcoming record as one that 'owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2),' and ADR-008 §2.2 routes the control to 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 assigned that home ownership of ingestion *mechanics realization*; ADR-004 §2.7 claims to own bare 'authority/locus' only while disclaiming the mechanics ('the port-level mechanics ... how the official-entry transition is enforced ... are the knowledge-service design's'). The record self-identifies as the discharge of ADR-008's forward reference while narrowing its ownership below what that reference assigned — the authority/mechanics distinction §2.7 rests on is not a distinction ADR-008's cited loci draw.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' + 'port-level mechanics ... are the knowledge-service design's') and §7 vs ADR-008 §2.2 / §7 (forthcoming ingestion record owns ingestion mechanics realization)

### [EA] MATERIAL — decision-bearing
- id: 5d8876563a31cdb0
- locus: §2.7 / §5.2 — 'externally-decided mirrored records' exclusion category not recognized by the cited governance record
- claim: §2.7 and §5.2 exempt 'externally-decided mirrored records' from the fidelity gate ('it is not applied to ... externally-decided mirrored records'; §5.2: 'mirrored externally-decided records are not gated'). ADR-008 §2.2's four calibrated source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' KG-ground-truth mutation class exists there. The corpus's mirrored external record (DDR-002 §2.4 GateDecision, origin_mechanism: ingested) is scoped to produced-Solution SDLC gates, not KG ground-truth entry. The record scopes its control 'per the governance record' while carving an exemption category that record does not enumerate as a mutation class — the exemption cites an authority (ADR-008 §2.2) that does not resolve to it.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt) against ADR-008 §2.2 four-class calibration table (no mirrored-external-record ingestion class)

### [EA] COSMETIC — decision-bearing
- id: 8efe3e1b7efa2acf
- locus: §2.7 / §5.2 — a scope-exclusion category ('mirrored externally-decided records') not recognized by the governance record it cites
- claim: §2.7 and §5.2 exempt 'externally-decided mirrored records' from the fidelity gate ('it is not applied to... externally-decided mirrored records'; §5.2: 'mirrored externally-decided records are not gated'). ADR-008 §2.2's four source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' class appears there as a KG-ground-truth mutation class. The mirrored-external record the corpus carries (DDR-002 §2.4 GateDecision, origin_mechanism: ingested) is scoped to produced-Solution SDLC gates, not KG ground-truth instantiation. The record introduces a scope-exclusion category the governance authority it cites does not enumerate — a posture that quietly asserts a mutation class exists in scope-terms the owning record does not recognize.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt from the fidelity gate) against ADR-008 §2.2 four-class calibration table (no mirrored-external-record ingestion class)

### [EA] COSMETIC — decision-bearing
- id: df712e9e1741d47f
- locus: §2.2 / §5.3 — constraint-versioning forward item has no locatable home or firing trigger
- claim: §2.2 defers constraint-versioning ownership ('a forward question ... tracked as a forward item against the schema-provisioning capability's design') and §5.3 restates it as 'a named forward question, not a silent gap.' Neither names a ticket, decision record, or event that re-surfaces the obligation, and the sole home offered ('the schema-provisioning capability's design') is itself an unauthored, un-enumerated design. Constraint evolution over a live populated instance carries real blast radius (it alters what the gateway validates every write against); leaving it deferred without a locatable home and firing trigger is a posture that calcifies — the obligation has nowhere concrete to land.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated with no named home or trigger)

### [EA] POSITIVE — unclassified
- id: 87bc598b00795abf
- locus: §2.1 / §2.2 / §4.1 / §4.2 (sole-driver line for instantiation)
- claim: I attacked the decision for carving a first-load exception into ADR-002's sole-owner-of-the-driver principle — the classic instantiation-bypass posture that would pull against the ratified system-of-record commitment. The record holds: it routes instantiation data through the ingestion port (§2.1), holds schema provisioning inside knowledge-service over the driver it already holds rather than a second driver (§2.2), and explicitly rejects both the privileged-bulk-load (§4.1) and separate-provisioning-tool-with-own-driver (§4.2) alternatives. The posture integrates with ADR-002 §2.5 rather than eroding it.
- cited_authority: canonical — ADR-002 §2.5 (sole-holder-of-the-driver principle) — ADR-004 §2.1/§2.2/§4.1/§4.2 preserve it for instantiation

### [EA] POSITIVE — unclassified
- id: 798858f049021c8f
- locus: §2.4 / §2.5 / §4.3 (additive-by-supersession, RG preserved by construction)
- claim: I attacked 'fresh / no migration' as a likely license to reset a live graph — the reading that would endanger the never-delete and supersession disciplines and silently discard reasoning state. The record forecloses it: §2.3 binds 'fresh' to origin only, §2.4 makes the load additive-by-supersession with no destructive-reset mode, §2.5 scopes instantiation to the KG and forbids writing/reconstructing/discarding the RG, and §4.3 rejects destructive re-instantiation on exactly the never-delete/supersession grounds. Reversibility is proportionate — additive accretion, not overwrite — and the RG-loss hazard is structurally, not aspirationally, closed.
- cited_authority: canonical — DDR-002 §6 supersession discipline + §7 never-delete; ADR-001 §2.2 reasoning-capture invariant — ADR-004 §2.3/§2.4/§2.5/§4.3 conform

### [EA] POSITIVE — unclassified
- id: e1d841bc7b01e183
- locus: §2.1 / §2.2 / §4.1 / §4.2 — sole-driver line preserved for instantiation
- claim: I attacked the decision at its most tempting failure posture: carving a first-load exception into ADR-002's sole-owner-of-the-driver principle, the classic instantiation-bypass that would erode the ratified system-of-record commitment. It held. The record routes instantiation data through the ingestion port (§2.1), holds schema provisioning inside knowledge-service over the driver it already owns rather than sanctioning a second driver (§2.2), and explicitly rejects both the privileged-bulk-load (§4.1) and separate-provisioning-tool-with-own-driver (§4.2) alternatives on grounds that trace to ADR-002's diffuse-driver hazard. The posture integrates with prior ratified platform direction rather than pulling against it — reversibility is proportionate because no standing exception is created.
- cited_authority: canonical — ADR-002 §2.5 (sole-holder-of-the-driver principle) — ADR-004 §2.1/§2.2/§4.1/§4.2 preserve it for instantiation

### [EA] POSITIVE — unclassified
- id: 868543a7e5c319bd
- locus: §2.3 / §2.4 / §2.5 / §4.3 — 'fresh / no migration' bounded to origin; RG-loss hazard structurally closed
- claim: I attacked 'fresh / no migration' as the likely license to reset a live graph — the reading that would endanger the never-delete and supersession disciplines and silently discard reasoning state, the platform's reason to exist. The record forecloses it: §2.3 binds 'fresh' to origin only, §2.4 makes the load additive-by-supersession with no destructive-reset mode, §2.5 scopes instantiation to the KG and forbids writing/reconstructing/discarding the RG, and §4.3 rejects destructive re-instantiation on exactly the never-delete/supersession grounds. The commitment integrates with prior decisions (ADR-002 §2.1, DDR-002 §6) and the RG-loss hazard is structurally, not aspirationally, closed. This posture should stand in this shape.
- cited_authority: canonical — ADR-001 §2.2 (reasoning-capture invariant), DDR-002 §6 (Option A supersession) / §7 (never-delete) — ADR-004 §2.3/§2.4/§2.5/§4.3 conform

### [LAA] MATERIAL — decision-bearing
- id: 52ca1e23119cc14d
- locus: §2.7 Authoritative-source fidelity control / title & summary claim
- claim: The record's title and §1 forcing-function frame it as instantiation/ingestion architecture, but §2.7 decides a substantive read-discipline invariant beyond instantiation: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' This commits a standing steady-state read-discipline invariant (excluding provisional nodes from ALL synthesis, not merely at instantiation) that is not surfaced in the §2 decision-sentence, which scopes the decision to greenfield instantiation ('The SOFIA graph is instantiated greenfield...'). A standing schema invariant governing steady-state synthesis rides along inside an instantiation ADR without being enumerated as a decision it claims to make.
- cited_authority: coherence — ADR-004 §2 (decision sentence, instantiation-scoped) vs ADR-004 §2.7 (schema-level read-exclusion invariant governing all ground-truth synthesis)

### [LAA] MATERIAL — decision-bearing
- id: 7084eb5383e55ee1
- locus: §2.7 dependency on a forthcoming schema amendment
- claim: §2.7 states the read-exclusion invariant 'is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' The record thus decides a schema invariant it does not itself own and that does not yet exist in the authority it cites (DDR-002 §7), while §2.6 and §6 present the fidelity gate as a committed compliance check. The record depends on an as-yet-unauthored DDR-002 amendment to make its own §2.7 commitment enforceable, but names that dependency only as a downstream obligation rather than declaring the record CONDITIONAL/blocked on it — a consequence (the commitment is inoperative until DDR-002 is amended) that is under-declared at decision altitude.
- cited_authority: coherence — ADR-004 §2.7 (forthcoming DDR-002 read-discipline invariant addition) vs DDR-002 §7 (current read-discipline invariant set, which does not carry it)

### [LAA] MATERIAL — decision-bearing
- id: 30eee3448560b641
- locus: §2.7 — routing-home claim vs ADR-008's named home
- claim: §2.7 claims 'this ADR ... is the record the governance record names as the home of the ingestion-mechanics authority.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)' and §2.2's realization-routes column routes the ingestion control to 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-004 §2.7 asserts it owns the ingestion-mechanics *authority* while simultaneously routing the port-level mechanics away ('The port-level mechanics ... are the knowledge-service design's'). The claimed decision content — that this record decides ingestion mechanics authority — is contradicted within §2.7 itself, which decides the locus/existence but explicitly does not decide the mechanics; the record claims to home an authority it then disclaims.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' vs 'port-level mechanics ... are the knowledge-service design's') and ADR-008 §7 / §2.2 (forthcoming ingestion decision record ownership)

### [LAA] MATERIAL — decision-bearing
- id: 80c28c05a43907e9
- locus: §2 Decision sentence vs §2.7 schema-level read-exclusion invariant
- claim: The §2 decision sentence scopes the record to greenfield instantiation ('The SOFIA graph is instantiated greenfield from declared source artifacts, and instantiation ... is orchestrated by a driver-less loader'). §2.7 then decides a standing steady-state read-discipline invariant that is not surfaced at the decision altitude: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' Exclusion from ALL ground-truth synthesis is a steady-state consumption rule, not an instantiation act; a standing schema invariant governing synthesis rides along inside an instantiation ADR without being enumerated as a decision the record claims to make.
- cited_authority: coherence — ADR-004 §2 (decision sentence, instantiation-scoped) vs §2.7 (schema-level read-exclusion invariant governing all ground-truth synthesis)

### [LAA] MATERIAL — decision-bearing
- id: 380c6cfeaa53e0d4
- locus: §2.7 — self-identification as ADR-008's named home vs disclaimed mechanics
- claim: §2.7 claims 'this ADR ... is the record the governance record names as the home of the ingestion-mechanics authority' and §7 restates 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' But ADR-008 §7 names that forthcoming record as one that 'owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2),' and ADR-008 §2.2 routes the control to 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-004 §2.7 simultaneously claims to own the 'authority' while routing mechanics away: 'The port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's.' The record claims to discharge a forward reference framed as owning *mechanics*, then internally narrows its own decision content to 'authority' only and disclaims the mechanics — the decision it claims to make (be ADR-008's named home) is not the decision its own §2.7 body supports.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' + 'port-level mechanics ... are the knowledge-service design's') and §7 vs ADR-008 §2.2 / §7 (forthcoming ingestion record owns ingestion mechanics)

### [LAA] MATERIAL — decision-bearing
- id: 36b1b7ecf6071693
- locus: §2.7 / §2.6 — fidelity gate presented as committed compliance check while its enforcement locus does not yet exist
- claim: §6 check 6 presents the fidelity gate as a mandatory conformance check ('Authoritative-source ground truth reaches official, consumable state only through a human fidelity verification, and provisional nodes are read-excluded from synthesis until then'), and §2.7 states the read-exclusion 'is committed as a schema-level invariant.' Yet §2.7 also states that invariant 'is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' The consequence — that the §2.7 read-exclusion commitment is inoperative until DDR-002 is amended, so §6 check 6's mechanized half does not yet exist — is a side effect of the decision that is under-declared at decision altitude; the record does not surface that a load-bearing safety commitment is conditional on an unauthored downstream amendment.
- cited_authority: coherence — ADR-004 §2.7 ('forthcoming addition ... not one the schema already carries') vs §2.6/§6 check 6 (fidelity gate presented as committed) — consequence under-declared

### [LAA] MATERIAL — decision-bearing
- id: 68df74197a06b16b
- locus: §2.7 / §5.2 — 'externally-decided mirrored records' exclusion category not owned by the cited authority
- claim: §2.7 and §5.2 exclude 'externally-decided mirrored records' from the fidelity gate ('it is not applied to the ungated Environment observation stream or to externally-decided mirrored records'). ADR-008 §2.2's four source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' class exists there. The record introduces a scope-exclusion category that the ground-truth-mutation governance record it cites as authority does not enumerate as a mutation class; the decision claims to scope a control per ADR-008 while naming an exclusion the governance record does not carry — a consequence/dependency the record does not declare.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt) vs ADR-008 §2.2 four-class calibration table (no mirrored-external-record class)

### [LAA] MATERIAL — decision-bearing
- id: 5041152469207d96
- locus: §2.7 / §7 — self-identification as ADR-008's named home vs disclaimed mechanics
- claim: §2.7 claims 'this ADR ... is the record the governance record names as the home of the ingestion-mechanics authority' and §7 restates 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names that forthcoming record as one that 'owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)', and ADR-008 §2.2 routes the control to 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 assigns that home ingestion *mechanics realization*. ADR-004 §2.7 disclaims owning port mechanics ('the port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's') and narrows its own decision content to 'authority' only — the decision it claims to make (be ADR-008's named home) is not the decision its own §2.7 body supports.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' + 'port-level mechanics ... are the knowledge-service design's') and §7 vs ADR-008 §2.2 / §7 (forthcoming ingestion record owns ingestion mechanics realization)

### [LAA] COSMETIC — decision-bearing
- id: 3d7f1f5fad3d5790
- locus: §2.2 constraint-versioning forward item
- claim: §2.2 defers constraint-versioning ownership ('a forward question ... tracked as a forward item against the schema-provisioning capability's design') but names no ticket, decision record, or firing trigger for it, and §5.3 restates it as a 'named forward question, not a silent gap' without a home. The consequence of a deferred sub-decision is declared, but the deferral is homed only to an unnamed 'capability's design,' leaving the forward obligation without a locatable home.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated with no named home or trigger)

### [LAA] COSMETIC — decision-bearing
- id: 9b73cee83ae39677
- locus: §2.7 'selection-catalog and standards planes' vs canonical plane name
- claim: §2.7 names the authoritative-source planes as 'the selection-catalog and standards planes.' The canonical plane name owned by the schema is 'Catalog' (DDR-002 §2.1 '(:Catalog:...)'; DDR-001 Decision.2 'Catalog'), and ADR-008 §2.2's ingestion row reads 'Catalog / Standards.' 'Selection-catalog' is not the plane name the owning records carry; the record depends on a shared entity name it renders in a form the authority does not use, a drift on a term this ADR does not own.
- cited_authority: coherence — ADR-004 §2.7 'selection-catalog' vs DDR-002 §2.1 / DDR-001 Decision.2 canonical plane name 'Catalog' (ADR-008 §2.2 'Catalog / Standards')

### [LAA] COSMETIC — decision-bearing
- id: bc6532111468301c
- locus: §2.2 / §5.3 — constraint-versioning forward item has no locatable home or firing trigger
- claim: §2.2 defers constraint-versioning ownership: 'a forward question ... tracked as a forward item against the schema-provisioning capability's design.' §5.3 restates it as 'a named forward question, not a silent gap.' Neither names a ticket, a decision record, or an event that re-surfaces the obligation; the deferral is homed only to an unnamed 'capability's design' that does not yet exist. A consequence of the decision (deferred constraint-versioning ownership) is declared but its home is not locatable.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated, no named home or trigger)

### [LAA] POSITIVE — unclassified
- id: 952caf2c356e8924
- locus: §2.5 KG-scoped / RG preserved by construction
- claim: Attacked whether §2.5 overclaims RG safety relative to what the decision content supports. It does not: the record carefully qualifies the guarantee to instantiation-caused loss ('neither written, reconstructed, nor discarded by instantiation'), explicitly states the RG 'is not source-recoverable and must not be presumed so,' and separates instance-loss durability onto backup/restore (§5.3 risk) rather than claiming the instantiation path secures it. §5.1 further scopes the positive consequence to 'safe *from instantiation-caused loss* by construction.' The prose claims exactly what the decision supports and no more — the scope of the RG guarantee is honestly bounded.
- cited_authority: coherence — ADR-004 §2.5 and §5.1 (RG guarantee bounded to instantiation-caused loss; instance-loss durability routed to §5.3 backup/restore) — consistent, not overclaimed

### [LAA] POSITIVE — unclassified
- id: 3f9ff61dbd8620ff
- locus: §2.4 Additive by supersession
- claim: Attacked whether §2.4 claims to decide destructive-reset behavior it does not actually foreclose, or contradicts the additive claim. It holds: the record states the behavior is 'selected per node by the graph's current state, not by a loader mode,' forecloses in-place overwrite ('requires an explicit version increment ... there is no in-place overwrite'), and states plainly 'The instantiation path exposes no destructive-reset operation.' Alternative C (§4.3) records the rejected wipe-and-reload with a specific rationale grounding it in the schema's never-delete discipline. The decision-content, its rejected alternative, and the §5.2 constraint all agree — the additive-not-destructive commitment is stated at a testable, non-contradictory grain.
- cited_authority: coherence — ADR-004 §2.4, §4.3 (Alternative C rejection), §5.2 (no destructive-reset constraint) — mutually consistent

### [LAA] POSITIVE — unclassified
- id: f6798d518c1490f1
- locus: §2.5 / §5.1 — RG-preservation guarantee scope
- claim: I attacked §2.5 for overclaiming RG safety beyond what the decision content supports — the classic instantiation ADR that promises the reasoning record is 'safe' when it only controls one path. The claim holds honestly: §2.5 bounds the guarantee to instantiation-caused loss ('neither written, reconstructed, nor discarded by instantiation'), explicitly states the RG 'is not source-recoverable and must not be presumed so,' routes instance-loss durability onto backup/restore (§5.3 risk), and §5.1 scopes the positive consequence to 'safe *from instantiation-caused loss* by construction.' The prose claims exactly what the decision supports and no more — the RG guarantee's scope is honestly bounded, and the side effect (RG not source-recoverable) is surfaced as a declared consequence.
- cited_authority: coherence — ADR-004 §2.5 and §5.1 (RG guarantee bounded to instantiation-caused loss; instance-loss durability routed to §5.3) — consistent, not overclaimed

### [LAA] POSITIVE — unclassified
- id: 13f71f0f9e2c85c5
- locus: §2.4 / §4.3 / §5.2 — additive-by-supersession decision grain
- claim: I attacked §2.4 for claiming to decide destructive-reset behavior it does not actually foreclose, or for contradicting its additive claim across Decision, Alternatives, and Consequences. It holds: §2.4 selects behavior per node by graph state ('not by a loader mode'), forecloses in-place overwrite ('requires an explicit version increment ... there is no in-place overwrite'), and states 'The instantiation path exposes no destructive-reset operation.' Alternative C (§4.3) records the rejected wipe-and-reload with a specific rationale, and the §5.2 constraint restates the no-reset commitment. The decision content, its rejected alternative, and its declared consequence agree at a testable grain — the additive-not-destructive commitment decides exactly what it claims, no more.
- cited_authority: coherence — ADR-004 §2.4, §4.3 (Alternative C rejection), §5.2 (no destructive-reset constraint) — mutually consistent decision content

### [SA] MATERIAL — decision-bearing
- id: 28c1a26163a267a7
- locus: §2.2 Schema provisioning holds the sole-driver line
- claim: §2.2 states schema provisioning 'is ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards. ... the service process can start and connect to an empty instance, so provisioning runs before readiness reports green (which checks that the schema is present).' SDD-001 §3.1 (cited by this ADR at §7) specifies readyz returns 503 unless '(2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate)' and states 'There is no degraded mode.' The ADR asserts knowledge-service exposes and executes a schema-provisioning capability over its driver while the service is not-ready by its own cited readiness contract; the cited authority does not substantiate that knowledge-service can serve any operation (including a provisioning operation) before readiness reports green.
- cited_authority: coherence — ADR-004 §2.2 vs SDD-001 §3.1 (readiness: schema-present check fails readyz, no degraded mode)

### [SA] MATERIAL — decision-bearing
- id: f089070e090281f0
- locus: §2.7 Authoritative-source fidelity control
- claim: §2.7 claims to realize ADR-008's fidelity control and states 'read-exclusion of provisional ground truth is committed as a schema-level invariant ... That invariant is a forthcoming addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' This ADR is PROPOSED and commits a schema-level invariant that DDR-002 does not carry, yet DDR-002 §7 (cited at §7) enumerates its read-discipline invariants (#9, #19, #21) with none covering provisional-authoritative-source read-exclusion; the ADR names an amendment obligation against DDR-002 without DDR-002 (or any accepted record) carrying it. The claimed schema-level enforcement locus is unsubstantiated in the cited schema authority at the time this record is offered.
- cited_authority: canonical — DDR-002 §7 (read-discipline invariant set — #9, #19, #21) — no provisional read-exclusion invariant present, cf. ADR-004 §2.7

### [SA] MATERIAL — decision-bearing
- id: bef4aa669a3045ae
- locus: §2.7 / §2.2 — routing of ingestion-mechanics authority
- claim: §2.7 states this ADR 'is the record the governance record names as the home of the ingestion-mechanics authority.' ADR-008 §2.2 (cited at §7) routes the authoritative-source ingestion control to 'The forthcoming ingestion decision record; the knowledge-service ingestion port' and ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2).' ADR-008 routes the ingestion *mechanics realization* to the forthcoming record and separately routes port mechanics to knowledge-service; ADR-004 §2.7 simultaneously claims to be the home of ingestion-mechanics *authority* AND routes 'the port-level mechanics ... how the official-entry transition is enforced' to the knowledge-service design — the split between what this ADR owns and what the port owns is asserted but the cited ADR-008 loci do not distinguish 'authority' from 'mechanics' in the terms §2.7 uses to divide them.
- cited_authority: coherence — ADR-004 §2.7 vs ADR-008 §2.2 and §7 (ingestion decision record / knowledge-service ingestion port routing)

### [SA] MATERIAL — decision-bearing
- id: 7728c4d8c05e9870
- locus: §3.1 readiness ordering vs SDD-001 §3.1 / §2.2 schema-provisioning-before-readiness
- claim: §2.2 states provisioning 'is ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards … the service process can start and connect to an empty instance, so provisioning runs before readiness reports green (which checks that the schema is present).' SDD-001 §3.1 (cited at §7) specifies readyz returns '503 otherwise' with '(2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode.' The ADR requires knowledge-service to execute a provisioning operation over its driver while the service reports not-ready by its own cited readiness contract; the cited SDD-001 §3.1 substantiates no capability, mode, or operation that runs before readiness reports green, so the claim that provisioning 'runs before readiness reports green' has no substantiation in the cited authority.
- cited_authority: coherence — ADR-004 §2.2 (provisioning ordered ahead of readiness, service serves it while not-ready) vs SDD-001 §3.1 (schema-present is a critical readiness precondition; no degraded mode; gateway must not execute writes it cannot validate)

### [SA] MATERIAL — decision-bearing
- id: 6ff050ca7bf7b2ce
- locus: §2.2 schema-provisioning capability vs SDD-001 §3.6 ingestion-port operation set
- claim: §2.2 commits knowledge-service to 'expose a schema-provisioning capability — an addition its service design does not yet enumerate, gained as a named obligation of this decision.' SDD-001 v1.6.0 is ACCEPTED and its §3.6 ingestion port enumerates exactly 'ingest', 'register-plane', and 'mirror-gate-decision', with no schema-DDL-provisioning operation; §2.1 enumerates the service's sole-authorised acts without any data-definition/constraint-provisioning operation. The ADR's own compliance check 2 ('Sole-driver-for-schema-too … Schema provisioning runs through knowledge-service's driver') is stated as a committed check, but the operation it verifies conformance against does not exist in the cited service design — the enforcement target is absent at the locus the ADR routes to.
- cited_authority: coherence — ADR-004 §2.2 / §6 check 2 (schema-provisioning capability + committed compliance check) vs SDD-001 §2.1 / §3.6 (ACCEPTED; no provisioning operation enumerated)

### [SA] MATERIAL — decision-bearing
- id: 34cb38c33c381821
- locus: §2.7 provisional read-exclusion committed as a schema-level invariant vs DDR-002 §7 read-discipline set
- claim: §2.7 states 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' It then concedes 'That invariant is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' DDR-002 §7 enumerates the CI-only invariant set and names the read-discipline invariants (#9 proposal-visibility, #19 conditional-consumption, #21 retraction-gated); none covers provisional-versus-official read-exclusion, and DDR-002 §2/§5 carry no provisional-state concept. The invariant this ADR states as 'committed' does not exist in the cited owning schema authority (DDR-002 §7), and DDR-002 does not reference or track the amendment obligation — the committed schema-level enforcement locus is unsubstantiated in the authority ADR-004 cites for it.
- cited_authority: canonical — DDR-002 §7 (read-discipline invariants #9/#19/#21; no provisional read-exclusion invariant) — cf. ADR-004 §2.7 'committed as a schema-level invariant'

### [SA] MATERIAL — decision-bearing
- id: 0793ed8eb06d74f9
- locus: §2.7 — 'home of the ingestion-mechanics authority' self-contradicting with disclaimed mechanics
- claim: §2.7 asserts this ADR 'is the record the governance record names as the home of the ingestion-mechanics authority — the decision that authority is routed to, distinct from the port-level mechanics that realize it,' while the same paragraph states 'The port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)', and ADR-008 §2.2's realization route reads 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 routes the ingestion *mechanics* to that record, but ADR-004 claims to own bare 'authority' while disclaiming the mechanics — the distinction between 'authority' and 'mechanics' on which §2.7's self-identification rests is not a distinction the cited ADR-008 loci draw, so the claim that this record discharges ADR-008's named forward reference is not substantiated by the reference it invokes.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' vs 'port-level mechanics … are the knowledge-service design's') against ADR-008 §2.2 / §7 (ingestion mechanics routed to the forthcoming record; port mechanics to knowledge-service)

### [SA] MATERIAL — decision-bearing
- id: 38c4ae886e2372c4
- locus: §2.7 / §5.2 — 'externally-decided mirrored records' exemption not an enumerated ingestion class in ADR-008
- claim: §2.7 states the fidelity gate 'is not applied to the ungated Environment observation stream or to externally-decided mirrored records', and §5.2 restates 'the ungated Environment observation stream and mirrored externally-decided records are not gated.' ADR-008 §2.2's four source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' class exists as a ground-truth mutation class there. The only mirrored external record in the corpus is DDR-002 §2.4's GateDecision (origin_mechanism: ingested), which DDR-002 §2.4 scopes to produced-Solution SDLC gates, not KG ground-truth instantiation. ADR-004 introduces a scope-exemption category the governance record it cites does not enumerate as a mutation class subject to (or exempt from) the ingestion control, so the exemption cites an authority (ADR-008 §2.2) that does not resolve to it.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt) against ADR-008 §2.2 four-class calibration table (no mirrored-external-record ingestion class) and DDR-002 §2.4 (GateDecision scoped to produced-Solution SDLC gates)

### [SA] MATERIAL — decision-bearing
- id: a37a85b16f877378
- locus: §2.7 'selection-catalog and standards planes' vs canonical plane name
- claim: §2.7 names the authoritative-source planes as 'the selection-catalog and standards planes'. ADR-008 §2.2 names the authoritative-source-ingestion class 'Catalog / Standards'; DDR-002 §2.1 and DDR-001 Decision.2 fix the canonical plane name as 'Catalog'. 'selection-catalog' is not the canonical plane name any owning authority uses — DDR-002 §2.1 titles §2.1 'Catalog — the selection graph', which describes the Catalog plane's role, not a plane named 'selection-catalog'. The term drifts the shared plane entity ADR-008/DDR-002 own into a name that resolves to no plane in the schema.
- cited_authority: coherence — ADR-004 §2.7 'selection-catalog and standards planes' vs DDR-002 §2.1 / DDR-001 Decision.2 canonical plane name 'Catalog' and ADR-008 §2.2 'Catalog / Standards'

### [SA] MATERIAL — decision-bearing
- id: 4ec9d57d6ddc0830
- locus: §2.2 constraint-versioning forward item — deferral with no locatable home
- claim: §2.2 defers constraint-versioning ownership: 'Ownership of constraint *versioning* over the platform's life … is a forward question, governed by construction … but with its policy not settled here — tracked as a forward item against the schema-provisioning capability's design.' §5.3 restates 'the versioning policy is a named forward question, not a silent gap.' No ticket, decision record, or firing trigger names where this obligation lives; 'the schema-provisioning capability's design' is itself an unauthored, un-enumerated capability (§2.2, per the operation absent in SDD-001 §3.6). The deferred obligation is stated but homed only to a design that does not yet exist and carries no trigger for its re-surfacing.
- cited_authority: soundness — ADR-004 §2.2 / §5.3 — deferred constraint-versioning obligation named without a locatable home, ticket, or firing trigger; the named home ('the schema-provisioning capability's design') is not itself a resolvable artifact in the set

### [SA] MATERIAL — decision-bearing
- id: afa739934083596c
- locus: §2.2 Schema provisioning holds the sole-driver line vs SDD-001 §3.1 readiness
- claim: §2.2 states provisioning 'is ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards ... the service process can start and connect to an empty instance, so provisioning runs before readiness reports green (which checks that the schema is present).' SDD-001 §3.1, cited by ADR-004 §7, states readyz returns '503 otherwise' and that '(2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode.' The claim that knowledge-service serves a provisioning operation over its driver 'before readiness reports green' is not substantiated by the cited authority, which supplies no pre-readiness operation mode and states the gateway must not execute writes it cannot validate.
- cited_authority: coherence — ADR-004 §2.2 (provisioning runs before readiness reports green) vs SDD-001 §3.1 (schema-present is a critical readiness precondition; no degraded mode; gateway must not execute writes it cannot validate)

### [SA] MATERIAL — decision-bearing
- id: 335eee1b9f6630d2
- locus: §2.2 / §6 check 2 schema-provisioning capability vs SDD-001 §2.1 / §3.6 operation set
- claim: §2.2 commits knowledge-service to 'expose a schema-provisioning capability — an addition its service design does not yet enumerate,' and §6 check 2 states as a committed conformance check that 'Schema provisioning runs through knowledge-service's driver.' SDD-001 v1.6.0 is ACCEPTED (cited at §7); its §3.6 ingestion port enumerates exactly 'ingest', 'register-plane', and 'mirror-gate-decision' with no schema-DDL-provisioning operation, and §2.1 lists knowledge-service's sole-authorised acts without any data-definition/constraint-provisioning operation. The operation §6 check 2 verifies conformance against does not exist in the cited service design — the enforcement target is absent at the locus the ADR routes to.
- cited_authority: coherence — ADR-004 §2.2 / §6 check 2 vs SDD-001 §2.1 / §3.6 (ACCEPTED; no provisioning operation enumerated)

### [SA] MATERIAL — decision-bearing
- id: 4e496c441eb10bd7
- locus: §2.7 — 'home of the ingestion-mechanics authority' vs disclaimed mechanics
- claim: §2.7 asserts this ADR 'is the record the governance record names as the home of the ingestion-mechanics authority — the decision that authority is routed to, distinct from the port-level mechanics that realize it,' while the same paragraph states 'The port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's,' and §7 restates 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)' and §2.2's realization route reads 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 assigns that home ownership of ingestion *mechanics*; ADR-004 self-identifies as that home while disclaiming the mechanics and claiming only bare 'authority.' The distinction between 'authority' and 'mechanics' on which the self-identification rests is not one the cited ADR-008 loci draw, so the claim that this record discharges ADR-008's forward reference is not substantiated by the reference it invokes.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' vs 'port-level mechanics ... are the knowledge-service design's') and §7 against ADR-008 §2.2 / §7 (forthcoming record owns ingestion mechanics realization)

### [SA] MATERIAL — decision-bearing
- id: 52b2f728bbb7741b
- locus: §2 decision sentence vs §2.7 standing steady-state read-discipline invariant
- claim: The §2 decision sentence scopes the record to greenfield instantiation ('The SOFIA graph is instantiated greenfield from declared source artifacts, and instantiation ... is orchestrated by a driver-less loader utility'). §2.7 commits a standing schema-level read-discipline invariant governing all synthesis, not merely instantiation: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' Exclusion from ground-truth synthesis binds steady-state consumption reads, a rule beyond the instantiation act the §2 decision sentence enumerates; the standing invariant is not surfaced among the sub-decisions §2 claims to make.
- cited_authority: coherence — ADR-004 §2 (decision sentence, instantiation-scoped) vs §2.7 (schema-level read-exclusion invariant governing all ground-truth synthesis)

### [SA] COSMETIC — decision-bearing
- id: 5a99d269f18fc884
- locus: §2.5 / §5.3 — RG durability under the deferred production runtime
- claim: §2.5 states RG durability 'rests on instance-level backup and restore. In the current development runtime that responsibility sits with the managed graph provider; the production runtime, and therefore its backup posture, is deferred (see §5.3).' ADR-002 §5.2 (cited at §7 as 'the managed-runtime backup/restore responsibility on which RG recovery rests') states the development managed-Aura runtime 'retires the self-managed operational burden — backup/restore, upgrade lifecycle, and cluster-health monitoring are the managed provider's responsibility.' The cited ADR-002 §5.2 substantiates the development-runtime claim; for production ADR-002 §5.2 states the burden 'returns for production ... weighed at the production-environment build' — the ADR-004 claim that production backup posture is deferred is consistent, but §2.5 asserts RG durability 'must not be presumed' source-recoverable without a cited invariant fixing that no instantiation path reconstructs RG — the guarantee rests only on §2.4's no-reset assertion, which is internal and adequately cross-referenced.
- cited_authority: canonical — ADR-002 §5.2 (managed-runtime backup/restore responsibility; production burden deferred to production-environment build)

### [SA] COSMETIC — decision-bearing
- id: ba2fd4e152d96ce2
- locus: §2.2 / §5.3 constraint-versioning forward item
- claim: §2.2 defers constraint-versioning ownership ('a forward question ... tracked as a forward item against the schema-provisioning capability's design') and §5.3 restates it as 'a named forward question, not a silent gap,' but neither names a ticket, decision record, or firing trigger; the home is an unnamed 'capability's design' that is not itself a resolvable artifact in the set (per §2.2, the operation it would design is absent from SDD-001 §3.6). The deferred obligation is declared without a locatable home or a re-surfacing trigger.
- cited_authority: soundness — ADR-004 §2.2 / §5.3 — deferred constraint-versioning obligation named without a resolvable home, ticket, or firing trigger; 'the schema-provisioning capability's design' resolves to no enumerated artifact in the set

### [SA] POSITIVE — unclassified
- id: 7a1ac002f54e497a
- locus: §2.8 Write authorship of instantiation
- claim: Checked §2.8's author/executor assignment against ADR-002 §2.6's general write-authority principle (every authoritative graph write has a named component-scoped author; the sole-owner gateway is sole executor and never the author). §2.8 conforms: it names the accountable authority declared by the source artifact (human curator / fidelity verifier) as author, the gateway as sole executor never author, and the loader as neither — a clean instance of the ADR-002 §2.6 principle for the instantiation domain. Attack: I sought an author-diffusion or gateway-as-author leak and found none; the loader is explicitly excluded from authorship. Held.
- cited_authority: canonical — ADR-002 §2.6 (author/executor/authorizer separation — gateway sole executor, never author)

### [SA] POSITIVE — unclassified
- id: 5f02445183b4a33a
- locus: §2.4 Additive by supersession, never destructive
- claim: Checked §2.4's additive-by-supersession commitment against DDR-002 §6 (Option A supersession — retained version nodes, effective-dating, superseded_by, never-delete) and DDR-002 §7 #8 (never-delete). §2.4 conforms: it selects create/supersede/no-new-version per node by graph state (not by a loader mode), requires a source-artifact version increment to change versioned ground truth, and exposes no destructive-reset operation — an accurate application of the schema's supersession and never-delete disciplines with no overwrite path. Attack: I sought an in-place-overwrite or wipe-and-reload path that would contradict DDR-002 §6/#8; §2.4 explicitly forecloses both. Held.
- cited_authority: canonical — DDR-002 §6 (Option A supersession) and §7 #8 (never-delete)

### [SA] POSITIVE — unclassified
- id: c4d17bb61e0617fd
- locus: §2.4 additive-by-supersession vs DDR-002 §6 / §7 #8
- claim: Attacked §2.4's 'additive by supersession, never destructive' for a hidden in-place-overwrite or wipe-and-reload path that would contradict DDR-002 §6 (Option A supersession: retained version nodes, effective-dating, superseded_by) and DDR-002 §7 #8 (never-delete). It held: §2.4 selects create/supersede/no-new-version per node by graph state (not by a loader mode), requires a source-artifact version increment to change versioned ground truth ('there is no in-place overwrite of ground truth'), exposes no destructive-reset operation, and routes age/distill planes to their own per-plane discipline per DDR-002 §2.2/§2.3 — an accurate application of the schema's supersession and never-delete disciplines with both overwrite and wipe paths foreclosed. Alternative C (§4.3) records the rejected wipe-and-reload on exactly those never-delete grounds.
- cited_authority: canonical — DDR-002 §6 (Option A supersession) and §7 #8 (never-delete) — ADR-004 §2.4 / §4.3 conform

### [cross-set] MATERIAL — decision-bearing
- id: 33a3dc7291d53f00
- locus: §2.2 Schema provisioning holds the sole-driver line vs §6 check 2 and §2 Decision
- claim: §2.2 commits knowledge-service to 'expose a schema-provisioning capability — an addition its service design does not yet enumerate' and asserts it is 'ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards.' SDD-001 §3.1 as fetched enumerates readiness as '(1) Neo4j connectivity ... (2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode.' SDD-001 §3.1 gives no provisioning operation and states the gateway must not execute writes it cannot validate; ADR-004 requires knowledge-service to run DDL provisioning writes before the schema is present, i.e. before readiness reports green — a mode SDD-001 §3.1's 'no degraded mode' and readiness-gated write posture does not supply.
- cited_authority: coherence — ADR-004 §2.2 (provisioning ordered ahead of readiness, capability not yet enumerated) in conflict with SDD-001 §3.1 (readiness fails until schema metadata loaded; no degraded mode; gateway must not execute writes it cannot validate)

### [cross-set] MATERIAL — decision-bearing
- id: 118c5884ea885d80
- locus: §2.7 / §2 fidelity-gate read-exclusion invariant vs DDR-002 §7 read-discipline invariant set
- claim: ADR-004 §2.7 asserts 'read-exclusion of provisional ground truth is committed as a schema-level invariant ... That invariant is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' DDR-002 §7 as fetched enumerates the CI-only invariant set (#1–#28) and the read-discipline invariants #9, #19, #21; no provisional-versus-official read-exclusion invariant appears in DDR-002 §7 or in its read-discipline list, and DDR-002's Decision block, §2.6 declaration model, and §5 read-discipline invariants carry no provisional-state concept. The ADR names an amendment obligation against DDR-002 that DDR-002's current text does not carry and does not reference, leaving the committed schema-level invariant with no home in the owning schema document.
- cited_authority: coherence — ADR-004 §2.7 (provisional read-exclusion as a forthcoming schema read-discipline invariant) against DDR-002 §7 read-discipline invariant set (#9/#19/#21) and §2/§5, which carry no provisional-versus-official state or its read-exclusion

### [cross-set] MATERIAL — decision-bearing
- id: 789a1238ad52f4f0
- locus: §2.7 authoritative-source ingestion control fidelity-gate scope vs ADR-008 §2.2
- claim: ADR-004 §2.7 states the fidelity control it realizes is 'scoped to the authoritative-source class — it is not applied to ... the Operational distillation class carries its own review control and is out of scope here.' ADR-008 §2.2 defines the authoritative-source-ingestion control as 'Pre-entry human fidelity verification of the captured representation, gating official (consumable) entry ... Per-write ... The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 §2.2's ingestion class is 'Catalog / Standards'; ADR-004 §2.7 renders this as 'the selection-catalog and standards planes' — a term ('selection-catalog') that does not match the owning record's plane name (Catalog), a drift in the shared entity ADR-008 owns.
- cited_authority: coherence — ADR-004 §2.7 'selection-catalog and standards planes' vs ADR-008 §2.2 authoritative-source-ingestion row 'Catalog / Standards' and DDR-001 Decision.2 / DDR-002 §2.1 canonical plane name 'Catalog'

### [cross-set] MATERIAL — decision-bearing
- id: 2399be6e00c5e105
- locus: §2.7 / §5.2 fidelity-gate scope exclusion of 'mirrored externally-decided records' vs ADR-008 §2.2
- claim: ADR-004 §2.7 and §5.2 exclude 'externally-decided mirrored records' from the fidelity gate alongside the Environment stream, stating 'it is not applied to ... externally-decided mirrored records.' ADR-008 §2.2's four source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' class exists there; the mirrored external record ADR-004 invokes is DDR-002 §2.4's GateDecision (origin_mechanism: ingested), which DDR-002 §2.4 scopes to produced-Solution SDLC gates, not KG ground-truth instantiation. ADR-004 introduces a scope-exclusion category ('mirrored externally-decided records') that the ground-truth-mutation governance record it cites does not enumerate as a mutation class subject to (or exempt from) the ingestion control.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt from the fidelity gate) against ADR-008 §2.2 four-class calibration table, which contains no mirrored-external-record ingestion class

### [cross-set] MATERIAL — decision-bearing
- id: c0804b5d7555e994
- locus: §2.7 fidelity-gate read-exclusion invariant vs DDR-002 §7 read-discipline invariant set
- claim: ADR-004 §2.7 states 'read-exclusion of provisional ground truth is committed as a schema-level invariant ... That invariant is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' DDR-002 §7 enumerates the CI-only invariant set #1–#28 with read-discipline invariants #9 (proposal-visibility), #19 (conditional-consumption), and #21 (retraction-gated); none covers provisional-versus-official read-exclusion, and DDR-002 §2.6's declaration model, §5 read-discipline invariants, and Named Gaps carry no provisional-state concept. ADR-004 commits a schema-level invariant against DDR-002 (ACCEPTED, downstream) that DDR-002's current text neither carries nor references as a gap.
- cited_authority: coherence — ADR-004 §2.7 (provisional read-exclusion as a forthcoming schema read-discipline invariant) in conflict with DDR-002 §7 read-discipline invariant set (#9/#19/#21) and §2.6/§5, which carry no provisional-versus-official state or its read-exclusion

### [cross-set] MATERIAL — decision-bearing
- id: 3d1aed4a75f35f2e
- locus: §2.2 Schema provisioning holds the sole-driver line vs SDD-001 §3.1 readiness
- claim: ADR-004 §2.2 states schema provisioning 'is ordered ahead of the readiness schema-present check rather than passing through the validated write path that check guards ... provisioning runs before readiness reports green (which checks that the schema is present).' SDD-001 §3.1 (ACCEPTED, cited by ADR-004 §7) states readyz returns '503 otherwise' with checks '(2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode.' ADR-004 requires knowledge-service to execute a schema-provisioning (DDL) operation over its driver while the service is not-ready by its own cited readiness contract; SDD-001 §3.1's no-degraded-mode, writes-only-after-schema-present posture does not supply a pre-readiness operation mode, and SDD-001 §3.6 enumerates ingest / register-plane / mirror-gate-decision with no schema-provisioning operation.
- cited_authority: coherence — ADR-004 §2.2 (provisioning ordered ahead of readiness; capability not yet enumerated) in conflict with SDD-001 §3.1 (readiness fails until schema metadata loaded; no degraded mode; gateway must not execute writes it cannot validate) and §3.6 (ingestion-port operation set with no provisioning operation)

### [cross-set] MATERIAL — decision-bearing
- id: 8a94ae100a449762
- locus: §2.7 authoritative-source class naming vs ADR-008 §2.2 and DDR-002 §2.1
- claim: ADR-004 §2.7 names the fidelity-gate's scope as 'the selection-catalog and standards planes.' ADR-008 §2.2's authoritative-source-ingestion row names the class 'Catalog / Standards'; DDR-002 §2.1 and DDR-001 Decision.2 fix the canonical plane name as 'Catalog' (with §2.1 titled 'Catalog — the selection graph'). 'selection-catalog' is not the canonical plane name owned by the schema; the shared plane entity ADR-008/DDR-002 own has drifted in this record's naming.
- cited_authority: coherence — ADR-004 §2.7 'selection-catalog and standards planes' vs ADR-008 §2.2 'Catalog / Standards' and DDR-002 §2.1 / DDR-001 Decision.2 canonical plane name 'Catalog'

### [cross-set] MATERIAL — decision-bearing
- id: 979ec95554d89e7d
- locus: §2.7 / §5.2 fidelity-gate scope exclusion of 'mirrored externally-decided records' vs ADR-008 §2.2 four-class calibration
- claim: ADR-004 §2.7 and §5.2 exclude 'externally-decided mirrored records' from the fidelity gate ('it is not applied to ... externally-decided mirrored records'). ADR-008 §2.2's four calibrated source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' ground-truth-mutation class exists there. The mirrored external record in the corpus is DDR-002 §2.4's GateDecision (origin_mechanism: ingested), which DDR-002 §2.4 scopes to produced-Solution SDLC gates, not KG ground-truth entry. ADR-004 introduces a scope-exclusion category the governance record it cites does not enumerate as a KG-mutation class subject to or exempt from the ingestion control.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 ('externally-decided mirrored records' exempt from the fidelity gate) against ADR-008 §2.2 four-class calibration table, which contains no mirrored-external-record ingestion class

### [cross-set] MATERIAL — decision-bearing
- id: d75f0d04e6359f91
- locus: §2 decision sentence vs §2.7 standing steady-state read-discipline invariant
- claim: The §2 decision sentence scopes the decision to greenfield instantiation ('The SOFIA graph is instantiated greenfield from declared source artifacts, and instantiation ... is orchestrated by a driver-less loader'). §2.7 commits a standing schema-level read-discipline invariant governing all synthesis, not merely instantiation: 'read-exclusion of provisional ground truth is committed as a schema-level invariant — a provisional authoritative-source node is excluded from ground-truth synthesis until officially entered.' A ground-truth-synthesis read-exclusion invariant that binds steady-state consumption rides inside an instantiation-scoped decision without being enumerated as one of the sub-decisions §2 claims to make; the Decision block is the contract's index and does not surface this ruling.
- cited_authority: coherence — ADR-004 §2 (decision sentence, instantiation-scoped) vs §2.7 (schema-level read-exclusion invariant governing all ground-truth synthesis) — decision not surfaced at decision altitude

### [cross-set] MATERIAL — decision-bearing
- id: ea75d36a134fbd1f
- locus: §2.7 self-identification as ADR-008's named ingestion-mechanics home
- claim: ADR-004 §2.7 asserts it 'is the record the governance record names as the home of the ingestion-mechanics authority' and §7 states 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)' and §2.2's realization route reads 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 routes ingestion *mechanics realization* to that record, but ADR-004 §2.7 disclaims owning port mechanics ('the port-level mechanics ... how the official-entry transition is enforced ... are the knowledge-service design's') and claims to own the *authority/locus* only. The record self-identifies as ADR-008's named home while narrowing its ownership below what ADR-008's forward reference assigned that home.
- cited_authority: coherence — ADR-004 §2.7 (claims to be ADR-008's named forthcoming ingestion record, authority-only, port mechanics disclaimed) vs ADR-008 §2.2 / §7 (routes ingestion mechanics realization to that record)

### [cross-set] MATERIAL — decision-bearing
- id: d059747127e3989a
- locus: §2.7 provisional read-exclusion invariant vs DDR-002 §7 read-discipline invariant set
- claim: §2.7 states 'read-exclusion of provisional ground truth is committed as a schema-level invariant' and concedes 'That invariant is a *forthcoming* addition to the schema's read-discipline invariant set (a named amendment obligation), not one the schema already carries.' DDR-002 §7 enumerates the CI-only invariant set #1–#28, with read-discipline invariants #9 (proposal-visibility), #19 (conditional-consumption), and #21 (retraction-gated); none covers provisional-versus-official read-exclusion, DDR-002 §2.6's declaration model and §5 read-discipline invariants carry no provisional-state concept, and DDR-002's Named Gaps do not list it. The invariant ADR-004 §2.7 states as 'committed' is present in neither the owning schema authority it cites (DDR-002 §7) nor that authority's gap enumeration.
- cited_authority: coherence — ADR-004 §2.7 ('committed as a schema-level invariant ... forthcoming addition') in conflict with DDR-002 §7 read-discipline set #9/#19/#21 and Named Gaps, which carry no provisional read-exclusion invariant

### [cross-set] MATERIAL — decision-bearing
- id: 5e7d83ae43a57b27
- locus: §2.2 schema-provisioning capability + pre-readiness ordering vs SDD-001 §3.1 / §3.6
- claim: §2.2 commits knowledge-service 'to expose a schema-provisioning capability — an addition its service design does not yet enumerate' and states provisioning 'runs before readiness reports green (which checks that the schema is present).' SDD-001 (ACCEPTED v1.6.0, cited at §7) §3.1 specifies readyz returns 503 unless '(2) schema metadata loaded — the PlaneDefinition registry and constraint/validation metadata the write paths enforce against — critical, fails readiness (the gateway must not execute writes it cannot validate). There is no degraded mode.' SDD-001 §3.6 enumerates the ingestion port as exactly 'ingest', 'register-plane', 'mirror-gate-decision', with no schema-DDL-provisioning operation, and §2.1 enumerates the service's sole-authorised acts without one. The provisioning operation ADR-004 §6 check 2 verifies conformance against does not exist in the cited ACCEPTED service design, and no pre-readiness operating mode is supplied there.
- cited_authority: coherence — ADR-004 §2.2 / §6 check 2 (schema-provisioning capability, runs before readiness green, committed compliance check) vs SDD-001 §3.1 (schema-present is a critical readiness precondition; no degraded mode; gateway must not execute writes it cannot validate) and §3.6 / §2.1 (ingestion-port operation set with no provisioning operation)

### [cross-set] MATERIAL — decision-bearing
- id: 5f0860656e7459bd
- locus: §2.7 / §7 — self-identification as ADR-008's named ingestion-mechanics home vs disclaimed mechanics
- claim: §2.7 asserts this ADR 'is the record the governance record names as the home of the ingestion-mechanics authority — the decision that authority is routed to, distinct from the port-level mechanics that realize it,' and §7 restates 'this record is the "forthcoming file-driven ingestion decision record" that governance record names.' ADR-008 §7 names 'The forthcoming file-driven ingestion decision record — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2)', and ADR-008 §2.2's realization route reads 'The forthcoming ingestion decision record; the knowledge-service ingestion port.' ADR-008 routes ingestion *mechanics realization* to that record; ADR-004 §2.7 disclaims owning the mechanics ('The port-level mechanics — how provisional state is represented and how the official-entry transition is enforced — are the knowledge-service design's') and claims to own only the 'authority.' The authority-vs-mechanics distinction on which ADR-004 rests its self-identification is not a distinction the cited ADR-008 loci draw; the record self-identifies as the named home while narrowing its ownership below what that forward reference assigned it.
- cited_authority: coherence — ADR-004 §2.7 ('home of the ingestion-mechanics authority' + 'port-level mechanics ... are the knowledge-service design's') and §7 vs ADR-008 §2.2 / §7 (forthcoming record owns the ingestion mechanics realization)

### [cross-set] MATERIAL — decision-bearing
- id: 80fc5fa4d3ebbca5
- locus: §2.7 / §5.2 / §6 check 6 — 'externally-decided mirrored records' exclusion not enumerated by ADR-008
- claim: §2.7 states the fidelity gate 'is not applied to the ungated Environment observation stream or to externally-decided mirrored records,' and §5.2 / §6 check 6 restate 'the ungated Environment observation stream and mirrored externally-decided records are not gated.' ADR-008 §2.2's four calibrated source classes are Promotion, Authoritative-source ingestion, Operational distillation, and Environment — no 'mirrored externally-decided records' class appears as a KG-ground-truth mutation class subject to (or exempt from) the ingestion control. The only mirrored external record in the corpus is DDR-002 §2.4's GateDecision (origin_mechanism: ingested), which DDR-002 §2.4 scopes to the enterprise SDLC gate on produced Solutions, not KG ground-truth instantiation. The exemption cites an authority (ADR-008 §2.2) that does not resolve to the category it names.
- cited_authority: coherence — ADR-004 §2.7 / §5.2 / §6 check 6 ('externally-decided mirrored records' exempt) against ADR-008 §2.2 four-class calibration table (no mirrored-external-record ingestion class) and DDR-002 §2.4 (GateDecision scoped to produced-Solution SDLC gates)

### [cross-set] MATERIAL — decision-bearing
- id: f0db91021949dc3a
- locus: §2 Decision / §2.5 / §5.3 — RG-durability guarantee resting on a deferred production runtime decision
- claim: §2.5 rests RG durability-across-instance-loss on 'instance-level backup and restore,' assigned in dev to the managed provider and for production 'deferred (see §5.3),' and commits 'the RG is not source-recoverable and must not be presumed so.' §5.1's positive consequence and §2.5 both lean on backup/restore as the sole RG recovery mechanism. ADR-002 §2.2 / §5.2 leave the production deployment runtime — and therefore its backup posture — deferred, with the self-managed burden that 'returns for production ... weighed at the production-environment build.' The record commits a no-destructive-reset structural guarantee whose only RG-durability backstop is a production backup posture the platform has not yet decided; the timing is acknowledged as a risk but the load-bearing durability property is not otherwise resolved.
- cited_authority: coherence — ADR-004 §2.5 / §5.3 (RG durability rests on backup/restore; production backup posture deferred) vs ADR-002 §2.2 / §5.2 (production deployment runtime deferred; burden weighed at the production-environment build)

### [cross-set] COSMETIC — decision-bearing
- id: f44f6b2eae012859
- locus: §2.2 / §5.3 constraint-versioning forward item
- claim: §2.2 defers constraint-versioning ownership ('a forward question ... tracked as a forward item against the schema-provisioning capability's design') and §5.3 restates it as 'a named forward question, not a silent gap,' but neither names a ticket, decision record, or firing trigger, and the home is an unnamed 'capability's design' that does not yet exist as an enumerated artifact. The deferred obligation is declared but left without a locatable home or a re-surfacing trigger.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated with no named home or firing trigger)

### [cross-set] COSMETIC — decision-bearing
- id: dbad933633392115
- locus: §2.2 / §5.3 — constraint-versioning forward item lacks a locatable home and firing trigger
- claim: §2.2 defers constraint-versioning ownership: 'Ownership of constraint *versioning* over the platform's life ... is a forward question ... with its policy not settled here — tracked as a forward item against the schema-provisioning capability's design.' §5.3 restates it as 'a named forward question, not a silent gap.' Neither names a ticket, decision record, or event that re-surfaces the obligation; the sole home is 'the schema-provisioning capability's design,' which is itself the unauthored capability §2.2 commits and which SDD-001 §3.6 does not enumerate. The deferred obligation is declared but homed only to an artifact that does not yet exist and carries no firing trigger.
- cited_authority: coherence — ADR-004 §2.2 (constraint-versioning deferred to 'the schema-provisioning capability's design') and §5.3 (restated with no named ticket, record, or firing trigger); the named home is itself unauthored per SDD-001 §3.6's operation set

### [cross-set] POSITIVE — unclassified
- id: 9a2abea73b33f4c7
- locus: §2.1–§2.2 sole-driver line vs ADR-002 §2.5
- claim: Checked ADR-004's central claim that instantiation preserves ADR-002's sole-owner-of-the-driver principle for both data and schema provisioning against ADR-002 §2.5 ('knowledge-service is the sole holder of the Neo4j driver and the single graph-access boundary'). ADR-004 §2.1/§2.2 route both the data load and DDL provisioning through knowledge-service and hold the loader driver-less, and the §2.2 circularity argument (provisioning is an administrative operation distinct from the schema-on-write data path) is internally consistent with ADR-002's boundary. The claim of no exception carved holds against the cited authority.
- cited_authority: coherence — ADR-004 §2.1/§2.2 (data and schema through the sole driver; loader driver-less) against ADR-002 §2.5 (knowledge-service sole Neo4j-driver holder)

### [cross-set] POSITIVE — unclassified
- id: 9d8241f48d0b9bdd
- locus: §2.4 additive-by-supersession vs DDR-002 §6
- claim: Attacked §2.4's 'additive by supersession, never destructive' claim for consistency with the schema's supersession discipline. DDR-002 §6 (Supersession — Option A) commits retained version nodes + effective-dating + superseded_by with never-delete, and §2.3/§2.2 give per-plane disciplines for aging (Environment) and distilling (Operational) planes. ADR-004 §2.4's per-node state-selected behavior (new key created, changed versioned-ground-truth node superseded on version increment, unchanged key adds no version, age/distill planes follow their own discipline) maps to DDR-002 §6's versioned-ground-truth scoping without asserting a supersession behavior the schema does not carry. The attack failed.
- cited_authority: coherence — ADR-004 §2.4 (additive-by-supersession, version-increment requirement, per-plane discipline) against DDR-002 §6 (Option A supersession, never-delete) and §2.2/§2.3 (per-plane aging/distillation)

### [cross-set] POSITIVE — unclassified
- id: 888b762174156db4
- locus: §2.1 / §2.2 / §4.1 / §4.2 — sole-driver line preserved for instantiation
- claim: Attacked the record for carving a first-load exception into ADR-002's sole-owner-of-the-driver principle — the classic instantiation-bypass hazard. It held: §2.1 routes instantiation data through the ingestion port, §2.2 holds schema provisioning inside knowledge-service over the driver it already holds (not a second driver) with an internally-consistent circularity argument (provisioning is an administrative operation distinct from the schema-on-write data path), and §4.1/§4.2 explicitly reject both the privileged-bulk-load and the separate-provisioning-tool-with-own-driver alternatives. Checked against ADR-002 §2.5 (knowledge-service sole Neo4j-driver holder); no exception is carved.
- cited_authority: canonical — ADR-002 §2.5 (sole-holder-of-the-driver principle) — ADR-004 §2.1/§2.2/§4.1/§4.2 preserve it for both data and schema provisioning

### [cross-set] POSITIVE — unclassified
- id: 3ba394625605445f
- locus: §2.4 additive-by-supersession vs DDR-002 §6 / §7 #8
- claim: Attacked 'fresh / no migration' as a likely license to reset a live graph — the reading that would breach the never-delete and supersession disciplines and endanger reasoning state. It held: §2.3 binds 'fresh' to origin only, §2.4 makes the load additive-by-supersession (per-node state-selected: new key created, changed versioned-ground-truth node superseded on an explicit source version increment, unchanged key adds no version, age/distill planes follow their own discipline) with no destructive-reset operation and no in-place overwrite, and §4.3 rejects destructive re-instantiation on the never-delete/supersession grounds. Checked against DDR-002 §6 (Option A supersession — retained version nodes, effective-dating, superseded_by) and §7 #8 (never-delete); the per-node behavior maps to the schema's versioned-ground-truth scoping without asserting a supersession behavior the schema does not carry.
- cited_authority: canonical — DDR-002 §6 (Option A supersession) and §7 #8 (never-delete) — ADR-004 §2.4/§4.3 conform, with the RG-loss hazard structurally closed via §2.5

### [cross-set] POSITIVE — unclassified
- id: 412cd01d0638bfc0
- locus: §2.3 / §2.4 / §2.5 / §4.3 — additive-by-supersession, RG-loss hazard structurally closed
- claim: Attacked 'fresh / no migration' as a license to reset a live graph — the reading that would breach the never-delete and supersession disciplines and silently discard reasoning state, the platform's reason to exist. It held: §2.3 binds 'fresh' to origin only, §2.4 makes the load additive-by-supersession per-node by graph state (new key created, changed versioned-ground-truth node superseded on an explicit source version increment, unchanged key adds no version, age/distill planes follow their own discipline) with no destructive-reset operation and no in-place overwrite, §2.5 scopes instantiation to the KG and forbids writing/reconstructing/discarding the RG, and §4.3 rejects destructive re-instantiation on exactly the never-delete/supersession grounds. Checked against DDR-002 §6 (Option A supersession — retained version nodes, effective-dating, superseded_by) and §7 #8 (never-delete); the per-node behavior maps to the schema's versioned-ground-truth scoping without asserting a supersession behavior the schema does not carry.
- cited_authority: canonical — DDR-002 §6 (Option A supersession) and §7 #8 (never-delete); ADR-001 §2.2 (reasoning-capture invariant) — ADR-004 §2.3/§2.4/§2.5/§4.3 conform

