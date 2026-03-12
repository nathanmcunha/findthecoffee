"""Add roasters and cafe_inventory, refactor coffee_beans

Revision ID: 0002_roasters
Revises: 0001_initial
Create Date: 2024-03-21 12:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0002_roasters'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

migrations_dir = Path(__file__).parent / "sql"

def upgrade() -> None:
    sql_file = migrations_dir / "0002_add_roasters_and_inventory_up.sql"
    op.execute(sql_file.read_text())

def downgrade() -> None:
    sql_file = migrations_dir / "0002_add_roasters_and_inventory_down.sql"
    op.execute(sql_file.read_text())
