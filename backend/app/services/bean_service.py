"""Business logic for coffee bean operations."""
import logging
import uuid
from typing import Any
from db.repository import CoffeeBeanRepository
from app.core.errors import NotFoundError


logger = logging.getLogger(__name__)


class BeanService:
    """Service layer for coffee bean business logic."""

    def __init__(self, bean_repo: CoffeeBeanRepository):
        self.bean_repo = bean_repo

    def get_all(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Get all coffee beans with pagination."""
        logger.debug("Fetching beans with limit=%s, offset=%s", limit, offset)
        return self.bean_repo.get_all(limit=limit, offset=offset)

    def get_by_id(self, bean_id: uuid.UUID) -> dict[str, Any]:
        """Get a single coffee bean by ID."""
        bean = self.bean_repo.get_by_id(bean_id)
        if bean is None:
            raise NotFoundError("CoffeeBean", str(bean_id))
        return bean

    def create(
        self,
        name: str,
        roaster_id: uuid.UUID | None = None,
        roast_level: str | None = None,
        origin: str | None = None,
        variety: str | None = None,
        processing: str | None = None,
        altitude: int | None = None,
        producer: str | None = None,
        farm: str | None = None,
        region: str | None = None,
        tasting_notes: list[str] | None = None,
        acidity: int | None = None,
        sweetness: int | None = None,
        body: int | None = None,
    ) -> uuid.UUID:
        """Create a new coffee bean."""
        logger.info("Creating coffee bean: %s", name)
        return self.bean_repo.create(
            name=name,
            roaster_id=roaster_id,
            roast_level=roast_level,
            origin=origin,
            variety=variety,
            processing=processing,
            altitude=altitude,
            producer=producer,
            farm=farm,
            region=region,
            tasting_notes=tasting_notes,
            acidity=acidity,
            sweetness=sweetness,
            body=body,
        )

    def search(
        self,
        roast_level: str | None = None,
        origin: str | None = None,
        roaster_id: uuid.UUID | None = None,
        variety: str | None = None,
        processing: str | None = None,
        region: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Search coffee beans with filters."""
        logger.debug(
            "Searching beans with roast=%s, origin=%s, roaster=%s, variety=%s, processing=%s, region=%s",
            roast_level,
            origin,
            roaster_id,
            variety,
            processing,
            region,
        )
        return self.bean_repo.search(
            roast_level=roast_level,
            origin=origin,
            roaster_id=roaster_id,
            variety=variety,
            processing=processing,
            region=region,
            limit=limit,
            offset=offset,
        )