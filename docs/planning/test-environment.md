# MVP test-environment requirements

Status: agreed requirements, 2026-11-17.

## User decisions

- Target free hosting initially. Sleeping services and slower startup are acceptable for early testing. Ask before choosing a paid option or enabling charges.
- Use disposable accounts and data, isolated from future production. The test environment may be reset; it is not a durable store for real user financial records.
- A SpendWise Supabase project does not exist yet and must be created during implementation. Supabase provides authentication and PostgreSQL; FastAPI needs its own hosting environment.
- Build the backend first in the agreed [milestone sequence](backend-build-order.md); detailed mobile screens follow afterward.

## Required deployment properties

- A reachable HTTPS API base URL usable by the later mobile client. A provider-generated domain is sufficient; no custom domain required.
- Runtime secrets supplied through host configuration; document variable names in a secret-free template. Only publishable Supabase configuration reaches the client. Keep migration-owner credentials separate from the restricted runtime database role.
- Configure Supabase email/password, verification/reset and Google authentication, with explicit test callback URLs. The later mobile phase adds its actual deep-link callbacks. A minimal SDK harness can verify real authentication before screens exist.
- Apply application migrations explicitly with migration credentials before deploying code that depends on them. Never create or alter managed Supabase auth internals. Validate clean migration and runtime grants against the verification plan.
- Provide process health checks and request-ID-based logs with token/secret redaction. Errors must not expose database internals. Document startup/sleep limitations and how to diagnose a failed deployment.
- Record the deployed code revision, migration revision, setup steps and test-data seeding/reset instructions. Reset only the explicitly designated test resources; recreate disposable test data using documented steps.
- Recovery for this disposable environment means redeploying a known compatible application revision or rebuilding the test environment from migrations and seed data. Do not promise production backup/PITR guarantees or assume rolling code backward reverses a database migration. Reassess durable backups before using real data.
- Run the agreed automated suite and one deployed smoke walkthrough before declaring the backend handoff ready.

## Implementation-time selection and setup

The exact FastAPI host, region and service configuration are implementation choices within these requirements, not selected providers in this plan. Verify current free-tier availability, payment requirements, Python/container support, HTTPS, outbound Supabase connectivity, connection limits and sleep behavior before choosing. Do not assume any vendor's free tier will remain available.

Create the Supabase project and record its non-secret connection details during setup; do not put passwords or secret keys into planning tickets. Match runtime database connection/pooling settings to the actual project and chosen host. If free options cannot meet the agreed requirements, return with the specific trade-off and cost before proceeding.

These requirements settle the planning ticket; provider research/provisioning and actual smoke evidence are explicit implementation steps. No hosting account, paid service, live migration or deployed environment was created by this decision.
