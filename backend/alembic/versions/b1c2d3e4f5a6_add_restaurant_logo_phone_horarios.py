"""add restaurant logo phone horarios

Revision ID: b1c2d3e4f5a6
Revises: 5147191857b1
Create Date: 2025-02-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'fcaef81be286'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('restaurants', sa.Column('logo_url', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('restaurants', sa.Column('horarios', JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column('restaurants', 'horarios')
    op.drop_column('restaurants', 'phone')
    op.drop_column('restaurants', 'logo_url')
