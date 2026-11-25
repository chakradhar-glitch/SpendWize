# Database design exploration

Status: exploring; not approved for implementation. Updated 2026-11-10.

[Open the interactive database design](design.html) for the primary review experience: relationships, column definitions, flows, agreed rules, and open questions. This Markdown file retains the interview record and supporting explanations.

[Documentation index](../README.md) | [MVP journeys](../mvp_user_journeys.md) | [Glossary](../GLOSSARY.md) | [Backend structure](../fastapi_backend_structure.md)

## Scope and approach

Design the PostgreSQL tables, relationships, monetary rules, balance calculations, history, constraints, indexes, and transaction boundaries needed for the group-expense MVP. Personal expenses, budgets, working charts, a dedicated Activity feed, and money transfers are outside this design's MVP scope.

This document distinguishes confirmed decisions from proposals. SQL migrations and backend implementation wait until the interview reaches a shared understanding confirmed by the user.

## Confirmed decisions

The MVP journeys remain the source for previously agreed behavior. The database interview additionally confirmed:

| Area | Decision |
| --- | --- |
| Authentication | Supabase Auth, including Google sign-in. Email/password, verification, reset, and sign out remain in MVP scope. |
| Application access | Confirmed: the app authenticates directly with Supabase and sends its access token to FastAPI for all SpendWise application data operations. |
| Application profile | One four-column `profiles` row per auth user: UUID `id` referencing `auth.users(id)`, `display_name`, `created_at`, and `updated_at`. FastAPI creates a missing row idempotently on first authenticated application use; later logins do not overwrite edited names. |
| Money representation | Store integer minor units, with at most two decimal places in input for all five supported currencies. Expense totals and repayments must be positive; rounded individual shares may be zero. |
| Percentage inputs and rounding | Percentages allow two decimal places and must total exactly 100%. Allocate leftover minor units to the largest fractional remainders, breaking ties by stable membership ID. Retain original percentage inputs and final allocated amounts. |
| Direct balances | Offset mutual debts within the same pair and group. Never reroute through a third member. If Alice owes Bob 500 and Bob owes Alice 200, Alice owes Bob 300. |
| New repayments | Allow partial or full repayment of an existing direct debt; reject amounts above that debt and payments in the opposite direction. |
| Corrections after repayment | Corrected expenses and recorded repayments both contribute to the resulting balance. For active members, a correction may reverse the debt direction: if a 500 debt was repaid and the expense is corrected to 400, the original recipient owes 100 back. |
| Departed members | Reject edits or deletions that leave any departed member with a nonzero direct balance. Corrections preserving zero balances remain possible. |
| Rejoining | Allowed through a valid invitation link, including after removal. Retain the same membership identity, record participation periods separately, and restore access to group history. A removed member holding a valid invitation can rejoin. |
| Final departure | Once all direct balances are zero, the final active member can leave. The group becomes inactive and its invitations are invalidated; restoration is outside MVP scope. |
| Supported currencies | INR (Indian rupee), USD (US dollar), CAD (Canadian dollar), GBP (UK pound), and EUR (euro). One currency per group; no conversion. |
| Currency changes | Currency becomes permanently fixed after the first financial entry, including when that entry is subsequently soft-deleted. |
| Transaction dates | Calendar dates can be edited and backdated; future dates are rejected using the group's fixed timezone, initially suggested from the creator's device. Creation and modification timestamps are separate. Sort newest transaction date first, with creation time and unique identifier as deterministic tie-breakers. |
| Invitations | Reusable bearer links expire seven days after creation. Any active member can revoke them. Anyone holding a valid link can join after authentication, required verification, and explicit acceptance; no recipient allowlist or admin approval. Share only with trusted people. Repeated acceptance by an active member creates no duplicate membership. |
| Invitation lifecycle | Multiple links may coexist. Store hashes of secret tokens and return the full link at creation. Revoke links when their creator leaves or is removed; any active member can also revoke any link. |
| Concurrent edits | Version expenses and repayments. Reject a save based on an obsolete version and require reloading before another save. |
| Immutable history | Record financial creation, edits, and soft deletion with actor, timestamp, and complete before/after financial values including shares. Record membership joins, departures, and removals. A dedicated Activity screen remains outside MVP scope. |
| Retry handling | Confirmed: reuse the same request ID for retries of one submission. Same ID and operation/data returns the original result; same ID with different operation/data is rejected. A different ID is a new submission subject to normal validation, even when its payload matches an earlier request. |
| Documentation | All new design documentation, including this exploration and the glossary, lives under `docs/` with navigation. |

## Candidate tables, pending detailed design

Except for the confirmed profile shape below, these names and boundaries are proposals, not approved DDL.

| Table | Responsibility | Main relationships |
| --- | --- | --- |
| Supabase-managed `auth.users` and identities | Authentication identity and sign-in methods | Application profile references an auth user. |
| `profiles` | SpendWise display name and application attribution | One profile per authenticated user; referenced by membership and actors. |
| `groups` | Group name, currency, and permanent currency-lock state | Has memberships, invitations, expenses, and repayments. |
| `group_memberships` | User participation and current access | One persistent membership per group/profile; reused on rejoining. |
| Membership participation history (name pending) | Joining, leaving, and removal history | References the persistent membership; exact representation remains open. |
| `group_invitations` | Shareable invitation lifecycle | Belongs to a group; creator, expiry, and revocation attribution. Token storage design remains open. |
| `expenses` | One payer, name, amount, transaction date, and split method | Belongs to a group; references payer and financial-entry actors. |
| `expense_shares` | Each participant's allocated amount | Belongs to one expense and references a group member. Preserve split inputs as well as final amounts; representation remains open. |
| `repayments` | An external payment recorded between two members | Belongs to a group; references sender and recipient. |
| Financial change history (name pending) | Actor, time, and previous values for corrections | References the changed entry; snapshot structure and creation history remain open. |

Expenses and repayments must preserve historical attribution after membership departure. Financial deletion is soft deletion. Balances derive from non-deleted expenses, shares, and repayments; corrections update balances atomically. No persisted balance table has been approved.

## Decision tree and remaining questions

- Supabase Auth (confirmed)
  - Direct Supabase authentication and FastAPI-only application data access (confirmed).
  - Four-column profile keyed by auth user UUID and idempotent FastAPI provisioning (confirmed).
  - Google/email account linking and whether manual linking has an MVP interface remain open.
  - Membership authorization, verification enforcement, schema exposure, and database role privileges.
- Pairwise balance netting and repayment caps (confirmed)
  - Corrections may create reverse balances between active members (confirmed).
  - INR, USD, CAD, GBP, EUR, integer minor units, two-decimal percentage inputs, and deterministic largest-remainder allocation (confirmed); amount limits remain open.
  - Editable calendar dates, backdating, no future dates, deterministic ordering, and a fixed group timezone (confirmed).
  - Repayment correction validation without applying creation rules retroactively to every old repayment.
- Departed members retain history and cannot acquire debt through corrections (confirmed)
  - Rejoin through valid invitation using persistent membership (confirmed); participation-history representation remains open.
  - Final departure inactivates group and invalidates invitations (confirmed).
  - Editing old entries involving departed members and participant eligibility.
- Reusable, revocable, seven-day invitations (confirmed)
  - Multiple concurrent links, hashed secret tokens, and automatic revocation after issuer departure (confirmed).
- Schema and integrity design (pending)
  - Keys, foreign keys enforcing same-group references, uniqueness, checks, and indexes.
  - Version-based concurrent edit detection (confirmed); serialization of balance-affecting writes with departure remains to be specified.
  - Request-ID retry semantics (confirmed); storage scope, retention, and representation remain schema proposals.
  - Immutable complete before/after financial history and membership events (confirmed); representation and atomic entry/share/history writes remain to be specified.
  - Table ownership, migrations, and transaction completion before successful responses.

## Retry handling (confirmed semantics)

A request ID identifies one intentional submission, not one set of financial values. The client generates it once and reuses it for all retries of that submission.

| Submission | Confirmed behavior |
| --- | --- |
| First request with key `requestid3` and a valid repayment | Create the repayment and remember its result atomically. |
| Retry using `requestid3` with the same operation and financial data | Return the original result; create no additional repayment. |
| Reuse `requestid3` with different operation or financial data | Reject key reuse as a conflict. |
| Submit a different key with identical financial data | Treat as a new intentional repayment, applying normal membership, amount, and outstanding-debt validation. Do not deduplicate by matching payload. |

For example, when Alice owes Bob 500, two separate 100 repayments with different request IDs are both valid. Retrying either repayment with its original request ID must not create another payment. If Alice instead fully repays 500, another 500 repayment with a different key is rejected because no debt remains, not because the payload matches an earlier request.

The final schema proposal will specify key scope, payload fingerprinting, concurrency handling, and storage lifetime; these details are not yet approved.

## Remaining interview and final deliverable

Retry semantics are confirmed. Two review sections remain, now collected in the interactive document rather than a continuing sequence of Markdown-only questions:

1. Final behavior edge cases: repayment corrections, historical entries involving departed members, and financial date interpretation. Consolidate closely related cases rather than reopening confirmed decisions.
2. Concrete schema review: present the table/column model and recommended technical choices for keys, constraints, history, transactions, indexes, and access boundaries. Ask for decisions only where real trade-offs remain, then request confirmation of the shared design.

The finished database design will include every application table and column with PostgreSQL types, nullability, defaults, primary/foreign keys, uniqueness and check constraints, indexes, and relationships/ER diagram. It will distinguish Supabase-managed auth tables from application-owned tables, define balance formulas and transaction boundaries, and map the agreed journeys and edge cases to the model. A schema SQL artifact may accompany the document after final confirmation; exploration alone does not authorize executing migrations against a live database.

Operational choices that do not change the database model, such as exact mobile storage libraries and auth session timeout values, can be recorded as implementation follow-ups rather than extending the schema interview.

## Direct authentication and token flow

Confirmed flow: the mobile app signs in with Supabase Auth using email/password or Google. Supabase issues an access token (JWT) and refresh token. The app sends only the access token to FastAPI in the HTTPS `Authorization: Bearer` header; the Supabase SDK uses the refresh token to obtain replacement access tokens. FastAPI does not issue a second authentication token.

FastAPI validates token signature, expiry, expected issuer, and audience using a maintained verifier, then uses the verified subject as the user identity. It independently checks verification status and current membership permissions from trusted sources. A user-supplied profile ID or group ID is not proof of authorization, and group membership must not be treated as permanently true because of an old token.

The frontend uses a publishable project key, never a secret or service-role key. The proposed architecture prevents direct client access to business tables with schema exposure and database grants, or by disabling the Data API if unused. Authentication alone does not enforce this boundary.

Token storage is platform-specific and remains to be designed. Tokens are sensitive bearer credentials: keep them out of logs and URLs, use HTTPS, and choose protected native storage for the mobile app. Browser storage and server-held cookie sessions are separate deployment choices if a web app is added.

JWT verification can use cached signing keys, so it need not call Supabase on every request. Signature/expiry verification alone does not immediately detect a revoked session: an already issued access token can remain usable until expiration. Decide whether sensitive writes need a current server-side session/user check before implementation. Membership removal is separately enforced by current application membership checks.

### Session and token maintenance

Supabase owns authentication users, provider identities, and session/refresh state in its managed `auth` schema. Its `auth.sessions` records identify signed-in sessions; the client receives the access/refresh pair. SpendWise does not create application tables for token strings or write to Supabase's session internals.

The access token is short-lived proof of identity. The SDK renews it by exchanging the current refresh token for a replacement access/refresh pair and persisting the updated session through the configured storage adapter. Supabase manages refresh-token rotation and reuse rules; application code should not implement a second rotation mechanism. Native session storage and app foreground/background refresh handling must be configured for the chosen mobile SDK.

Refreshing a token does not create a user, profile, or membership. Signing in on another device creates another session for the same user, not another SpendWise profile. Signing out clears the selected client session and revokes refresh capability according to the chosen sign-out scope; already issued JWTs have the expiration limitation described above. Session lifetime and sign-out scope are not yet selected.

### Application profile maintenance

Confirmed: the four-column profile shape and idempotent FastAPI provisioning described below. Schema placement, exact name validation limits, and deletion constraints remain technical proposals pending final schema review.

Keep the profile in the same Supabase PostgreSQL database as application data, separate from Supabase's managed authentication schema. The application schema name is still open; `profiles` here is a logical table name, not permission to expose it through the Data API.

| Confirmed column | Type | Rule |
| --- | --- | --- |
| `id` | UUID | Primary key and foreign key to `auth.users(id)`; use the verified token subject, never a user ID supplied by the client. |
| `display_name` | Text | Application-owned name; validate length/content in the API. Seed once from available sign-up/provider metadata with a safe fallback. Exact limits remain open. |
| `created_at` | Timestamp with time zone | Set by the database on insertion. |
| `updated_at` | Timestamp with time zone | Maintained when the application profile changes. |

Do not duplicate password hashes, tokens, provider identities, or email verification state here. Authentication email remains authoritative in Supabase Auth; the Account response combines current trusted auth email with the SpendWise display name. Group-facing profile responses need not expose email.

Provision through an idempotent FastAPI bootstrap/current-profile operation after verified authentication. Insert a missing profile using the verified auth user ID, then read it back; uniqueness handles concurrent first requests. Run this before any application use case needs a profile reference, including group creation and invitation acceptance. A retry after network failure must not create a second profile or overwrite an existing display name. Email verification still gates group actions independently of profile existence.

Considered alternative: an auth-user insertion trigger can create the profile at signup, including before email verification. Supabase documents this pattern but notes a failing trigger can block signups. The chosen FastAPI bootstrap keeps profile provisioning retryable without adding this dependency to signup; a signed-up user can temporarily have no application profile until first app API use.

Profile updates go through FastAPI, authorize the current profile, and change `profiles.display_name` and `updated_at`. Later Google logins and token refreshes must not overwrite a user-edited display name. Read the profile table for current names rather than treating token metadata as a live profile record. Group memberships and financial actors reference this stable profile identity across sessions and rejoining.

Do not cascade auth-user deletion into profiles or financial history. Proposed foreign-key behavior is `ON DELETE RESTRICT`; account deletion remains outside the MVP. Supabase owns provider linking; the app keys references by auth user UUID, not email or a Google provider ID. A separate manual account-linking UI remains an open scope decision.

## Supabase reference notes

These are provider facts, not additional approved application policies:

- Supabase supports [Google sign-in](https://supabase.com/docs/guides/auth/social-sign-in/auth-google).
- Supabase recommends referencing the primary key of managed tables such as `auth.users`; its [user management guide](https://supabase.com/docs/guides/auth/managing-user-data) describes separate application profile data. Its example's cascading profile deletion is not adopted here: account deletion is outside MVP scope and financial attribution must survive.
- Supabase documents automatic linking for matching verified email addresses and a separate manual linking flow in its [identity linking guide](https://supabase.com/docs/guides/auth/auth-identity-linking). SpendWise's policy remains to be confirmed; application membership must not be keyed by email address.
- [API keys](https://supabase.com/docs/guides/getting-started/api-keys) distinguishes client publishable keys from privileged backend-only keys.
- [JWT verification](https://supabase.com/docs/guides/auth/jwts) and [Python verified claims](https://supabase.com/docs/reference/python/auth-getclaims) describe signature verification and signing-key caching.
- [Auth session details](https://supabase.com/docs/guides/auth/server-side/advanced-guide) describes access/refresh tokens, storage options, and the limitation of local verification after revocation.
- [Securing data](https://supabase.com/docs/guides/database/secure-data) describes Data API permissions and disabling the Data API for direct database connection architectures.
- [React Native authentication](https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native) describes configurable session storage, including encrypted storage backed by protected device keys.
- [User sessions](https://supabase.com/docs/guides/auth/sessions) describes managed sessions, access/refresh pairs, and refresh-token rotation.
