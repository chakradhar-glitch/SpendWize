"""Privileged fixtures are restricted to the designated local disposable database."""

import os
from collections.abc import Iterator
from pathlib import Path
from uuid import UUID

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.test")


def test_url(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set {name}; see backend/README.md (no skipped DB tests).")
    parsed = make_url(value)
    if (
        parsed.host not in {"localhost", "127.0.0.1"}
        or parsed.database != "spendwise_test"
    ):
        raise RuntimeError("Fixtures may only reset local spendwise_test.")
    return value


def connect(url: str) -> psycopg.Connection:
    return psycopg.connect(url.replace("postgresql+psycopg://", "postgresql://"))


@pytest.fixture(scope="session")
def database() -> Iterator[Engine]:
    from alembic import command
    from alembic.config import Config

    admin_url = test_url("SPENDWISE_TEST_ADMIN_URL")
    migration_url = test_url("SPENDWISE_TEST_MIGRATION_URL")
    runtime_url = test_url("SPENDWISE_TEST_RUNTIME_URL")
    # Only the fixture connection creates the local stand-in for managed identities.
    with connect(admin_url) as admin:
        admin.execute("DROP SCHEMA IF EXISTS app CASCADE")
        admin.execute("CREATE SCHEMA IF NOT EXISTS auth")
        admin.execute("CREATE TABLE IF NOT EXISTS auth.users (id uuid PRIMARY KEY)")
        for url in (migration_url, runtime_url):
            parsed = make_url(url)
            role = parsed.username
            if role not in {"spendwise_owner", "spendwise_runtime"}:
                raise RuntimeError("Unexpected test role")
            if not admin.execute(
                "SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)
            ).fetchone():
                admin.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(role), sql.Literal(parsed.password)
                    )
                )
        for role in ("anon", "authenticated"):
            if not admin.execute(
                "SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)
            ).fetchone():
                admin.execute(
                    sql.SQL("CREATE ROLE {} NOLOGIN").format(sql.Identifier(role))
                )
        admin.execute("GRANT CREATE ON DATABASE spendwise_test TO spendwise_owner")
        admin.execute("GRANT USAGE ON SCHEMA auth TO spendwise_owner")
        admin.execute("GRANT REFERENCES ON auth.users TO spendwise_owner")
    os.environ["SPENDWISE_MIGRATION_DATABASE_URL"] = migration_url
    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    engine = create_engine(runtime_url, hide_parameters=True)
    yield engine
    engine.dispose()


@pytest.fixture
def runtime(database: Engine) -> Engine:
    with connect(test_url("SPENDWISE_TEST_ADMIN_URL")) as admin:
        tables = admin.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='app' "
            "AND tablename <> 'alembic_version'"
        ).fetchall()
        if tables:
            admin.execute(
                sql.SQL("TRUNCATE {} CASCADE").format(
                    sql.SQL(",").join(
                        sql.Identifier("app", row[0]) for row in tables
                    )
                )
            )
        admin.execute("DELETE FROM auth.users")
    return database


@pytest.fixture
def roster(runtime: Engine) -> dict[str, UUID]:
    ids = {
        name: UUID(int=index)
        for index, name in enumerate(
            ("A", "B", "C", "U", "X", "INR", "USD", "a", "b", "c", "x"), 1
        )
    }
    with connect(test_url("SPENDWISE_TEST_ADMIN_URL")) as admin:
        for name in ("A", "B", "C", "U", "X"):
            admin.execute("INSERT INTO auth.users(id) VALUES (%s)", (ids[name],))
    with runtime.begin() as connection:
        for name in ("A", "B", "C", "U", "X"):
            connection.execute(
                text(
                    "INSERT INTO app.profiles(id,display_name) VALUES (:id,:name)"
                ),
                {"id": ids[name], "name": name},
            )
        for currency in ("INR", "USD"):
            connection.execute(
                text(
                    "INSERT INTO app.groups"
                    "(id,name,currency_code,timezone,created_by) "
                    "VALUES (:id,:name,:name,'Asia/Kolkata',:actor)"
                ),
                {"id": ids[currency], "name": currency, "actor": ids["A"]},
            )
        for member, profile, group in (
            ("a", "A", "INR"),
            ("b", "B", "INR"),
            ("c", "C", "INR"),
            ("x", "X", "USD"),
        ):
            connection.execute(
                text(
                    "INSERT INTO app.group_memberships(id,profile_id,group_id) "
                    "VALUES (:id,:profile,:group)"
                ),
                {"id": ids[member], "profile": ids[profile], "group": ids[group]},
            )
    return ids
