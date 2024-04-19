"""Add version to existing wallets

Revision ID: d9284cc0ed9f
Revises: d9284cc0ed9d
Create Date: 2024-04-19 18:30:44.625719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9284cc0ed9f'
down_revision = 'd9284cc0ed9d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE wallet SET version = 0")
    

def downgrade():
    pass
