"""create phone number column in Users

Revision ID: 9ccda807db8f
Revises: 
Create Date: 2025-09-06 15:25:32.776057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ccda807db8f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    col = sa.Column('phone_number', sa.String(), nullable=True)
    op.add_column('Users', col)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('Users', 'phone_number')
