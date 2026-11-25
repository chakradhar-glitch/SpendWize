# Define the mobile-facing backend API contract

Type: grilling
Labels: wayfinder:grilling
Status: resolved
Assignee: current user (with Codex)
Parent: ../map.md
Blocked by: 01

## Question

What endpoints, requests, responses, validation errors, pagination and ordering conventions, idempotency and version-conflict behavior support every agreed MVP journey? Define representative examples and acceptance scenarios without requiring finished screens. Preserve Supabase-owned authentication and FastAPI-owned business access.

## Comments

2026-11-17: User approved refresh on opening/pull-to-refresh/after writes; no live updates required. Retain history but defer browsing endpoints/screens. Active members may rename groups and change currency before its permanent financial-entry lock; timezone remains fixed.

Draft asset: [MVP API contract](../../../docs/api/mvp-contract.md). Remaining review: monetary wire format, financial retry/version conventions, paging and response/error details. Ticket stays claimed until shared agreement on the contract.

## Answer

Resolved 2026-11-17 after the user confirmed all three review choices: money as strings of integer minor units; retry keys for all expense/repayment creates, edits and deletions with expected versions for edits/deletions; and expense-row positions reflecting that expense while group balances include repayments.

The [agreed API contract](../../../docs/api/mvp-contract.md) holds the endpoint inventory, input/output conventions, authorization, error shapes/codes, pagination, mutation behavior, representative examples and acceptance coverage. Its technical conventions are implementation defaults; the product and review choices above were explicitly confirmed. Earlier draft comments are historical.

The contract covers every agreed MVP journey while deferring live updates, history browsing, personal tracking, charts, account/group deletion and manual identity linking. Group rename and pre-lock currency edits are included; timezone remains fixed. Supabase owns authentication; FastAPI owns business operations.

The [verification decision](03-verification.md) is now unblocked. Provider configuration, production throttling values, deployment, and test implementation remain later work. No API code or live configuration was changed.
