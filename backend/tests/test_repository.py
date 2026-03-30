"""Repository layer tests for FindTheCoffee backend.

Tests cover CafeRepository search, CRUD operations, soft delete behavior,
geolocation filtering, and full-text search functionality.
"""
import pytest
import uuid
from unittest.mock import MagicMock
from db.repository import CafeRepository

DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0


def test_search_uses_fts_when_query_provided(mock_db):
    """Verify that the search method constructs the FTS query when query_text is present."""
    repo = CafeRepository()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Test Cafe", "relevance": 0.9, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result

    results = repo.search(query_text="specialty")

    sql_query, params = mock_db.execute.call_args.args

    assert "search_vector" in sql_query
    assert params["q"] == "specialty"
    assert params["limit"] == DEFAULT_LIMIT
    assert params["offset"] == DEFAULT_OFFSET
    assert len(results) == 1
    assert results[0]["name"] == "Test Cafe"


def test_search_uses_ilike_when_no_query_provided(mock_db):
    """Verify that the search method uses a simple ILIKE query when no query_text is present."""
    repo = CafeRepository()

    mock_result = MagicMock()
    mock_result.mappings.return_value = []
    mock_db.execute.return_value = mock_result

    repo.search(roast_level="Dark")

    sql_query, _ = mock_db.execute.call_args.args

    assert "WITH matching_cafes" not in sql_query
    assert "b.roast_level = :roast_level" in sql_query


def test_search_fallback_logic_present_in_fts(mock_db):
    """Verify that the FTS query includes the ILIKE fallback for immediate results."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search(query_text="new_cafe")

    sql_query, params = mock_db.execute.call_args.args

    assert "c.name ILIKE :q_like" in sql_query
    assert params["q_like"] == "%new_cafe%"


def test_search_returns_empty_matching_beans(mock_db):
    """Verify that matching_beans is correctly aggregated even if empty."""
    repo = CafeRepository()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Empty Cafe", "relevance": 0, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result

    results = repo.search(query_text="empty")
    assert len(results) == 1
    assert results[0]["matching_beans"] == []


# ============== SOFT DELETE TESTS ==============


def test_search_excludes_soft_deleted_cafes(mock_db):
    """Verify that search excludes cafes where deleted_at is not NULL."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search()

    sql_query, _ = mock_db.execute.call_args.args

    assert "deleted_at IS NULL" in sql_query


def test_get_all_excludes_soft_deleted(mock_db):
    """Verify that get_all excludes soft-deleted cafes."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.get_all()

    sql_query, _ = mock_db.execute.call_args.args

    assert "deleted_at IS NULL" in sql_query


def test_get_by_id_excludes_soft_deleted(mock_db):
    """Verify that get_by_id excludes soft-deleted cafes."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    test_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    repo.get_by_id(test_id)

    sql_query, _ = mock_db.execute.call_args.args

    assert "deleted_at IS NULL" in sql_query


# ============== GEOLOCATION TESTS ==============


def test_search_nearby_uses_haversine(mock_db):
    """Verify that search_nearby uses Haversine formula for distance calculation."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search_nearby(lat=37.7749, lng=-122.4194, radius_m=5000)

    sql_query, params = mock_db.execute.call_args.args

    # Verify Haversine formula components are present
    assert "6371000" in sql_query  # Earth radius in meters
    assert "radians" in sql_query.lower()
    assert "acos" in sql_query.lower()
    assert params["lat"] == 37.7749
    assert params["lng"] == -122.4194
    assert params["radius"] == 5000


def test_search_nearby_default_radius(mock_db):
    """Verify that search_nearby uses default 5000m radius when not specified."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search_nearby(lat=37.7749, lng=-122.4194)

    _, params = mock_db.execute.call_args.args
    assert params["radius"] == 5000


def test_search_nearby_custom_radius(mock_db):
    """Verify that search_nearby respects custom radius parameter."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search_nearby(lat=37.7749, lng=-122.4194, radius_m=1000)

    _, params = mock_db.execute.call_args.args
    assert params["radius"] == 1000


# ============== PAGINATION TESTS ==============


def test_search_respects_limit_parameter(mock_db):
    """Verify that search respects custom limit parameter."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search(limit=10)

    _, params = mock_db.execute.call_args.args

    assert params["limit"] == 10


def test_search_respects_offset_parameter(mock_db):
    """Verify that search respects custom offset parameter."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search(offset=100)

    _, params = mock_db.execute.call_args.args

    assert params["offset"] == 100


def test_search_default_pagination(mock_db):
    """Verify that search uses default limit and offset when not provided."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()

    repo.search()

    _, params = mock_db.execute.call_args.args

    assert params["limit"] == DEFAULT_LIMIT
    assert params["offset"] == DEFAULT_OFFSET


# ============== CafeRepository CRUD ==============


def test_cafe_get_all_returns_list(mock_db):
    """Verify get_all returns a list of cafe dictionaries."""
    repo = CafeRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Cafe A", "location": "Porto", "website": None}
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Cafe A"


def test_cafe_get_by_id_found(mock_db):
    """Verify get_by_id returns a dict when the cafe exists."""
    repo = CafeRepository()
    row = {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Cafe A", "location": "Porto", "website": None}
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result == dict(row)


def test_cafe_get_by_id_not_found(mock_db):
    """Verify get_by_id returns None when no cafe matches the ID."""
    repo = CafeRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result is None


def test_cafe_create_returns_uuid(mock_db):
    """Verify create returns the new cafe's UUID on success."""
    repo = CafeRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    cafe_id = repo.create("New Cafe", "Lisbon")

    assert cafe_id == uuid.UUID('00000000-0000-0000-0000-000000000001')


def test_cafe_create_raises_when_row_is_none(mock_db):
    """Verify create raises ValueError when the INSERT returns no row."""
    repo = CafeRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Cafe")


def test_cafe_create_with_optional_fields(mock_db):
    """Verify create handles optional fields (website)."""
    repo = CafeRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    cafe_id = repo.create(
        "Cafe with Website",
        "Porto",
        website="https://cafe.example.com"
    )

    assert cafe_id == uuid.UUID('00000000-0000-0000-0000-000000000001')
    sql_query, params = mock_db.execute.call_args.args
    assert params["website"] == "https://cafe.example.com"
    assert params["location"] == "Porto"


def test_cafe_get_inventory_returns_list(mock_db):
    """Verify get_inventory returns a list of beans with roaster info."""
    repo = CafeRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {
            "id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "name": "Bean A",
            "roast_level": "Dark",
            "origin": "Brazil",
            "roaster_id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "roaster_name": "Roaster X"
        }
    ]

    results = repo.get_inventory(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert len(results) == 1
    assert results[0]["name"] == "Bean A"


def test_cafe_add_to_inventory_executes(mock_db):
    """Verify add_to_inventory executes the INSERT statement."""
    repo = CafeRepository()

    repo.add_to_inventory(uuid.UUID('00000000-0000-0000-0000-000000000001'), uuid.UUID('00000000-0000-0000-0000-000000000002'))

    mock_db.execute.assert_called_once()
