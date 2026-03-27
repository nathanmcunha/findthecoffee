import uuid
from tests.conftest import TEST_API_KEY

AUTH = {"X-API-Key": TEST_API_KEY}
TEST_UUID = str(uuid.UUID('00000000-0000-0000-0000-000000000001'))
TEST_UUID_2 = str(uuid.UUID('00000000-0000-0000-0000-000000000002'))
TEST_UUID_3 = str(uuid.UUID('00000000-0000-0000-0000-000000000003'))


def test_ping(client):
    """Test health check endpoint."""
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.get_json()["status"] == "online"


def test_add_cafe_validation_error(client):
    """Test that POST /api/cafes fails with invalid data (missing name)."""
    res = client.post("/api/cafes", json={}, headers=AUTH)
    assert res.status_code == 400
    assert "Validation Error" in res.get_json()["error"]


def test_add_cafe_requires_auth(client):
    """Test that POST /api/cafes returns 401 without a valid API key."""
    res = client.post("/api/cafes", json={"name": "Test"})
    assert res.status_code == 401


def test_add_cafe_success(client, mocker):
    """Test that POST /api/cafes succeeds with valid data."""
    mocker.patch("main.cafe_repo.create", return_value=uuid.UUID(TEST_UUID))

    res = client.post(
        "/api/cafes", json={"name": "Testing Cafe", "location": "Internet"}, headers=AUTH
    )

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


def test_add_cafe_rejects_invalid_website(client):
    """Test that POST /api/cafes rejects a non-HTTP website URL."""
    res = client.post(
        "/api/cafes",
        json={"name": "Bad Cafe", "website": "javascript:alert(1)"},
        headers=AUTH,
    )
    assert res.status_code == 400


def test_list_cafes_with_filters(client, mocker):
    """Test that GET /api/cafes passes filters correctly to the repository."""
    mock_search = mocker.patch("main.cafe_repo.search", return_value=[])

    res = client.get(f"/api/cafes?q=test&roast=Dark&roaster_id={TEST_UUID}")

    assert res.status_code == 200
    mock_search.assert_called_once_with(
        roast_level="Dark", origin=None, roaster_id=uuid.UUID(TEST_UUID), cafe_name=None, query_text="test", limit=50, offset=0
    )


def test_list_cafes_no_filters_calls_search(client, mocker):
    """Test that GET /api/cafes with no filters calls search with all-None params."""
    mock_search = mocker.patch("main.cafe_repo.search", return_value=[])

    res = client.get("/api/cafes")

    assert res.status_code == 200
    mock_search.assert_called_once_with(
        roast_level=None, origin=None, roaster_id=None, cafe_name=None, query_text=None, limit=50, offset=0
    )


def test_get_cafe_success(client, mocker):
    """Test GET /api/cafes/<id> returns the cafe when found."""
    mocker.patch("main.cafe_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Test Cafe", "location": "Porto", "website": None})

    res = client.get(f"/api/cafes/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Test Cafe"


def test_get_cafe_not_found(client, mocker):
    """Test GET /api/cafes/<id> returns 404 when not found."""
    mocker.patch("main.cafe_repo.get_by_id", return_value=None)

    res = client.get(f"/api/cafes/{TEST_UUID}")

    assert res.status_code == 404


def test_get_cafe_inventory_success(client, mocker):
    """Test GET /api/cafes/<id>/inventory returns inventory when cafe exists."""
    mocker.patch("main.cafe_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Test Cafe"})
    mocker.patch("main.cafe_repo.get_inventory", return_value=[{"id": uuid.UUID(TEST_UUID_2), "name": "Dark Roast"}])

    res = client.get(f"/api/cafes/{TEST_UUID}/inventory")

    assert res.status_code == 200
    assert len(res.get_json()) == 1


def test_get_cafe_inventory_not_found(client, mocker):
    """Test GET /api/cafes/<id>/inventory returns 404 when cafe not found."""
    mocker.patch("main.cafe_repo.get_by_id", return_value=None)

    res = client.get(f"/api/cafes/{TEST_UUID}/inventory")

    assert res.status_code == 404


# ============== ROASTER ENDPOINT TESTS ==============


def test_list_roasters(client, mocker):
    """Test GET /api/roasters returns a list."""
    mocker.patch("main.roaster_repo.get_all", return_value=[{"id": uuid.UUID(TEST_UUID), "name": "Roaster A"}])

    res = client.get("/api/roasters")

    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 1
    assert data["page"] == 1
    assert data["per_page"] == 50


def test_get_roaster_success(client, mocker):
    """Test GET /api/roasters/<id> returns the roaster when found."""
    mocker.patch("main.roaster_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Roaster A", "website": None, "location": None})

    res = client.get(f"/api/roasters/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Roaster A"


def test_get_roaster_not_found(client, mocker):
    """Test GET /api/roasters/<id> returns 404 when not found."""
    mocker.patch("main.roaster_repo.get_by_id", return_value=None)

    res = client.get(f"/api/roasters/{TEST_UUID}")

    assert res.status_code == 404


def test_add_roaster_success(client, mocker):
    """Test POST /api/roasters creates a roaster and returns its ID."""
    mocker.patch("main.roaster_repo.create", return_value=uuid.UUID(TEST_UUID))

    res = client.post("/api/roasters", json={"name": "New Roaster"}, headers=AUTH)

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


def test_add_roaster_validation_error(client):
    """Test POST /api/roasters fails with missing name."""
    res = client.post("/api/roasters", json={}, headers=AUTH)

    assert res.status_code == 400
    assert "Validation Error" in res.get_json()["error"]


def test_add_roaster_requires_auth(client):
    """Test that POST /api/roasters returns 401 without a valid API key."""
    res = client.post("/api/roasters", json={"name": "New Roaster"})
    assert res.status_code == 401


# ============== BEAN ENDPOINT TESTS ==============


def test_list_beans(client, mocker):
    """Test GET /api/beans returns a list."""
    mocker.patch("main.bean_repo.search", return_value=[{"id": uuid.UUID(TEST_UUID), "name": "Bean A"}])

    res = client.get("/api/beans")

    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 1
    assert data["page"] == 1
    assert data["per_page"] == 50


def test_get_bean_success(client, mocker):
    """Test GET /api/beans/<id> returns the bean when found."""
    mocker.patch("main.bean_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Bean A", "roast_level": "Dark"})

    res = client.get(f"/api/beans/{TEST_UUID}")

    assert res.status_code == 200
    assert res.get_json()["name"] == "Bean A"


def test_get_bean_not_found(client, mocker):
    """Test GET /api/beans/<id> returns 404 when not found."""
    mocker.patch("main.bean_repo.get_by_id", return_value=None)

    res = client.get(f"/api/beans/{TEST_UUID}")

    assert res.status_code == 404


def test_add_bean_success(client, mocker):
    """Test POST /api/beans creates a bean and returns its ID."""
    mocker.patch("main.bean_repo.create", return_value=uuid.UUID(TEST_UUID))

    res = client.post("/api/beans", json={"name": "New Bean"}, headers=AUTH)

    assert res.status_code == 201
    assert res.get_json()["id"] == TEST_UUID
    assert res.get_json()["status"] == "created"


def test_add_bean_validation_error(client):
    """Test POST /api/beans fails with missing name."""
    res = client.post("/api/beans", json={}, headers=AUTH)

    assert res.status_code == 400
    assert "Validation Error" in res.get_json()["error"]


def test_add_bean_requires_auth(client):
    """Test that POST /api/beans returns 401 without a valid API key."""
    res = client.post("/api/beans", json={"name": "New Bean"})
    assert res.status_code == 401


# ============== INVENTORY POST TESTS ==============


def test_add_to_inventory_success(client, mocker):
    """Test POST /api/cafes/<id>/inventory adds a bean to inventory."""
    mocker.patch("main.cafe_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Test Cafe"})
    mocker.patch("main.bean_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID_2), "name": "Bean A"})
    mocker.patch("main.cafe_repo.add_to_inventory")

    res = client.post(f"/api/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 200
    assert res.get_json()["status"] == "success"


def test_add_to_inventory_cafe_not_found(client, mocker):
    """Test POST /api/cafes/<id>/inventory returns 404 when cafe not found."""
    mocker.patch("main.cafe_repo.get_by_id", return_value=None)

    res = client.post(f"/api/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 404


def test_add_to_inventory_bean_not_found(client, mocker):
    """Test POST /api/cafes/<id>/inventory returns 404 when bean not found."""
    mocker.patch("main.cafe_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Test Cafe"})
    mocker.patch("main.bean_repo.get_by_id", return_value=None)

    res = client.post(f"/api/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2}, headers=AUTH)

    assert res.status_code == 404


def test_add_to_inventory_missing_bean_id(client, mocker):
    """Test POST /api/cafes/<id>/inventory returns 400 when bean_id is absent from body."""
    mocker.patch("main.cafe_repo.get_by_id", return_value={"id": uuid.UUID(TEST_UUID), "name": "Test Cafe"})

    res = client.post(f"/api/cafes/{TEST_UUID}/inventory", json={}, headers=AUTH)

    assert res.status_code == 400
    assert "Validation Error" in res.get_json()["error"]


def test_add_to_inventory_requires_auth(client):
    """Test that POST /api/cafes/<id>/inventory returns 401 without a valid API key."""
    res = client.post(f"/api/cafes/{TEST_UUID}/inventory", json={"bean_id": TEST_UUID_2})
    assert res.status_code == 401


def test_list_beans_no_filters_still_calls_search(client, mocker):
    """Test that GET /api/beans with no filters always routes through search."""
    mock_search = mocker.patch("main.bean_repo.search", return_value=[])

    res = client.get("/api/beans")

    assert res.status_code == 200
    mock_search.assert_called_once_with(roast_level=None, origin=None, roaster_id=None, limit=50, offset=0)


# ============== 500 ERROR PATH TESTS ==============


def test_list_cafes_repo_error_returns_500(client, mocker):
    """Test GET /api/cafes returns 500 when the repository raises an unexpected exception."""
    mocker.patch("main.cafe_repo.search", side_effect=Exception("DB connection failed"))

    res = client.get("/api/cafes")

    assert res.status_code == 500
    # Internal error details must NOT be exposed to the caller
    assert "DB connection failed" not in res.get_json().get("error", "")


def test_get_cafe_repo_error_returns_500(client, mocker):
    """Test GET /api/cafes/<id> returns 500 when the repository raises an unexpected exception."""
    mocker.patch("main.cafe_repo.get_by_id", side_effect=Exception("DB connection failed"))

    res = client.get(f"/api/cafes/{TEST_UUID}")

    assert res.status_code == 500


def test_list_roasters_repo_error_returns_500(client, mocker):
    """Test GET /api/roasters returns 500 when the repository raises an unexpected exception."""
    mocker.patch("main.roaster_repo.get_all", side_effect=Exception("DB connection failed"))

    res = client.get("/api/roasters")

    assert res.status_code == 500


def test_list_beans_repo_error_returns_500(client, mocker):
    """Test GET /api/beans returns 500 when the repository raises an unexpected exception."""
    mocker.patch("main.bean_repo.search", side_effect=Exception("DB connection failed"))

    res = client.get("/api/beans")

    assert res.status_code == 500
