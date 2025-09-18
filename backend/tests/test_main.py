import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
class TestMainApp:
    """Test main application functionality."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Check for some expected metrics
        content = response.text
        assert "http_requests_total" in content or "process_" in content
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/organizations")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_request_id_middleware(self, client):
        """Test request ID middleware."""
        response = client.get("/health")
        
        assert response.status_code == 200
        # Request ID should be added by middleware
        assert "x-request-id" in response.headers or "X-Request-ID" in response.headers
    
    def test_api_documentation(self, client):
        """Test API documentation endpoints."""
        # OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "EcoBench API"
        
        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
