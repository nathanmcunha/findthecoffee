from typing import Any
from .connection import Database


class CafeRepository:
    """Equivalent to a @Repository in Spring."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all cafes. Similar to a simple findAll()."""
        query = "SELECT id, name, location FROM cafes"
        result = self.db.execute(query)
        # Convert rows to dictionaries (like a RowMapper)
        return [dict(row) for row in result.mappings()]

    def create(self, name: str, location: str) -> int:
        """Inserts a new cafe and returns its ID."""
        query = (
            "INSERT INTO cafes (name, location) VALUES (:name, :location) RETURNING id"
        )
        result = self.db.execute(query, {"name": name, "location": location})
        # Fetches the first row, first column
        row = result.fetchone()
        if row is None:
            raise ValueError("Failed to insert cafe or retrieve ID")
        return int(row[0])
