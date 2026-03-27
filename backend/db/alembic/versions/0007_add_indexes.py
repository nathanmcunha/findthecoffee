"""Add missing indexes for FK joins, filters, and trigram search

Revision ID: 0007_add_indexes
Revises: 0006_add_geo_fields
Create Date: 2026-03-27 00:02:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0007_add_indexes'
down_revision: str | None = '0006_add_geo_fields'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0007_add_indexes_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0007_add_indexes_down.sql"
    op.execute(sql_file.read_text())
