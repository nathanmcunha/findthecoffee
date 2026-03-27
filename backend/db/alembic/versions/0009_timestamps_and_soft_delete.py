"""Add timestamps and soft delete support

Revision ID: 0009_timestamps_and_soft_delete
Revises: 0008_refactor_fts
Create Date: 2026-03-27 00:04:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0009_timestamps_and_soft_delete'
down_revision: str | None = '0008_refactor_fts'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0009_timestamps_and_soft_delete_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0009_timestamps_and_soft_delete_down.sql"
    op.execute(sql_file.read_text())
