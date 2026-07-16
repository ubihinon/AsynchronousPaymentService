"""add outbox

Revision ID: d386d604be57
Revises: 1262ce360bc9
Create Date: 2026-07-16 07:44:26.908860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd386d604be57'
down_revision: Union[str, Sequence[str], None] = '1262ce360bc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('outbox',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('aggregate_type', sa.String(length=50), nullable=False),
    sa.Column('aggregate_id', sa.UUID(), nullable=False),
    sa.Column('payload', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_outbox_event_type'), 'outbox', ['event_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_outbox_event_type'), table_name='outbox')
    op.drop_table('outbox')
