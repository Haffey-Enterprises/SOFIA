# ADR-999: Fixture — Malformed (RBT-50 acceptance demonstration)

| Field | Value |
|---|---|
| **Document ID** | ADR-999 |
| **Status** | INVALID |
| **Version** | 9.9.9 |
| **Date** | 2026-07-05 |

---

## 1. Context

This is a deliberately malformed fixture authored for RBT-50. It exists only to
drive the documentation-structure validator RED in a draft pull request, and it
never lands anywhere. It has no authorship header (Check A), an out-of-vocabulary
Status and no Change Log row matching its metadata Version (Check E), and a bare
operational identifier — RBT-50 — sitting in this normative body rather than on an
audit surface, which the diff-mode contract-purity check should flag (Check D).

## 2. Decision

None. This document is a test fixture and carries no decision.

## 9. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.0.1 | 2026-07-05 | — | Fixture authoring; note there is deliberately no row for Version 9.9.9. |
