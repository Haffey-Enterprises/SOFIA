# SOFIA

**Semantic Orchestration for Intelligent Architecture / Applications** — the reasoning-capture layer for the enterprise SDLC.

SOFIA's durable value is the **Knowledge Graph** (enterprise ground-truth context) and the **Reasoning Graph** (institutional memory — every inference, its evidence, and rejected alternatives, as a traversable asset). It operates at Position 5 (hybrid reasoning within encoded boundaries) on a trajectory toward Position 4 (SOFIA-as-reasoner, LLM-as-renderer). See `docs/adr/ADR-001` for the authoritative statement.

## Engineering conventions

This project follows the **bedrock** engineering skills (`application-code`, `testing`, `code-review`, `author-decision-record`, `debug`), installed in Claude (account + Claude Code plugin) and triggered automatically. The conventions are ambient, not vendored into this repo. See `CLAUDE.md` for project orientation.

## Layout

- `CLAUDE.md` — repo-root orientation
- `docs/adr/` — Architecture Decision Records (platform principles)
- `docs/ddr/` — Design Decision Records (specific design rulings)
- `docs/sdd/` — Service Design Documents (per-service designs; forthcoming)
- `docs/reviews/` — review-of-record artifacts
- `conformance/` — contract-test suite enforcing the graph data-layer invariants (ADR-002 / DDR-001 / DDR-002)

## Lineage

This is the go-forward SOFIA, stamped from the `bedrock` project template. It supersedes the frozen `SOFIA-legacy` (the original build) and `SOFIA-Reboot` (the design restart from which the accepted ADRs/DDRs were transplanted). History for both is preserved in their archived repos.
