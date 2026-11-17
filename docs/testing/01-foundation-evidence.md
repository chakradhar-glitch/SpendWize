# Ticket 01 evidence

Status: foundation verified locally, 2026-11-17.

## Executed verification

- `uv sync` resolved 38 packages and installed 37. Exact versions are in the
  lockfile. Python 3.11.3 was used on Windows.
- `ruff check app`: passed. `mypy app`: passed, eight source files.
- Started Uvicorn at loopback port 18080 with access logging disabled. Real HTTP
  requests confirmed health `200 {"status":"ok"}`, generated UUID request IDs,
  propagation of a supplied UUID, standard 404 response/request-ID agreement,
  and a generated OpenAPI health operation.
- Captured process logs contained timing and IDs. A marker placed in a query,
  Authorization header and invalid request-ID header did not appear in logs.
  The disposable database password was also absent.
- An invalid database URL caused startup to fail without exposing its value.
- Docker Engine 29.8.2 became reachable after starting Docker Desktop.
- Two independent review axes found no standards issues and one availability
  classification gap. Fixed initial connection failures and pool timeouts to use
  503. A real refused PostgreSQL connection returned the standard secret-free
  `temporarily_unavailable` response. Ruff and mypy passed again after the fix.

The contract required process liveness without specifying a body; this foundation
sets the concrete response to `{"status":"ok"}`. No database readiness is implied.

## Historical artifact reconciliation

The initial checkout contained no backend source, manifest, migrations or tests.
The approved structure is a design illustration, not an inventory of existing code.
Its budgets, analytics, notifications, email and worker examples are deferred;
its multi-layer test layout is superseded by the approved six-group API/database plan.

[schema.md](../database/schema.md) referenced three absent artifacts:

- `scripts/render-schema.mjs`: absent; the dictionary and JSON are design inputs,
  not proof that a runnable renderer exists. No renderer is needed for runtime startup.
- `docs/database/implementation.md`: absent; current write rules are in the
  [MVP spec](../planning/backend-mvp-spec.md),
  [API contract](../api/mvp-contract.md) and resolved planning tickets.
- `backend/migrations/0001_initial.sql`: absent; ticket 02 owns real versioned
  migrations, constraints and grants. The historical name is not a migration baseline.

Ticket 01 creates only the runtime foundation. Ticket 02 owns real-database
transaction/rollback/grants evidence. No successful database verification is claimed here.
