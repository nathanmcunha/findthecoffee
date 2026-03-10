from typing import Any, Optional
from .connection import Database


class CafeRepository:
    """Equivalent to a @Repository in Spring."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all cafes. Similar to a simple findAll()."""
        query = "SELECT id, name, location, website FROM cafes"
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]

    def get_by_id(self, cafe_id: int) -> Optional[dict[str, Any]]:
        """Fetches a single cafe by ID."""
        query = "SELECT id, name, location, website FROM cafes WHERE id = :id"
        result = self.db.execute(query, {"id": cafe_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def create(self, name: str, location: Optional[str] = None, website: Optional[str] = None) -> int:
        """Inserts a new cafe and returns its ID."""
        query = """
            INSERT INTO cafes (name, location, website) 
            VALUES (:name, :location, :website) RETURNING id
        """
        result = self.db.execute(query, {"name": name, "location": location, "website": website})
        row = result.fetchone()
        if row is None:
            raise ValueError("Failed to insert cafe or retrieve ID")
        return int(row[0])

    def get_with_beans(self, cafe_id: int) -> Optional[dict[str, Any]]:
        """Fetches a cafe with all its coffee beans using JSON_AGG."""
        query = """
            SELECT 
                c.id, c.name, c.location, c.website,
                COALESCE(
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'id', b.id,
                            'name', b.name,
                            'roast_level', b.roast_level,
                            'origin', b.origin
                        )
                    ) FILTER (WHERE b.id IS NOT NULL),
                    '[]'
                ) AS beans
            FROM cafes c
            LEFT JOIN coffee_beans b ON b.cafe_id = c.id
            WHERE c.id = :id
            GROUP BY c.id
        """
        result = self.db.execute(query, {"id": cafe_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def get_all_with_beans(self) -> list[dict[str, Any]]:
        """Fetches all cafes with their beans aggregated using JSON_AGG."""
        query = """
            SELECT 
                c.id, c.name, c.location, c.website,
                COALESCE(
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'id', b.id,
                            'name', b.name,
                            'roast_level', b.roast_level,
                            'origin', b.origin
                        )
                    ) FILTER (WHERE b.id IS NOT NULL),
                    '[]'
                ) AS beans
            FROM cafes c
            LEFT JOIN coffee_beans b ON b.cafe_id = c.id
            GROUP BY c.id
            ORDER BY c.name
        """
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]


class CoffeeBeanRepository:
    """Repository for coffee bean operations."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all coffee beans."""
        query = "SELECT id, name, roast_level, origin, cafe_id FROM coffee_beans"
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]

    def get_by_id(self, bean_id: int) -> Optional[dict[str, Any]]:
        """Fetches a single coffee bean by ID."""
        query = "SELECT id, name, roast_level, origin, cafe_id FROM coffee_beans WHERE id = :id"
        result = self.db.execute(query, {"id": bean_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def get_by_cafe(self, cafe_id: int) -> list[dict[str, Any]]:
        """Fetches all beans for a specific cafe."""
        query = "SELECT id, name, roast_level, origin, cafe_id FROM coffee_beans WHERE cafe_id = :cafe_id"
        result = self.db.execute(query, {"cafe_id": cafe_id})
        return [dict(row) for row in result.mappings()]

    def create(
        self,
        name: str,
        cafe_id: int,
        roast_level: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> int:
        """Inserts a new coffee bean and returns its ID."""
        query = """
            INSERT INTO coffee_beans (name, roast_level, origin, cafe_id)
            VALUES (:name, :roast_level, :origin, :cafe_id) RETURNING id
        """
        result = self.db.execute(query, {
            "name": name,
            "roast_level": roast_level,
            "origin": origin,
            "cafe_id": cafe_id,
        })
        row = result.fetchone()
        if row is None:
            raise ValueError("Failed to insert coffee bean or retrieve ID")
        return int(row[0])

    def get_by_roast_level(self, roast_level: str) -> list[dict[str, Any]]:
        """Fetches beans filtered by roast level."""
        query = """
            SELECT id, name, roast_level, origin, cafe_id 
            FROM coffee_beans WHERE roast_level = :roast_level
        """
        result = self.db.execute(query, {"roast_level": roast_level})
        return [dict(row) for row in result.mappings()]

    def get_by_origin(self, origin: str) -> list[dict[str, Any]]:
        """Fetches beans filtered by origin (partial match)."""
        query = """
            SELECT id, name, roast_level, origin, cafe_id 
            FROM coffee_beans WHERE origin ILIKE :origin
        """
        result = self.db.execute(query, {"origin": f"%{origin}%"})
        return [dict(row) for row in result.mappings()]
