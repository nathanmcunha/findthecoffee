import os
from sqlalchemy import create_engine, text, Engine, CursorResult
from typing import Any, Optional


class Database:
    _instance = None
    engine: Engine

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            # DATABASE_URL is typically provided by environment variables
            url = os.getenv(
                "DATABASE_URL", "postgresql://user:password@localhost:5432/coffeedb"
            )
            # Ensure we use psycopg (v3) dialect, not psycopg2
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            cls._instance.engine = create_engine(url)
        return cls._instance

    def execute(self, query: str, params: Optional[dict[str, Any]] = None) -> CursorResult[Any]:
        """Wrapper for raw SQL execution, similar to JdbcTemplate.query()."""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result
