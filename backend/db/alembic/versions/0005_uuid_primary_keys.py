"""Convert primary keys from SERIAL to UUIDv7

Revision ID: 0005_uuid_primary_keys
Revises: 0004_fts_triggers
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0005_uuid_primary_keys'
down_revision: str | None = '0004_fts_triggers'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0005_uuid_primary_keys_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0005_uuid_primary_keys_down.sql"
    op.execute(sql_file.read_text())
