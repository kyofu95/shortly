"""passwor field fix

Revision ID: ec836d7a9567
Revises: 5236d244e3c2
Create Date: 2023-05-04 18:56:34.833404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec836d7a9567'
down_revision = '5236d244e3c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=60),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.String(length=60),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    # ### end Alembic commands ###