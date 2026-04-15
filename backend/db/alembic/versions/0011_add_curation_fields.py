"""Add curator's pick fields to cafes and roasters

Revision ID: 0011_add_curation_fields
Revises: 0010_add_bean_details
Create Date: 2026-04-13 00:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0011_add_curation_fields'
down_revision: str | None = '0010_add_bean_details'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0011_add_curation_fields_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0011_add_curation_fields_down.sql"
    op.execute(sql_file.read_text())