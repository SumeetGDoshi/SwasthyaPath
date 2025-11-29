import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from main import app
from database.supabase_client import get_db

# Mock data
MOCK_USER_ID = "test-user-123"
MOCK_EMAIL = "test@example.com"
MOCK_PASSWORD = "securepassword123"
MOCK_HASHED_PASSWORD = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"



@pytest.fixture
def mock_db():
    """Mock database client"""
    mock = MagicMock()
    # Setup default behaviors
    mock.create_auth_user.return_value = {
        "id": MOCK_USER_ID,
        "email": MOCK_EMAIL,
        "name": "Test User"
    }
    mock.get_user_by_email.return_value = {
        "id": MOCK_USER_ID,
        "email": MOCK_EMAIL,
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW" # hashed "password123"
    }
    mock.verify_refresh_token.return_value = True
    return mock

@pytest.fixture
def auth_client(mock_db):
    """Test client with mocked database"""
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_signup_success(auth_client, mock_db):
    """Test successful user signup"""
    # Configure mock for this specific test if needed
    mock_db.get_user_by_email.return_value = None # User doesn't exist yet
    
    response = auth_client.post("/api/auth/signup", json={
        "email": MOCK_EMAIL,
        "password": MOCK_PASSWORD,
        "name": "Test User",
        "phone": "1234567890"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == MOCK_EMAIL
    assert "id" in data
    assert "access_token" in data
    assert "refresh_token" in data

def test_signup_duplicate_email(auth_client, mock_db):
    """Test signup with existing email"""
    mock_db.get_user_by_email.return_value = {"id": "existing"}
    
    response = auth_client.post("/api/auth/signup", json={
        "email": MOCK_EMAIL,
        "password": MOCK_PASSWORD,
        "name": "Test User"
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(auth_client, mock_db):
    """Test successful login"""
    # We need to mock verify_password since we're using a real hash but maybe different salt
    with patch('utils.auth_utils.verify_password', return_value=True):
        response = auth_client.post("/api/auth/login", json={
            "email": MOCK_EMAIL,
            "password": MOCK_PASSWORD
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert "refresh_token" in data

def test_login_invalid_credentials(auth_client, mock_db):
    """Test login with wrong password"""
    with patch('utils.auth_utils.verify_password', return_value=False):
        response = auth_client.post("/api/auth/login", json={
            "email": MOCK_EMAIL,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

def test_protected_route_access(auth_client):
    """Test accessing protected route with valid token"""
    # Create a valid token
    from utils.auth_utils import create_access_token
    token = create_access_token(data={"sub": MOCK_USER_ID})
    
    response = auth_client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_USER_ID
    assert data["email"] == MOCK_EMAIL

def test_protected_route_no_token(auth_client):
    """Test accessing protected route without token"""
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 403  # FastAPI returns 403 for missing bearer token

def test_refresh_token_success(auth_client, mock_db):
    """Test refreshing access token"""
    from utils.auth_utils import create_refresh_token
    refresh_token = create_refresh_token(data={"sub": MOCK_EMAIL, "user_id": MOCK_USER_ID})

    # Mock verify_token to return valid payload (since we can't easily rely on real verification if keys differ)
    with patch('utils.auth_utils.verify_token') as mock_verify_jwt:
        mock_verify_jwt.return_value = {"sub": MOCK_USER_ID, "type": "refresh"}
        
        response = auth_client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()
