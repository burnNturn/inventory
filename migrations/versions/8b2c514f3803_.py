"""empty message

Revision ID: 8b2c514f3803
Revises: 138aa37a406d
Create Date: 2023-04-11 15:10:13.247083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b2c514f3803'
down_revision = '138aa37a406d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_id',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
