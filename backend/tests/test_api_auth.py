import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_mock_login_success(self, client):
        """Test successful mock login."""
        response = client.post("/api/auth/mock-login", json={
            "email": "test@example.com",
            "name": "Test User"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_mock_login_invalid_data(self, client):
        """Test mock login with invalid data."""
        response = client.post("/api/auth/mock-login", json={
            "email": "invalid-email",
            "name": ""
        })
        
        assert response.status_code == 422
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    def test_validate_token(self, client, auth_headers):
        """Test token validation."""
        response = client.get("/api/auth/validate", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    def test_validate_invalid_token(self, client):
        """Test validation with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/auth/validate", headers=headers)
        
        assert response.status_code == 401
