# 05: Invite members and accept invitations

**What to build:** An active member can share a time-limited invitation and a verified recipient can preview and explicitly accept it without duplicate membership.

**Blocked by:** 04: Create and manage groups.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver invitation create/list/revoke and authenticated verified preview/acceptance with the contract's statuses, fields and minimal preview data.
- [ ] Generate high-entropy bearer tokens, store only SHA-256 digests, return full URLs only at creation and never expose secrets/hashes in list responses or logs. Extracted tokens travel in POST bodies.
- [ ] Make links reusable for seven days, permit multiple concurrent links, allow any active member to revoke and make repeated revocation of a group-owned link succeed as agreed.
- [ ] Reject invalid, expired, revoked and inactive-group tokens with the same unavailable response. Revalidate link/group eligibility while holding the group lock.
- [ ] Explicit repeated acceptance by an active member returns the same membership without another join event. Reactivate an existing inactive membership rather than creating a duplicate; full departure/rejoin journeys complete in 10.
- [ ] Preserve first-joined identity and record join/rejoin events atomically. Verify simultaneous acceptance cannot duplicate membership or events.
- [ ] Extend lifecycle/access cases for joining, expiry with controlled application clock, privacy and list cursors using shared fixtures. Provide a two-user join demonstration without screens.

## Verification ownership

Extend groups 1, 3 and shared list checks in 4. Issuer-departure revocation, access loss and final-group inactivation are completed in 10.

