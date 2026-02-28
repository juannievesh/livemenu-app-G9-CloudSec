"""initial schema — users, restaurants, categories, dishes

Revision ID: 001_initial
Revises:
Create Date: 2026-02-03 15:18:06.361397

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Users ──
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # ── Restaurants ──
    op.create_table(
        "restaurants",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("horarios", JSONB, nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id"),
    )
    op.create_index(op.f("ix_restaurants_slug"), "restaurants", ["slug"], unique=True)

    # ── Categories ──
    op.create_table(
        "categories",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── Dishes ──
    op.create_table(
        "dishes",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(300), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("offer_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("image_urls", JSONB, nullable=True),
        sa.Column("available", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("featured", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("tags", ARRAY(sa.String()), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dishes_deleted_at"), "dishes", ["deleted_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_dishes_deleted_at"), table_name="dishes")
    op.drop_table("dishes")
    op.drop_table("categories")
    op.drop_index(op.f("ix_restaurants_slug"), table_name="restaurants")
    op.drop_table("restaurants")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
