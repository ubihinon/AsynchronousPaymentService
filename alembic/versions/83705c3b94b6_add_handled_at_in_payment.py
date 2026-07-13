"""add handled_at in payment

Revision ID: 83705c3b94b6
Revises: 115d62b1aad8
Create Date: 2026-07-13 16:33:42.022411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83705c3b94b6'
down_revision: Union[str, Sequence[str], None] = '115d62b1aad8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('payments', sa.Column('handled_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('payments', 'handled_at')
