# Choose requirements for the deployed test environment

Type: grilling
Labels: wayfinder:grilling
Status: resolved
Assignee: current user (with Codex)
Parent: ../map.md
Blocked by: none

## Question

What budget, hosting constraints, Supabase project availability, test-data isolation, HTTPS/API access, configuration, logs, migration process, and recovery expectations should the MVP test environment satisfy? Decide requirements first; create provider research tickets only if those requirements need external facts to choose an option.

## Answer

Resolved with the user on 2026-11-17: target free hosting, accept sleeping services/slower startup, use resettable disposable test accounts/data, and create a new Supabase project during implementation. Ask before choosing paid services or enabling charges.

The [environment requirements](../../../docs/planning/test-environment.md) record the required HTTPS access, secret/runtime-role separation, auth configuration, explicit migrations, logs and disposable-environment recovery. Exact hosting provider selection and provisioning are implementation steps constrained by these requirements; no provider/free-tier claims are made by this decision.

No accounts, services, migrations or paid resources were created. Build-order finalization is now unblocked.
