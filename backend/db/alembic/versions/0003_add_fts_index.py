"""Add Full-Text Search index with Materialized View

Revision ID: 0003_fts
Revises: 0002_roasters
Create Date: 2024-03-21 14:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0003_fts'
down_revision: Union[str, None] = '0002_roasters'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0003_add_fts_index_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0003_add_fts_index_down.sql"
    op.execute(sql_file.read_text())
