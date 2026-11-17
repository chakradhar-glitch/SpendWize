import os

from alembic import context
from sqlalchemy import create_engine, text

from app.core.config import Settings

url = os.environ.get("SPENDWISE_MIGRATION_DATABASE_URL")
if not url:
    raise RuntimeError(
        "Set SPENDWISE_MIGRATION_DATABASE_URL with migration-owner credentials"
    )
settings = Settings(database_url=url)
engine = create_engine(settings.database_url.get_secret_value(), hide_parameters=True)
try:
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        context.configure(
            connection=connection,
            version_table_schema="app",
            transactional_ddl=True,
        )
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
