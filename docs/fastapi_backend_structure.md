# FastAPI Backend Structure — Personal Finance & Expense Splitting (V1)

**Architecture:** Modular monolith, feature-based modules, service-layer orchestration (no separate domain layer yet).

backend/
├── app/
│   ├── __init__.py                  # Package marker; no app initialization side effects
│   ├── main.py                      # ASGI entry point: app = create_app()
│   ├── factory.py                   # Construct FastAPI app; register routers, middleware, handlers, lifespan
│   │
│   ├── core/                        # Shared application infrastructure/configuration
│   │   ├── config.py                # Typed environment configuration
│   │   ├── logging.py               # Central logging setup (structured logs, redaction)
│   │   ├── security.py              # JWT verification and current-user dependency
│   │   ├── exceptions.py            # Shared application exceptions
│   │   ├── error_handlers.py        # Map application exceptions to HTTP responses
│   │   ├── database/                # Shared database infrastructure
│   │   │   ├── __init__.py           # Export database dependencies/helpers
│   │   │   ├── base.py               # SQLAlchemy DeclarativeBase and model metadata
│   │   │   ├── engine.py             # Engine creation and connection pooling
│   │   │   └── session.py            # Session factory + transactional context manager + FastAPI dependency
│   │   └── middleware/              # Request ID, access logging, CORS configuration
│   │       ├── request_id.py         # Assign/propagate request correlation IDs
│   │       └── access_log.py         # Request timing/access log middleware
│   │
│   ├── modules/                     # Feature-owned APIs, rules, and persistence
│   │   ├── auth/                    # Auth endpoints and auth-related use cases
│   │   ├── users/                   # Profiles and preferences
│   │   ├── groups/                  # Group membership and invitations
│   │   ├── expenses/                # Expense creation/editing and split calculations
│   │   │   ├── __init__.py           # Package marker
│   │   │   ├── router.py             # Expense endpoints; acquire/inject session; call service
│   │   │   ├── schemas.py            # Expense request/response Pydantic models
│   │   │   ├── models.py             # Expense and expense_split SQLAlchemy tables
│   │   │   ├── service.py            # Orchestrate validations, splits, persistence via other services
│   │   │   └── repository.py         # Expense-related SQL queries; no commit/rollback
│   │   ├── settlements/             # Repayments and balance queries derived from splits + repayments
│   │   ├── budgets/                 # Budget planning and limits
│   │   ├── analytics/               # Read-only spending reports and summaries
│   │   └── notifications/           # Notification rules, templates, post-commit dispatch
│   │
│   ├── infrastructure/              # Third-party adapters, not business rules
│   │   └── email/
│   │       └── provider.py           # Email API/SMTP integration
│   ├── workers/                     # Separately executed background jobs/queue consumers
│   │   └── notification_worker.py    # Deliver queued notifications and retry failures
│   └── shared/
│       └── money.py                 # Decimal, currency, rounding helpers
│
├── migrations/                      # Alembic revision files and configuration
├── tests/                           # Unit, service, repository, and API tests
├── Dockerfile                       # Backend image build
├── .dockerignore                    # Exclude secrets, caches, local files from build
├── compose.yaml                     # Local backend + PostgreSQL (+ worker if needed)
├── .env.example                     # Document required environment variables; no secrets
├── alembic.ini                      # Alembic CLI configuration
└── pyproject.toml                   # Dependencies and lint/test/tooling configuration
## Session ownership rule

- `core/database/engine.py` creates **one SQLAlchemy engine per process**, with configured connection pooling.
- `core/database/session.py` provides a `sessionmaker` and a `@contextmanager` transactional helper that **commits on success, rolls back on exception, and always closes** the session.
- Each router obtains **one session per request/use case** via a FastAPI `yield` dependency backed by that helper; it passes the same session to the service and all involved repositories/services.
- **Services and repositories never call `commit()`, `rollback()` or `close()`**. Avoid starting nested transactions independently.
- For a **synchronous SQLAlchemy session**, use synchronous (`def`) route handlers to avoid blocking the async event loop. If adopting `AsyncSession`, switch consistently to `async_sessionmaker` and `@asynccontextmanager`.
- Since a `yield` dependency commits during teardown, database commit may occur **after endpoint execution**. Don't send success-dependent email before commit; for reliable delivery, insert an **outbox event in the same transaction**, then let a worker send it after commit. For critical writes, prefer explicit transaction completion before returning a success response.

## Cross-module interaction rule

`ExpenseService.add_expense(session, data, current_user)` orchestrates the use case: call `GroupService` to validate membership, calculate and validate splits, and save expenses/shares through `ExpenseRepository` using the **same session**. `SettlementService` records repayments; balance queries derive amounts from expense shares and settlements. Cross-module interactions should normally use public service methods rather than another module's repository.

**No `domain.py` for V1.** Extract standalone domain objects/rules only if service logic becomes difficult to maintain or test.
