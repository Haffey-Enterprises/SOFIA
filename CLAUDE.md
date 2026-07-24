# CLAUDE.md — SOFIA

Repo-root orientation for Claude (auto-loaded by Claude Code). This file is **context, not conventions** — what SOFIA is, its stack, and where things live. The engineering conventions are not here: they live in the installed `bedrock` plugin's skills, which trigger on their own; the plugin owns the current skill list — this file does not mirror it. Keep this file lean; prune as it grows.

## What this is

**SOFIA — Semantic Orchestration for Intelligent Architecture / Applications** — is the reasoning-capture layer for the enterprise SDLC. It applies enterprise context consistently and automatically at every lifecycle stage, with all decisions explainable and auditable.

Its distinguishing commitment is the **reasoning-capture invariant**: whoever does the reasoning — encoded SOFIA logic, a specialized agent, an LLM, or a human — SOFIA captures that reasoning in the **Reasoning Graph (RG)** alongside the **Knowledge Graph (KG)**. This ensures the *why* behind architecture decisions accumulates as a durable, queryable asset rather than living transiently in a prompt.

The platform operates with **hybrid reasoning** (LLM and SOFIA) within encoded boundaries, on a trajectory toward **SOFIA-as-reasoner, LLM-as-tool**. The authoritative statement of purpose and core behaviors is the spine ADR: **ADR-001** (`docs/adr/`); the graph-as-system-of-record decision is **ADR-002**.

## Operating constraints (initial build)

- **No PHI by design** — enforced via data classification at intake/ingestion, with compensating controls as a backstop.
- **No CMEK** in the initial build; a future PHI scope-change is its own ADR.

## Stack

- **Language / runtime:** Python 3.11+
- **Framework:** FastAPI (async)
- **System of record:** graph database (Neo4j Enterprise; deployment runtime environment-differentiated per ADR-002 §2.2 — dev on managed Aura, prod deferred) — per ADR-002 / DDR-002
- **Persistence backbone:** Neo4j (architecture + reasoning state), PostgreSQL (workflow/audit/staging), Firestore (immutable snapshots) — no vector store
- **Cloud / host:** GCP / GitHub

The `bedrock:` corpus is multi-stack: each skill declares its own binding, and that declaration — not this list — governs what it assumes. The service-side skills bind to the stack above; others bind to their own, and some are stack-independent. Wherever a skill's binding is the stack above, a materially different choice on any axis is a **rebind**, not a substitution — re-derive the conventions for that stack and capture it as an ADR.

## Branch model

`feature/*` → `develop` → `main`, via PRs; never commit directly to `main`. All agent-loop deliberation/run artifacts (`agent-loop/deliberation/`, `agent-loop/runs/`) land via PR to `develop` like every other change — the prior direct-commit exemption is retired (ruled RBT-10 session, 2026-07-22, resolving the RBT-77-named conflict with branch protection). Confirm the current branch before any git operation.

## Services

Platform is at the design stage — ADRs and DDRs accepted; per-service designs (SDDs) not yet authored. Graph access is sole-owned by **knowledge-service** (per ADR-002 §2.5); other services reach the graph through its gateway. Inventory fills as services land.

| Service | Purpose | Status |
|---|---|---|
| knowledge-service | Sole graph-access gateway (KG/RG) | designed, not built |

## Project-specific rules

**Anti-simplification.** The reasoning-capture invariant (KG + RG) is the platform's reason to exist. Do not remove, simplify, or short-circuit it into an LLM-wrapping pattern — that regression is the specific failure mode this architecture exists to prevent. Any design or change that touches the reasoning path is checked against ADR-001 §6 and ADR-002 §6 at review.
