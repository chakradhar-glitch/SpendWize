# 03: Authenticate users and manage profiles

**What to build:** An authenticated person can bootstrap, read and edit their SpendWise profile without duplicate identity or overwritten names, while Supabase remains responsible for credentials and sessions.

**Blocked by:** 02: Establish persistence and database access boundaries.

**Status:** claimed (2026-11-17). Triage label: ready-for-agent.

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Implement account bootstrap/read/display-name edit with agreed response fields/statuses and trusted email, verification and password-reset capability data. Derive the actor from verified subject, never request bodies.
- [ ] Validate Supabase token signature, issuer, audience and expiry through a maintained verifier. Locally signed fixtures exercise the real verifier using a controlled signing-key source.
- [ ] Provision a missing profile idempotently, including concurrent first use; seed its name once with the agreed fallback. Repeated bootstrap and later sign-ins preserve user edits.
- [ ] Permit authenticated unverified users to bootstrap/read/edit profiles; expose a reusable verified-user gate for group operations. Validate name limits, unknown fields and the shared error shape.
- [ ] Document Supabase SDK ownership of registration, Google/email sign-in, verification/reset, refresh and current-session sign-out. Accept otherwise-valid access tokens until expiry without per-request session-revocation lookup; issue no second token or email-based user merging.
- [ ] Seed verified A/B/C, unverified U and outsider X with repeatable IDs using shared builders. Cover missing/expired/wrong-signature/issuer/audience tokens and profile/name behavior without mocked repositories.

## Verification ownership

Extend groups 1 and 3 for profiles/auth and reusable endpoint access assertions. Actual Google/email delivery, reset and multi-session sign-out are reserved for the single deployed smoke walkthrough in 12.

