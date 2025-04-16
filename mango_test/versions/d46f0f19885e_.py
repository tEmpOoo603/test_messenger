"""empty message

Revision ID: d46f0f19885e
Revises: a8160c7b8f4e
Create Date: 2025-04-15 21:28:38.917236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd46f0f19885e'
down_revision: Union[str, None] = 'a8160c7b8f4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
