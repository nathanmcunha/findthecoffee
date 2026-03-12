"""Add triggers to refresh FTS materialized view

Revision ID: 0004_fts_triggers
Revises: 0003_fts
Create Date: 2024-03-21 15:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0004_fts_triggers'
down_revision: str | None = '0003_fts'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0004_add_fts_triggers_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0004_add_fts_triggers_down.sql"
    op.execute(sql_file.read_text())
