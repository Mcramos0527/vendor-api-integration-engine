"""
Vendor API Integration Engine
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import router
from src.api.middleware import RequestLoggingMiddleware
from src.config.settings import settings
from src.services.audit_logger import audit_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    audit_logger.info("Vendor API Integration Engine starting up")
    audit_logger.info(f"Environment: {settings.ENVIRONMENT}")
    audit_logger.info(f"Debug mode: {settings.DEBUG}")
    yield
    audit_logger.info("Vendor API Integration Engine shutting down")


app = FastAPI(
    title="Vendor API Integration Engine",
    description=(
        "Enterprise middleware that transforms vendor catalog data "
        "into ERP-compatible Intermediate Documents (IDocs) in near real-time."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Register routes
app.include_router(router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
    )
