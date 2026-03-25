import pytest
from unittest.mock import MagicMock
from main import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def mock_db(mocker):
    """Mocks the Database connection object."""
    # We must patch the class where it's USED, not where it's defined.
    # It's used inside CafeRepository which is in db.repository.
    mock_class = mocker.patch("db.repository.Database")
    instance = mock_class.return_value

    # Setup default return for execute to prevent NoneType unpack errors
    mock_result = MagicMock()
    mock_result.mappings.return_value = []
    instance.execute.return_value = mock_result

    return instance
