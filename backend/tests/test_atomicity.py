"""Group 5 infrastructure check; business commands grow at this API/DB seam."""

from typing import Annotated
from uuid import uuid4

from conftest import test_url as database_url
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
from test_persistence import insert_expense

from app.core.config import Settings
from app.core.database import get_session
from app.factory import create_app


class ProbeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: int


def test_deferred_commit_failure_cannot_return_success_or_retain_partial_state(
    runtime,
    roster,
):
    # Test-only route exercises the actual transaction dependency and error stack.
    # It is not registered by the production application.
    app = create_app(Settings(database_url=database_url("SPENDWISE_TEST_RUNTIME_URL")))
    key = uuid4()

    @app.post("/_test/transaction", status_code=201)
    def write(
        data: ProbeInput,
        session: Annotated[Session, Depends(get_session, scope="function")],
    ):
        expense = insert_expense(session, roster, amount=data.amount)
        session.execute(
            text(
                "INSERT INTO app.expense_revisions "
                "(group_id,expense_id,version,action,actor_id,after_values) "
                "VALUES (:INR,:expense,1,'created',:A,'{}')"
            ),
            dict(roster, expense=expense),
        )
        session.execute(
            text(
                "INSERT INTO app.idempotency_requests "
                "(actor_id,request_key,group_id,operation,request_hash,"
                "response_status,response_body) "
                "VALUES (:A,:key,:INR,'create_expense',"
                "decode(repeat('ab',32),'hex'),201,'{}')"
            ),
            dict(roster, key=key),
        )
        return {"id": str(expense)}

    with TestClient(app, raise_server_exceptions=False) as client:
        failed = client.post("/_test/transaction", json={"amount": 101})
        assert failed.status_code == 500
        assert failed.json() == {
            "error": {
                "code": "internal_error",
                "message": "Request failed.",
                "fields": [],
                "details": {},
            },
            "request_id": failed.headers["x-request-id"],
        }
        with runtime.connect() as connection:
            for table in (
                "expenses",
                "expense_shares",
                "expense_revisions",
                "idempotency_requests",
            ):
                assert (
                    connection.execute(
                        text(f"SELECT count(*) FROM app.{table}")
                    ).scalar_one()
                    == 0
                )
        # Same key can succeed after removing the cause of failure.
        succeeded = client.post("/_test/transaction", json={"amount": 100})
        assert succeeded.status_code == 201
        with runtime.connect() as connection:
            assert (
                connection.execute(
                    text("SELECT amount_minor FROM app.expenses WHERE id=:id"),
                    {"id": succeeded.json()["id"]},
                ).scalar_one()
                == 100
            )
            assert (
                connection.execute(
                    text("SELECT response_status FROM app.idempotency_requests")
                ).scalar_one()
                == 201
            )

        rejected = client.post("/_test/transaction", json={"amount": "SECRET_VALUE"})
        assert rejected.status_code == 422
        assert rejected.json()["error"]["code"] == "validation_error"
        assert "SECRET_VALUE" not in rejected.text
