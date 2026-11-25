# SpendWise documentation

All project design documentation belongs under `docs/`, including exploration drafts, the glossary, and architecture decisions. Keep related documents in subfolders and update this index when adding documents.

## Product and architecture

- [Backend implementation tickets](planning/backend-implementation-tickets.md): approved 12-ticket breakdown, blocking dependencies, verification ownership and local tracker links.
- [Backend MVP implementation specification](planning/backend-mvp-spec.md): ready-for-agent scope synthesized from the completed planning map, preserving lean verification and deferring frontend screens; local Markdown tracker entry.
- [Backend build sequence](planning/backend-build-order.md): agreed milestones and frontend handoff.
- [Test-environment requirements](planning/test-environment.md): free-hosting target, disposable data, Supabase setup, deployment and recovery requirements.

- [Lean backend verification plan](testing/backend-readiness.md): agreed minimal scenario groups and backend-ready pass criteria; tests follow during implementation.

- [MVP API contract](api/mvp-contract.md): agreed endpoints, data formats, examples, errors, and mutation safety; implementation pending.

- [Backend-first MVP planning map](../.scratch/backend-first-mvp/map.md): completed decisions and dependencies informing implementation.
- Planning direction confirmed 2026-11-17: backend first; React Native with Expo and TypeScript for Android/iOS afterward. Detailed screen design is deferred to the frontend phase. Backend readiness includes tested APIs, request/response examples, and a deployed test environment.

- [MVP user journeys](mvp_user_journeys.md): agreed product scope and journeys.
- [FastAPI backend structure](fastapi_backend_structure.md): proposed backend layout and transaction ownership.
- [Glossary](GLOSSARY.md): agreed domain vocabulary.

## Database design

- [Interactive database design](database/design.html): primary review document, with clickable relationships, table/column details, financial scenarios, confirmed decisions, and remaining questions. Opens locally without a server.
- [Database design exploration notes](database/design.md): historical interview record and supporting explanations. The user approved the current database design on 2026-11-17; earlier draft/proposal wording is historical. Revisit the model only for concrete gaps found during backend planning. Approval does not mean a live migration has been applied.

## Architecture decisions

- [0001: Use Supabase Auth](adr/0001-use-supabase-auth.md).
