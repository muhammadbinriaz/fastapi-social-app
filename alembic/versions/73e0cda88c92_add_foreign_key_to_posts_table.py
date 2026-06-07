"""add foreign key to posts table

Revision ID: 73e0cda88c92
Revises: 9870ae20a113
Create Date: 2026-06-07 22:35:33.639821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73e0cda88c92'
down_revision: Union[str, Sequence[str], None] = '9870ae20a113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        "post_users_fk",
        source_table="posts",
        referent_table="users",
        local_cols=["owner_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("post_users_fk", "posts", type_="foreignkey")
