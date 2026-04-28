"""
=============================================================================
📋 CONFIG.PY - CENTRAL CONFIGURATION MANAGEMENT
=============================================================================
Purpose: 
    This file manages all application settings loaded from environment variables.
    It acts as the single source of truth for all configuration parameters.
    
Key Concepts:
    - Uses Pydantic Settings for type-safe configuration
    - Loads from .env file during development
    - Automatically validates all settings
    - Provides defaults for optional settings

Why This Structure:
    ✅ Centralized configuration
    ✅ Type-safe (catches errors early)
    ✅ Environment-aware (dev/prod)
    ✅ Easy to override for testing
    ✅ Secrets management
=============================================================================
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    APPLICATION SETTINGS CLASS
    
    This class defines all environment variables the app needs.
    Pydantic automatically:
    - Validates types (str, int, bool)
    - Raises errors if required vars are missing
    - Loads from .env file (development)
    - Loads from environment variables (production)
    
    Example:
        settings = Settings()  # Loaded from .env or env vars
        print(settings.DATABASE_URL)  # Access like normal attribute
    """
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    # PostgreSQL connection URL format: postgresql://user:password@host:port/dbname
    # This URL tells SQLAlchemy how to connect to the PostgreSQL database
    DATABASE_URL: str
    
    # ============================================================================
    # JWT AUTHENTICATION CONFIGURATION
    # ============================================================================
    # Secret key used to encode/decode JWT tokens
    # A secure token should be: openssl rand -hex 32
    # NEVER expose this in production!
    SECRET_KEY: str
    
    # Expiration time for JWT tokens (in days)
    # After this time, users need to login again
    JWT_EXPIRATION_DAYS: int = 30
    
    # Algorithm used for JWT encoding (HS256 = HMAC-SHA256 - most common)
    ALGORITHM: str = "HS256"
    
    # ============================================================================
    # SERVER CONFIGURATION
    # ============================================================================
    # Environment type: "development", "staging", or "production"
    # Controls logging, error messages, and CORS settings
    ENVIRONMENT: str = "development"
    
    # Debug mode: True shows detailed error messages (NEVER use in production!)
    DEBUG: bool = True
    
    # API version
    API_VERSION: str = "v1"
    
    # ============================================================================
    # CORS CONFIGURATION (Cross-Origin Resource Sharing)
    # ============================================================================
    # Frontend URL that's allowed to access the API
    # Without this, browser will block requests from frontend
    # Example: "http://localhost:3000" for development
    FRONTEND_URL: str = "http://localhost:3000"
    
    # List of allowed origins (CORS)
    # Frontend URL is dynamically added here
    @property
    def ALLOWED_ORIGINS(self) -> list:
        """Return list of allowed origins for CORS"""
        origins = [self.FRONTEND_URL]
        if self.ENVIRONMENT == "development":
            origins.extend(["http://localhost", "http://localhost:3000"])
        return origins
    
    # ============================================================================
    # AWS S3 CONFIGURATION (File Uploads)
    # ============================================================================
    # AWS credentials for uploading files to S3
    # Used for storing images, audio files, documents
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # S3 bucket name where files will be stored
    AWS_S3_BUCKET: Optional[str] = None
    
    # AWS region (us-east-1, us-west-2, etc.)
    AWS_REGION: str = "us-east-1"
    
    # ============================================================================
    # TWILIO CONFIGURATION (SMS OTP)
    # ============================================================================
    # Twilio credentials for sending OTP via SMS
    # Used for phone number verification and OTP login
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # ============================================================================
    # OPENAI CONFIGURATION (AI/Whisper Integration)
    # ============================================================================
    # OpenAI API key for:
    # - Whisper: Audio transcription
    # - GPT: Report generation
    OPENAI_API_KEY: Optional[str] = None
    
    # ============================================================================
    # EMAIL CONFIGURATION (SMTP)
    # ============================================================================
    # SMTP server details for sending emails
    # Used for: verification emails, notifications, password reset
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================
    class Config:
        """
        Pydantic configuration
        env_file: Loads variables from .env file
        case_sensitive: True means DATABASE_URL != database_url
        """
        env_file = ".env"
        case_sensitive = True
        from_attributes = True


# --- INITIALIZATION ---
# Create global settings instance
# This is loaded once when the app starts
# Access from anywhere in code: from app.core.config import settings
settings = Settings()


# --- HELPER FUNCTIONS ---
def get_database_url() -> str:
    """
    Get the database connection URL
    
    Returns:
        str: PostgreSQL connection URL
        
    Example:
        url = get_database_url()
        # Output: postgresql://user:pass@localhost:5432/db_name
    """
    return settings.DATABASE_URL


def is_development() -> bool:
    """
    Check if running in development environment
    
    Returns:
        bool: True if ENVIRONMENT == "development"
        
    Usage:
        if is_development():
            enable_detailed_logging()
    """
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """
    Check if running in production environment
    
    Returns:
        bool: True if ENVIRONMENT == "production"
        
    Usage:
        if is_production():
            disable_debug_mode()
    """
    return settings.ENVIRONMENT == "production"
