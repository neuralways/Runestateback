"""
=============================================================================
🚀 MAIN.PY - APPLICATION ENTRY POINT
=============================================================================
Purpose:
    FastAPI application initialization and configuration.
    Defines middleware, routes, CORS, and startup/shutdown events.
    
Architecture:
    app = FastAPI()
    → Add middleware (CORS, logging, etc.)
    → Add routes
    → Add startup/shutdown events
    → Ready to serve requests!
    
Key Concepts:
    - Middleware: Processes every request/response
    - CORS: Allows frontend to access backend
    - Routes: API endpoints
    - Startup/Shutdown: Database connection management
    
Start Server:
    uvicorn app.main:app --reload
    
Then visit:
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs
=============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.routes import router
from app.db.session import engine, Base

# ============================================================================
# SETUP LOGGING
# ============================================================================
# Configure logging to see SQL queries and app logs
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CREATE DATABASE TABLES
# ============================================================================
# This creates all tables defined in models if they don't exist
# In production, use Alembic for migrations
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")


# ============================================================================
# INITIALIZE FASTAPI APP
# ============================================================================
app = FastAPI(
    title="Runestate API",
    description="AI-powered construction management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

"""
FastAPI() Parameters Explained:
    - title: API name (shown in docs)
    - description: API description (shown in docs)
    - version: API version (for tracking changes)
    - docs_url: Swagger UI documentation page
    - redoc_url: ReDoc documentation page
    - openapi_url: OpenAPI schema endpoint
"""


# ============================================================================
# CORS MIDDLEWARE - Allow Frontend to Access Backend
# ============================================================================
# Without CORS, browser blocks requests from frontend
# CORS = Cross-Origin Resource Sharing

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Allowed frontend URLs
    allow_credentials=True,                   # Allow cookies/auth
    allow_methods=["*"],                      # Allow all HTTP methods
    allow_headers=["*"],                      # Allow all headers
)

"""
CORS Explanation:
Browser Security Policy:
- http://localhost:3000 (frontend) makes request
- http://localhost:8000 (backend) receives it
- Browser checks: Is origin allowed?
- CORS headers must match, or browser blocks

Settings:
- allow_origins: List of allowed frontend URLs
- allow_credentials: Allow auth headers (JWT tokens)
- allow_methods: GET, POST, PUT, DELETE, etc.
- allow_headers: Accept custom headers (Authorization, etc.)

Frontend Requests:
fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <token>'
    },
    body: JSON.stringify({...})
})
"""


# ============================================================================
# INCLUDE API ROUTES
# ============================================================================
# Register all routes from routes.py
# Routes are prefixed with /api/v1

app.include_router(router)

"""
Routes Registered:
    /api/v1/auth/* → Authentication endpoints
    /api/v1/users/* → User management
    /api/v1/sites/* → Site management
    /api/v1/updates/* → Progress updates
    /api/v1/expenses/* → Expense tracking
    /api/v1/alerts/* → Alerts/notifications
    /api/v1/chat/* → Messaging
    /api/v1/dashboard/* → Dashboard data
    /api/v1/ai/* → AI operations
"""


# ============================================================================
# STARTUP EVENT - Run when server starts
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """
    STARTUP EVENT - Runs when server starts
    
    Use for:
    - Database connection setup
    - Cache initialization
    - Third-party API connections
    - Loading configuration
    
    Runs ONCE when server starts.
    """
    logger.info("🚀 Runestate API starting...")
    logger.info(f"✅ Environment: {settings.ENVIRONMENT}")
    logger.info(f"✅ Debug mode: {settings.DEBUG}")
    logger.info(f"✅ Database: {settings.DATABASE_URL}")
    logger.info("🚀 Runestate API started successfully!")


# ============================================================================
# SHUTDOWN EVENT - Run when server shuts down
# ============================================================================
@app.on_event("shutdown")
async def shutdown_event():
    """
    SHUTDOWN EVENT - Runs when server shuts down
    
    Use for:
    - Close database connections
    - Clean up resources
    - Save state
    - Log shutdown
    
    Runs ONCE when server stops.
    """
    logger.info("🛑 Runestate API shutting down...")
    # Clean up resources here
    logger.info("🛑 Runestate API stopped")


# ============================================================================
# ROOT ENDPOINT - Welcome message
# ============================================================================
@app.get("/")
async def root():
    """
    ROOT ENDPOINT
    
    Endpoint: GET /
    
    Welcome message and API info.
    Used to verify server is running.
    
    Response (200):
    {
        "message": "Welcome to Runestate API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs"
    }
    """
    return {
        "message": "Welcome to Runestate API - AI-powered construction management",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "environment": settings.ENVIRONMENT
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    VALIDATION ERROR HANDLER
    
    Handles Pydantic validation errors (bad request data).
    Returns clean error message.
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    GENERAL ERROR HANDLER
    
    Catches all unhandled exceptions.
    Returns error response (don't expose internal stack trace in production).
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if settings.ENVIRONMENT == "production" else str(exc)
        }
    )


# ============================================================================
# AUTO-GENERATED DOCUMENTATION
# ============================================================================
"""
FastAPI automatically generates interactive API documentation at:

Swagger UI (Interactive Testing):
    http://localhost:8000/docs
    
ReDoc (Clean Documentation):
    http://localhost:8000/redoc
    
OpenAPI Schema:
    http://localhost:8000/openapi.json

What's Included:
✅ All endpoints with descriptions
✅ Request/response examples
✅ Schema validation
✅ Try-it-out functionality
✅ Authentication support
✅ Error handling

These are auto-generated from:
- Router descriptions
- Pydantic models (schemas)
- Status codes
- Docstrings
"""


# ============================================================================
# DEPLOYMENT NOTES
# ============================================================================
"""
DEVELOPMENT (Local Testing):
    uvicorn app.main:app --reload
    - Auto-reloads on code changes
    - Debug mode enabled
    - Visit http://localhost:8000

PRODUCTION (Live Server):
    - Use Gunicorn + Uvicorn
    - Command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
    - Set DEBUG=False
    - Use production database (RDS/Supabase)
    - Enable HTTPS
    - Set proper CORS origins
    - Use environment variables for secrets
    
Docker:
    Build: docker build -t runestate-api .
    Run: docker run -p 8000:8000 runestate-api
    
Environment Variables (.env or Secrets):
    DATABASE_URL=postgresql://...
    SECRET_KEY=<very-long-random-string>
    ENVIRONMENT=production
    DEBUG=False
"""
