# Backend

Run commands from this directory. Python 3.11–3.13 and [uv](https://docs.astral.sh/uv/)
are required. Exact dependency versions are recorded in [uv.lock](uv.lock).

```powershell
uv sync --locked
Copy-Item .env.example .env
# Edit .env: choose local passwords and the runtime/migration URLs.
docker compose up -d postgres
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

`GET http://127.0.0.1:8000/health` returns `200 {"status":"ok"}` and
`X-Request-ID`. Health checks process liveness, without querying PostgreSQL.
OpenAPI is at `/openapi.json`; interactive documentation is at `/docs`.
Use HTTPS at the deployed proxy. Bind locally during development.

The local development container creates the migration owner, not the runtime role.
Provision `spendwise_runtime` separately as LOGIN/NOSUPERUSER/NOCREATEDB/NOCREATEROLE/
NOBYPASSRLS with no membership in the owner role. Provision `anon` and `authenticated`
if using plain PostgreSQL (Supabase already owns them). The migration owner needs
CREATE on the database and USAGE/REFERENCES on the existing `auth.users(id)`.
Only the disposable test fixture creates a minimal local auth table; do not run
that fixture or create managed auth internals on Supabase.

Apply migrations explicitly with the migration URL in the environment:

```powershell
# Set SPENDWISE_MIGRATION_DATABASE_URL securely; Alembic does not load .env.
uv run --locked alembic upgrade head
```

The version table and application tables live in the private `app` schema.
Runtime receives only DML needed by the API and SELECT/INSERT on immutable history
and retry results. Client roles receive no schema/table/function grants. The
migration owner must own the application schema; runtime must never own it.
Do not give the migration-owner URL to the API or infer database readiness from health.
No business routes are available yet.
Hosted URLs use the provider's actual host/port, SSL requirements and restricted
runtime credentials; never run this local container initialization against Supabase.
Adjust pool size to the host's connection budget.

Missing/invalid configuration fails startup with a secret-free message. Requests
log only correlation ID, response status and elapsed milliseconds. Disable Uvicorn
access logs as above: they otherwise record paths and query strings. UUID request
IDs are propagated; invalid IDs are replaced. Bodies, auth headers, invitation
tokens, URLs and raw exceptions are excluded. Correlate failures with `X-Request-ID`.

Use synchronous route functions and the one shared transaction session:

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_session

# Parameter on a synchronous route:
# session: Annotated[Session, Depends(get_session, scope="function")]
```

Function-scope dependency teardown commits before the response is sent. Exceptions,
including commit failure, roll back and close the session. Services share that
session and never commit, roll back or close it. No post-success background writes.
The engine is created once per application process and disposed at shutdown.

Pytest is the single runner for the approved six API/PostgreSQL scenario groups:

```powershell
uv run --locked pytest
uv run --locked mypy app
uv run --locked ruff check app
```

Start the designated disposable PostgreSQL database first (Docker Desktop required):

```powershell
./scripts/start-test-database.ps1
uv run --locked pytest
```

The script generates ignored `.env.test` credentials once and starts a PostgreSQL
17.7 container pinned by digest at loopback port 55432. Each suite run rebuilds
only the `app` schema in local `spendwise_test`, migrates from empty as the
non-superuser owner, and connects the API/journeys as the restricted runtime role.
Privileged fixture connections alone seed local auth identities, inspect/inject
faults and clean tables between scenarios. Tests refuse remote hosts or a different
database name and fail rather than skip if configuration/PostgreSQL is unavailable.
Do not run concurrent suite processes against this one disposable database.

To reset the entire designated test container, use
`docker compose --env-file .env.test -f compose.test.yaml down`, then run the startup
script again. No named data volume is configured for tests; removing that container
discards its data. Keep `.env.test` to reuse its credentials. This does not reset
development Compose or hosted data. Downgrade is intentionally unsupported; rebuild
designated disposable resources or deploy compatible code instead.

Later tickets add behavior cases at the same API/PostgreSQL seam. Ticket 01 uses
a startup/HTTP demonstration, not another test suite. Never substitute SQLite.

See [foundation evidence](../docs/testing/01-foundation-evidence.md) for actual
verification and the inventory of absent historical artifacts.
