"""empty message

Revision ID: 79f876fad9b6
Revises: 8b2c514f3803
Create Date: 2023-04-11 15:17:51.476444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79f876fad9b6'
down_revision = '8b2c514f3803'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=False)

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=False)

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
