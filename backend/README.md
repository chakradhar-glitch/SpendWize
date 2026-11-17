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

The local container creates the migration owner, not the runtime role. Ticket 02
adds explicit migrations, restricted-role provisioning and their verification.
Until then, do not use owner credentials in the running API or assume database
readiness from health. No business routes or migration commands are available yet.
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

Ticket 02 supplies the migrated database harness; later tickets add behavior cases
at that seam. Ticket 01 uses a startup/HTTP demonstration, not another test suite.
Never replace the real database with SQLite or skip unavailable database checks.

See [foundation evidence](../docs/testing/01-foundation-evidence.md) for actual
verification and the inventory of absent historical artifacts.
