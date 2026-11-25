# SpendWise MVP API contract

Status: agreed planning contract, 2026-11-17. Endpoints are not yet implemented. User confirmed the reviewed product choices, minor-unit string amounts, financial retry/version conventions, and expense-row position semantics. Remaining technical details below are implementation defaults within this contract.

Decision owner: [Define the mobile-facing backend API contract](../../.scratch/backend-first-mvp/issues/02-api-contracts.md).

## Confirmed scope

- Refresh on screen opening, pull-to-refresh, and after successful writes; no live updates required.
- Retain complete financial and membership history; history browsing endpoints and screens are deferred.
- Active members may rename groups and change currency before the first financial entry. Timezone is immutable; currency locks permanently after the first entry.
- Preserve the [approved model](../database/schema.md), [journeys](../mvp_user_journeys.md), and [access policies](../../.scratch/backend-first-mvp/issues/01-backend-behavior-and-access.md).

## Transport and values

- HTTPS JSON under `/api/v1`. Authentication is `Authorization: Bearer <Supabase access token>`.
- Supabase SDK owns registration, login, Google sign-in, password reset, verification and current-device sign-out. FastAPI issues no second token.
- UUIDs are strings. Dates are `YYYY-MM-DD`; audit timestamps are UTC RFC 3339 strings. Group timezone is an IANA identifier.
- All monetary amounts, including aggregate balances, are decimal strings of integer minor units: `"1050"` means INR 10.50 in an INR group. Never send decimal currency units or floating-point money. Frontend formats these values for display.
- Financial-entry amounts are 1 through 99999999999 minor units; shares may be zero. Aggregates can exceed the per-entry cap and remain strings.
- Percentages use integer basis points: `3333` means 33.33%; inputs total 10000. Equal split inputs omit amounts; exact split inputs supply minor-unit strings. API returns final allocated shares for every method.
- Membership IDs identify payers, participants, senders and recipients; profile IDs identify people. Actor IDs come from authentication, never request bodies.
- Trim names: profile/group 1–100 characters; expense 1–200. Payment labels for `other` are trimmed 1–100 characters; `cash` requires null. Reject unknown request fields and invalid enum/UUID/date values.
- Success returns the resource directly; lists return `{ "items": [], "next_cursor": null }`. Empty results are successful, not errors.

## Endpoints

All paths below are relative to `/api/v1`. All group operations require verified authentication and current active membership, except accepting a valid invitation to join. Profile operations require authentication but permit an unverified user.

| Method and path | Input / result |
| --- | --- |
| `POST /me/bootstrap` | Empty body; idempotently create a missing profile, preserving existing names. Return current profile/account as 200. |
| `GET /me` | Current profile, trusted auth email, verification state, and supported sign-in capabilities; 200. |
| `PATCH /me` | `{display_name}`; return updated account, 200. Login email changes are deferred. |
| `GET /groups` | Cursor list of caller's active groups, currency, active count, own membership ID, and owed/receivable summary. |
| `POST /groups` | `{name,currency_code,timezone}`; create group and creator membership atomically, return group, 201. |
| `GET /groups/{group_id}` | Group details and caller summary, including `currency_locked` and `active_member_count`. |
| `PATCH /groups/{group_id}` | Name and/or currency; return updated group, 200. Validate currency lock while holding group lock. |
| `GET /groups/{group_id}/members` | Cursor list; active by default, `include_departed=true` includes historical members. Return membership/profile IDs, display name, active state; no emails. |
| `POST /groups/{group_id}/leave` | Empty body; depart caller after zero direct-balance checks; 204. |
| `DELETE /groups/{group_id}/members/{membership_id}` | Remove another active member after zero direct-balance checks; 204. Use leave for self. |
| `POST /groups/{group_id}/invitations` | Empty body; return invitation ID, full share URL and expiry, 201. Full secret appears only in this creation response. |
| `GET /groups/{group_id}/invitations` | Cursor list of unexpired, unrevoked links, with creator and expiry; never return token/hash/full URL. |
| `DELETE /groups/{group_id}/invitations/{invitation_id}` | Revoke link; 204, including an already-revoked link still owned by this group. |
| `POST /invitations/preview` | `{token}` after verified authentication; return group name/currency and active member count for confirmation. No roster or financial data. |
| `POST /invitations/accept` | `{token}`; return group and caller membership IDs, 200 for join/rejoin/already active. Revalidate link in transaction. |
| `GET /groups/{group_id}/transactions` | Cursor list merging non-deleted expenses and repayments; tagged `type`, display fields, version and dates. |
| `GET /groups/{group_id}/expenses/{expense_id}` | Complete editable expense and allocated shares. |
| `POST /groups/{group_id}/expenses` | Full expense input; return saved resource with shares/version, 201. |
| `PUT /groups/{group_id}/expenses/{expense_id}` | Full replacement financial input plus `expected_version`; return updated resource, 200. |
| `DELETE /groups/{group_id}/expenses/{expense_id}?expected_version=N` | Soft-delete matching version; return tombstone `{id,version,deleted_at}`, 200. |
| `GET /groups/{group_id}/repayments/{repayment_id}` | Complete editable repayment and payment metadata. |
| `POST /groups/{group_id}/repayments` | Sender, recipient, amount, date, method and nullable label; return resource/version, 201. |
| `PUT /groups/{group_id}/repayments/{repayment_id}` | Amount/date/method/label plus `expected_version`; sender/recipient remain fixed. Return updated resource, 200. |
| `DELETE /groups/{group_id}/repayments/{repayment_id}?expected_version=N` | Soft-delete matching version; return tombstone, 200. |
| `GET /groups/{group_id}/balances` | Positive direct debts as `{debtor_membership_id,creditor_membership_id,amount_minor}` plus caller owed/receivable totals and currency. No debt simplification. |

Process liveness remains `GET /health` outside the business API. No working charts, personal tracking, activity/history browsing, restore-entry, account deletion, group deletion, or provider-linking endpoints.

## Resource and read conventions

- Group responses: `id,name,currency_code,timezone,currency_locked,active_member_count,my_membership_id,i_owe_minor,i_am_owed_minor,created_at,updated_at`.
- Account responses: `id,display_name,email,email_verified,can_reset_password,created_at,updated_at`; derive auth fields from trusted Supabase information, not profile storage.
- Expense resources include ID, group ID, currency, full submitted financial fields, final shares, version, actor IDs and timestamps. Share objects contain membership ID, allocated amount, and percentage basis points (null outside percentage method).
- Repayment resources include ID, group ID, currency, parties, amount/date/payment metadata, version, actor IDs and timestamps.
- Expense transaction rows include name, payer membership/display name, total, `icon_key` from a fixed keyword mapping with `generic` fallback, and `my_position` (`lent`, `borrowed`, `neutral`) with nonnegative `my_amount_minor`. Position is amount paid by caller minus caller's allocated share, independent of subsequent repayments.
- Repayment transaction rows include both parties/display names, amount, method and label. Repayments never increase spending.
- Group-list summaries and balances return separate owed/receivable totals; never combine currencies. Balances include only nonzero pairwise debts.
- Financial detail reads hide soft-deleted entries with 404. Tombstones appear only as successful delete responses and retained history; restoration is deferred.
- All paginated lists accept `limit` (default 30, maximum 100) and an opaque `cursor`. Reject invalid cursors or using one for a different resource/filter.
- Transactions order descending by transaction date, creation timestamp, type and UUID. Type gives a deterministic cross-table tie-breaker. Groups use descending creation timestamp/UUID; members ascending first-joined timestamp/UUID; invitations descending creation timestamp/UUID.
- Pagination describes current data, not a frozen snapshot. Backdated inserts, date edits and deletions can affect traversal; restart from the first page on refresh. No exact total count required.
- Group detail/summary and balance data within one response must use one consistent database read snapshot. Separate HTTP reads may see newer writes. After a successful mutation, invalidate/refetch group lists, details, transactions and balances.

## Mutation safety

- Require UUID `Idempotency-Key` on expense and repayment creation, replacement and deletion. Scope uniqueness by authenticated actor/key; fingerprint operation, target and canonical validated payload, including expected version where applicable.
- Same key/data returns original status/body after current-access checks, even if the entry was subsequently edited/deleted. Check replay before stale-version/deleted-entry validation. Changed target/operation/data yields 409.
- Failed operations roll back their reservation; retain successful keys for the MVP lifetime. Concurrent identical submissions replay the committed result. A different key creates a new attempt subject to ordinary rules.
- Other mutations use ordinary validation/state semantics; retry keys are not promised. A lost response to group/link creation may require refreshing the list, and retrying can create a second resource. Profiles bootstrap and invitation acceptance are explicitly idempotent.
- Financial versions start at 1; every correction/deletion increments. A stale expected version yields 409 with `current_version`, never overwrites data. New key against an already-deleted entry yields 404.
- Name/profile updates apply only submitted fields; concurrent edits to the same field use last committed write. Financial entries retain stricter version checks.
- Apply access checks, group locking, debt/participant validation, entry/shares/history writes, version changes and retry-result persistence atomically. Commit before success.
- Preserve the approved repayment-correction, departed-member and backdating policies. Financial dates are checked against the group's current local date at save time.
- Bearer invitation tokens go in POST bodies after the app extracts them from the share URL. Redact bodies/headers containing tokens in logs. Never expose hashes or store raw invitation secrets in list responses.

## Errors

Use one shape for application and request-validation errors:

```json
{"error":{"code":"version_conflict","message":"This entry changed. Reload before saving.","fields":[],"details":{"current_version":3}},"request_id":"request-correlation-id"}
```

| HTTP status | Codes / behavior |
| --- | --- |
| 401 | `authentication_required`, `invalid_token`, `token_expired`. |
| 403 | `email_verification_required`. |
| 404 | `not_found` for absent resources or groups the caller cannot access; do not reveal another group's existence. |
| 409 | `version_conflict`, `idempotency_conflict`, `currency_locked`, `outstanding_debt`, `repayment_exceeds_debt`, `no_debt_in_direction`, `departed_member_balance`. |
| 422 | `validation_error` with field paths/messages for invalid inputs, totals, duplicate participants, unsupported currency/timezone, future dates, missing headers, or invalid pagination. |
| 410 | `invitation_unavailable` for invalid, expired, revoked or inactive-group invitation tokens; no distinction that discloses group data. |
| 429 | `rate_limited` with `Retry-After` when throttled. |
| 503 | `temporarily_unavailable` for temporary dependency/lock availability failures; caller may retry financial submission with same key. |
| 500 | `internal_error`; no database messages, tokens or stack traces exposed. |

## Examples

Illustrative UUIDs below stand for members already returned by the group roster.

Create INR 10.00 expense paid by A, divided equally between A and B:

```http
POST /api/v1/groups/{group_id}/expenses
Authorization: Bearer <access-token>
Idempotency-Key: 10000000-0000-4000-8000-000000000001
Content-Type: application/json
```

```json
{
  "name":"Tea",
  "amount_minor":"1000",
  "transaction_date":"2026-11-17",
  "payer_membership_id":"20000000-0000-4000-8000-000000000001",
  "split_method":"equal",
  "participants":[
    {"membership_id":"20000000-0000-4000-8000-000000000001"},
    {"membership_id":"20000000-0000-4000-8000-000000000002"}
  ]
}
```

201 returns the full saved expense, including `version:1` and two shares of `"500"`. B owes A `"500"`; A's row says lent `"500"`, B's says borrowed `"500"`. The same key/body returns that original 201 result without adding debt.

For exact splits, each participant instead includes `amount_minor`, summing to the total. For percentage splits, each includes integer `percentage_basis_points`, summing to 10000. Reject fields belonging to another split method.

Record B repaying INR 3.00 to A using a new idempotency key:

```json
{
  "sender_membership_id":"20000000-0000-4000-8000-000000000002",
  "recipient_membership_id":"20000000-0000-4000-8000-000000000001",
  "amount_minor":"300",
  "transaction_date":"2026-11-17",
  "payment_method":"other",
  "payment_method_label":"GPay"
}
```

201 returns the saved repayment/version. B now owes A `"200"`. Group totals change, while the original expense row still shows its own `"500"` position.

Replace Tea with total `"400"`, same participants and `expected_version:1`, using another key. The server returns version 2 and `"200"` shares: after the existing `"300"` repayment, A owes B `"100"`. This is valid for active members. If either departed, reject the correction because it creates a nonzero balance involving that member. A later update still expecting version 1 returns 409.

## Acceptance coverage

- Verified users bootstrap profiles, create groups, share/preview/accept invitations, read groups and current/historical memberships, and depart only when every direct balance is zero.
- An unverified user can bootstrap/read/edit their profile but cannot perform group actions. Removed users cannot read group resources or replay financial results.
- All three split methods return deterministic shares and correct current-user positions, including rounding, zero shares and a payer outside the participants.
- Full/partial repayments update direct balances without spending; invalid direction, excessive amounts and departed-member violations fail atomically.
- Edits/deletions retain complete history and enforce expected versions. Currency remains locked after deletion of the first entry.
- Concurrent same-key submissions create one financial result. Changed payloads conflict; different keys undergo normal validation.
- Paging merges both entry types deterministically, omits deleted entries, and refresh restarts traversal after changes.
- Names and currency edits follow approved permissions/locks; member responses never disclose authentication emails.

The API-contract decision is resolved. Test implementation and deployment choices belong to their separate tickets. Validate the eventual implementation against this contract; document concrete gaps rather than silently changing agreed behavior.
