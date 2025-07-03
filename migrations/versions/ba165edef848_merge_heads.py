"""merge heads

Revision ID: ba165edef848
Revises: 20250703_add_customer_id_to_expenses, 601ce7f26b47
Create Date: 2025-07-03 21:02:47.758245

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba165edef848'
down_revision = ('20250703_add_customer_id_to_expenses', '601ce7f26b47')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
