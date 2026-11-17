# Backend MVP implementation tickets

Status: approved breakdown published 2026-11-17. Tickets retain the ready-for-agent
triage label; individual ticket files record claimed/resolved lifecycle states and
actual completion evidence. Ticket 01 is resolved; implementation proceeds in order.

Parent: [Backend MVP specification](backend-mvp-spec.md). The parent and completed planning decisions remain unchanged.

## Tickets and dependencies

| Ticket | Blocked by | Verification ownership |
| --- | --- | --- |
| [01: Run the backend locally](../../.scratch/backend-mvp-implementation/issues/01-run-backend-locally.md) | None | Startup demonstration/shared runner |
| [02: Establish persistence and database access boundaries](../../.scratch/backend-mvp-implementation/issues/02-persistence-and-access-boundary.md) | 01 | 6: persistence and harness |
| [03: Authenticate users and manage profiles](../../.scratch/backend-mvp-implementation/issues/03-authentication-and-profiles.md) | 02 | 1/3: profiles and auth |
| [04: Create and manage groups](../../.scratch/backend-mvp-implementation/issues/04-create-and-manage-groups.md) | 03 | 1/3/4: groups and roster |
| [05: Invite members and accept invitations](../../.scratch/backend-mvp-implementation/issues/05-invitations-and-joining.md) | 04 | 1/3/4: invitations and joining |
| [06: Record expenses and read direct balances](../../.scratch/backend-mvp-implementation/issues/06-expenses-and-direct-balances.md) | 05 | 2/3/5/6: expense creation and balances |
| [07: Correct and soft-delete expenses](../../.scratch/backend-mvp-implementation/issues/07-expense-corrections.md) | 06 | 2/3/5: expense corrections |
| [08: Record external repayments](../../.scratch/backend-mvp-implementation/issues/08-record-repayments.md) | 06 | 2/3/5: repayment creation |
| [09: Correct and soft-delete repayments](../../.scratch/backend-mvp-implementation/issues/09-repayment-corrections.md) | 08 | 2/3/5: repayment corrections |
| [10: Leave, remove and rejoin safely](../../.scratch/backend-mvp-implementation/issues/10-membership-departure-and-rejoin.md) | 05, 07, 09 | 1/2/3/5: departure and rejoin |
| [11: Complete transaction reads and pagination](../../.scratch/backend-mvp-implementation/issues/11-transaction-reads-and-pagination.md) | 07, 09 | 2/3/4: completed reads |
| [12: Deploy and prove the backend handoff](../../.scratch/backend-mvp-implementation/issues/12-deployed-backend-handoff.md) | 10, 11 | Six-group audit and deployed smoke |

## Working the frontier

Start with 01. A ticket may start only when all its listed blockers are resolved, even though every ticket carries the ready-for-agent triage label. Claim before working; retain the label as triage metadata and record a claimed/resolved lifecycle state plus completion evidence. Tickets 07 and 08 may proceed independently after 06; tickets 10 and 11 may proceed independently after their prerequisites. Do not infer authorization to run concurrent agents from this graph.

The approved foundation and persistence milestones (01/02) establish the runnable and integrity boundary before business slices. Later tickets deliver verifiable API-to-database behavior; UI remains deferred. Ticket 10 finishes financial-dependent membership behavior after the financial core, as allowed by the build sequence.

Ticket 09 keeps its approved blocker 08 only: repayment edit/delete behavior can be completed independently of 07. Its cross-feature expense-correction-after-repayment assertion joins the shared financial journey when 07 is available; that assertion belongs to the 07+09 integration and must pass before 10/11/12 are complete. This is not permission to omit or skip the final assertion.

## Shared verification and handoff

Follow the [lean verification plan](../testing/backend-readiness.md): six scenario groups, compact case tables and shared fixtures, real API requests against PostgreSQL using restricted runtime credentials, focused direct-SQL/grants checks, and one deployed smoke walkthrough. Add relevant cases with each feature; no separate testing phase, numerical coverage target or duplicated unit/service/repository/API suites. Six groups are not a six-test limit. Each ticket supplies its actual response examples and evidence; 12 audits and packages them.

Keep the [API contract](../api/mvp-contract.md), [build sequence](backend-build-order.md), [test-environment requirements](test-environment.md) and [parent spec](backend-mvp-spec.md) authoritative. Hosting/provider research and provisioning occur during implementation; paid choices require approval. No provider was selected or live service created by this ticket publication.

Frontend screens, frontend implementation and mobile release remain deferred. The final deliverable is tested APIs, current examples/OpenAPI and a deployed disposable test environment suitable for later mobile work.
