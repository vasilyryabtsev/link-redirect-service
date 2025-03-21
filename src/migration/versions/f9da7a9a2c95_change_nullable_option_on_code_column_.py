"""change nullable option on code column in links

Revision ID: f9da7a9a2c95
Revises: d623869eb95b
Create Date: 2025-03-21 20:51:55.183591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9da7a9a2c95'
down_revision: Union[str, None] = 'd623869eb95b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('links', 'code',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('links', 'code',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
