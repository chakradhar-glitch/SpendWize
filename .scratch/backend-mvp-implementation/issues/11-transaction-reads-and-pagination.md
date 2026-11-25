# 11: Complete transaction reads and pagination

**What to build:** Members can browse a coherent newest-first financial record and refresh all group views after changes, with correct expense positions and predictable cursor behavior.

**Blocked by:** 07: Correct and soft-delete expenses; 09: Correct and soft-delete repayments.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver the merged non-deleted expense/repayment transaction list with tagged types, versions, dates and agreed display metadata. Repayment rows identify both parties and payment metadata.
- [ ] Expense rows include payer/name/amount, a fixed keyword icon mapping with generic fallback and caller lent/borrowed/neutral position equal to paid amount minus that expense's allocated share, independent of repayments.
- [ ] Enforce descending transaction date/creation timestamp/type/UUID ordering, group creation ordering, member first-join ordering and invitation creation ordering. Use the contract's list envelopes, default 30/max 100 limits and opaque resource/filter-bound cursors.
- [ ] Traverse unchanged tied-date/tied-timestamp data in small pages without omissions/duplicates using shared assertions across lists. Cover empty results, limit validation and invalid/wrong-filter/resource cursors.
- [ ] After backdating, editing, insertion or soft deletion, refreshing from page one returns current data; no frozen cross-request snapshot or exact total count is promised.
- [ ] One response's summaries/balances agree through a consistent read snapshot, separate currencies stay separate and aggregates remain minor-unit strings even above entry caps.
- [ ] Complete the route-to-scenario checklist and reuse shared auth/outsider/wrong-group access and validation cases for every delivered read. Removed-user checks are finalized with 10 before handoff.
- [ ] Update actual read/pagination/error examples and OpenAPI. Confirm corrected-expense positions differ appropriately from repayment-inclusive group balances without adding frontend screens.

## Verification ownership

Own group 4 and complete relevant read assertions in groups 2/3. Financial protections and scenarios stay with their originating tickets; final coverage is audited in 12, not duplicated here.

