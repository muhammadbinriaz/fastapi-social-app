"""adding owner

Revision ID: 1a45275dfb35
Revises: e3ae55987927
Create Date: 2026-06-07 22:20:56.785486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a45275dfb35'
down_revision: Union[str, Sequence[str], None] = 'e3ae55987927'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("owner_id", sa.Integer, nullable=False))

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "owner_id")
    pass
