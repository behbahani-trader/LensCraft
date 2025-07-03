"""remove email unique constraint

Revision ID: 25a64d6c751d
Revises: 1716303e4d21
Create Date: 2024-06-05 11:34:50.015294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25a64d6c751d'
down_revision = '1716303e4d21'
branch_labels = None
depends_on = None


def upgrade():
    # حذف محدودیت یکتا بودن ایمیل
    with op.batch_alter_table('customers') as batch_op:
        pass  # حذف ایندکس انجام نمی‌شود چون وجود ندارد


def downgrade():
    # بازگرداندن محدودیت یکتا بودن ایمیل
    with op.batch_alter_table('customers') as batch_op:
        batch_op.create_index('ix_customers_email', ['email'], unique=True)
