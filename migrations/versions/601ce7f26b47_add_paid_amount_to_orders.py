"""add paid_amount to orders

Revision ID: 601ce7f26b47
Revises: e8778b39bb2e
Create Date: 2025-07-03 18:46:10.720932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '601ce7f26b47'
down_revision = 'e8778b39bb2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_customers_email_unique'))

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('paid_amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('is_settled', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('settlement_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('settlement_notes', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('settlement_notes')
        batch_op.drop_column('settlement_date')
        batch_op.drop_column('is_settled')
        batch_op.drop_column('paid_amount')

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_customers_email_unique'), ['email'], unique=1)

    # ### end Alembic commands ###
