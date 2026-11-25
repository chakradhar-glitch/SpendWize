# 04: Create and manage groups

**What to build:** Verified users can create and browse their groups, inspect membership and change permitted group settings while outsiders cannot discover private group data.

**Blocked by:** 03: Authenticate users and manage profiles.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver group create/list/detail/update and active/historical roster reads under the agreed API contract. Creation atomically persists the group, creator membership and initial membership event.
- [ ] Support INR/USD/CAD/GBP/EUR and valid immutable IANA timezones. Apply agreed trimmed name limits; allow rename and currency changes only before permanent currency locking.
- [ ] All active members have equal rights. Require verified auth and current membership as applicable, return the agreed concealed-resource response for inaccessible/wrong-group IDs and omit auth emails from roster data.
- [ ] Establish group-row locking and in-transaction actor access rechecks for mutations, including currency edits; share this boundary with later invitation, membership and financial operations.
- [ ] Return actual member counts, own membership and separate owed/receivable fields. Empty groups return zero; connect financial-derived values when 06 introduces entries rather than retaining placeholders.
- [ ] Honor list ordering/cursor/limit contracts from introduction, using shared paging helpers/assertions; 11 completes cross-resource and mixed-data verification.
- [ ] Extend lifecycle, validation/access and relevant read cases using INR/USD isolation and a compact supported-currency table. Verify unverified/outsider denial and immutable timezone behavior.

## Verification ownership

Extend groups 1, 3 and relevant portions of 4. Financial currency-lock and summary behavior is implemented and proved in 06/07 rather than simulated here.

