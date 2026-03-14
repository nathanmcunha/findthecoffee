from unittest.mock import MagicMock
from db.repository import CafeRepository

def test_search_uses_fts_when_query_provided(mock_db):
    """Verify that the search method constructs the FTS query when query_text is present."""
    repo = CafeRepository()
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": 1, "name": "Test Cafe", "relevance": 0.9, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result
    
    results = repo.search(query_text="specialty")
    
    # Check if the query contains FTS keywords
    call_args = mock_db.execute.call_args
    sql_query = call_args.args[0]
    # In CafeRepository, execute is called as execute(query, params_dict)
    # So the dict is the second positional argument
    params = call_args.args[1]
    
    assert "WITH matching_cafes" in sql_query
    assert "ts_rank" in sql_query
    assert "search_document @@ query" in sql_query
    assert params["q"] == "specialty"
    assert len(results) == 1
    assert results[0]["name"] == "Test Cafe"

def test_search_uses_ilike_when_no_query_provided(mock_db):
    """Verify that the search method uses a simple ILIKE query when no query_text is present."""
    repo = CafeRepository()
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = []
    mock_db.execute.return_value = mock_result
    
    repo.search(roast_level="Dark")
    
    call_args = mock_db.execute.call_args
    sql_query = call_args.args[0]
    
    assert "WITH matching_cafes" not in sql_query
    assert "b.roast_level = :roast_level" in sql_query

def test_search_fallback_logic_present_in_fts(mock_db):
    """Verify that the FTS query includes the ILIKE fallback for immediate results."""
    repo = CafeRepository()
    mock_db.execute.return_value = MagicMock()
    
    repo.search(query_text="new_cafe")
    
    call_args = mock_db.execute.call_args
    sql_query = call_args.args[0]
    params = call_args.args[1]
    
    # The hybrid search should contain both FTS and ILIKE fallback
    assert "m.cafe_id IS NOT NULL" in sql_query
    assert "c.name ILIKE :q_like" in sql_query
    assert params["q_like"] == "%new_cafe%"

def test_search_filters_out_null_beans(mock_db):
    """Verify that matching_beans is correctly aggregated even if empty."""
    repo = CafeRepository()
    
    mock_result = MagicMock()
    mock_result.mappings.return_value = [
        {"id": 1, "name": "Empty Cafe", "relevance": 0, "matching_beans": []}
    ]
    mock_db.execute.return_value = mock_result
    
    results = repo.search(query_text="empty")
    assert len(results) == 1
    assert results[0]["matching_beans"] == []
