"""Add coffee bean technical details (ficha técnica)

Revision ID: 0010_add_bean_details
Revises: 0009_timestamps_and_soft_delete
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0010_add_bean_details'
down_revision: str | None = '0009_timestamps_and_soft_delete'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0010_add_bean_details_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0010_add_bean_details_down.sql"
    op.execute(sql_file.read_text())
