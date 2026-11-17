# Database table dictionary

Updated 2026-11-17. Implementation baseline; no live migrations applied.

Design dictionary corresponding to [schema.json](schema.json). The historical
`node scripts/render-schema.mjs` renderer is absent from this checkout.

Implement writes using the [MVP specification](../planning/backend-mvp-spec.md)
and [API contract](../api/mvp-contract.md). The previously referenced
`implementation.md` and `backend/migrations/0001_initial.sql` do not exist;
[ticket 02](../../.scratch/backend-mvp-implementation/issues/02-persistence-and-access-boundary.md)
owns the executable migration baseline. See the
[artifact inventory](../testing/01-foundation-evidence.md).

## auth.users

Supabase-owned authentication identity. Only the referenced primary key is shown; this is not a complete definition of the managed table.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | Supabase managed | PK |  | Stable authenticated user ID. |

Constraints and write rules:

- Read authentication state through supported Supabase APIs; do not manage passwords or refresh records in application tables.
- One auth user can have multiple provider identities and device sessions.

Indexes:

- Managed by Supabase.

## profiles

The SpendWise display identity shared across sessions, group memberships, and financial attribution.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | Verified token subject | PK FK | auth.users.id | One profile per auth user. |
| display_name | text | yes | Seed once; fallback Member |  |  | Proposed trimmed length: 1–100 characters. Later Google sign-ins never overwrite edits. |
| created_at | timestamptz | yes | now() |  |  | Creation instant. |
| updated_at | timestamptz | yes | now(); update on change |  |  | Last profile change. |

Constraints and write rules:

- FastAPI provisions missing profiles idempotently before group use.
- No password, email verification, or access/refresh token columns. Email remains authoritative in Supabase Auth.
- Proposed FK deletion policy: RESTRICT to preserve attribution. No direct client grants.

Indexes:

- PRIMARY KEY (id).

## groups

One shared-expense group with one currency, one date-validation timezone, and a permanent currency lock after financial activity.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| name | text | yes | — |  |  | Proposed trimmed length: 1–100 characters. |
| currency_code | text | yes | — |  |  | CHECK in INR, USD, CAD, GBP, EUR. |
| timezone | text | yes | Creator suggestion |  |  | Validate against supported IANA timezone names; immutable after creation. |
| currency_locked_at | timestamptz | no | NULL |  |  | Set on first financial entry, never cleared after deletion. |
| is_active | boolean | yes | true |  |  | Set false when final active member leaves. |
| created_by | uuid | yes | Current profile | FK | profiles.id | Creation attribution. |
| created_at | timestamptz | yes | now() |  |  |  |
| updated_at | timestamptz | yes | now(); update on change |  |  |  |

Constraints and write rules:

- Currency cannot change once currency_locked_at is non-null. Group timezone is fixed.
- Proposed: serialize financial and membership changes by locking the group row. Recheck actor access after acquiring the lock.
- Final departure requires all balances zero, inactivates the group and revokes invitations in one transaction.
- Group renaming is proposed; permanent group deletion is outside the MVP.

Indexes:

- PRIMARY KEY (id).
- No extra group-name index required for joined-group lists.

## group_memberships

Persistent identity of a profile in a group. The same membership row is reactivated after a valid invitation is accepted.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK UQ | groups.id | Group scope. |
| profile_id | uuid | yes | Current profile | FK UQ | profiles.id | The participating person. |
| is_active | boolean | yes | true |  |  | Current access flag; removal is not row deletion. |
| first_joined_at | timestamptz | yes | now() |  |  | Never reset on rejoin. |
| last_joined_at | timestamptz | yes | now() |  |  | Updated on rejoin. |
| departed_at | timestamptz | no | NULL |  |  | Non-null while inactive; departure details remain in membership_events. |

Constraints and write rules:

- UNIQUE (group_id, profile_id) prevents duplicate memberships.
- UNIQUE (group_id, id) supports same-group composite foreign keys from financial tables.
- CHECK active implies departed_at is NULL; inactive implies it is non-null.
- Leaving or removal requires every direct balance involving this member to be zero.
- Never physically delete memberships; departure removes group access.

Indexes:

- UNIQUE (group_id, profile_id).
- UNIQUE (group_id, id).
- Partial index (profile_id, group_id) WHERE is_active for joined-group lists.

## group_invitations

Reusable bearer invitation with expiry, creator attribution, hashed secret, and revocation state.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Invitation target. |
| token_hash | bytea | yes | SHA-256 of random token | UQ |  | Store only the digest of a cryptographically random high-entropy token. |
| created_by | uuid | yes | Current profile | FK | profiles.id | Revoke this creator’s links on departure. |
| created_at | timestamptz | yes | now() |  |  |  |
| expires_at | timestamptz | yes | created_at + 7 days |  |  |  |
| revoked_at | timestamptz | no | NULL |  |  |  |
| revoked_by | uuid | no | NULL | FK | profiles.id | Explicit or automatic revocation actor. |

Constraints and write rules:

- CHECK expires_at > created_at; creation service fixes duration at seven days.
- Reject expiry, revocation, inactive group, or unverified acceptance. Revalidate under the group lock.
- Multiple links can coexist. Repeated acceptance while active returns existing membership.
- Full token is returned once; a replacement link can be created if it is no longer available.

Indexes:

- UNIQUE (group_id, id) for same-group membership-event references.
- UNIQUE (token_hash) for token lookup.
- Partial index (group_id, created_by) WHERE revoked_at IS NULL for revocation.

## membership_events

Append-only join, leave, and removal history, including rejoining and the invitation accepted.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Enforces group scope. |
| membership_id | uuid | yes | — | FK | group_memberships.id | Composite FK (group_id, membership_id). |
| event_type | text | yes | — |  |  | CHECK in joined, left, removed. A later joined event records rejoining. |
| actor_id | uuid | yes | Current profile | FK | profiles.id | The joining/leaving user or remover. |
| invitation_id | uuid | no | NULL | FK | group_invitations.id | Null for creator’s initial join; otherwise the accepted invite on joining. |
| occurred_at | timestamptz | yes | now() |  |  |  |

Constraints and write rules:

- Append-only; never edit or delete past events.
- Membership state and event are written in the same transaction.
- When invitation_id is present, validate that it belongs to the same group; proposed composite FK requires UNIQUE (group_id, id) on invitations.

Indexes:

- Index (membership_id, occurred_at, id).
- UNIQUE (group_id, id) on invitations for same-group references.

## expenses

One shared expense, one payer, editable transaction date, split method, and versioned soft deletion.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Group and currency scope. |
| payer_membership_id | uuid | yes | — | FK | group_memberships.id | Composite FK (group_id, payer_membership_id); payer need not be a participant. |
| name | text | yes | — |  |  | Proposed trimmed length: 1–200 characters; icons derived from name. |
| amount_minor | bigint | yes | — |  |  | Positive whole minor units; no floating point. CHECK <= 99999999999. |
| transaction_date | date | yes | — |  |  | Editable; no future date in group timezone. |
| split_method | text | yes | — |  |  | CHECK in equal, exact, percentage. |
| version | integer | yes | 1 |  |  | CHECK > 0; increment for every correction or deletion. |
| created_by | uuid | yes | Current profile | FK | profiles.id | Creation actor. |
| updated_by | uuid | yes | Current profile | FK | profiles.id | Latest correction actor. |
| created_at | timestamptz | yes | now() |  |  |  |
| updated_at | timestamptz | yes | now(); update on change |  |  |  |
| deleted_at | timestamptz | no | NULL |  |  | Soft-deleted entries are excluded from balances and normal lists. |

Constraints and write rules:

- UNIQUE (group_id, id) enables same-group child references.
- Validate active payer/participants for new entries. Departed-member edit policy is still under review.
- Sum of current shares must equal amount_minor. Percentages must sum to 10000 basis points for percentage splits.
- Proposed: deferred database constraint triggers validate cross-row share totals and split inputs at commit.
- Entry, shares, history, version increment, and permanent currency lock change atomically.
- CHECK date against today is service validation, not a time-dependent table CHECK.

Indexes:

- UNIQUE (group_id, id).
- Partial (group_id, transaction_date DESC, created_at DESC, id DESC) WHERE deleted_at IS NULL.
- Index (group_id, payer_membership_id).

## expense_shares

Final allocated amount for each participant, plus original percentage input where applicable.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| expense_id | uuid | yes | — | PK FK | expenses.id | Composite FK (group_id, expense_id). |
| membership_id | uuid | yes | — | PK FK | group_memberships.id | Composite FK (group_id, membership_id); one share per participant. |
| group_id | uuid | yes | Parent expense group | FK | groups.id | Explicit same-group integrity. |
| amount_minor | bigint | yes | — |  |  | CHECK >= 0. Exact input is this amount; equal input is implicit. CHECK <= 99999999999. |
| percentage_basis_points | integer | no | NULL |  |  | 0–10000 for percentage splits, otherwise NULL. 3333 means 33.33%. |

Constraints and write rules:

- PRIMARY KEY (expense_id, membership_id).
- Payer’s own share is spending participation but creates no self-debt.
- Use integer/rational split calculation; largest fractional remainder wins leftover units, stable membership ID breaks ties.
- No independent share deletion or soft-delete flag: shares belong to an expense revision. Old versions live in immutable expense history.
- Cross-row and parent split-method consistency checked by proposed deferred constraint triggers.

Indexes:

- PRIMARY KEY (expense_id, membership_id).
- Index (group_id, membership_id, expense_id) for balance queries.

## repayments

A recorded external payment between two group members. It reduces direct debt and never counts as spending.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Repayment group. |
| sender_membership_id | uuid | yes | — | FK | group_memberships.id | Composite FK (group_id, sender_membership_id). |
| recipient_membership_id | uuid | yes | — | FK | group_memberships.id | Composite FK (group_id, recipient_membership_id). |
| amount_minor | bigint | yes | — |  |  | CHECK > 0. New repayment cannot exceed current direct debt. CHECK <= 99999999999. |
| transaction_date | date | yes | — |  |  | Editable and backdatable; no future date in group timezone. |
| payment_method | text | yes | cash |  |  | One method per repayment: cash or other. User requested payment_methods; singular column stores the selected value. |
| payment_method_label | text | no | NULL |  |  | NULL for cash; required trimmed 1–100 characters for other, e.g. GPay, PhonePe, CRED. |
| version | integer | yes | 1 |  |  | CHECK > 0; optimistic concurrency token. |
| created_by | uuid | yes | Current profile | FK | profiles.id | Any active member may record it. |
| updated_by | uuid | yes | Current profile | FK | profiles.id | Latest correction actor. |
| created_at | timestamptz | yes | now() |  |  |  |
| updated_at | timestamptz | yes | now(); update on change |  |  |  |
| deleted_at | timestamptz | no | NULL |  |  |  |

Constraints and write rules:

- CHECK sender_membership_id <> recipient_membership_id.
- UNIQUE (group_id, id) for same-group history references.
- For creation: both parties active; sender currently owes recipient; amount <= that debt. Check under group lock.
- Do not retroactively invalidate a historical repayment when an expense correction reverses balances.
- Repayment edit validation and party changes remain explicit open questions.
- CHECK payment_method in cash, other. Cash requires NULL label; other requires trimmed nonblank label up to 100 characters.
- Payment method and label are included in repayment revisions and canonical retry fingerprints.

Indexes:

- UNIQUE (group_id, id).
- Partial (group_id, transaction_date DESC, created_at DESC, id DESC) WHERE deleted_at IS NULL.
- Indexes (group_id, sender_membership_id) and (group_id, recipient_membership_id).

## expense_revisions

Immutable full before/after snapshots of expense creation, correction, and soft deletion, including all shares.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Group scope. |
| expense_id | uuid | yes | — | FK UQ | expenses.id | Composite FK (group_id, expense_id). |
| version | integer | yes | Entry version | UQ |  | UNIQUE (expense_id, version). |
| action | text | yes | — |  |  | CHECK in created, updated, deleted. |
| actor_id | uuid | yes | Current profile | FK | profiles.id | Immutable correction attribution. |
| occurred_at | timestamptz | yes | now() |  |  |  |
| before_values | jsonb | no | NULL on creation |  |  | Full prior entry and ordered shares; required for update/delete. |
| after_values | jsonb | yes | — |  |  | Full resulting entry and ordered shares, including deletion state. |

Constraints and write rules:

- Append-only. Proposed role grants allow INSERT/SELECT but no UPDATE/DELETE, backed by mutation-rejecting triggers.
- Creation has NULL before_values; update/delete has a complete object. Snapshots contain integer money and IDs.
- Snapshot creation is atomic with expense/share mutation. Never store tokens or credentials.
- Snapshots preserve values at revision time; current profile names may still change separately.

Indexes:

- UNIQUE (expense_id, version).
- Index (group_id, occurred_at, id).

## repayment_revisions

Immutable before/after snapshots of repayment creation, correction, and soft deletion.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | yes | gen_random_uuid() | PK |  |  |
| group_id | uuid | yes | — | FK | groups.id | Group scope. |
| repayment_id | uuid | yes | — | FK UQ | repayments.id | Composite FK (group_id, repayment_id). |
| version | integer | yes | Entry version | UQ |  | UNIQUE (repayment_id, version). |
| action | text | yes | — |  |  | CHECK in created, updated, deleted. |
| actor_id | uuid | yes | Current profile | FK | profiles.id | Immutable attribution. |
| occurred_at | timestamptz | yes | now() |  |  |  |
| before_values | jsonb | no | NULL on creation |  |  | Full prior repayment; required for update/delete. |
| after_values | jsonb | yes | — |  |  | Full resulting repayment, including deletion state. |

Constraints and write rules:

- Same append-only and atomic write policies as expense_revisions.
- Dedicated history tables keep real foreign keys to their parent records.
- Changing a transaction date is a normal audited correction, not a new repayment.

Indexes:

- UNIQUE (repayment_id, version).
- Index (group_id, occurred_at, id).

## idempotency_requests

Remembers one successful financial-create submission so a network retry returns the original result.

| Column | PostgreSQL type | Required | Default | Keys | Reference | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| actor_id | uuid | yes | Current profile | PK FK | profiles.id | The authenticated caller scopes each request key. |
| request_key | uuid | yes | Client generated once | PK |  | PRIMARY KEY (actor_id, request_key); reuse on retry. |
| group_id | uuid | yes | Target group | FK | groups.id | Recheck current authorization before replay. |
| operation | text | yes | — |  |  | CHECK in create_expense, create_repayment. |
| request_hash | bytea | yes | Canonical request digest |  |  | Includes operation, group, and normalized financial data. |
| response_status | smallint | yes | Successful response status |  |  | Recorded only with successful committed creation. |
| response_body | jsonb | yes | Creation response |  |  | Original response; no auth credentials. |
| created_at | timestamptz | yes | now() |  |  |  |

Constraints and write rules:

- Confirmed: same key + same operation/data returns original result; changed operation/data conflicts. Different key is a new command, never payload deduplication.
- Proposed: reserve key, lock group, validate, create entry/history, and record response in one transaction; failed attempts roll back.
- Concurrent duplicate submissions wait on uniqueness and replay the committed result.
- Proposed retention: retain successful keys for MVP lifetime; do not purge and silently turn late retries into new payments.
- Replay still requires current group access and verified authentication. A replay response describes the original operation, not the latest edited entry.

Indexes:

- PRIMARY KEY (actor_id, request_key).
- Index (group_id) for administration; no cleanup TTL proposed.
