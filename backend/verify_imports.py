"""
Import verification script - Run this to test all imports
Usage:
    python verify_imports.py
"""

print("🔍 Verifying all imports...")

try:
    print("✓ Importing FastAPI...")
    import fastapi
    print(f"  FastAPI version: {fastapi.__version__}")
except ImportError as e:
    print(f"✗ FastAPI import failed: {e}")

try:
    print("✓ Importing SQLAlchemy...")
    from sqlalchemy import create_engine
    import sqlalchemy
    print(f"  SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"✗ SQLAlchemy import failed: {e}")

try:
    print("✓ Importing Pydantic...")
    from pydantic import BaseModel
    import pydantic
    print(f"  Pydantic version: {pydantic.VERSION}")
except ImportError as e:
    print(f"✗ Pydantic import failed: {e}")

try:
    print("✓ Importing PyJWT...")
    import jwt
    print("  JWT imported successfully")
except ImportError as e:
    print(f"✗ PyJWT import failed: {e}")

try:
    print("✓ Importing BCrypt...")
    import bcrypt
    print("  BCrypt imported successfully")
except ImportError as e:
    print(f"✗ BCrypt import failed: {e}")

try:
    print("✓ Importing python-dotenv...")
    from dotenv import load_dotenv
    print("  python-dotenv imported successfully")
except ImportError as e:
    print(f"✗ python-dotenv import failed: {e}")

# Test app imports
try:
    print("✓ Importing app config...")
    from app.core.config import settings
    print(f"  Environment: {settings.ENVIRONMENT}")
except Exception as e:
    print(f"✗ App config import failed: {e}")

try:
    print("✓ Importing app models...")
    from app.models.models import User, Site, Update
    print("  Models imported successfully")
except Exception as e:
    print(f"✗ App models import failed: {e}")

try:
    print("✓ Importing app schemas...")
    from app.schemas.schemas import UserResponse, SiteResponse
    print("  Schemas imported successfully")
except Exception as e:
    print(f"✗ App schemas import failed: {e}")

try:
    print("✓ Importing app services...")
    from app.services.services import AuthService, UserService
    print("  Services imported successfully")
except Exception as e:
    print(f"✗ App services import failed: {e}")

try:
    print("✓ Importing app helpers...")
    from app.utils.helpers import hash_password, create_access_token
    print("  Helpers imported successfully")
except Exception as e:
    print(f"✗ App helpers import failed: {e}")

try:
    print("✓ Importing app main...")
    from app.main import app
    print("  FastAPI app imported successfully")
except Exception as e:
    print(f"✗ App main import failed: {e}")

print("\n✅ Import verification complete!")
print("\n💡 If all imports passed, you're ready to run:")
print("   uvicorn app.main:app --reload")
