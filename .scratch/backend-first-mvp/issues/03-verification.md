# Define evidence that the backend is ready

Type: grilling
Labels: wayfinder:grilling
Status: resolved
Assignee: current user (with Codex)
Parent: ../map.md
Blocked by: 01, 02

## Question

Which automated checks and manual acceptance scenarios prove the contracts, authorization, monetary rules, concurrent writes, retries, history, and migrations work? Define the local test setup, test data, and pass criteria for handing a deployed backend to frontend development.

## Comments

User constraint: write as few tests as practical while covering the whole agreed MVP. Favor end-to-end API/database journeys and compact data-driven cases; avoid repeating identical rules at unit, service, repository and API layers. No test code is authorized by this planning ticket alone.

Proposed review asset: [Lean backend verification plan](../../../docs/testing/backend-readiness.md).

## Answer

User approved the [lean backend verification plan](../../../docs/testing/backend-readiness.md) on 2026-11-17. Use six automated scenario groups with shared setup and compact case tables, plus one deployed smoke walkthrough. Minimize duplicated coverage across layers while preserving financial, authorization, concurrency, rollback and persistence checks. Six groups are a starting structure, not a claim that six individual test cases cover every input.

The linked plan defines test setup, expected-value anchors, route/behavior coverage and backend-ready pass criteria. Test code is written during backend implementation, not this planning effort. No tests were implemented or executed by this decision.

Test-environment requirements remain the next open decision. The build-order ticket remains blocked on that decision.
