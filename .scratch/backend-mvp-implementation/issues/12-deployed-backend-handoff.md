# 12: Deploy and prove the backend handoff

**What to build:** The later mobile team receives a reachable verified test backend, real authentication evidence and enough connection/reset/recovery guidance to begin frontend work.

**Blocked by:** 10: Leave, remove and rejoin safely; 11: Complete transaction reads and pagination.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] During implementation, verify current free-compatible hosting availability, payment requirements, Python/container support, HTTPS, Supabase outbound connectivity and connection/pooling limits. Accept sleep/startup delays; ask before choosing paid services or enabling charges.
- [ ] Create a separate Supabase project and disposable test accounts/data; configure supported auth providers, verification/reset and explicit test callbacks. A minimal SDK harness is sufficient before mobile screens exist.
- [ ] Deploy a reachable HTTPS API with server-side secrets, public-only client configuration, separate migration/runtime credentials, explicit application migrations, health checks and request-ID redacted logs. Never modify Supabase-managed auth internals.
- [ ] Run all six shared scenario groups against migrated real PostgreSQL/runtime credentials and audit every API route against the coverage checklist. No skipped financial/access/race/rollback cases; fix flaky synchronization rather than rerun until green.
- [ ] Run the one approved deployed smoke walkthrough: real email sign-up/verification/reset and Google sign-in; two-user group/invitation/expense/repayment/correction/readback; current-session sign-out preserving another session, token-expiry limitation and removed access with an unexpired token.
- [ ] Inspect logs/errors for secrets/tokens/invitation/email leakage and confirm deployed role/configuration boundaries match those tested. Repeat smoke for auth/deployment configuration changes without duplicating all automated financial cases manually.
- [ ] Deliver API base URL, non-secret Supabase configuration and auth callback requirements, matching real request/response/error examples and generated OpenAPI, supported currencies/timezone rules, one-command suite instructions and actual run evidence with known limitations.
- [ ] Document deployed code/migration revisions, seeding/designated disposable-resource reset, sleep diagnosis and recovery by compatible revision redeployment or migrations/seed rebuild. A code rollback does not imply reversing migrations; promise no production backup/PITR.
- [ ] Declare backend readiness only when all gates pass. Defer detailed screens, React Native/Expo implementation, native storage design and Android/iOS distribution to the later frontend phase.

## Verification ownership

Own the final coverage/evidence audit and single real-auth deployed smoke walkthrough. Reuse the existing six groups rather than creating a seventh suite or delaying earlier tests to deployment.

