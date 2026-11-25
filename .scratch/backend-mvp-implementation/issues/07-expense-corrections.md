# 07: Correct and soft-delete expenses

**What to build:** Any active member can correct or remove an expense while preserving history, rejecting stale edits and returning the original result for a retried command.

**Blocked by:** 06: Record expenses and read direct balances.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver full expense replacement with expected_version and soft deletion with expected version, both requiring UUID retry keys. Increment versions and return agreed resources/tombstones; stale versions conflict with current_version.
- [ ] Record complete immutable before/after snapshots including ordered shares, actor and timestamp atomically with every change and retry result. Deleted detail returns 404; deleted entries no longer contribute to balances.
- [ ] Exact authorized replay runs before stale/deleted-entry validation and returns the original status/body even after later updates/deletion. Changed payload/operation/target/version under a reused key conflicts; a fresh key against a deleted entry returns 404.
- [ ] Permit already-referenced departed memberships to remain but never newly add departed payers/participants. Reject any correction/deletion producing nonzero direct balances involving a departed member.
- [ ] Recompute direct balances and summaries after changes; currency remains locked even when the first/all entries are soft-deleted. Preserve compatibility with repayment-derived balances introduced by 08.
- [ ] Extend shared operation tables for expense replacement/deletion, same-version edit races, retries and atomic rollback. Use seeded inactive membership fixtures for protection until live departure journeys are available in 10.
- [ ] Document correction/delete examples. The correction-after-repayment debt-reversal anchor is exercised with real repayments in 09, without adding a blocker on repayment creation here.

## Verification ownership

Extend groups 2, 3 and 5, using the common financial scenario/command cases. Own expense edit/delete/version behavior; 09 owns the cross-feature repayment correction anchor, and 10 owns public departure races.

