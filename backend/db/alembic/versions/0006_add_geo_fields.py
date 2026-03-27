"""Add address and geolocation fields with PostGIS

Revision ID: 0006_add_geo_fields
Revises: 0005_uuid_primary_keys
Create Date: 2026-03-27 00:01:00.000000

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op

revision: str = '0006_add_geo_fields'
down_revision: str | None = '0005_uuid_primary_keys'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

migrations_dir = Path(__file__).parent / "sql"


def upgrade() -> None:
    sql_file = migrations_dir / "0006_add_geo_fields_up.sql"
    op.execute(sql_file.read_text())


def downgrade() -> None:
    sql_file = migrations_dir / "0006_add_geo_fields_down.sql"
    op.execute(sql_file.read_text())
