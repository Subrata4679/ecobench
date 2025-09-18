from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import (
    auth, organizations, reports, ingestion, 
    kpis, benchmarks, recommendations, search,
    scraping, chatbot, analytics
)
from app.utils.logging import configure_logging, get_logger, audit_logger
from app.utils.metrics import get_metrics, get_metrics_content_type, MetricsCollector
from app.middleware.monitoring import (
    RequestTrackingMiddleware, 
    SecurityMiddleware, 
    HealthCheckMiddleware
)

# Configure structured logging
configure_logging(
    log_level=settings.log_level,
    json_logs=not settings.debug
)

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting EcoBench on IUX application")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down EcoBench on IUX application")


# Create FastAPI application
app = FastAPI(
    title="EcoBench on IUX",
    description="Enterprise-grade ESG benchmarking platform with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add monitoring middleware (order matters - add from outermost to innermost)
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(RequestTrackingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Initialize Prometheus metrics (but we'll use our custom endpoint)
instrumentator = Instrumentator()
instrumentator.instrument(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        method=request.method,
        url=str(request.url),
        request_id=request_id
    )
    
    # Log security event for potential attacks
    audit_logger.log_security_event(
        event="unhandled_exception",
        details={
            "error_type": type(exc).__name__,
            "method": request.method,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id
        }
    )


# Custom metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "ecobench-api"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["Ingestion"])
app.include_router(kpis.router, prefix="/api/kpis", tags=["KPIs"])
app.include_router(benchmarks.router, prefix="/api/benchmarks", tags=["Benchmarks"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(scraping.router, prefix="/api/scraping", tags=["Web Scraping"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["ESG Chatbot"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Advanced Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EcoBench on IUX",
        "description": "Enterprise-grade ESG benchmarking platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
