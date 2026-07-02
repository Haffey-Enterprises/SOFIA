# Module: agent_loop
# Purpose: Walking skeleton for the design-review agent loop — the dry-mode
#          plumbing (ledger, admission gate, mechanical gates, arbiter port,
#          canned reviewer stubs, runner) that proves the durable spine and the
#          convergence gates fire deterministically on a dummy case.
# Scope:   Repo-agnostic harness. Reviewers are canned stubs; the only LLM
#          judgment (the arbiter) is a port with a canned adapter for the
#          skeleton and an unwired LLM adapter seam for production.
# Invariant: Convergence is mechanical — a boolean conjunction over ledger state.
#            No LLM anywhere on the "done" decision.
