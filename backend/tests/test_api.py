"""API endpoint tests for FindTheCoffee backend.

Tests cover authentication, validation, CRUD operations, and error handling
for cafes, roasters, beans, and inventory endpoints.
"""
import os
import uuid
import pytest
from app.core.errors import NotFoundError

# Expose the test API key so test modules can reference it
TEST_API_KEY = os.environ["API_KEY"]

AUTH = {"X-API-Key": TEST_API_KEY}
TEST_UUID = str(uuid.UUID('00000000-0000-0000-0000-000000000001'))
TEST_UUID_2 = str(uuid.UUID('00000000-0000-0000-0000-000000000002'))
TEST_UUID_3 = str(uuid.UUID('00000000-0000-0000-0000-000000000003'))

# Pagination constants
DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0


def test_ping(client):
    """Test health check endpoint."""
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.get_json()["status"] == "online"


# ============== VALIDATION TESTS (PARAMETRIZED) ==============


@pytest.mark.parametrize("endpoint,expected_status", [
    ("/api/v1/cafes", 400),
    ("/api/v1/roasters", 400),
    ("/api/v1/beans", 400),
])
def test_create_validation_error_missing_name(client, endpoint, expected_status):
    """Test that POST endpoints fail with 400 when name is missing."""
    res = client.post(endpoint, json={}, headers=AUTH)
    assert res.status_code == expected_status
    assert "Validation Error" in res.get_json()["error"]


@pytest.mark.parametrize("endpoint,json_payload", [
    ("/api/v1/cafes", {"name": "Test"}),
    ("/api/v1/roasters", {"name": "New Roaster"}),
    ("/api/v1/beans", {"name": "New Bean"}),
])
def test_create_requires_auth(client, endpoint, json_payload):
    """Test that POST endpoints return 401 without valid API key."""
    res = client.post(endpoint, json=json_payload)
    assert res.status_code == 401


# ============== CAFE ENDPOINT TESTS ==============


def test_add_cafe_success(client, mocker):
    """Test that POST /api/v1/cafes succeeds with valid data."""
    mock_service = mocker.MagicMock()
    mock_service.create.return_value = uuid.UUID(TEST_UUID)
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.post(
        "/api/v1/cafes", json={"name": "Testing Cafe", "location": "Internet"}, headers=AUTH
    )

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


def test_add_cafe_rejects_invalid_website(client):
    """Test that POST /api/v1/cafes rejects a non-HTTP website URL."""
    res = client.post(
        "/api/v1/cafes",
        json={"name": "Bad Cafe", "website": "javascript:alert(1)"},
        headers=AUTH,
    )
    assert res.status_code == 400


def test_list_cafes_with_filters(client, mocker):
    """Test that GET /api/v1/cafes passes filters correctly to the service."""
    mock_service = mocker.MagicMock()
    mock_service.search.return_value = []
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes?q=test&roast=Dark&roaster_id={TEST_UUID}")

    assert res.status_code == 200
    mock_service.search.assert_called_once_with(
        roast_level="Dark",
        origin=None,
        roaster_id=uuid.UUID(TEST_UUID),
        cafe_name=None,
        query_text="test",
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET
    )


def test_list_cafes_no_filters_calls_search(client, mocker):
    """Test that GET /api/v1/cafes with no filters calls search with all-None params."""
    mock_service = mocker.MagicMock()
    mock_service.search.return_value = []
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get("/api/v1/cafes")

    assert res.status_code == 200
    mock_service.search.assert_called_once_with(
        roast_level=None,
        origin=None,
        roaster_id=None,
        cafe_name=None,
        query_text=None,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET
    )


def test_get_cafe_success(client, mocker):
    """Test GET /api/v1/cafes/<id> returns the cafe when found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.return_value = {
        "id": uuid.UUID(TEST_UUID),
        "name": "Test Cafe",
        "location": "Porto",
        "website": None
    }
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Test Cafe"


def test_get_cafe_not_found(client, mocker):
    """Test GET /api/v1/cafes/<id> returns 404 when not found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.side_effect = NotFoundError("Cafe", TEST_UUID)
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes/{TEST_UUID}")

    assert res.status_code == 404


def test_get_cafe_inventory_success(client, mocker):
    """Test GET /api/v1/cafes/<id>/inventory returns inventory when cafe exists."""
    mock_service = mocker.MagicMock()
    mock_service.get_inventory.return_value = [{
        "id": uuid.UUID(TEST_UUID_2),
        "name": "Dark Roast"
    }]
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes/{TEST_UUID}/inventory")

    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_get_cafe_inventory_not_found(client, mocker):
    """Test GET /api/v1/cafes/<id>/inventory returns 404 when cafe not found."""
    mock_service = mocker.MagicMock()
    mock_service.get_inventory.side_effect = NotFoundError("Cafe", TEST_UUID)
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes/{TEST_UUID}/inventory")

    assert res.status_code == 404


# ============== ROASTER ENDPOINT TESTS ==============


def test_list_roasters(client, mocker):
    """Test GET /api/v1/roasters returns a list."""
    mock_service = mocker.MagicMock()
    mock_service.get_all.return_value = [{
        "id": uuid.UUID(TEST_UUID),
        "name": "Roaster A"
    }]
    mocker.patch("app.core.dependencies.container._roaster_service", mock_service)

    res = client.get("/api/v1/roasters")

    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 1
    assert data["page"] == 1
    assert data["per_page"] == DEFAULT_LIMIT


def test_get_roaster_success(client, mocker):
    """Test GET /api/v1/roasters/<id> returns the roaster when found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.return_value = {
        "id": uuid.UUID(TEST_UUID),
        "name": "Roaster A",
        "website": None,
        "location": None
    }
    mocker.patch("app.core.dependencies.container._roaster_service", mock_service)

    res = client.get(f"/api/v1/roasters/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Roaster A"


def test_get_roaster_not_found(client, mocker):
    """Test GET /api/v1/roasters/<id> returns 404 when not found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.side_effect = NotFoundError("Roaster", TEST_UUID)
    mocker.patch("app.core.dependencies.container._roaster_service", mock_service)

    res = client.get(f"/api/v1/roasters/{TEST_UUID}")

    assert res.status_code == 404


def test_add_roaster_success(client, mocker):
    """Test POST /api/v1/roasters creates a roaster and returns its ID."""
    mock_service = mocker.MagicMock()
    mock_service.create.return_value = uuid.UUID(TEST_UUID)
    mocker.patch("app.core.dependencies.container._roaster_service", mock_service)

    res = client.post("/api/v1/roasters", json={"name": "New Roaster"}, headers=AUTH)

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


# ============== BEAN ENDPOINT TESTS ==============


def test_list_beans(client, mocker):
    """Test GET /api/v1/beans returns a list."""
    mock_service = mocker.MagicMock()
    mock_service.search.return_value = [{
        "id": uuid.UUID(TEST_UUID),
        "name": "Bean A"
    }]
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.get("/api/v1/beans")

    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 1
    assert data["page"] == 1
    assert data["per_page"] == DEFAULT_LIMIT


def test_get_bean_success(client, mocker):
    """Test GET /api/v1/beans/<id> returns the bean when found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.return_value = {
        "id": uuid.UUID(TEST_UUID),
        "name": "Bean A",
        "roast_level": "Dark"
    }
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.get(f"/api/v1/beans/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Bean A"


def test_get_bean_not_found(client, mocker):
    """Test GET /api/v1/beans/<id> returns 404 when not found."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.side_effect = NotFoundError("CoffeeBean", TEST_UUID)
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.get(f"/api/v1/beans/{TEST_UUID}")

    assert res.status_code == 404


def test_add_bean_success(client, mocker):
    """Test POST /api/v1/beans creates a bean and returns its ID."""
    mock_service = mocker.MagicMock()
    mock_service.create.return_value = uuid.UUID(TEST_UUID)
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.post("/api/v1/beans", json={"name": "New Bean"}, headers=AUTH)

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


# ============== INVENTORY POST TESTS ==============


def test_add_to_inventory_success(client, mocker):
    """Test POST /api/v1/cafes/<id>/inventory adds a bean to inventory."""
    mock_service = mocker.MagicMock()
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.post(f"/api/v1/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 200
    assert res.get_json()["status"] == "success"


def test_add_to_inventory_cafe_not_found(client, mocker):
    """Test POST /api/v1/cafes/<id>/inventory returns 404 when cafe not found."""
    mock_service = mocker.MagicMock()
    mock_service.add_to_inventory.side_effect = NotFoundError("Cafe", TEST_UUID)
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.post(f"/api/v1/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 404


def test_add_to_inventory_bean_not_found(client, mocker):
    """Test POST /api/v1/cafes/<id>/inventory returns 404 when bean not found."""
    mock_service = mocker.MagicMock()
    mock_service.add_to_inventory.side_effect = NotFoundError("CoffeeBean", TEST_UUID_2)
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.post(f"/api/v1/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 404


def test_add_to_inventory_missing_bean_id(client, mocker):
    """Test POST /api/v1/cafes/<id>/inventory returns 400 when bean_id is absent from body."""
    res = client.post(f"/api/v1/cafes/{TEST_UUID}/inventory", json={}, headers=AUTH)

    assert res.status_code == 400
    assert "Validation Error" in res.get_json()["error"]


def test_add_to_inventory_requires_auth(client):
    """Test that POST /api/v1/cafes/<id>/inventory returns 401 without a valid API key."""
    res = client.post(f"/api/v1/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2})
    assert res.status_code == 401


def test_list_beans_no_filters_still_calls_search(client, mocker):
    """Test that GET /api/v1/beans with no filters always routes through search."""
    mock_service = mocker.MagicMock()
    mock_service.search.return_value = []
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.get("/api/v1/beans")

    assert res.status_code == 200
    mock_service.search.assert_called_once_with(
        roast_level=None,
        origin=None,
        roaster_id=None,
        variety=None,
        processing=None,
        region=None,
        limit=DEFAULT_LIMIT,
        offset=DEFAULT_OFFSET
    )


# ============== 500 ERROR PATH TESTS ==============


def test_list_cafes_repo_error_returns_500(client, mocker):
    """Test GET /api/v1/cafes returns 500 when the service raises an unexpected exception."""
    mock_service = mocker.MagicMock()
    mock_service.search.side_effect = Exception("DB connection failed")
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get("/api/v1/cafes")

    assert res.status_code == 500
    # Internal error details must NOT be exposed to the caller
    assert "DB connection failed" not in res.get_json().get("error", "")


def test_get_cafe_repo_error_returns_500(client, mocker):
    """Test GET /api/v1/cafes/<id> returns 500 when the service raises an unexpected exception."""
    mock_service = mocker.MagicMock()
    mock_service.get_by_id.side_effect = Exception("DB connection failed")
    mocker.patch("app.core.dependencies.container._cafe_service", mock_service)

    res = client.get(f"/api/v1/cafes/{TEST_UUID}")

    assert res.status_code == 500


def test_list_roasters_repo_error_returns_500(client, mocker):
    """Test GET /api/v1/roasters returns 500 when the service raises an unexpected exception."""
    mock_service = mocker.MagicMock()
    mock_service.get_all.side_effect = Exception("DB connection failed")
    mocker.patch("app.core.dependencies.container._roaster_service", mock_service)

    res = client.get("/api/v1/roasters")

    assert res.status_code == 500


def test_list_beans_repo_error_returns_500(client, mocker):
    """Test GET /api/v1/beans returns 500 when the service raises an unexpected exception."""
    mock_service = mocker.MagicMock()
    mock_service.search.side_effect = Exception("DB connection failed")
    mocker.patch("app.core.dependencies.container._bean_service", mock_service)

    res = client.get("/api/v1/beans")

    assert res.status_code == 500
