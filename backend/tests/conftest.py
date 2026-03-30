"""
Test configuration and fixtures for FindTheCoffee backend.

Sets up test environment with mocked database connections and Flask test client.
All tests should use the fixtures provided here for consistency and isolation.
"""
import os
import uuid

# Set required env vars before importing main, which creates the DB singleton at module level
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
os.environ.setdefault("API_KEY", "test-api-key")

import pytest
from unittest.mock import MagicMock
from main import app as flask_app


@pytest.fixture(scope="session")
def test_api_key() -> str:
    """Provide the test API key for authentication headers."""
    return os.environ["API_KEY"]


@pytest.fixture
def auth_headers(test_api_key: str) -> dict:
    """Provide authentication headers for API requests."""
    return {"X-API-Key": test_api_key}


@pytest.fixture
def client():
    """Create a Flask test client for API endpoint testing."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def mock_db(mocker):
    """Mocks the Database connection object.
    
    Patches the Database class where it's used (db.repository) and provides
    a mock instance with safe defaults to prevent NoneType errors.
    """
    mock_class = mocker.patch("db.repository.Database")
    instance = mock_class.return_value

    mock_result = MagicMock()
    mock_result.mappings.return_value = []
    instance.execute.return_value = mock_result

    return instance


@pytest.fixture
def test_uuid() -> uuid.UUID:
    """Provide a consistent test UUID for use in tests."""
    return uuid.UUID('00000000-0000-0000-0000-000000000001')


@pytest.fixture
def test_uuid_2() -> uuid.UUID:
    """Provide a second test UUID for relationship tests."""
    return uuid.UUID('00000000-0000-0000-0000-000000000002')
