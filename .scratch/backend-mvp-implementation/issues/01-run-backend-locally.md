# 01: Run the backend locally

**What to build:** A maintainer can start SpendWise locally, reach its health endpoint and diagnose configuration/request failures using the same runtime foundation that later business operations will use.

**Blocked by:** None (can start immediately).

**Status:** resolved (2026-11-17). Triage label: ready-for-agent.

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [x] Provide a runnable FastAPI application with pinned/reproducible Python dependency setup, typed configuration and a secret-free environment template; document local startup and PostgreSQL setup.
- [x] Health returns the agreed process-liveness response. Request IDs, request timing, redacted logs and the standard application/validation error envelope are available without leaking credentials or database internals.
- [x] Establish synchronous SQLAlchemy sessions and synchronous routes, one shared session per use case, rollback/close on failure and explicit commit before write success. Services/repositories do not independently commit, roll back or close.
- [x] Select one test runner and document its invocation; prepare shared infrastructure only as needed for the existing six scenario groups. Demonstrate local startup/health without inventing a separate foundation test stack.
- [x] Inventory and reconcile historical references to absent scaffolding/generated artifacts; record concrete gaps without reopening approved design. Do not scaffold budgets, analytics, notifications, workers or frontend screens.

## Verification ownership

Own the runnable foundation demonstration and shared runner/configuration setup. The migrated runtime-role API/database harness is completed in 02; behavioral cases then grow within the approved scenario groups.


## Completion evidence

See [foundation verification](../../../docs/testing/01-foundation-evidence.md) and [startup instructions](../../../backend/README.md). Local HTTP startup, secret-free failures/logs, Ruff and mypy passed. Real PostgreSQL harness verification follows in 02.

