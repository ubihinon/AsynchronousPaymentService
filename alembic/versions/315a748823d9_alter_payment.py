"""alter payment

Revision ID: 315a748823d9
Revises: cbc890b4ef33
Create Date: 2026-07-15 09:26:35.838908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '315a748823d9'
down_revision: Union[str, Sequence[str], None] = 'cbc890b4ef33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('payments', sa.Column('request_payload_hash', sa.String(length=64), nullable=False))
    op.add_column('payments', sa.Column('response_data', sa.JSON(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('payments', 'response_data')
    op.drop_column('payments', 'request_payload_hash')
