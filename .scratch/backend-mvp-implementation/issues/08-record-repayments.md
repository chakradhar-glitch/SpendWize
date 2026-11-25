# 08: Record external repayments

**What to build:** An active member can record a partial or full payment made outside SpendWise and immediately see the correct reduced direct debt without treating repayment as spending.

**Blocked by:** 06: Record expenses and read direct balances.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver repayment creation/detail with sender, recipient, amount, transaction date and cash/other metadata. Both distinct parties must currently be active members; any active member may record the payment.
- [ ] Under the group lock, require a current direct debt from sender to recipient and cap the new payment at that debt. Reject opposite direction/no debt and overpayment using agreed errors with unchanged state.
- [ ] Backdating validates against current corrected debt at save time, not a replay of historical dates. Reject future dates using group timezone and apply agreed minor-unit money limits.
- [ ] Cash requires null label; other requires trimmed nonblank label of 1–100 characters. Include payment metadata in history and canonical retry fingerprints.
- [ ] Reuse financial mutation infrastructure for version 1, creation history, currency lock and actor-scoped retry replay/conflict; commit everything before success and roll back failed reservations.
- [ ] Include repayments in direct balances and group summaries, never spending; demonstrate A pays 1000 split A/B, B owes 500, then repays 300 and owes 200.
- [ ] Extend the same financial/access/retry tables for repayments, and synchronize competing payments against one debt to prove overpayment cannot succeed. Check distinct keys follow ordinary remaining-debt rules.

## Verification ownership

Extend groups 2, 3 and 5. Reuse common financial fixtures and retry/rollback assertions from 06; correction and replay-after-correction cases complete in 09.

