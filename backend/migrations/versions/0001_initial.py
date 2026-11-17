"""Approved application model; managed auth.users must already exist."""

from pathlib import Path

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    ddl = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(ddl, execution_options={"no_parameters": True})


def downgrade() -> None:
    raise RuntimeError(
        "No destructive downgrade: rebuild designated disposable resources."
    )
