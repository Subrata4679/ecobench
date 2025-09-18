import logging
import structlog
import sys
from typing import Any, Dict
from contextvars import ContextVar
from datetime import datetime
import json

# Context variable for request ID
request_id_ctx: ContextVar[str] = ContextVar('request_id', default='')

def configure_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    """Configure structured logging with structlog."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        add_timestamp,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def add_request_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request ID to log entries."""
    request_id = request_id_ctx.get('')
    if request_id:
        event_dict['request_id'] = request_id
    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add timestamp to log entries."""
    event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    return event_dict


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggingMixin:
    """Mixin class to add logging capabilities to services."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_operation(self, operation: str, **kwargs):
        """Log an operation with context."""
        self.logger.info(
            f"{operation} started",
            operation=operation,
            **kwargs
        )
    
    def log_success(self, operation: str, duration: float = None, **kwargs):
        """Log successful operation."""
        log_data = {
            "operation": operation,
            "status": "success",
            **kwargs
        }
        if duration is not None:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        self.logger.info(f"{operation} completed", **log_data)
    
    def log_error(self, operation: str, error: Exception, **kwargs):
        """Log error with context."""
        self.logger.error(
            f"{operation} failed",
            operation=operation,
            status="error",
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
    
    def log_warning(self, message: str, **kwargs):
        """Log warning with context."""
        self.logger.warning(message, **kwargs)


class AuditLogger:
    """Specialized logger for audit events."""
    
    def __init__(self):
        self.logger = get_logger("audit")
    
    def log_user_action(
        self, 
        user_id: int, 
        action: str, 
        resource_type: str, 
        resource_id: int = None,
        details: Dict[str, Any] = None
    ):
        """Log user action for audit trail."""
        self.logger.info(
            "User action",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            event_type="user_action"
        )
    
    def log_system_event(
        self, 
        event: str, 
        component: str, 
        details: Dict[str, Any] = None
    ):
        """Log system event."""
        self.logger.info(
            "System event",
            event=event,
            component=component,
            details=details or {},
            event_type="system_event"
        )
    
    def log_security_event(
        self, 
        event: str, 
        user_id: int = None, 
        ip_address: str = None,
        details: Dict[str, Any] = None
    ):
        """Log security-related event."""
        self.logger.warning(
            "Security event",
            event=event,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {},
            event_type="security_event"
        )


class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_query_performance(
        self, 
        query_type: str, 
        duration: float, 
        record_count: int = None,
        filters: Dict[str, Any] = None
    ):
        """Log database query performance."""
        self.logger.info(
            "Database query",
            query_type=query_type,
            duration_ms=round(duration * 1000, 2),
            record_count=record_count,
            filters=filters or {},
            metric_type="db_query"
        )
    
    def log_api_performance(
        self, 
        endpoint: str, 
        method: str, 
        duration: float, 
        status_code: int,
        user_id: int = None
    ):
        """Log API endpoint performance."""
        self.logger.info(
            "API request",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration * 1000, 2),
            status_code=status_code,
            user_id=user_id,
            metric_type="api_request"
        )
    
    def log_llm_performance(
        self, 
        operation: str, 
        duration: float, 
        token_count: int = None,
        model: str = None
    ):
        """Log LLM operation performance."""
        self.logger.info(
            "LLM operation",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            token_count=token_count,
            model=model,
            metric_type="llm_operation"
        )


# Global instances
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
