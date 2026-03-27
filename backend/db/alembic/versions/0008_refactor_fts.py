"""Refactor FTS to use inline tsvector column

Revision ID: 0008_refactor_fts
Revises: 0007_add_indexes
Create Date: 2026-03-27 00:03:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0008_refactor_fts'
down_revision: str | None = '0007_add_indexes'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0008_refactor_fts_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0008_refactor_fts_down.sql"
    op.execute(sql_file.read_text())
