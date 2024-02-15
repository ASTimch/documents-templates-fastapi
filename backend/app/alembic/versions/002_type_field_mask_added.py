"""type_field mask added

Revision ID: 002
Revises: 001
Create Date: 2023-12-15 12:09:50.358114

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "field_type", sa.Column("mask", sa.String(length=256), nullable=True)
    )
    op.create_unique_constraint(
        "type_unique_constraint", "field_type", ["type"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("type_unique_constraint", "field_type", type_="unique")
    op.drop_column("field_type", "mask")
    # ### end Alembic commands ###