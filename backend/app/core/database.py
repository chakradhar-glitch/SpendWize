from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def create_session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = create_engine(
        settings.database_url.get_secret_value(),
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 10},
    )
    return sessionmaker(engine, expire_on_commit=False)


@contextmanager
def transaction(factory: sessionmaker[Session]) -> Iterator[Session]:
    """The use-case boundary owns commit, rollback and session lifetime."""
    with factory() as session:
        with session.begin():
            yield session


def get_session(request: Request) -> Iterator[Session]:
    """Use Depends(get_session, scope='function') to commit before sending success.

    Routes are synchronous and pass this single session to every collaborator.
    Never use the default request teardown scope for write endpoints.
    """
    with transaction(request.app.state.session_factory) as session:
        yield session
