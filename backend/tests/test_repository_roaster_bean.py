import pytest
from unittest.mock import MagicMock
from db.repository import RoasterRepository, CoffeeBeanRepository


# ============== RoasterRepository ==============


def test_roaster_get_all_returns_list(mock_db):
    """Verify get_all returns a list of roaster dicts."""
    repo = RoasterRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": 1, "name": "Roaster A", "website": None, "location": "Porto"}
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Roaster A"


def test_roaster_get_by_id_found(mock_db):
    """Verify get_by_id returns a dict when the roaster exists."""
    repo = RoasterRepository()
    row = {"id": 1, "name": "Roaster A", "website": None, "location": "Porto"}
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(1)

    assert result == dict(row)


def test_roaster_get_by_id_not_found(mock_db):
    """Verify get_by_id returns None when no roaster matches the ID."""
    repo = RoasterRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(999)

    assert result is None


def test_roaster_create_returns_id(mock_db):
    """Verify create returns the new roaster's ID on success."""
    repo = RoasterRepository()
    mock_db.execute.return_value.fetchone.return_value = (7,)

    roaster_id = repo.create("New Roaster")

    assert roaster_id == 7


def test_roaster_create_raises_when_row_is_none(mock_db):
    """Verify create raises ValueError when the INSERT returns no row."""
    repo = RoasterRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Roaster")


# ============== CoffeeBeanRepository ==============


def test_bean_get_all_returns_list(mock_db):
    """Verify get_all returns a list of bean dicts with roaster info."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": 1, "name": "Bean A", "roast_level": "Dark", "origin": "Brazil", "roaster_id": 1, "roaster_name": "Roaster A"}
    ]

    results = repo.get_all()

    assert len(results) == 1
    assert results[0]["name"] == "Bean A"


def test_bean_get_by_id_found(mock_db):
    """Verify get_by_id returns a dict when the bean exists."""
    repo = CoffeeBeanRepository()
    row = {"id": 1, "name": "Bean A", "roast_level": "Dark", "origin": "Brazil", "roaster_id": 1, "roaster_name": "Roaster A"}
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = row
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(1)

    assert result == dict(row)


def test_bean_get_by_id_not_found(mock_db):
    """Verify get_by_id returns None when no bean matches the ID."""
    repo = CoffeeBeanRepository()
    mock_mappings = MagicMock()
    mock_mappings.fetchone.return_value = None
    mock_db.execute.return_value.mappings.return_value = mock_mappings

    result = repo.get_by_id(999)

    assert result is None


def test_bean_create_returns_id(mock_db):
    """Verify create returns the new bean's ID on success."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.fetchone.return_value = (12,)

    bean_id = repo.create("New Bean", roast_level="Medium", origin="Colombia")

    assert bean_id == 12


def test_bean_create_raises_when_row_is_none(mock_db):
    """Verify create raises ValueError when the INSERT returns no row."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError):
        repo.create("Ghost Bean")


def test_bean_search_with_filters(mock_db):
    """Verify search passes roast_level and origin as params to the DB execute call."""
    repo = CoffeeBeanRepository()
    mock_db.execute.return_value.mappings.return_value = [
        {"id": 1, "name": "Dark Bean", "roast_level": "Dark", "origin": "Brazil", "roaster_id": 1, "roaster_name": "Roaster A"}
    ]

    results = repo.search(roast_level="Dark", origin="Brazil")

    assert len(results) == 1
    assert results[0]["roast_level"] == "Dark"
    _, params = mock_db.execute.call_args.args  # (query_str, params_dict)
    assert "roast_level" in params
    assert "origin" in params
