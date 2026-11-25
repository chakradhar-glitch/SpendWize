# 06: Record expenses and read direct balances

**What to build:** Active members can record shared expenses using all approved split methods and immediately read correct direct debts and group summaries, with retries unable to duplicate an expense.

**Blocked by:** 05: Invite members and accept invitations.

**Status:** ready-for-agent

**Parent:** [Backend MVP specification](../../../docs/planning/backend-mvp-spec.md).

**Shared rules:** Follow the approved API contract, schema, glossary and Supabase Auth ADR referenced by the parent. Preserve the six-group lean verification plan; add only relevant distinct behavior at the API/real-PostgreSQL seam using the runtime role. Frontend screens and frontend implementation remain out of scope. This ticket is open work; claim before implementation and record completion evidence.

## Acceptance criteria

- [ ] Deliver expense creation/detail and direct-balance reads, and connect group list/detail summaries to committed financial data. Use minor-unit strings, entry bounds 1–99999999999, nonnegative shares and aggregate strings without the per-entry cap.
- [ ] Support one active payer and unique active participants, including payer outside participants, with equal/exact/percentage rules. Reject invalid/method-inappropriate fields; percentages total 10000 basis points.
- [ ] Use integer/rational largest-remainder allocation with stable membership-ID ties. Literal anchors include equal 100 -> 34/33/33, equal 1 -> 1/0/0, and percentage 101 at 3333/3333/3334 -> 34/33/34.
- [ ] Compute only pairwise mutual netting, exclude self-debt and keep groups/currencies separate. Return positive direct debts and separate caller owed/receivable totals using a consistent read snapshot per response.
- [ ] Validate calendar dates against the group's current local date, allowing backdates but rejecting future dates. Lock currency permanently in the same transaction as the first financial entry.
- [ ] From the first financial endpoint, require UUID retry keys scoped by actor; fingerprint the canonical command/target, retain/replay original successful status/body after current-access checks and reject changed-command reuse. New keys are ordinary new submissions.
- [ ] Under the shared group lock, atomically commit entry/shares, version 1, creation revision, currency lock and retry result before success. Race identical keys and inject mid-write/deferred-commit failure to prove one result or complete rollback with retry possible.
- [ ] Provide actual request/response examples and extend shared validation/access, financial, persistence and retry scenarios. Do not introduce temporary unprotected financial writes.

## Verification ownership

Extend groups 2, 3, 5 and distinct persisted assertions in 6. Own shared financial command/retry/rollback helpers and create-expense race cases; subsequent tickets extend operation tables rather than copy test bodies.

