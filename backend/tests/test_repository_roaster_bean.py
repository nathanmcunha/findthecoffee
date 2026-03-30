"""Repository tests for RoasterRepository and CoffeeBeanRepository.

Tests cover CRUD operations, search functionality, and data integrity
for roasters and coffee beans.
"""
import pytest
import uuid
from unittest.mock import MagicMock
from db.repository import RoasterRepository, CoffeeBeanRepository

DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0


# ============== RoasterRepository ==============


def test_roaster_get_all_returns_list(mock_db):
    """Verify get_all returns a list of roaster dictionaries."""
    repo = RoasterRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Roaster A", "website": None, "location": "Porto"}
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Roaster A"


def test_roaster_get_by_id_found(mock_db):
    """Verify get_by_id returns a dict when the roaster exists."""
    repo = RoasterRepository()
    row = {"id": uuid.UUID('00000000-0000-0000-0000-000000000001'), "name": "Roaster A", "website": None, "location": "Porto"}
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result == dict(row)


def test_roaster_get_by_id_not_found(mock_db):
    """Verify get_by_id returns None when no roaster matches the ID."""
    repo = RoasterRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result is None


def test_roaster_create_returns_uuid(mock_db):
    """Verify create returns the new roaster's UUID on success."""
    repo = RoasterRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    roaster_id = repo.create("New Roaster")

    assert roaster_id == uuid.UUID('00000000-0000-0000-0000-000000000001')


def test_roaster_create_raises_when_row_is_none(mock_db):
    """Verify create raises ValueError when the INSERT returns no row."""
    repo = RoasterRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Roaster")


def test_roaster_create_with_optional_fields(mock_db):
    """Verify create handles optional fields (website, location)."""
    repo = RoasterRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    roaster_id = repo.create("Roaster with Info", website="https://roaster.example.com", location="Lisbon")

    assert roaster_id == uuid.UUID('00000000-0000-0000-0000-000000000001')
    sql_query, params = mock_db.execute.call_args.args
    assert params["website"] == "https://roaster.example.com"
    assert params["location"] == "Lisbon"


# ============== CoffeeBeanRepository ==============


def test_bean_get_all_returns_list(mock_db):
    """Verify get_all returns a list of bean dictionaries with roaster info."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {
            "id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "name": "Bean A",
            "roast_level": "Dark",
            "origin": "Brazil",
            "roaster_id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "roaster_name": "Roaster A"
        }
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Bean A"


def test_bean_get_by_id_found(mock_db):
    """Verify get_by_id returns a dict when the bean exists."""
    repo = CoffeeBeanRepository()
    row = {
        "id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
        "name": "Bean A",
        "roast_level": "Dark",
        "origin": "Brazil",
        "roaster_id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
        "roaster_name": "Roaster A"
    }
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result == dict(row)


def test_bean_get_by_id_not_found(mock_db):
    """Verify get_by_id returns None when no bean matches the ID."""
    repo = CoffeeBeanRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(uuid.UUID('00000000-0000-0000-0000-000000000001'))

    assert result is None


def test_bean_create_returns_uuid(mock_db):
    """Verify create returns the new bean's UUID on success."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    bean_id = repo.create("New Bean", roast_level="Medium", origin="Colombia")

    assert bean_id == uuid.UUID('00000000-0000-0000-0000-000000000001')


def test_bean_create_raises_when_row_is_none(mock_db):
    """Verify create raises ValueError when the INSERT returns no row."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Bean")


def test_bean_create_with_all_optional_fields(mock_db):
    """Verify create handles all optional fields correctly."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.fetchone.return_value = (uuid.UUID('00000000-0000-0000-0000-000000000001'),)

    bean_id = repo.create(
        "Premium Bean",
        roast_level="Dark",
        origin="Ethiopia",
        variety="Yirgacheffe",
        processing="Washed",
        region="Yirgacheffe",
        tasting_notes=["Floral", "Citrus"],
        roaster_id=uuid.UUID('00000000-0000-0000-0000-000000000002')
    )

    assert bean_id == uuid.UUID('00000000-0000-0000-0000-000000000001')
    sql_query, params = mock_db.execute.call_args.args
    assert params["variety"] == "Yirgacheffe"
    assert params["processing"] == "Washed"
    assert params["tasting_notes"] == ["Floral", "Citrus"]


def test_bean_search_with_filters(mock_db):
    """Verify search passes roast_level and origin as params to the DB."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {
            "id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "name": "Dark Bean",
            "roast_level": "Dark",
            "origin": "Brazil",
            "roaster_id": uuid.UUID('00000000-0000-0000-0000-000000000001'),
            "roaster_name": "Roaster A"
        }
    ]

    results = repo.search(roast_level="Dark", origin="Brazil")

    assert len(results) == 1
    assert results[0]["roast_level"] == "Dark"
    _, params = mock_db.execute.call_args.args
    assert "roast_level" in params
    assert "origin" in params


def test_bean_search_with_all_filters(mock_db):
    """Verify search handles all filter parameters correctly."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = []

    repo.search(
        roast_level="Medium",
        origin="Colombia",
        roaster_id=uuid.UUID('00000000-0000-0000-0000-000000000001'),
        variety="Caturra",
        processing="Natural",
        region="Huila"
    )

    _, params = mock_db.execute.call_args.args
    assert params["roast_level"] == "Medium"
    # ILIKE filters use % wildcards
    assert params["origin"] == "%Colombia%"
    assert params["variety"] == "%Caturra%"
    assert params["processing"] == "%Natural%"
    assert params["region"] == "%Huila%"


def test_bean_search_default_pagination(mock_db):
    """Verify search uses default limit and offset when not provided."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = []

    repo.search()

    _, params = mock_db.execute.call_args.args
    assert params["limit"] == DEFAULT_LIMIT
    assert params["offset"] == DEFAULT_OFFSET


def test_bean_search_custom_pagination(mock_db):
    """Verify search respects custom limit and offset parameters."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = []

    repo.search(limit=20, offset=40)

    _, params = mock_db.execute.call_args.args
    assert params["limit"] == 20
    assert params["offset"] == 40
