import pytest
import io
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestReportsAPI:
    """Test reports API endpoints."""
    
    def test_get_reports(self, client, auth_headers, sample_report):
        """Test getting list of reports."""
        response = client.get("/api/reports", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["title"] == "Test Sustainability Report"
    
    def test_get_reports_with_filters(self, client, auth_headers, sample_report):
        """Test getting reports with filters."""
        response = client.get(
            "/api/reports", 
            headers=auth_headers,
            params={"year": 2023, "report_type": "sustainability"}
        )
        
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["year"] == 2023
            assert item["report_type"] == "sustainability"
    
    def test_get_report_by_id(self, client, auth_headers, sample_report):
        """Test getting report by ID."""
        response = client.get(
            f"/api/reports/{sample_report.id}", 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_report.id
        assert data["title"] == "Test Sustainability Report"
    
    def test_create_report(self, client, auth_headers, sample_organization):
        """Test creating a new report."""
        report_data = {
            "title": "Annual Report 2023",
            "organization_id": sample_organization.id,
            "year": 2023,
            "report_type": "annual",
            "description": "Annual sustainability report"
        }
        
        response = client.post(
            "/api/reports", 
            headers=auth_headers,
            json=report_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Annual Report 2023"
        assert data["year"] == 2023
        assert data["report_type"] == "annual"
    
    def test_upload_report(self, client, auth_headers, sample_organization, sample_file_upload):
        """Test uploading a report file."""
        form_data = {
            "title": "Uploaded Report",
            "organization_id": str(sample_organization.id),
            "year": "2023",
            "report_type": "sustainability"
        }
        
        response = client.post(
            "/api/reports/upload",
            headers=auth_headers,
            data=form_data,
            files=sample_file_upload
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Uploaded Report"
        assert data["status"] == "uploaded"
    
    def test_fetch_report_from_url(self, client, auth_headers, sample_organization):
        """Test fetching report from URL."""
        fetch_data = {
            "title": "Remote Report",
            "organization_id": sample_organization.id,
            "year": 2023,
            "report_type": "sustainability",
            "url": "https://example.com/report.pdf"
        }
        
        response = client.post(
            "/api/reports/fetch",
            headers=auth_headers,
            json=fetch_data
        )
        
        assert response.status_code == 202  # Accepted for background processing
        data = response.json()
        assert "job_id" in data
    
    def test_get_report_chunks(self, client, auth_headers, sample_report, sample_embedding):
        """Test getting report chunks."""
        response = client.get(
            f"/api/reports/{sample_report.id}/chunks",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
    
    def test_update_report(self, client, auth_headers, sample_report):
        """Test updating a report."""
        update_data = {
            "title": "Updated Report Title",
            "description": "Updated description"
        }
        
        response = client.put(
            f"/api/reports/{sample_report.id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Report Title"
    
    def test_delete_report(self, client, auth_headers, sample_report):
        """Test deleting a report."""
        response = client.delete(
            f"/api/reports/{sample_report.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
