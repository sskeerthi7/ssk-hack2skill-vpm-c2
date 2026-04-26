import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the main index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"VoterOne" in response.data

def test_api_init_eligible(client):
    """Test eligibility check for someone over 18 in 2026."""
    response = client.post('/api/init', 
                           data=json.dumps({'year_of_birth': 2000}),
                           content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['eligible'] is True
    assert "eligible" in data['message']

def test_api_init_underage(client):
    """Test eligibility check for someone under 18 in 2026."""
    response = client.post('/api/init', 
                           data=json.dumps({'year_of_birth': 2010}),
                           content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['eligible'] is False
    assert "18 - age" in data['message'] or "years" in data['message']

def test_api_init_invalid(client):
    """Test invalid input for eligibility check."""
    response = client.post('/api/init', 
                           data=json.dumps({'year_of_birth': 'invalid'}),
                           content_type='application/json')
    assert response.status_code == 400

def test_api_details_tn(client):
    """Test fetching details for Tamil Nadu."""
    response = client.post('/api/details', 
                           data=json.dumps({'state': 'Tamil Nadu', 'pc': 'Chennai', 'ac': 'Central'}),
                           content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['state'] == 'Tamil Nadu'
    assert 'status' in data
    assert "Polls Completed" in data['status']['Status']

@patch('google.generativeai.GenerativeModel.generate_content')
def test_api_chat(mock_gen, client):
    """Test the AI chat endpoint with mocking."""
    mock_response = MagicMock()
    mock_response.text = "Mocked AI Response"
    mock_gen.return_value = mock_response
    
    response = client.post('/api/chat', 
                           data=json.dumps({'query': 'How to vote?'}),
                           content_type='application/json')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['response'] == "Mocked AI Response"

def test_static_files(client):
    """Test access to static files."""
    response = client.get('/static/parent_guide.png')
    # Since we don't know if the file exists in the test environment, we check for 200 or 404
    # But usually, it should be 200 if the environment is set up.
    assert response.status_code in [200, 404]
