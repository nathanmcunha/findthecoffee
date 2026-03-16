from typing import Any
from .connection import Database


class RoasterRepository:
    """Repository for coffee roaster operations."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all roasters."""
        query = "SELECT id, name, website, location FROM roasters ORDER BY name"
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]

    def get_by_id(self, roaster_id: int) -> dict[str, Any] | None:
        """Fetches a single roaster by ID."""
        query = "SELECT id, name, website, location FROM roasters WHERE id = :id"
        result = self.db.execute(query, {"id": roaster_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def create(self, name: str, website: str | None = None, location: str | None = None) -> int:
        """Inserts a new roaster and returns its ID."""
        query = """
            INSERT INTO roasters (name, website, location) 
            VALUES (:name, :website, :location) RETURNING id
        """
        result = self.db.execute(query, {"name": name, "website": website, "location": location})
        row = result.fetchone()
        if row is None:
            raise ValueError("Failed to insert roaster or retrieve ID")
        return int(row[0])


class CafeRepository:
    """Repository for cafe operations, including inventory."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all cafes."""
        query = "SELECT id, name, location, website FROM cafes ORDER BY name"
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]

    def get_by_id(self, cafe_id: int) -> dict[str, Any] | None:
        """Fetches a single cafe by ID."""
        query = "SELECT id, name, location, website FROM cafes WHERE id = :id"
        result = self.db.execute(query, {"id": cafe_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def create(self, name: str, location: str | None = None, website: str | None = None) -> int:
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

    def get_inventory(self, cafe_id: int) -> list[dict[str, Any]]:
        """Fetches all beans available at a specific cafe, including roaster details."""
        query = """
            SELECT 
                b.id, b.name, b.roast_level, b.origin,
                r.id as roaster_id, r.name as roaster_name
            FROM coffee_beans b
            JOIN cafe_inventory i ON i.bean_id = b.id
            LEFT JOIN roasters r ON b.roaster_id = r.id
            WHERE i.cafe_id = :cafe_id
        """
        result = self.db.execute(query, {"cafe_id": cafe_id})
        return [dict(row) for row in result.mappings()]

    def add_to_inventory(self, cafe_id: int, bean_id: int):
        """Adds a bean to a cafe's inventory."""
        query = "INSERT INTO cafe_inventory (cafe_id, bean_id) VALUES (:cafe_id, :bean_id) ON CONFLICT DO NOTHING"
        _ = self.db.execute(query, {"cafe_id": cafe_id, "bean_id": bean_id})

    def search(
        self,
        roast_level: str | None = None,
        origin: str | None = None,
        roaster_id: int | None = None,
        cafe_name: str | None = None,
        query_text: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Global search: Finds cafes based on criteria (Cafe, Roaster, or Bean).
        If query_text is provided, uses the FTS index for sub-millisecond filtering.
        """
        params = {}
        
        # We use a CTE (Common Table Expression) to perform the FTS filtering first.
        # This keeps the main query clean and ensures Postgres uses the GIN index efficiently.
        if query_text:
            sql_query = """
                WITH matching_cafes AS (
                    SELECT 
                        cafe_id, 
                        ts_rank(search_document, query) AS relevance
                    FROM 
                        coffee_search_index, 
                        plainto_tsquery('portuguese', :q) AS query
                    WHERE 
                        search_document @@ query
                )
                SELECT 
                    c.id, c.name, c.location, c.website,
                    COALESCE(m.relevance, 0) AS relevance,
                    COALESCE(
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'id', b.id,
                                'name', b.name,
                                'roast_level', b.roast_level,
                                'origin', b.origin,
                                'roaster_name', r.name
                            )
                        ) FILTER (WHERE b.id IS NOT NULL),
                        '[]'::json
                    ) AS matching_beans
                FROM cafes c
                LEFT JOIN matching_cafes m ON c.id = m.cafe_id
                LEFT JOIN cafe_inventory i ON i.cafe_id = c.id
                LEFT JOIN coffee_beans b ON i.bean_id = b.id
                LEFT JOIN roasters r ON b.roaster_id = r.id
                WHERE (
                    m.cafe_id IS NOT NULL  -- FTS Match
                    OR c.name ILIKE :q_like  -- Immediate Fallback
                    OR b.name ILIKE :q_like
                    OR r.name ILIKE :q_like
                )
            """
            params["q"] = query_text
            params["q_like"] = f"%{query_text}%"
            
            # Additional Filters (AND logic)
            if roast_level is not None:
                sql_query += " AND b.roast_level = :roast_level"
                params["roast_level"] = roast_level
            if origin is not None:
                sql_query += " AND b.origin ILIKE :origin"
                params["origin"] = f"%{origin}%"
            if roaster_id is not None:
                sql_query += " AND b.roaster_id = :roaster_id"
                params["roaster_id"] = roaster_id
            if cafe_name is not None:
                sql_query += " AND c.name ILIKE :cafe_name"
                params["cafe_name"] = f"%{cafe_name}%"

            sql_query += " GROUP BY c.id, relevance ORDER BY relevance DESC, c.name"
        else:
            # Traditional ILIKE search if no global query text is provided
            sql_query = """
                SELECT 
                    c.id, c.name, c.location, c.website,
                    COALESCE(
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'id', b.id,
                                'name', b.name,
                                'roast_level', b.roast_level,
                                'origin', b.origin,
                                'roaster_name', r.name
                            )
                        ) FILTER (WHERE b.id IS NOT NULL),
                        '[]'::json
                    ) AS matching_beans
                FROM cafes c
                LEFT JOIN cafe_inventory i ON i.cafe_id = c.id
                LEFT JOIN coffee_beans b ON i.bean_id = b.id
                LEFT JOIN roasters r ON b.roaster_id = r.id
                WHERE 1=1
            """
            if roast_level is not None:
                sql_query += " AND b.roast_level = :roast_level"
                params["roast_level"] = roast_level
            if origin is not None:
                sql_query += " AND b.origin ILIKE :origin"
                params["origin"] = f"%{origin}%"
            if roaster_id is not None:
                sql_query += " AND b.roaster_id = :roaster_id"
                params["roaster_id"] = roaster_id
            if cafe_name is not None:
                sql_query += " AND c.name ILIKE :cafe_name"
                params["cafe_name"] = f"%{cafe_name}%"

            sql_query += " GROUP BY c.id ORDER BY c.name"
        
        result = self.db.execute(sql_query, params)
        return [dict(row) for row in result.mappings()]


class CoffeeBeanRepository:
    """Repository for coffee bean operations."""

    def __init__(self):
        self.db = Database()

    def get_all(self) -> list[dict[str, Any]]:
        """Fetches all coffee beans with roaster information."""
        query = """
            SELECT b.id, b.name, b.roast_level, b.origin, b.roaster_id, r.name as roaster_name
            FROM coffee_beans b
            LEFT JOIN roasters r ON b.roaster_id = r.id
        """
        result = self.db.execute(query)
        return [dict(row) for row in result.mappings()]

    def get_by_id(self, bean_id: int) -> dict[str, Any] | None:
        """Fetches a single coffee bean by ID with roaster information."""
        query = """
            SELECT b.id, b.name, b.roast_level, b.origin, b.roaster_id, r.name as roaster_name
            FROM coffee_beans b
            LEFT JOIN roasters r ON b.roaster_id = r.id
            WHERE b.id = :id
        """
        result = self.db.execute(query, {"id": bean_id})
        row = result.mappings().fetchone()
        return dict(row) if row else None

    def create(
        self,
        name: str,
        roaster_id: int | None = None,
        roast_level: str | None = None,
        origin: str | None = None,
    ) -> int:
        """Inserts a new coffee bean and returns its ID."""
        query = """
            INSERT INTO coffee_beans (name, roast_level, origin, roaster_id)
            VALUES (:name, :roast_level, :origin, :roaster_id) RETURNING id
        """
        result = self.db.execute(query, {
            "name": name,
            "roast_level": roast_level,
            "origin": origin,
            "roaster_id": roaster_id,
        })
        row = result.fetchone()
        if row is None:
            raise ValueError("Failed to insert coffee bean or retrieve ID")
        return int(row[0])

    def search(
        self, 
        roast_level: str | None = None, 
        origin: str | None = None, 
        roaster_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Searches beans with multiple filters."""
        query = """
            SELECT b.id, b.name, b.roast_level, b.origin, b.roaster_id, r.name as roaster_name
            FROM coffee_beans b
            LEFT JOIN roasters r ON b.roaster_id = r.id
            WHERE 1=1
        """
        params = {}
        if roast_level is not None:
            query += " AND b.roast_level = :roast_level"
            params["roast_level"] = roast_level
        if origin is not None:
            query += " AND b.origin ILIKE :origin"
            params["origin"] = f"%{origin}%"
        if roaster_id is not None:
            query += " AND b.roaster_id = :roaster_id"
            params["roaster_id"] = roaster_id
            
        result = self.db.execute(query, params)
        return [dict(row) for row in result.mappings()]
