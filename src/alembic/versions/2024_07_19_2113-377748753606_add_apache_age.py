"""add-apache-age

Revision ID: 377748753606
Revises: f82269e25cac
Create Date: 2024-07-19 21:13:41.320325

"""
from typing import Sequence, Union

from alembic import op

from app.config import Config

app_config = Config()

# revision identifiers, used by Alembic.
revision: str = '377748753606'
down_revision: Union[str, None] = 'f82269e25cac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS age;")
    op.execute(f"SELECT * FROM ag_catalog.create_graph('{app_config.DB.graph_name}');")


def downgrade() -> None:
    op.execute(f"SELECT * FROM ag_catalog.drop_graph('{app_config.DB.graph_name}', true);")
