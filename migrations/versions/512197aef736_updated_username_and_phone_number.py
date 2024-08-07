"""Updated username and phone_number

Revision ID: 512197aef736
Revises: 60a1eed024d1
Create Date: 2024-01-16 18:18:46.792385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "512197aef736"
down_revision: Union[str, None] = "60a1eed024d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("users", "username", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        "users", "phone_number", existing_type=sa.VARCHAR(length=15), nullable=False
    )
    op.create_unique_constraint(None, "users", ["phone_number"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.alter_column(
        "users", "phone_number", existing_type=sa.VARCHAR(length=15), nullable=True
    )
    op.alter_column("users", "username", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###
