"""Dependency injection container for application services."""
import logging
from dataclasses import dataclass, field
from db.repository import CafeRepository, CoffeeBeanRepository, RoasterRepository
from app.services.cafe_service import CafeService
from app.services.roaster_service import RoasterService
from app.services.bean_service import BeanService


logger = logging.getLogger(__name__)


@dataclass
class Container:
    """
    Dependency injection container.

    Manages application dependencies with lazy initialization.
    Follows the Service Locator pattern for Flask compatibility.
    """

    # Repositories (data access layer)
    _cafe_repo: CafeRepository | None = field(default=None, init=False)
    _roaster_repo: RoasterRepository | None = field(default=None, init=False)
    _bean_repo: CoffeeBeanRepository | None = field(default=None, init=False)

    # Services (business logic layer)
    _cafe_service: CafeService | None = field(default=None, init=False)
    _roaster_service: RoasterService | None = field(default=None, init=False)
    _bean_service: BeanService | None = field(default=None, init=False)

    @property
    def cafe_repo(self) -> CafeRepository:
        """Get or create CafeRepository instance."""
        if self._cafe_repo is None:
            self._cafe_repo = CafeRepository()
        return self._cafe_repo

    @property
    def roaster_repo(self) -> RoasterRepository:
        """Get or create RoasterRepository instance."""
        if self._roaster_repo is None:
            self._roaster_repo = RoasterRepository()
        return self._roaster_repo

    @property
    def bean_repo(self) -> CoffeeBeanRepository:
        """Get or create CoffeeBeanRepository instance."""
        if self._bean_repo is None:
            self._bean_repo = CoffeeBeanRepository()
        return self._bean_repo

    @property
    def cafe_service(self) -> CafeService:
        """Get or create CafeService instance."""
        if self._cafe_service is None:
            self._cafe_service = CafeService(self.cafe_repo, self.bean_repo)
        return self._cafe_service

    @property
    def roaster_service(self) -> RoasterService:
        """Get or create RoasterService instance."""
        if self._roaster_service is None:
            self._roaster_service = RoasterService(self.roaster_repo)
        return self._roaster_service

    @property
    def bean_service(self) -> BeanService:
        """Get or create BeanService instance."""
        if self._bean_service is None:
            self._bean_service = BeanService(self.bean_repo)
        return self._bean_service

    def override_for_testing(self, **kwargs: object) -> None:
        """Override dependencies for testing (dependency injection)."""
        for key, value in kwargs.items():
            attr = f"_{key}"
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                raise AttributeError(f"Unknown dependency: {key}")


# Global application container
container = Container()