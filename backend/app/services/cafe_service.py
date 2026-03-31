"""Business logic for cafe operations."""
import logging
import uuid
from typing import Any
from db.repository import CafeRepository, CoffeeBeanRepository
from app.core.errors import NotFoundError


logger = logging.getLogger(__name__)


class CafeService:
    """
    Service layer for cafe business logic.

    Responsibilities:
    - Validate business rules
    - Orchestrate repository operations
    - Handle cross-cutting concerns (logging, error handling)
    """

    def __init__(
        self,
        cafe_repo: CafeRepository,
        bean_repo: CoffeeBeanRepository,
    ):
        self.cafe_repo = cafe_repo
        self.bean_repo = bean_repo

    def get_all(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Get all cafes with pagination."""
        logger.debug("Fetching cafes with limit=%s, offset=%s", limit, offset)
        return self.cafe_repo.get_all(limit=limit, offset=offset)

    def get_by_id(self, cafe_id: uuid.UUID) -> dict[str, Any]:
        """Get a single cafe by ID."""
        cafe = self.cafe_repo.get_by_id(cafe_id)
        if cafe is None:
            raise NotFoundError("Cafe", str(cafe_id))
        return cafe

    def create(
        self,
        name: str,
        location: str | None = None,
        website: str | None = None,
    ) -> uuid.UUID:
        """Create a new cafe."""
        logger.info("Creating cafe: %s", name)
        return self.cafe_repo.create(name, location, website)

    def search(
        self,
        roast_level: str | None = None,
        origin: str | None = None,
        roaster_id: uuid.UUID | None = None,
        cafe_name: str | None = None,
        query_text: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Search cafes with multiple filters."""
        logger.debug(
            "Searching cafes: roast=%s, origin=%s, roaster=%s, name=%s, q=%s",
            roast_level,
            origin,
            roaster_id,
            cafe_name,
            query_text,
        )
        return self.cafe_repo.search(
            roast_level=roast_level,
            origin=origin,
            roaster_id=roaster_id,
            cafe_name=cafe_name,
            query_text=query_text,
            limit=limit,
            offset=offset,
        )

    def search_nearby(
        self,
        lat: float,
        lng: float,
        radius_m: int = 5000,
    ) -> list[dict[str, Any]]:
        """Search cafes near a location."""
        logger.info(
            "Searching cafes near lat=%s, lng=%s, radius=%sm",
            lat,
            lng,
            radius_m,
        )
        return self.cafe_repo.search_nearby(lat, lng, radius_m)

    def get_inventory(self, cafe_id: uuid.UUID) -> list[dict[str, Any]]:
        """Get cafe's coffee bean inventory."""
        # Verify cafe exists
        self.get_by_id(cafe_id)
        return self.cafe_repo.get_inventory(cafe_id)

    def add_to_inventory(
        self,
        cafe_id: uuid.UUID,
        bean_id: uuid.UUID,
    ) -> None:
        """Add a coffee bean to cafe inventory."""
        # Verify both entities exist
        self.get_by_id(cafe_id)
        bean = self.bean_repo.get_by_id(bean_id)
        if bean is None:
            raise NotFoundError("CoffeeBean", str(bean_id))

        logger.info(
            "Adding bean %s to cafe %s inventory",
            bean_id,
            cafe_id,
        )
        self.cafe_repo.add_to_inventory(cafe_id, bean_id)