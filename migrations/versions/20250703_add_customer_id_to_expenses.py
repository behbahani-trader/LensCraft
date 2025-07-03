"""Add customer_id column to expenses table

Revision ID: 20250703_add_customer_id_to_expenses
Revises: 20250703_remove_expense_date_from_expense
Create Date: 2025-07-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250703_add_customer_id_to_expenses'
down_revision = '20250703_remove_expense_date_from_expense'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'customer_id',
            sa.Integer(),
            sa.ForeignKey('customers.id', name='fk_expenses_customer_id_customers'),
            nullable=True
        ))

def downgrade():
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_column('customer_id')
