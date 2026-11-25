# Settle remaining backend behavior and access policies

Type: grilling
Labels: wayfinder:grilling
Status: resolved
Assignee: current user (with Codex)
Parent: ../map.md
Blocked by: none

## Question

Which backend behavior and access policies still need decisions after reconciling the approved schema with the MVP journeys? Separate historical draft wording from genuine gaps. Cover current-session/revocation expectations, authorization boundaries, invitation handling, retry/conflict responses, and financial corrections only where approved documents leave behavior ambiguous. What are the concrete expected outcomes for those cases?

## Answer

Resolved with the user on 2026-11-17. The user answered yes to all three authentication recommendations.

### Authentication choices

- Sign out affects only the current device/session. Other devices remain signed in. A dedicated sign-out-everywhere feature is deferred.
- FastAPI accepts an otherwise valid access token until expiration without an additional current-session revocation check on each request. Continue validating signature, issuer, audience, and expiry. A copied token may remain usable after sign-out until expiry; the user accepted this MVP trade-off.
- Check current group membership on every group request. For mutations, recheck membership within the same serialized transaction as the write. Membership removal denies subsequent group access even when the caller's token has not expired.
- Defer a dedicated manual account-linking interface. Supabase owns authentication identities; SpendWise profiles and memberships reference the stable auth user UUID. Do not merge application users by email.

### Approved baseline carried forward

The user explicitly approved the database design before this ticket. Its existing recommendations are part of that baseline; historical draft wording does not reopen them.

- Supabase authentication; FastAPI-only application data access; email verification gates group actions; idempotent profile provisioning never overwrites an edited name.
- Active members have equal permissions. Reusable seven-day invitations require authenticated, verified, explicit acceptance; repeated acceptance does not duplicate membership. Departures revoke the issuer's links, and the final departure inactivates the group.
- Financial corrections use expected versions, preserve immutable before/after history, and recalculate direct balances atomically. Obsolete versions conflict rather than overwrite.
- Existing repayment amount/date corrections and soft deletion represent historical payments; do not reapply the new-payment debt cap. Keep sender and recipient fixed. Correct wrong parties through deletion and a new repayment subject to normal creation validation. All corrections preserve zero direct balances for departed members.
- Existing expenses may retain already-referenced departed members; do not newly select departed payers/participants. Corrections must preserve their zero direct balances.
- Backdated repayment creation validates against current corrected debt at save time. Transaction dates control display ordering, not historical replay.
- Retry keys identify intentional submissions: same caller/key/operation/data replays the original result; changed operation/data conflicts; a different key is a new command subject to normal validation. Replay requires current access and describes the original success, not the entry's latest version.
- Keep the approved application schema, database integrity rules, group serialization, and commit-before-success boundaries. Resolve concrete contract details in the API ticket rather than repeating schema design.

### Acceptance examples

- Signing out on phone A leaves phone B signed in.
- An otherwise valid copied access token can remain accepted until expiry after sign-out; an expired token is rejected.
- A removed member cannot read group data, mutate financial entries, or replay a previously successful group request using an unexpired token.
- A correction after repayment can reverse debt between active members; any correction producing a nonzero direct balance involving a departed member is rejected atomically.
- A stale financial edit or retry-key payload mismatch returns a conflict; exact HTTP shapes belong to the API-contract ticket.

### Follow-ups

- [Define the mobile-facing backend API contract](02-api-contracts.md) is now unblocked. Specify concrete endpoints, validation, errors, pagination, expected versions, and retry-key coverage.
- Exact token lifetime, SDK configuration, and sign-out implementation must match these policies during implementation; no numeric lifetime or provider setting is approved by this ticket.
- No application code, migrations, or live service settings were changed by this decision.
