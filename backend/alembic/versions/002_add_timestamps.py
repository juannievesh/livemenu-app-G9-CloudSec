"""add created_at and updated_at to restaurants, categories, dishes

Revision ID: 002_timestamps
Revises: 001_initial
Create Date: 2026-02-28

"""

import sqlalchemy as sa
from alembic import op

revision = "002_timestamps"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def _add_timestamps(table_name: str) -> None:
    """Add created_at / updated_at only if they don't already exist."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing = {c["name"] for c in inspector.get_columns(table_name)}

    if "created_at" not in existing:
        op.add_column(
            table_name,
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if "updated_at" not in existing:
        op.add_column(
            table_name,
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )


def upgrade() -> None:
    for table in ("restaurants", "categories", "dishes"):
        _add_timestamps(table)

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = {idx["name"] for idx in inspector.get_indexes("dishes")}
    if "ix_dishes_deleted_at" not in indexes:
        op.create_index(op.f("ix_dishes_deleted_at"), "dishes", ["deleted_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_dishes_deleted_at"), table_name="dishes")
    for table in ("dishes", "categories", "restaurants"):
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")
