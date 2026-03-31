"""Application configuration and settings."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

_ = load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "FindTheCoffee API"
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", "5000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Database
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # Security
    API_KEY: str | None = os.getenv("API_KEY")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # Rate Limiting
    RATELIMIT_STORAGE_URI: str = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT: list[str] | None = None

    def __post_init__(self):
        """Validate required settings."""
        if self.DATABASE_URL is None:
            raise ValueError("DATABASE_URL environment variable is required")
        if self.RATELIMIT_DEFAULT is None:
            object.__setattr__(
                self, "RATELIMIT_DEFAULT", ["200 per day", "60 per hour"]
            )

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG


# Global settings instance
settings = Settings()
