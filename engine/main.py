"""
Cognition Engine API Server

Main FastAPI application that provides HTTP endpoints for the Cognition Engine SDK.
This creates a standalone API service that EdTech companies can integrate with.
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import os
from supabase import create_client

# Import our API components
from .api_auth import validate_api_key, track_api_usage
from .api_endpoints import router as cognition_router
from .cognition_engine import CognitionEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cognition Engine API",
    description="""
    Advanced learning analytics and prediction API for EdTech platforms.

    ## Authentication
    All API requests require an API key in the X-API-Key header.

    ## Rate Limits
    - Starter: 1,000 requests/hour
    - Professional: 10,000 requests/hour
    - Enterprise: Unlimited

    ## Support
    Contact: support@cognition-engine.com
    Documentation: https://docs.cognition-engine.com
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging and API key validation middleware
@app.middleware("http")
async def logging_and_auth_middleware(request: Request, call_next):
    """Log requests and validate API keys for /api/v1 endpoints"""
    start_time = time.time()

    # Log request
    logger.info(f"→ {request.method} {request.url.path}")

    # Validate API key for API endpoints
    if request.url.path.startswith("/api/v1"):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing API key", "message": "X-API-Key header is required"}
            )

        # Create database client for validation
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
        key_info = await validate_api_key(api_key, db)

        if not key_info:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key", "message": "API key is invalid or expired"}
            )

        # Store key info in request state for endpoints to use
        request.state.api_key_info = key_info
        request.state.db = db

    # Process request
    response = await call_next(request)

    # Log response
    duration = (time.time() - start_time) * 1000
    logger.info(f"← {response.status_code} {request.url.path} ({duration".2f"}ms)")

    return response


# Include API routers
app.include_router(cognition_router)


# ===== ROOT ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cognition Engine API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "pricing": "/pricing"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "cognition-engine-api",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


# ===== ADMIN ENDPOINTS =====

@app.post("/admin/create-api-key")
async def create_customer_api_key(
    company_name: str,
    contact_email: str,
    master_key: str = Header(...),
    db: Client = None
):
    """
    Create new API key for customer (admin only).

    This endpoint is protected by a master key and should only be used
    by the service administrator to onboard new customers.
    """
    if master_key != os.getenv("MASTER_API_KEY"):
        raise HTTPException(
            status_code=403,
            detail="Invalid master key"
        )

    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    try:
        from .api_auth import APIKeyManager
        api_key_manager = APIKeyManager(db)
        result = await api_key_manager.create_api_key(company_name, contact_email)

        logger.info(f"Created API key for {company_name} ({contact_email})")

        return {
            "success": True,
            "data": result,
            "message": f"API key created for {company_name}"
        }

    except Exception as e:
        logger.error(f"Failed to create API key: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create API key: {str(e)}"
        )


@app.get("/admin/usage")
async def get_admin_usage(
    master_key: str = Header(...),
    timeframe_days: int = 30,
    db: Client = None
):
    """
    Get usage analytics for all customers (admin only).

    Returns comprehensive usage statistics for billing and monitoring.
    """
    if master_key != os.getenv("MASTER_API_KEY"):
        raise HTTPException(
            status_code=403,
            detail="Invalid master key"
        )

    if db is None:
        db = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

    try:
        # Get API keys usage
        keys_result = db.table("api_keys").select("*").execute()

        # Get usage logs summary
        logs_result = db.table("api_usage_logs").select("*").execute()

        # Calculate statistics
        total_customers = len(keys_result.data)
        total_requests = len(logs_result.data)

        # Group by endpoint
        endpoint_usage = {}
        for log in logs_result.data:
            endpoint = log.get("endpoint", "unknown")
            endpoint_usage[endpoint] = endpoint_usage.get(endpoint, 0) + 1

        return {
            "success": True,
            "data": {
                "total_customers": total_customers,
                "total_requests": total_requests,
                "timeframe_days": timeframe_days,
                "endpoint_usage": endpoint_usage,
                "api_keys": keys_result.data,
                "recent_logs": logs_result.data[-100:]  # Last 100 requests
            },
            "message": "Usage statistics retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Failed to get admin usage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage statistics: {str(e)}"
        )


# ===== ERROR HANDLING =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with proper logging"""
    logger.error(f"Unexpected error in {request.url.path}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


# ===== STARTUP AND SHUTDOWN =====

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Cognition Engine API")

    # Validate required environment variables
    required_env_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "MASTER_API_KEY"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise ValueError(f"Missing required environment variables: {missing_vars}")

    logger.info("✅ All required environment variables present")
    logger.info("✅ Cognition Engine API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Cognition Engine API")


# ===== MAIN ENTRY POINT =====

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting server on {host}:{port} (debug={debug})")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )
