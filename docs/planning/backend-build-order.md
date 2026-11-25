# Backend build sequence and frontend handoff

Status: agreed build sequence, 2026-11-17. Planning only; no application or test implementation performed here. User approved the sequence and the [test-environment requirements](test-environment.md).

## Starting point

Inspected 2026-11-17: current checkout has the approved database design, backend structure, API contract and verification plan. The backend directory has no application source, dependency manifest or migration files. Start from the approved design rather than assuming earlier referenced implementation artifacts exist. Documentation referencing missing generated scripts/migrations must be reconciled during foundation work.

## Proposed milestones

| Order | Work | Demonstration / completion evidence |
| --- | --- | --- |
| 1. Runnable foundation | Python dependency setup; FastAPI factory/entry point; typed configuration; request IDs, redacted logging, standard errors; synchronous SQLAlchemy sessions with explicit commit before write success; local PostgreSQL setup. | Documented local startup, health response, environment-variable template without secrets. No unused budgets/analytics/workers modules. |
| 2. Persistence and access boundary | Translate approved schema into versioned migrations; constraints/indexes/history protection; separate migration-owner and runtime privileges; local fixtures for Supabase-owned identities; real Supabase connection configuration. | Clean-database migration and runtime/client-role boundary checks from the lean verification plan. Never create or modify managed auth internals on Supabase. |
| 3. Authentication and profiles | Verify Supabase tokens and verification state; bootstrap/read/edit profile; trusted account fields; current-session sign-out expectations remain SDK-owned. | Account endpoints work with token validation and idempotent profile creation; focused shared auth cases pass. |
| 4. Groups and joining | Group create/list/detail/update; roster; invitation creation/list/revocation/preview/acceptance; departure/removal/rejoin and membership events. Establish group locking and access rechecks for all mutations. | Two users join the same group; denied outsider access, no duplicate acceptance, invitation lifecycle and settled departures demonstrated. Financial-dependent departure cases complete after milestone 5. |
| 5. Financial write and balance core | Exact integer/rational splits; expenses/shares; direct balances; repayments; corrections and soft deletion; expected versions; actor-scoped retry keys and atomic history. | Approved money examples work; corrections/retries/versions and departed-member protection hold. Add the compact financial, race and rollback cases alongside implementation. |
| 6. Complete read contract | Combined transaction list, pagination/tie-breakers, caller positions, icons, group summaries and detail responses; finish shared validation/error contract checks. | All API routes covered, lists refresh correctly, read results agree with committed financial state, examples match actual responses. |
| 7. Test environment and handoff | Deploy chosen environment; set runtime secrets and auth redirects/providers; apply migrations using migration credentials; complete real-auth smoke walkthrough and configuration/recovery notes. | Reachable HTTPS API, lean suite passing, deployment smoke evidence, API examples/OpenAPI and documented frontend connection setup. |

Start implementing the agreed lean tests with each milestone; do not write tests during this planning effort or postpone all verification until the final deployment. Reuse the six scenario groups rather than create a separate test stack per milestone.

## Dependencies and boundaries

- Order is foundation → persistence → authentication → groups → financial core → completed reads → deployed handoff. Environment provisioning may start early once its choices are agreed; deployment readiness still depends on the completed contract.
- Build financial write operations with their transactional history/idempotency/version behavior together; do not ship temporary unprotected money endpoints.
- Maintain a compact route-to-scenario checklist so shared test groups cover the whole API without duplicate layer tests.
- Target free hosting with acceptable sleep/startup delays and disposable test data. Create a Supabase project during implementation. Follow the [environment requirements](test-environment.md) for configuration, recovery and provider selection; paid options require the user's approval.

## Frontend receives

- Test API base URL, public Supabase connection configuration and auth/deep-link callback requirements; backend secrets remain server-side.
- Actual request/response examples and generated OpenAPI matching the agreed API contract, including errors, pagination, minor-unit strings, retry keys and versions.
- Disposable tester accounts/data workflow, data-reset expectations and supported currencies/timezone behavior.
- Successful automated verification and deployed real-auth smoke evidence, with any known limitations explicitly recorded.
- A subsequent frontend phase for screen design and React Native/Expo/TypeScript implementation. Android/iOS build distribution is planned there, not added as a backend completion requirement.

## Planning completion

Environment requirements and this milestone sequence are agreed. The wayfinder planning effort is complete. Next, turn these milestones into implementation-sized tickets with dependencies and acceptance criteria. This document is a build plan, not authorization to deploy services, spend money or apply live migrations during planning.
