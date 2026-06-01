"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

from alembic import op

from app.db.schema import metadata

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    metadata.drop_all(bind=op.get_bind())
