# 10: Leave, remove and rejoin safely

**What to build:** Settled members can leave or be removed and later rejoin without losing history, while outstanding direct debt, removed access and concurrent financial writes are handled safely.

**Blocked by:** 05: Invite members and accept invitations; 07: Correct and soft-delete expenses; 09: Correct and soft-delete repayments.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver leave/self and remove/other membership operations using current active access, group locks and debt checks. Every direct balance involving the departing member must be zero; zero overall net is insufficient.
- [ ] Atomically persist inactive membership state and append-only leave/removal events, retaining profile, membership identity, financial attribution and prior participation records.
- [ ] Revoke departing issuers' invitations. Final settled departure inactivates the group and revokes all remaining links; inactive groups cannot be joined or restored through MVP APIs.
- [ ] Removed members immediately lose read/mutation/invitation/list access and financial-result replay despite an otherwise valid unexpired token. Extend the shared route/access matrix rather than add handwritten tests per route.
- [ ] Demonstrate rejoin with a still-valid invitation from another eligible issuer, preserving membership ID/first-joined timestamp/history and restoring access with one new join event.
- [ ] Using public journeys, verify corrections/deletions cannot give departed members debt/receivables or newly select them, while existing references may remain if every direct balance remains zero.
- [ ] Race financial writes/repayments against departure with independent synchronized connections and inspect persisted outcomes. Only states preserving current membership and direct-debt invariants may commit.
- [ ] Complete lifecycle coverage including settled leave/removal, zero-net-but-unsettled denial, issuer revocation and final inactivation. No Activity/history UI is added.

## Verification ownership

Complete departure/rejoin portions of group 1, departed-reference parts of 2, removed-access rows in 3 and write/departure races in 5. Existing operation tests remain shared.

