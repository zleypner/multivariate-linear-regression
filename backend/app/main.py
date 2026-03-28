"""
FastAPI application entry point for Campaign Analytics API.

This module configures and creates the FastAPI application with:
- CORS middleware for frontend integration
- Error handling middleware
- API routes for upload, training, prediction, and results
- Health check endpoints
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .config import settings
from .middleware.error_handler import ErrorHandlerMiddleware, APIError
from .routes import upload_router, train_router, predict_router, results_router
from .models.schemas import HealthResponse

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
        if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info(
        "Starting Campaign Analytics API",
        version=settings.app_version,
        environment=settings.environment,
    )

    # Ensure upload directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    logger.info("Upload directory ready", path=str(settings.upload_path))

    yield

    # Shutdown
    logger.info("Shutting down Campaign Analytics API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
Campaign Analytics API for multivariate regression analysis.

## Features

* **Upload** - Upload CSV files with campaign data
* **Train** - Train regression models with configurable parameters
* **Predict** - Make predictions for new campaign data
* **Results** - View training metrics and feature importance

## Workflow

1. Upload a CSV file using `/api/upload`
2. Train a model using `/api/train` with the file_id
3. Make predictions using `/api/predict`
4. View results using `/api/results`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add error handling middleware
app.add_middleware(ErrorHandlerMiddleware)


# Exception handlers
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Include routers
app.include_router(upload_router)
app.include_router(train_router)
app.include_router(predict_router)
app.include_router(results_router)


# Health check endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the API is healthy and running.",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for liveness probes.

    Returns the current health status of the API.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.utcnow(),
        details={
            "app_name": settings.app_name,
        },
    )


@app.get(
    "/ready",
    tags=["health"],
    summary="Readiness check",
    description="Check if the API is ready to accept requests.",
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.

    Verifies that all dependencies are available.
    """
    # Could add checks for database, cache, etc.
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "upload_dir": settings.upload_path.exists(),
        },
    }


@app.get(
    "/metrics",
    tags=["health"],
    summary="Metrics endpoint",
    description="Prometheus-compatible metrics endpoint (placeholder).",
)
async def metrics() -> dict:
    """
    Metrics endpoint for Prometheus scraping.

    This is a placeholder - in production, use prometheus-client.
    """
    return {
        "status": "metrics_placeholder",
        "message": "Integrate prometheus-client for production metrics",
    }


@app.get(
    "/",
    tags=["root"],
    summary="API root",
    description="Get basic API information.",
)
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "upload": "/api/upload",
            "train": "/api/train",
            "predict": "/api/predict",
            "results": "/api/results",
        },
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
