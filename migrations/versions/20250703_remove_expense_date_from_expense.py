"""Remove expense_date from Expense model

Revision ID: 20250703_remove_expense_date_from_expense
Revises: ad2fa441693a
Create Date: 2025-07-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250703_remove_expense_date_from_expense'
down_revision = 'ad2fa441693a'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_column('expense_date')

def downgrade():
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expense_date', sa.DateTime(), nullable=True))
