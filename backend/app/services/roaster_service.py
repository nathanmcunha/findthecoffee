"""Business logic for roaster operations."""
import logging
import uuid
from typing import Any
from db.repository import RoasterRepository
from app.core.errors import NotFoundError


logger = logging.getLogger(__name__)


class RoasterService:
    """Service layer for roaster business logic."""

    def __init__(self, roaster_repo: RoasterRepository):
        self.roaster_repo = roaster_repo

    def get_all(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Get all roasters with pagination."""
        logger.debug("Fetching roasters with limit=%s, offset=%s", limit, offset)
        return self.roaster_repo.get_all(limit=limit, offset=offset)

    def get_by_id(self, roaster_id: uuid.UUID) -> dict[str, Any]:
        """Get a single roaster by ID."""
        roaster = self.roaster_repo.get_by_id(roaster_id)
        if roaster is None:
            raise NotFoundError("Roaster", str(roaster_id))
        return roaster

    def create(
        self,
        name: str,
        website: str | None = None,
        location: str | None = None,
    ) -> uuid.UUID:
        """Create a new roaster."""
        logger.info("Creating roaster: %s", name)
        return self.roaster_repo.create(name, website, location)