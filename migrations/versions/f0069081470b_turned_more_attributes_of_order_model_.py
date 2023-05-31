"""turned more attributes of Order model into properties, to allow for dynamic calculations

Revision ID: f0069081470b
Revises: 0f49499356dd
Create Date: 2023-05-31 00:16:38.569080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0069081470b'
down_revision = '0f49499356dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('_fees', sa.Float(), nullable=False))
        batch_op.drop_column('fees')
        batch_op.drop_column('tax')
        batch_op.drop_column('total_sale_price')
        batch_op.drop_column('shipping_charged')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_charged', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('total_sale_price', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('tax', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('fees', sa.FLOAT(), nullable=False))
        batch_op.drop_column('_fees')

    # ### end Alembic commands ###
