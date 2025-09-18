import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestOrganizationsAPI:
    """Test organizations API endpoints."""
    
    def test_get_organizations(self, client, auth_headers, sample_organization):
        """Test getting list of organizations."""
        response = client.get("/api/organizations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == "Test Organization"
    
    def test_get_organizations_with_filters(self, client, auth_headers, sample_organization):
        """Test getting organizations with filters."""
        response = client.get(
            "/api/organizations", 
            headers=auth_headers,
            params={"industry": "Technology", "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5
    
    def test_get_organization_by_id(self, client, auth_headers, sample_organization):
        """Test getting organization by ID."""
        response = client.get(
            f"/api/organizations/{sample_organization.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_organization.id
        assert data["name"] == "Test Organization"
    
    def test_get_organization_not_found(self, client, auth_headers):
        """Test getting non-existent organization."""
        response = client.get("/api/organizations/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_create_organization(self, client, auth_headers):
        """Test creating a new organization."""
        org_data = {
            "name": "New Test Corp",
            "industry": "Finance",
            "size": "large",
            "description": "A new test organization",
            "website": "https://newtestcorp.com"
        }
        
        response = client.post(
            "/api/organizations", 
            headers=auth_headers,
            json=org_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Corp"
        assert data["industry"] == "Finance"
        assert data["size"] == "large"
    
    def test_create_organization_invalid_data(self, client, auth_headers):
        """Test creating organization with invalid data."""
        org_data = {
            "industry": "Technology"
            # Missing required name field
        }
        
        response = client.post(
            "/api/organizations", 
            headers=auth_headers,
            json=org_data
        )
        
        assert response.status_code == 422
    
    def test_update_organization(self, client, auth_headers, sample_organization):
        """Test updating an organization."""
        update_data = {
            "name": "Updated Organization",
            "industry": "Healthcare",
            "description": "Updated description"
        }
        
        response = client.put(
            f"/api/organizations/{sample_organization.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Organization"
        assert data["industry"] == "Healthcare"
    
    def test_delete_organization(self, client, auth_headers, sample_organization):
        """Test deleting an organization."""
        response = client.delete(
            f"/api/organizations/{sample_organization.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify organization is deleted
        get_response = client.get(
            f"/api/organizations/{sample_organization.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_get_organization_stats(self, client, auth_headers, sample_organization, sample_report):
        """Test getting organization statistics."""
        response = client.get(
            f"/api/organizations/{sample_organization.id}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reports_count" in data
        assert "kpis_count" in data
        assert data["reports_count"] >= 1
    
    def test_unauthorized_access(self, client, sample_organization):
        """Test accessing organizations without authentication."""
        response = client.get("/api/organizations")
        assert response.status_code == 401
        
        response = client.post("/api/organizations", json={"name": "Test"})
        assert response.status_code == 401
