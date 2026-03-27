import pytest
import uuid
from unittest.mock import MagicMock
from db.repository import CafeRepository

TEST_UUID = uuid.UUID('00000000-0000-0000-0000-000000000001')

def test_search_uses_fts_when_query_provided(mock_db):
    """Verify that the search method constructs the FTS query when query_text is present."""
    repo = CafeRepository()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": TEST_UUID, "name": "Test Cafe", "relevance": 0.9, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result

    results = repo.search(query_text="specialty")

    # Check if the query uses inline search_vector
    sql_query, params = mock_db.execute.call_args.args

    assert "search_vector" in sql_query
    assert params["q"] == "specialty"
    assert params["limit"] == 50
    assert params["offset"] == 0
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

    # Verify the ILIKE fallback is present alongside FTS matching
    assert "c.name ILIKE :q_like" in sql_query
    assert params["q_like"] == "%new_cafe%"

def test_search_returns_empty_matching_beans(mock_db):
    """Verify that matching_beans is correctly aggregated even if empty."""
    repo = CafeRepository()

    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": TEST_UUID, "name": "Empty Cafe", "relevance": 0, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result

    results = repo.search(query_text="empty")
    assert len(results) == 1
    assert results[0]["matching_beans"] == []


# ============== CafeRepository CRUD ==============


def test_cafe_get_all_returns_list(mock_db):
    repo = CafeRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": TEST_UUID, "name": "Cafe A", "location": "Porto", "website": None}
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Cafe A"


def test_cafe_get_by_id_found(mock_db):
    repo = CafeRepository()
    row = {"id": TEST_UUID, "name": "Cafe A", "location": "Porto", "website": None}
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(TEST_UUID)

    assert result == dict(row)


def test_cafe_get_by_id_not_found(mock_db):
    repo = CafeRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(TEST_UUID)

    assert result is None


def test_cafe_create_returns_uuid(mock_db):
    repo = CafeRepository()
    mock_db.execute.return_value.fetchone.return_value = (TEST_UUID,)

    cafe_id = repo.create("New Cafe", "Lisbon")

    assert cafe_id == TEST_UUID


def test_cafe_create_raises_when_row_is_none(mock_db):
    repo = CafeRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Cafe")


def test_cafe_get_inventory_returns_list(mock_db):
    repo = CafeRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": TEST_UUID, "name": "Bean A", "roast_level": "Dark", "origin": "Brazil", "roaster_id": TEST_UUID, "roaster_name": "Roaster X"}
    ]

    results = repo.get_inventory(TEST_UUID)

    assert len(results) == 1
    assert results[0]["name"] == "Bean A"


def test_cafe_add_to_inventory_executes(mock_db):
    repo = CafeRepository()

    repo.add_to_inventory(TEST_UUID, TEST_UUID)

    mock_db.execute.assert_called_once()
