# Plan the backend-first SpendWise MVP

Labels: wayfinder:map
Status: resolved

## Destination

Agree a backend-first MVP build plan defining API contracts, remaining behavior and access rules, acceptance checks, deployment requirements, and implementation order. The backend handoff is tested APIs with request/response examples and a deployed test environment suitable for the later mobile client.

## Notes

- Planning only: implementation follows the agreed plan.
- User confirmed the destination and scope on 2026-11-17.
- Use the existing [MVP journeys](../../docs/mvp_user_journeys.md), [approved database model](../../docs/database/schema.md), [design interview](../../docs/database/design.md), [glossary](../../docs/GLOSSARY.md), and [backend structure](../../docs/fastapi_backend_structure.md) as the baseline.
- Database design is approved. Reopen only concrete gaps; do not repeat the schema interview. Some source documents retain historical proposal wording.
- Mobile frontend: React Native, Expo, TypeScript; Android/iOS. Detailed screen design follows backend work.
- Backend readiness means tested APIs, documented request/response examples, and a deployed test environment.
- Testing preference: as few tests as practical to cover agreed behavior; combine API/database journeys and use compact case tables rather than duplicate coverage across layers.
- Consult wayfinder, grilling, and domain-modeling for decision sessions.
- Local Markdown tracker: individual child files under issues/. Status is open, claimed, or resolved. Claim before working; append resolutions under Answer. Blocking uses ticket numbers. The frontier is open, unclaimed tickets whose blockers are all resolved, ordered by number.
- No tracker was configured; this follows the skill's local fallback. Run /setup-matt-pocock-skills if a different tracker is desired later.

## Decisions so far

- [Settle remaining backend behavior and access policies](issues/01-backend-behavior-and-access.md): approved design carried forward; current-device sign-out, token validity until expiry with current membership checks, and manual account-linking UI deferred.
- [Define the mobile-facing backend API contract](issues/02-api-contracts.md): API coverage and examples recorded; minor-unit strings, financial retry/version protection, and expense-specific transaction positions agreed.
- [Define evidence that the backend is ready](issues/03-verification.md): lean scenario-based verification and readiness gates agreed; test code follows during implementation.
- [Choose requirements for the deployed test environment](issues/04-test-environment.md): free-hosting target, disposable data and a new Supabase project during implementation; paid services require approval.
- [Agree the backend build order and frontend handoff](issues/05-build-order.md): seven milestones and frontend handoff agreed; next generate implementation work tickets.

## Not yet specified

None blocking the backend build plan. Exact provider selection/setup is assigned to implementation under the agreed requirements.

## Out of scope

- Implementation during this charting effort.
- Repeating approved database design without evidence of a gap.
- Detailed screens and frontend implementation.
- Hosting provisioning and current provider research, handled during implementation within the agreed environment requirements.
- Personal expense tracking, working Charts, Activity feed, budgets, notifications, money transfers, currency conversion, and public app-store release.
