"""recording blobs for hosts without persistent disk

Revision ID: 20261019_01
Revises: 20261014_01
Create Date: 2026-10-19 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20261019_01'
down_revision: Union[str, None] = '20261014_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('recording_blobs',
    sa.Column('path', sa.String(length=500), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('path')
    )


def downgrade() -> None:
    op.drop_table('recording_blobs')
