# Agree the backend build order and frontend handoff

Type: grilling
Labels: wayfinder:grilling
Status: resolved
Assignee: current user (with Codex)
Parent: ../map.md
Blocked by: 02, 03, 04

## Question

Given the agreed contracts, verification criteria, and test-environment decisions, what implementation milestones and dependency order lead from the current repository to the backend-ready handoff? Inspect actual files before assuming scaffold or migrations exist. Define what each milestone demonstrates and what the frontend receives; keep detailed screen design for its later phase.

## Comments

User requested both remaining decisions in the same session. Build order can be drafted provisionally from resolved contracts and verification; final resolution still waits for the environment decision. Current checkout contains design documents and an effectively empty backend directory, not an implemented scaffold or migration. Treat earlier mentions of implemented artifacts as historical, not current checkout facts.

Draft: [Backend build sequence](../../../docs/planning/backend-build-order.md).

## Answer

Resolved 2026-11-17. The user explicitly requested both remaining decisions together and approved the sequence: foundation, persistence, authentication/profiles, groups/joining, financial core, completed reads, deployed handoff. Environment requirements were resolved first; this resolution follows that dependency.

The [agreed build sequence](../../../docs/planning/backend-build-order.md) holds milestone boundaries, demonstrations, dependencies and frontend handoff requirements. Follow the lean verification plan during implementation; do not write tests during planning. Create the missing Supabase project and choose free-compatible API hosting as implementation setup under the agreed environment requirements.

The current checkout has design artifacts but no application source or migrations. Implementation begins from the approved model and architecture rather than assuming a prior scaffold exists. Screens and React Native/Expo/TypeScript frontend work follow backend readiness.

Next handoff: generate implementation-sized work tickets from these milestones. All five wayfinder decision tickets are resolved; application and test implementation have not started in this effort.
