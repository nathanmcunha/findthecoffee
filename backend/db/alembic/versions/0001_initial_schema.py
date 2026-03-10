"""Initial schema - cafes and coffee_beans tables

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op


revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0001_initial_schema_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0001_initial_schema_down.sql"
    op.execute(sql_file.read_text())
