"""alter idempotency_key

Revision ID: cbc890b4ef33
Revises: afdca2eec403
Create Date: 2026-07-15 09:25:50.207247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbc890b4ef33'
down_revision: Union[str, Sequence[str], None] = 'afdca2eec403'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_payments_idempotency_key'), 'payments', ['idempotency_key'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_payments_idempotency_key'), table_name='payments')
