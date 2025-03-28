"""add archive table

Revision ID: a2ae9ab530b4
Revises: ec44df782509
Create Date: 2025-03-23 23:13:25.474875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ae9ab530b4'
down_revision: Union[str, None] = 'ec44df782509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('archivedlinks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('usage_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('archivedlinks')
    # ### end Alembic commands ###
