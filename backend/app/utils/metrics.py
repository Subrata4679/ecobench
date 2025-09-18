from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict, Any
import time
from functools import wraps
from contextvars import ContextVar

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['query_type', 'table']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table']
)

llm_operations_total = Counter(
    'llm_operations_total',
    'Total LLM operations',
    ['operation_type', 'provider', 'status']
)

llm_operation_duration_seconds = Histogram(
    'llm_operation_duration_seconds',
    'LLM operation duration in seconds',
    ['operation_type', 'provider']
)

llm_token_usage_total = Counter(
    'llm_token_usage_total',
    'Total LLM tokens used',
    ['operation_type', 'provider']
)

file_uploads_total = Counter(
    'file_uploads_total',
    'Total file uploads',
    ['file_type', 'status']
)

file_upload_size_bytes = Histogram(
    'file_upload_size_bytes',
    'File upload size in bytes',
    ['file_type']
)

ingestion_jobs_total = Counter(
    'ingestion_jobs_total',
    'Total ingestion jobs',
    ['job_type', 'status']
)

ingestion_job_duration_seconds = Histogram(
    'ingestion_job_duration_seconds',
    'Ingestion job duration in seconds',
    ['job_type']
)

active_users_gauge = Gauge(
    'active_users_total',
    'Number of active users'
)

embeddings_generated_total = Counter(
    'embeddings_generated_total',
    'Total embeddings generated',
    ['provider']
)

search_queries_total = Counter(
    'search_queries_total',
    'Total search queries',
    ['search_type']
)

search_query_duration_seconds = Histogram(
    'search_query_duration_seconds',
    'Search query duration in seconds',
    ['search_type']
)

kpi_extractions_total = Counter(
    'kpi_extractions_total',
    'Total KPI extractions',
    ['extraction_method', 'status']
)

recommendations_generated_total = Counter(
    'recommendations_generated_total',
    'Total recommendations generated',
    ['recommendation_type', 'status']
)

# Application info
app_info = Info('app_info', 'Application information')
app_info.info({
    'version': '1.0.0',
    'name': 'EcoBench',
    'description': 'ESG Benchmarking Platform'
})

# Context variable for current request metrics
current_request_ctx: ContextVar[Dict[str, Any]] = ContextVar('current_request', default={})


class MetricsCollector:
    """Centralized metrics collection utility."""
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    @staticmethod
    def record_database_query(query_type: str, table: str, duration: float):
        """Record database query metrics."""
        database_queries_total.labels(
            query_type=query_type,
            table=table
        ).inc()
        
        database_query_duration_seconds.labels(
            query_type=query_type,
            table=table
        ).observe(duration)
    
    @staticmethod
    def record_llm_operation(
        operation_type: str, 
        provider: str, 
        status: str, 
        duration: float, 
        token_count: int = None
    ):
        """Record LLM operation metrics."""
        llm_operations_total.labels(
            operation_type=operation_type,
            provider=provider,
            status=status
        ).inc()
        
        llm_operation_duration_seconds.labels(
            operation_type=operation_type,
            provider=provider
        ).observe(duration)
        
        if token_count:
            llm_token_usage_total.labels(
                operation_type=operation_type,
                provider=provider
            ).inc(token_count)
    
    @staticmethod
    def record_file_upload(file_type: str, status: str, file_size: int):
        """Record file upload metrics."""
        file_uploads_total.labels(
            file_type=file_type,
            status=status
        ).inc()
        
        file_upload_size_bytes.labels(
            file_type=file_type
        ).observe(file_size)
    
    @staticmethod
    def record_ingestion_job(job_type: str, status: str, duration: float = None):
        """Record ingestion job metrics."""
        ingestion_jobs_total.labels(
            job_type=job_type,
            status=status
        ).inc()
        
        if duration is not None:
            ingestion_job_duration_seconds.labels(
                job_type=job_type
            ).observe(duration)
    
    @staticmethod
    def record_search_query(search_type: str, duration: float):
        """Record search query metrics."""
        search_queries_total.labels(
            search_type=search_type
        ).inc()
        
        search_query_duration_seconds.labels(
            search_type=search_type
        ).observe(duration)
    
    @staticmethod
    def record_kpi_extraction(extraction_method: str, status: str):
        """Record KPI extraction metrics."""
        kpi_extractions_total.labels(
            extraction_method=extraction_method,
            status=status
        ).inc()
    
    @staticmethod
    def record_recommendation_generation(recommendation_type: str, status: str):
        """Record recommendation generation metrics."""
        recommendations_generated_total.labels(
            recommendation_type=recommendation_type,
            status=status
        ).inc()
    
    @staticmethod
    def update_active_users(count: int):
        """Update active users gauge."""
        active_users_gauge.set(count)
    
    @staticmethod
    def record_embedding_generation(provider: str):
        """Record embedding generation."""
        embeddings_generated_total.labels(
            provider=provider
        ).inc()


def time_operation(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to time operations and record metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metric
                if metric_name == "database_query":
                    MetricsCollector.record_database_query(
                        labels.get("query_type", "unknown"),
                        labels.get("table", "unknown"),
                        duration
                    )
                elif metric_name == "llm_operation":
                    MetricsCollector.record_llm_operation(
                        labels.get("operation_type", "unknown"),
                        labels.get("provider", "unknown"),
                        "success",
                        duration
                    )
                elif metric_name == "search_query":
                    MetricsCollector.record_search_query(
                        labels.get("search_type", "unknown"),
                        duration
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failure metric
                if metric_name == "llm_operation":
                    MetricsCollector.record_llm_operation(
                        labels.get("operation_type", "unknown"),
                        labels.get("provider", "unknown"),
                        "error",
                        duration
                    )
                
                raise e
        return wrapper
    return decorator


class BusinessMetrics:
    """Business-specific metrics collection."""
    
    @staticmethod
    def track_report_processing_pipeline():
        """Track the complete report processing pipeline."""
        # This would be called at various stages of report processing
        pass
    
    @staticmethod
    def track_user_engagement(user_id: int, action: str):
        """Track user engagement metrics."""
        # Could be extended to track specific user actions
        pass
    
    @staticmethod
    def track_esg_data_quality():
        """Track ESG data quality metrics."""
        # Could track confidence scores, extraction accuracy, etc.
        pass


def get_metrics():
    """Get current metrics in Prometheus format."""
    return generate_latest()


def get_metrics_content_type():
    """Get the content type for metrics."""
    return CONTENT_TYPE_LATEST
