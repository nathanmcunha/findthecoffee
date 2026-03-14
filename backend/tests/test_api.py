import pytest
from main import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_ping(client):
    """Test health check endpoint."""
    res = client.get('/ping')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'online'

def test_add_cafe_validation_error(client):
    """Test that POST /api/cafes fails with invalid data (missing name)."""
    res = client.post('/api/cafes', json={})
    assert res.status_code == 400
    assert "Validation Error" in res.get_json()['error']

def test_add_cafe_success(client, mocker):
    """Test that POST /api/cafes succeeds with valid data."""
    # Patch the global instance repo inside the main module
    mocker.patch('main.cafe_repo.create', return_value=99)
    
    res = client.post('/api/cafes', json={
        "name": "Testing Cafe",
        "location": "Internet"
    })
    
    assert res.status_code == 201
    assert res.get_json()['id'] == 99
    assert res.get_json()['status'] == 'created'

def test_list_cafes_with_filters(client, mocker):
    """Test that GET /api/cafes passes filters correctly to the repository."""
    mock_search = mocker.patch('main.cafe_repo.search', return_value=[])
    
    # Call with filters
    client.get('/api/cafes?q=test&roast=Dark&roaster_id=1')
    
    # Verify repository was called with correct arguments
    mock_search.assert_called_once_with(
        roast_level="Dark",
        origin=None,
        roaster_id=1,
        cafe_name=None,
        query_text="test"
    )
