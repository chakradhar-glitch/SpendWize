# 09: Correct and soft-delete repayments

**What to build:** Active members can correct historical payment records without changing their parties, with auditable versioned changes and balances reflecting the corrected financial facts.

**Blocked by:** 08: Record external repayments.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver repayment replacement and soft deletion with expected versions and retry keys, complete atomic before/after revisions, version increments and agreed responses/errors.
- [ ] Keep sender/recipient fixed. Permit amount/date/payment-metadata correction or deletion without reapplying the creation debt cap; wrong parties require deletion plus a new normally validated repayment.
- [ ] Preserve zero direct balances for departed members on all corrections/deletions, while allowing debt reversal between active members. Use inactive fixtures until 10 completes public departure journeys.
- [ ] Extend the common command table to repayment replacement/deletion, authorized replay after later changes/deletion, changed command conflicts, stale versions, deleted-detail 404 and rollback/deferred-commit failures.
- [ ] Exercise correction after repayment using available expense replacement: A pays 1000 split A/B, B repays 300, correction to total 400 makes A owe B 100. Keep the expense position based on its corrected allocation when read by 11.
- [ ] Verify repayment corrections, unlike new payments, can exceed the current creation cap if otherwise valid; metadata/date constraints still apply. Preserve permanent currency lock after deletion.
- [ ] Provide actual correction/delete/conflict examples and persist complete actor/time/history evidence. Add distinct cases to shared scenarios, not a second financial test stack.

## Verification ownership

Extend groups 2, 3 and 5; own the cross-feature correction-after-repayment anchor using 07 when available. This acceptance check is completed before final handoff; it does not change the approved blocking edge (08 only).

