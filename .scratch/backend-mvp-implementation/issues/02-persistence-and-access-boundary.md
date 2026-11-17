# 02: Establish persistence and database access boundaries

**What to build:** A maintainer can build the approved database from empty and run application operations with restricted credentials, while database constraints and immutable history protect shared financial records.

**Blocked by:** 01: Run the backend locally.

**Status:** resolved (2026-11-17). Triage label: ready-for-agent.

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [x] Create versioned migrations for the approved application model, indexes, same-group foreign keys, unique persistent memberships, append-only membership events/revisions, financial checks and deferred expense/share consistency constraints.
- [x] Reconcile retry persistence with all six expense/repayment create, replacement and deletion operations. Support actor/key uniqueness, target/payload/version fingerprints and atomic original success status/body retention for the MVP lifetime.
- [x] Separate migration-owner and non-owner runtime privileges. Anonymous/client roles cannot access business tables; runtime cannot alter schema or update/delete immutable history.
- [x] Migrate an empty disposable real PostgreSQL database and provide isolated privileged fixture setup/cleanup for identities, revision inspection and failure injection. Never create or modify hosted Supabase-managed auth internals.
- [x] Use the intended runtime role for API/database journeys, reusable fixture builders and one documented suite command. Prove representative cross-group, duplicate-membership, malformed-total/share and protected-history violations through direct SQL/grants checks.
- [x] Document local versus hosted connection configuration and reconcile missing migration/implementation artifacts with actual outputs; never treat a historical filename reference as an existing migration.

## Verification ownership

Own scenario group 6 (persistence boundary) and the real PostgreSQL harness reused by all later tickets. Later financial tickets extend persisted-outcome assertions only for their distinct behavior.

## Completion evidence

See [persistence verification](../../../docs/testing/02-persistence-evidence.md). Real PostgreSQL clean migration, 36 tests with no skips, grants/immutability and deferred commit rollback passed. Standards/spec reviews found no remaining issues after correcting the application schema to the approved app name.
