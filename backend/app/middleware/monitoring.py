import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import request_id_ctx, get_logger, performance_logger
from app.utils.metrics import MetricsCollector


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track requests with metrics and logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("middleware")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_ctx.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Extract request info
        method = request.method
        url = str(request.url)
        path = request.url.path
        user_agent = request.headers.get("user-agent", "")
        client_ip = self._get_client_ip(request)
        
        # Log request start
        self.logger.info(
            "Request started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract response info
            status_code = response.status_code
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Record metrics
            endpoint = self._normalize_endpoint(path)
            MetricsCollector.record_http_request(method, endpoint, status_code, duration)
            
            # Log performance
            performance_logger.log_api_performance(
                endpoint=endpoint,
                method=method,
                duration=duration,
                status_code=status_code,
                user_id=getattr(request.state, 'user_id', None)
            )
            
            # Log request completion
            self.logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
                response_size=response.headers.get("content-length", 0)
            )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            
            # Record error metrics
            endpoint = self._normalize_endpoint(path)
            MetricsCollector.record_http_request(method, endpoint, 500, duration)
            
            # Log error
            self.logger.error(
                "Request failed",
                method=method,
                path=path,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            
            raise e
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path for metrics."""
        # Replace path parameters with placeholders to avoid high cardinality
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path


class DatabaseQueryMiddleware:
    """Middleware to track database queries."""
    
    def __init__(self):
        self.logger = get_logger("database")
    
    def track_query(self, query_type: str, table: str, duration: float, record_count: int = None):
        """Track database query execution."""
        MetricsCollector.record_database_query(query_type, table, duration)
        
        performance_logger.log_query_performance(
            query_type=query_type,
            duration=duration,
            record_count=record_count
        )
        
        self.logger.debug(
            "Database query executed",
            query_type=query_type,
            table=table,
            duration_ms=round(duration * 1000, 2),
            record_count=record_count
        )


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security-focused middleware for monitoring."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("security")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for suspicious patterns
        self._check_suspicious_activity(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response
    
    def _check_suspicious_activity(self, request: Request):
        """Check for suspicious request patterns."""
        path = request.url.path.lower()
        
        # Check for common attack patterns
        suspicious_patterns = [
            "script", "javascript:", "vbscript:", "onload", "onerror",
            "../", "..\\", "/etc/passwd", "/proc/", "cmd.exe",
            "union select", "drop table", "insert into"
        ]
        
        query_string = str(request.query_params).lower()
        
        for pattern in suspicious_patterns:
            if pattern in path or pattern in query_string:
                self.logger.warning(
                    "Suspicious request pattern detected",
                    pattern=pattern,
                    path=path,
                    query_string=query_string,
                    client_ip=request.client.host if request.client else "unknown"
                )
                break


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware to handle health checks efficiently."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip detailed logging for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        return await call_next(request)
