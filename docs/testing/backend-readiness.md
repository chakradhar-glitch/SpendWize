# Lean backend verification plan

Status: agreed plan, 2026-11-17. The user approved the lean verification plan and confirmed that tests are not written during planning. Test code has not been written or run by this planning decision.

Decision: [Define evidence that the backend is ready](../../.scratch/backend-first-mvp/issues/03-verification.md). Baseline: [agreed API contract](../api/mvp-contract.md).

## Principle

Use the fewest independent scenarios that demonstrate the behavior, not an artificially low test-function count. Start with six automated scenario groups. Small parameter tables cover distinct boundaries without copying test bodies. Keep failure messages specific to each checkpoint. Do not duplicate a rule across unit, service, repository and API tests unless the extra layer catches a distinct failure.

## Test setup

- One disposable real PostgreSQL test database, migrated from empty before the suite. Use the intended non-owner runtime role for API requests. Use an isolated privileged fixture connection only to seed identities, inspect retained history, inject test failures and clean up.
- Use actual application routes, validation, transaction services and SQL. No mocked repositories or mocked monetary calculations. SQLite/in-memory emulation does not prove PostgreSQL locking, grants, constraints or rollback.
- Verify tokens through the real verifier with locally signed fixtures and a controlled signing-key source. Seed verified A/B/C, unverified U and unrelated outsider X. Wrong signature/issuer/audience and expired credentials must be rejected. Real provider OAuth/email delivery are checked once in the deployed smoke walkthrough.
- Share fixture builders, not mutable test state. Each scenario gets isolated groups and repeatable member UUIDs. Freeze the application clock for expiration/date-boundary cases; keep real database concurrency for race cases.
- Create an INR group and a second group in USD to prove cross-group and currency isolation; accept all five supported currencies in a compact validation table.
- Provide one documented command for the automated suite. Exact runner/dependency setup belongs to implementation; use existing project tooling where available rather than introduce multiple runners.

## Six automated scenario groups

| Group | Actions and essential assertions |
| --- | --- |
| 1. Identity and group lifecycle | Bootstrap twice without duplicate profile; edit name and bootstrap again without overwriting it. Read account fields. U can manage their profile but cannot perform group actions. A creates, reads, lists, renames and changes pre-entry currency; timezone is fixed. Create/list/preview invitations and explicitly accept twice with one membership/join event. Check expired, revoked, invalid tokens and issuer-departure revocation. Read active/historical roster without email leakage. Settled members leave or are removed; removed access fails; valid rejoin restores the same membership and history. Final departure inactivates group and invitations. |
| 2. Financial journey | Create equal, exact and percentage expenses with known expected shares. Read details and transaction positions. Include payer outside participants, neutral row, zero rounded share, deterministic remainder, cash/other metadata, partial and full repayment. Verify pairwise netting without rerouting, separate owed/receivable totals and currencies. Correct expense after repayment to reverse a balance; correct repayment without creation cap; sender/recipient fixed. Exercise both expense and repayment soft deletion, version/history snapshots, deleted-detail 404 and permanent currency lock. Prove nonzero direct debts block departure even when overall net is zero; departed references can remain but cannot acquire debt or be newly added. |
| 3. Validation and access matrix | Reuse valid request builders and mutate one input per row. Cover missing/expired/invalid tokens; outsider/removed and wrong-group IDs across every protected route family (read, edit, delete, membership, invitation and replay). Cover money type/bounds, bad split sums/method fields/duplicate participants, unsupported currency/timezone, future dates at group-local midnight, name/label limits, missing retry/version inputs and wrong-direction/overpayment. Assert agreed status/code/field shape and unchanged financial state/history after rejected writes. Reuse the same parameterized authentication checks across endpoints; avoid separate handwritten tests per route. |
| 4. Reads and pagination | Seed expenses/repayments with tied dates/timestamps and distinct IDs. Traverse small pages with no missing or duplicate items in unchanged data; assert merged descending order, deleted omission, current-user positions and balances. Exercise groups/members/invitations list cursors using shared paging assertions, empty lists, limits and invalid or wrong-filter cursors. After edit/delete/backdating, refresh from page one and see current data. Check one response's balances/summary agree, without demanding a snapshot across separate requests. |
| 5. Retries, conflicts and atomicity | With independent connections and explicit synchronization, race identical retry keys: one financial write/history result, identical original response. Parameterize create/update/delete over expenses and repayments; check changed key payload/target conflicts, same payload with new key follows ordinary rules, successful replay after later edits/deletion and denied replay after removal. Race two edits from one version: exactly one succeeds. Race repayments against the same debt and financial writes against departure: only outcomes preserving debt/membership invariants are allowed. Inject a failure between financial/history/result writes and a deferred commit failure: everything rolls back, no success response or retained key; retry succeeds once fault is removed. |
| 6. Persistence boundary | Empty-database migration succeeds. Using runtime credentials, direct malformed SQL cannot create cross-group references or invalid totals; history update/delete is denied. Anonymous/client roles cannot access business tables; runtime role cannot alter schema. Check required foreign keys, unique membership, append-only history, atomic shares and totals using representative violations rather than one test per column. Verify rollback/debt outcomes through persisted rows, not only HTTP responses. |

Use focused subcases within a group when a long scenario would hide failures. Six groups are a starting structure, not a cap that justifies dropping behavior. Add a new regression case only for an uncovered bug or distinct risk.

## Expected-value anchors

- Equal 100 minor units over A/B/C allocates 34/33/33 in stable membership-ID order. Equal 1 over three members allocates 1/0/0.
- Percentage 101 at 3333/3333/3334 basis points allocates 34/33/34 for ascending A/B/C IDs: C wins the largest remainder, then A wins the tie.
- A pays 1000, A/B split equally: B owes A 500. B repays 300: B owes A 200. Correct expense total to 400: A owes B 100. Original expense-row position reflects its corrected share, not repayment history.
- Construct A owing B and being owed the same amount by C: A's net is zero but departure fails until both direct debts settle.
- Use known literal outcomes or an independently derived table; never calculate expected shares/balances with the production helper being tested.

## One deployed smoke walkthrough

Run against an isolated test environment with disposable accounts after the automated suite passes. No public app release or finished screens are required.

1. Check HTTPS health and documented authenticated API examples. Sign up using email/password, verify email and reset password; sign in with Google through a minimal SDK harness if the mobile UI is not built. Confirm FastAPI accepts issued tokens. These checks exercise integration configuration, not Supabase's own implementation.
2. With two accounts, create a group, preview/accept an invitation, add an expense, record repayment, make a correction and refresh balances. Confirm visible results agree with the examples and that success survives a later read.
3. Sign out the current session while another device/session stays usable; check the agreed token-expiry limitation. Remove a settled member and verify denied access with their still-unexpired token.
4. Check logs/errors for accidental token/invitation/email leakage, and confirm runtime credentials/configuration match the tested access boundary. Deployment/recovery specifics are completed by the test-environment ticket.

Repeat this smoke walkthrough for deployment/auth configuration changes; do not repeat every automated financial boundary manually.

## Backend-ready gate

- Every agreed API route is exercised successfully at least once by the six groups; protected routes receive the shared access checks. Financial mutations include versions/retries, both entity types and deletes.
- All automated groups pass against real PostgreSQL using the runtime role. No skipped financial, access, race or rollback cases. Flaky race tests are failures; fix synchronization rather than rerun until green.
- Migration and grants checks pass from a clean database. Deployed smoke walkthrough passes with real Supabase auth.
- Request/response examples, one-command test instructions, test-data setup and actual run evidence are available. No numerical coverage target or large low-value snapshot suite is required.
- Test-environment decision supplies a reachable HTTPS API and configuration/recovery expectations before the handoff is declared complete.

This plan specifies evidence to collect during implementation. It does not claim current code passes these checks or that six scenarios exhaust every possible input.
