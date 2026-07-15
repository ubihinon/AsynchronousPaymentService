"""alter response_data

Revision ID: 1262ce360bc9
Revises: 315a748823d9
Create Date: 2026-07-15 09:57:28.876927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1262ce360bc9'
down_revision: Union[str, Sequence[str], None] = '315a748823d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('payments', 'response_data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('payments', 'response_data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
