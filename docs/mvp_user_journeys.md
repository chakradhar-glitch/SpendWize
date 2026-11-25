# SpendWise MVP User Journeys

## Purpose and scope

SpendWise's long-term goal is to bring group expense splits and personal spending together in one mobile app. The first MVP delivers group expense tracking and basic account management.

The app has four footer tabs: **Groups**, **You**, **Activity**, and **Account**. Groups and Account are functional in the MVP. You and Activity show a coming-soon state. Personal expense entry and aggregation are deferred.

This document captures the agreed journeys and product decisions for the next database design step. It does not define a database schema or implement the backend.

## User journeys

### 1. Create an account and sign in

- A user can register and sign in through Google or email/password.
- Email/password users must verify their email before creating or joining groups or performing group actions.
- Email/password users can reset their password through email.
- Signed-in users can sign out from Account.

### 2. Create a group and invite people

- A signed-in, verified user creates a group with a name and currency.
- Each group uses one currency. Mixed-currency expenses and currency conversion are outside the MVP.
- A member can share a group invitation link through another app.
- A recipient opens the link, signs in or registers, completes verification if required, and explicitly accepts the invitation.
- Accepting an invitation more than once must not create duplicate memberships.
- All active members have equal permissions to manage group membership and financial entries.

### 3. Browse groups and open a group

- The Groups tab lists the user's joined groups and their balance in each group.
- Balances remain separate by group and currency.
- Opening a group shows its name, active member count, and separate amounts the current user owes and gets back as quick information.
- Below the summary are **Settle up**, **Balances**, and **Charts** buttons.
- Settle up and Balances work in the MVP. Charts shows a coming-soon state.

### 4. Read group transactions

- Below the group actions, show expenses and recorded repayments sorted newest first by transaction date.
- An expense row shows its date, an icon selected automatically from its name, the expense name, and the current user's net **you lent** or **you borrowed** amount.
- A subtitle identifies who paid and how much they paid.
- Show a neutral state when the current user's net amount for an expense is zero.
- Repayment rows identify the sender, recipient, amount, and date, and are distinguishable from expenses.
- Keep a floating **Add expense** button available on the group screen.

### 5. Add a group expense

- A member taps Add expense and enters the expense name, total amount, date, payer, participating members, and split method.
- Each expense has one payer. Multiple payers are outside the MVP.
- The payer and participants are selected from active group members; the payer need not be one of the participants.
- Supported split methods are equal shares, exact amounts, and percentages.
- Shares must add up to the expense total. Percentage inputs must total 100%.
- Saving a valid expense adds it to the transaction list and updates the group's balances.

### 6. View balances and settle up

- Balances shows who owes whom within the group.
- Preserve direct debts from expenses and repayments; do not reroute debts between members to simplify payments.
- Settle up records a full or partial repayment made outside SpendWise.
- A recorded repayment updates balances immediately; recipient confirmation is not required.
- SpendWise does not transfer money in the MVP.
- Repayments reduce debts and do not count as spending.

### 7. Correct financial entries

- Any active member can edit or delete expenses and recorded repayments.
- Keep change history identifying the actor, timestamp, and previous values.
- Use soft deletion for removed financial entries so historical records remain available.
- Recalculate balances after corrections, including corrections made after a repayment.
- A dedicated Activity feed remains outside the MVP even though change history is retained.

### 8. Leave a group or remove a member

- Any active member can manage membership, including removing another member.
- A member can leave or be removed only when every direct debt involving that member is zero. A zero overall net balance alone is insufficient.
- Preserve the departed member's historical expenses, shares, repayments, and attribution.
- Departed members lose access to the group.

### 9. Manage an account

- Account displays the user's name and email.
- Users can edit their display name and access sign out and, for email/password accounts, password reset.
- Account deletion is outside the agreed MVP scope.

## Questions asked and answers

| Question | Answer |
| --- | --- |
| Should personal expense tracking be usable in this MVP? | Groups only; personal tracking and aggregation are deferred. |
| Which split and payer options should Add expense support? | One payer, with equal, exact-amount, and percentage splits. |
| How should people join a group? | Shareable invite links, followed by sign-in and explicit acceptance. |
| What should Settle up do? | Record a full or partial repayment made outside the app. |
| How should balances between members be presented? | Keep direct debts; no group debt simplification. |
| What currency rules should groups use? | One currency per group, with no conversion. |
| Who should manage group expenses and membership? | All members equally. |
| Should Charts work in the MVP? | Show coming soon. |
| What should Account include? | Basic account details, profile editing, sign out, and password reset. |
| How should edits, deletions, and repayment corrections work? | Keep change history, soft-delete removed entries, and recalculate balances. |
| When may a member leave or be removed? | Only when every direct debt involving that member is settled. |
| Must email/password users verify their email before group actions? | Yes. |

## Implementation defaults

These defaults were proposed in the planning handoff; they are separate from the explicit answers above.

- Treat Gmail login as Google sign-in.
- A group's currency becomes immutable after its first financial entry.
- Any active member can revoke invitation links.
- Calculate monetary values using the currency's minor units and allocate rounding remainders deterministically.
- Use keyword-based automatic expense icons with a generic fallback.
- Profile editing in the MVP covers the display name; changing the login email is not specified.

## Acceptance scenarios

- A user can register and sign in with either supported authentication method; unverified email/password users cannot perform group actions.
- Password reset and sign out work for the applicable account type.
- A user can create a group, share an invitation, and join through a valid invitation without duplicate membership.
- Group screens display the correct name, active member count, and amounts owed and receivable.
- Equal, exact-amount, and percentage splits produce valid shares, including rounding cases; invalid totals are rejected.
- Expense rows show the correct payer, amount, date, icon, and current-user lending or borrowing position.
- A full or partial repayment updates the correct direct balances without increasing spending totals.
- Any active member can correct an entry; change history survives edits and soft deletion, and balances reflect the correction.
- A member with outstanding direct debts cannot leave or be removed, even when their overall net balance is zero.
- A settled member can depart; their historical attribution remains and group access is removed.
- Groups with different currencies remain separate, and transaction lists appear newest first.
- You, Activity, and Charts show coming soon; Groups and Account are usable.

## Next step: database design

Use these journeys alongside [the FastAPI backend structure](fastapi_backend_structure.md) to design the PostgreSQL model.

Cover authentication identities, user profiles, groups, memberships, invitation links, expenses, expense shares, repayments, and change history. Define balance calculations, monetary constraints, historical references, indexes, and transaction boundaries during that design step.

The database design should also resolve remaining technical policies such as invitation expiry, supported currencies, repayment validation, stable transaction ordering, concurrent edits, and account identity linking before implementation.
