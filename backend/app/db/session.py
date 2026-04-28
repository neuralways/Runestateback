"""
=============================================================================
📊 SESSION.PY - DATABASE CONNECTION MANAGEMENT
=============================================================================
Purpose:
    Manages SQLAlchemy database engine and session creation.
    Provides database session dependency injection for FastAPI routes.
    
Key Concepts:
    - Engine: The database connection pool (maintains multiple connections)
    - SessionLocal: Factory for creating database sessions (transactions)
    - Dependencies: FastAPI way of injecting sessions into route handlers
    
Why This Structure:
    ✅ Connection pooling (efficient)
    ✅ Thread-safe sessions
    ✅ Easy dependency injection
    ✅ Automatic session cleanup
    
Flow:
    User Request → FastAPI → get_db() → Session → Query DB → Response
=============================================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# ============================================================================
# DATABASE ENGINE CREATION
# ============================================================================
# Engine = Connection Pool + Dialect
# Creates a pool of connections to PostgreSQL
# Parameters explained:
#   - echo=True: Logs all SQL queries (good for debugging, disable in production)
#   - pool_size=5: Number of connections to keep in pool
#   - max_overflow=10: Max connections beyond pool_size to create when needed
#   - pool_pre_ping=True: Tests connection before using (handles stale connections)

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries only in debug mode
    pool_size=5,          # Default pool size
    max_overflow=10,      # Max overflow connections
    pool_pre_ping=True,   # Verify connection is alive before using
)

# ============================================================================
# SESSION FACTORY CREATION
# ============================================================================
# SessionLocal = Session Factory
# Calling SessionLocal() creates a new database session
# Each session represents a database transaction
# Parameters explained:
#   - autocommit=False: Explicit commit required
#   - autoflush=False: Manual flush control (better for complex operations)
#   - bind=engine: Uses the engine we created above

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================================
# DEPENDENCY INJECTION FUNCTION
# ============================================================================
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency: Provides database session for route handlers
    
    Automatically:
    1. Creates a new session
    2. Passes it to the route handler
    3. Closes it after request completes (even if error occurs)
    
    Usage in Routes:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            # Use db to query database
            return db.query(User).all()
    
    Why yield:
        - Allows cleanup code after response is sent
        - Ensures database session is always closed
        - Prevents connection leaks
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        # Provide session to route handler
        yield db
    finally:
        # Cleanup: Always close session, even if error occurs
        db.close()


# ============================================================================
# BASE CLASS FOR MODELS (Declarative Base)
# ============================================================================
# This is used in models.py to define database tables
# We'll import and use it in the models file
from sqlalchemy.orm import declarative_base

Base = declarative_base()
"""
Base = Declarative Base for SQLAlchemy ORM models
Every database model inherits from this:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
"""
