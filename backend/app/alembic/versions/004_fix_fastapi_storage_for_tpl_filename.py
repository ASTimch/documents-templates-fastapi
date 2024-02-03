"""fix: fastapi-storage for tpl filename and thumbnail

Revision ID: 004
Revises: 003
Create Date: 2023-12-21 16:15:32.461268

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# import path_to_custom_types_py_file


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "template_owner_id_fkey", "template", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "template", "user", ["owner_id"], ["id"], ondelete="SET NULL"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "template", type_="foreignkey")
    op.create_foreign_key(
        "template_owner_id_fkey", "template", "user", ["owner_id"], ["id"]
    )
    # ### end Alembic commands ###
