# Ticket 02 evidence

Status: resolved; local verification and review passed, 2026-11-17.

## Implemented boundary

Alembic revision `0001` creates the eleven approved application tables and version
table in private schema `app`. It assumes an existing managed `auth.users`
and named runtime/client roles; only local fixtures create stand-ins. Role
provisioning precedes migrations and is separate from application startup.

The migrated schema includes same-group keys, persistent unique memberships,
money/name/payment-method checks, deferred expense/share sum and percentage
consistency, immutable history triggers and restricted DML grants. Database
triggers preserve timezone and the permanent currency lock after financial entry.
No balance table is stored. Snapshots and financial services remain responsible
for complete business-command history; financial tickets prove those behaviors.

Retry persistence supports six operations (`create`, `replace`, `delete` for each
entry type), actor/key uniqueness, a SHA-256 request digest and original successful
status/body. The digest must fingerprint operation, group, target and canonical
validated payload including expected version; the later financial service computes
it and stores its result in the same transaction. No TTL or mutable retry result.

## Verification

The initial empty-database test failed for absent Alembic configuration before
migrations were implemented, then passed against real PostgreSQL 17.7. Repeated
`upgrade head` and runtime-role checks are included in the shared pytest runner.
Direct-SQL cases cover cross-group references, duplicate memberships, invalid
amounts/shares/percentages, append-only history, client denials and runtime DDL/
managed-identity denials. Failures assert rollback, including the currency lock.

A test-only HTTP route exercises the production session dependency/error stack:
a deferred commit failure returns 500 instead of 201 and retains no expense,
shares, revision or retry result; removing the fault allows the same key to succeed.
It is absent from production routes and is not a claim that financial APIs exist.

The isolated privileged fixture may inspect/reset only local `spendwise_test`.
See [backend instructions](../../backend/README.md) for the single suite command,
role setup, local/hosted differences and disposable reset/recovery procedure.

Executed: `pytest -q --tb=short` — 36 passed in 6.35s on real PostgreSQL 17.7,
with no skipped cases. Strict `mypy app` passed (eight source files); Ruff passed
after formatting/import fixes. The installed Starlette reports a deprecation of
its httpx TestClient adapter; this does not skip or change the executed API checks.

Review: standards and spec axes found no additional issues. Self-review corrected
the SQL schema name to match the approved schema.json app value, then rebuilt
the disposable container and reran all 36 tests (6.92s), Ruff and mypy successfully.
