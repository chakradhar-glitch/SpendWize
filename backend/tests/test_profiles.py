from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import Settings
from app.factory import create_app
from auth_source import AuthSource
from conftest import connect
from conftest import test_url as database_url


@pytest.fixture
def authenticated_app(runtime):
    source = AuthSource()
    with connect(database_url("SPENDWISE_TEST_ADMIN_URL")) as admin:
        for index in range(1, 6):
            admin.execute("INSERT INTO auth.users(id) VALUES (%s)", (UUID(int=index),))
    app = create_app(Settings(
        database_url=database_url("SPENDWISE_TEST_RUNTIME_URL"),
        supabase_url=source.url, supabase_publishable_key="local-fixture",
    ))
    with TestClient(app) as client:
        yield client, source
    source.close()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_profile_bootstrap_and_edit_preserve_name_and_trusted_account_fields(authenticated_app):
    client, source = authenticated_app
    headers = auth(source.token(UUID(int=1)))
    response = client.post("/api/v1/me/bootstrap", headers=headers)
    assert response.status_code == 200
    assert response.json()["display_name"] == "Seed Name"
    assert response.json()["email"] == "1@example.test"
    assert response.json()["email_verified"] is True
    assert response.json()["can_reset_password"] is True
    edited = client.patch("/api/v1/me", headers=headers, json={"display_name": "  Alice  "})
    assert edited.status_code == 200
    assert edited.json()["display_name"] == "Alice"
    assert client.post("/api/v1/me/bootstrap", headers=headers).json()["display_name"] == "Alice"
    assert client.get("/api/v1/me", headers=headers).json()["display_name"] == "Alice"


def test_concurrent_first_use_creates_one_profile(authenticated_app, runtime):
    client, source = authenticated_app
    headers = auth(source.token(UUID(int=2)))
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.post("/api/v1/me/bootstrap", headers=headers), range(2)))
    assert [response.status_code for response in responses] == [200, 200]
    assert responses[0].json() == responses[1].json()
    with runtime.connect() as connection:
        assert connection.execute(text("select count(*) from app.profiles")).scalar_one() == 1
