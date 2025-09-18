import pytest
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.utils.logging import get_logger, audit_logger, performance_logger, LoggingMixin
from app.utils.metrics import MetricsCollector, get_metrics
from app.middleware.monitoring import RequestTrackingMiddleware


@pytest.mark.unit
class TestLogging:
    """Test logging utilities."""
    
    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_audit_logger(self):
        """Test audit logger functionality."""
        with patch.object(audit_logger.logger, 'info') as mock_info:
            audit_logger.log_user_action(
                user_id=1,
                action="create",
                resource_type="organization",
                resource_id=123,
                details={"name": "Test Org"}
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert call_args[0][0] == "User action"
            assert call_args[1]["user_id"] == 1
            assert call_args[1]["action"] == "create"
            assert call_args[1]["resource_type"] == "organization"
    
    def test_performance_logger(self):
        """Test performance logger functionality."""
        with patch.object(performance_logger.logger, 'info') as mock_info:
            performance_logger.log_api_performance(
                endpoint="/api/organizations",
                method="GET",
                duration=0.123,
                status_code=200,
                user_id=1
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            assert call_args[0][0] == "API request"
            assert call_args[1]["endpoint"] == "/api/organizations"
            assert call_args[1]["duration_ms"] == 123.0
    
    def test_logging_mixin(self):
        """Test logging mixin functionality."""
        class TestService(LoggingMixin):
            def test_operation(self):
                self.log_operation("test_op", param1="value1")
                self.log_success("test_op", duration=0.1, result="success")
        
        service = TestService()
        assert hasattr(service, 'logger')
        
        with patch.object(service.logger, 'info') as mock_info:
            service.test_operation()
            assert mock_info.call_count == 2


@pytest.mark.unit
class TestMetrics:
    """Test metrics collection."""
    
    def test_metrics_collector_http_request(self):
        """Test HTTP request metrics recording."""
        # This will increment the actual metrics
        MetricsCollector.record_http_request("GET", "/api/test", 200, 0.1)
        
        # Check that metrics are generated
        metrics_output = get_metrics()
        assert "http_requests_total" in metrics_output
        assert "http_request_duration_seconds" in metrics_output
    
    def test_metrics_collector_database_query(self):
        """Test database query metrics recording."""
        MetricsCollector.record_database_query("SELECT", "organizations", 0.05)
        
        metrics_output = get_metrics()
        assert "database_queries_total" in metrics_output
        assert "database_query_duration_seconds" in metrics_output
    
    def test_metrics_collector_llm_operation(self):
        """Test LLM operation metrics recording."""
        MetricsCollector.record_llm_operation(
            "embedding", "openai", "success", 0.5, 100
        )
        
        metrics_output = get_metrics()
        assert "llm_operations_total" in metrics_output
        assert "llm_operation_duration_seconds" in metrics_output
        assert "llm_token_usage_total" in metrics_output
    
    def test_metrics_collector_file_upload(self):
        """Test file upload metrics recording."""
        MetricsCollector.record_file_upload("pdf", "success", 1024000)
        
        metrics_output = get_metrics()
        assert "file_uploads_total" in metrics_output
        assert "file_upload_size_bytes" in metrics_output
    
    def test_metrics_collector_search_query(self):
        """Test search query metrics recording."""
        MetricsCollector.record_search_query("semantic", 0.2)
        
        metrics_output = get_metrics()
        assert "search_queries_total" in metrics_output
        assert "search_query_duration_seconds" in metrics_output


@pytest.mark.integration
class TestMonitoringMiddleware:
    """Test monitoring middleware integration."""
    
    def test_request_tracking_middleware(self, client):
        """Test request tracking middleware functionality."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        
        # Check that metrics were recorded
        metrics_output = get_metrics()
        assert "http_requests_total" in metrics_output
    
    def test_metrics_endpoint(self, client):
        """Test custom metrics endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        content = response.text
        assert "http_requests_total" in content
        assert "app_info" in content
    
    def test_security_middleware_headers(self, client):
        """Test security headers are added."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    
    def test_error_handling_with_monitoring(self, client):
        """Test error handling includes monitoring."""
        # This should trigger a 404
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        
        # Check that error was recorded in metrics
        metrics_output = get_metrics()
        assert "http_requests_total" in metrics_output


@pytest.mark.integration
class TestObservabilityIntegration:
    """Test full observability stack integration."""
    
    def test_end_to_end_request_monitoring(self, client):
        """Test complete request monitoring flow."""
        # Make a request that should be fully monitored
        response = client.get("/api/organizations", headers={"Authorization": "Bearer mock-token"})
        
        # Should have monitoring headers
        assert "X-Request-ID" in response.headers
        
        # Should be recorded in metrics
        metrics_output = get_metrics()
        assert "http_requests_total" in metrics_output
        assert "http_request_duration_seconds" in metrics_output
    
    def test_health_check_monitoring(self, client):
        """Test health check is properly monitored."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        
        # Should still have monitoring headers
        assert "X-Request-ID" in response.headers
    
    def test_application_info_in_metrics(self, client):
        """Test application info is included in metrics."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        content = response.text
        
        # Check for application info
        assert "app_info" in content
        assert "EcoBench" in content
        assert "version" in content
