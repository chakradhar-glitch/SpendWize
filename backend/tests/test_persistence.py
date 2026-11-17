from uuid import uuid4

import psycopg
import pytest
from conftest import connect
from conftest import test_url as database_url
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError


def expense_sql() -> str:
    return (
        "INSERT INTO app.expenses(id,group_id,payer_membership_id,name,"
        "amount_minor,transaction_date,split_method,created_by,updated_by) "
        "VALUES (:expense,:INR,:a,'Tea',:amount,current_date,:method,:A,:A)"
    )


def insert_expense(
    connection,
    roster,
    *,
    amount=100,
    shares=(50, 50),
    method="equal",
    percentages=(None, None),
):
    expense = uuid4()
    parameters = dict(roster, expense=expense, amount=amount, method=method)
    connection.execute(text(expense_sql()), parameters)
    for member, share, percentage in zip(("a", "b"), shares, percentages):
        connection.execute(
            text(
                "INSERT INTO app.expense_shares "
                "(expense_id,group_id,membership_id,amount_minor,"
                "percentage_basis_points) "
                "VALUES (:expense,:group,:member,:share,:percentage)"
            ),
            {
                "expense": expense,
                "group": roster["INR"],
                "member": roster[member],
                "share": share,
                "percentage": percentage,
            },
        )
    return expense


def test_empty_database_migrates_to_approved_tables(runtime: Engine) -> None:
    assert set(inspect(runtime).get_table_names(schema="app")) == {
        "alembic_version",
        "profiles",
        "groups",
        "group_memberships",
        "group_invitations",
        "membership_events",
        "expenses",
        "expense_shares",
        "repayments",
        "expense_revisions",
        "repayment_revisions",
        "idempotency_requests",
    }
    with runtime.connect() as connection:
        assert (
            connection.execute(text("select current_user")).scalar_one()
            == "spendwise_runtime"
        )


def test_migration_is_repeatable_and_roles_are_restricted(runtime):
    from alembic import command
    from alembic.config import Config
    from conftest import ROOT

    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    with runtime.connect() as connection:
        assert (
            connection.execute(
                text("SELECT version_num FROM app.alembic_version")
            ).scalar_one()
            == "0001"
        )
        assert (
            connection.execute(
                text(
                    "SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolbypassrls "
                    "FROM pg_roles WHERE rolname=current_user"
                )
            ).scalar_one()
            is False
        )
        assert (
            connection.execute(
                text("SELECT pg_has_role(current_user,'spendwise_owner','MEMBER')")
            ).scalar_one()
            is False
        )


@pytest.mark.parametrize(
    "amount,shares,method,percentages",
    [
        (0, (0, 0), "equal", (None, None)),
        (100000000000, (50000000000, 50000000000), "equal", (None, None)),
        (100, (49, 50), "equal", (None, None)),
        (100, (-1, 101), "exact", (None, None)),
        (100, (50, 50), "percentage", (5000, 4999)),
        (100, (50, 50), "percentage", (10000, None)),
        (100, (50, 50), "equal", (5000, 5000)),
    ],
)
def test_invalid_expense_rolls_back_all_rows(
    runtime: Engine,
    roster,
    amount,
    shares,
    method,
    percentages,
) -> None:
    with pytest.raises(DBAPIError):
        with runtime.begin() as connection:
            insert_expense(
                connection,
                roster,
                amount=amount,
                shares=shares,
                method=method,
                percentages=percentages,
            )
    with runtime.connect() as connection:
        assert (
            connection.execute(
                text("select count(*) from app.expenses")
            ).scalar_one()
            == 0
        )
        assert (
            connection.execute(
                text("select count(*) from app.expense_shares")
            ).scalar_one()
            == 0
        )
        assert (
            connection.execute(
                text("select currency_locked_at from app.groups where id=:id"),
                {"id": roster["INR"]},
            ).scalar_one()
            is None
        )


def test_valid_deferred_expense_and_permanent_currency_lock(runtime, roster):
    with runtime.begin() as connection:
        insert_expense(connection, roster, amount=1, shares=(1, 0))
    with runtime.begin() as connection:
        connection.execute(text("UPDATE app.expenses SET deleted_at=now()"))
    for statement in (
        "UPDATE app.groups SET currency_code='USD' WHERE currency_code='INR'",
        "UPDATE app.groups SET currency_locked_at=NULL WHERE currency_code='INR'",
        "UPDATE app.groups SET timezone='UTC' WHERE currency_code='INR'",
    ):
        with pytest.raises(DBAPIError):
            with runtime.begin() as connection:
                connection.execute(text(statement))


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO app.group_memberships(group_id,profile_id) VALUES (:INR,:A)",
        "INSERT INTO app.membership_events"
        "(group_id,membership_id,event_type,actor_id) "
        "VALUES (:INR,:x,'joined',:A)",
        "INSERT INTO app.expenses(group_id,payer_membership_id,name,amount_minor,"
        "transaction_date,split_method,created_by,updated_by) "
        "VALUES (:INR,:x,'Tea',100,current_date,'equal',:A,:A)",
        "INSERT INTO app.repayments(group_id,sender_membership_id,"
        "recipient_membership_id,amount_minor,transaction_date,created_by,updated_by) "
        "VALUES (:INR,:b,:x,10,current_date,:A,:A)",
        "INSERT INTO app.repayments(group_id,sender_membership_id,"
        "recipient_membership_id,amount_minor,transaction_date,created_by,updated_by) "
        "VALUES (:INR,:a,:a,10,current_date,:A,:A)",
        "UPDATE app.group_memberships SET is_active=false WHERE id=:a",
    ],
)
def test_same_group_membership_and_financial_constraints(runtime, roster, statement):
    with pytest.raises(DBAPIError):
        with runtime.begin() as connection:
            connection.execute(text(statement), roster)


@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_client_roles_cannot_access_any_business_table(runtime, role):
    tables = inspect(runtime).get_table_names(schema="app")
    for table in tables:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            with connect(database_url("SPENDWISE_TEST_ADMIN_URL")) as admin:
                admin.execute(f"SET LOCAL ROLE {role}")
                admin.execute(f"SELECT * FROM app.{table}")


@pytest.mark.parametrize(
    "statement",
    [
        "CREATE TABLE app.forbidden(id int)",
        "ALTER TABLE app.profiles ADD COLUMN forbidden int",
        "DROP TABLE app.profiles CASCADE",
        "UPDATE app.membership_events SET event_type='left'",
        "DELETE FROM app.membership_events",
        "TRUNCATE app.expense_revisions",
        "UPDATE app.expense_revisions SET after_values='{}'",
        "DELETE FROM app.repayment_revisions",
        "DELETE FROM app.idempotency_requests",
        "SELECT * FROM auth.users",
    ],
)
def test_runtime_cannot_alter_schema_identities_or_history(runtime, statement):
    with pytest.raises(DBAPIError):
        with runtime.begin() as connection:
            connection.execute(text(statement))


def test_owner_cannot_mutate_history_even_with_table_privileges(runtime, roster):
    with runtime.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO app.membership_events"
                "(group_id,membership_id,event_type,actor_id) "
                "VALUES (:INR,:a,'joined',:A)"
            ),
            roster,
        )
    with pytest.raises(psycopg.errors.CheckViolation):
        with connect(database_url("SPENDWISE_TEST_MIGRATION_URL")) as owner:
            owner.execute("DELETE FROM app.membership_events")


@pytest.mark.parametrize(
    "operation",
    [
        "create_expense",
        "replace_expense",
        "delete_expense",
        "create_repayment",
        "replace_repayment",
        "delete_repayment",
    ],
)
def test_retry_results_cover_all_six_operations_and_enforce_actor_key(
    runtime, roster, operation
):
    parameters = dict(roster, operation=operation, key=uuid4())
    statement = text(
        "INSERT INTO app.idempotency_requests(actor_id,request_key,group_id,"
        "operation,request_hash,response_status,response_body) "
        "VALUES (:A,:key,:INR,:operation,decode(repeat('ab',32),'hex'),"
        '200,\'{"id":"original"}\')'
    )
    with runtime.begin() as connection:
        connection.execute(statement, parameters)
    with pytest.raises(DBAPIError):
        with runtime.begin() as connection:
            connection.execute(statement, parameters)
    with runtime.connect() as connection:
        assert connection.execute(
            text("select response_body from app.idempotency_requests")
        ).scalar_one() == {"id": "original"}
