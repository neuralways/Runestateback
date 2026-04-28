# 🏗️ RUNESTATE BACKEND - FastAPI Construction Management API

Welcome to the Runestate backend! This is a comprehensive FastAPI-based REST API for managing construction projects with AI-powered features.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Database Setup](#database-setup)
8. [Running the Server](#running-the-server)
9. [API Documentation](#api-documentation)
10. [API Endpoints](#api-endpoints)
11. [Authentication](#authentication)
12. [Code Explanations](#code-explanations)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Runestate** is an AI-powered construction management SaaS platform that helps:

- **Site Managers**: Upload photos, attendance, voice updates quickly
- **AI Layer**: Convert raw data into structured, verified insights
- **Builders/Owners**: See real-time progress, costs, risks, reports

### Key Features

✅ **User Management** - Builders & Site Managers  
✅ **Site Management** - Manage multiple construction projects  
✅ **Progress Updates** - Photos, notes, voice transcription  
✅ **Expense Tracking** - Budget vs actual expenses  
✅ **Alerts/Notifications** - Stay informed of issues  
✅ **Real-time Dashboard** - Site overview & statistics  
✅ **Chat/Messaging** - Team communication  
✅ **AI Integration** - Whisper (voice → text), YOLOv8 (image analysis)  

---

## 🏛️ Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│    FastAPI Routes (HTTP Handlers)   │  ← Receives requests, returns responses
├─────────────────────────────────────┤
│  Services (Business Logic)          │  ← Decision making, validation
├─────────────────────────────────────┤
│  Models & Database (Data Layer)     │  ← Persistence
├─────────────────────────────────────┤
│  PostgreSQL Database                │  ← Actual data
└─────────────────────────────────────┘
```

### Request Flow

```
1. User Request (Frontend)
    ↓
2. FastAPI Route Handler
    ↓
3. Validate with Pydantic Schema
    ↓
4. Call Service Layer
    ↓
5. Query Database with SQLAlchemy ORM
    ↓
6. Process & Return Response
    ↓
7. Send to Frontend (JSON)
```

### Design Patterns

- **MVC Model**: Models (data), Views (routes), Controllers (services)
- **Dependency Injection**: FastAPI `Depends()` for database sessions & auth
- **Repository Pattern**: Services handle all database queries
- **Schema Validation**: Pydantic ensures data integrity
- **JWT Authentication**: Stateless token-based auth

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Server** | Uvicorn |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic |
| **Authentication** | JWT (PyJWT) |
| **Password Hashing** | BCrypt |
| **AI/Transcription** | OpenAI Whisper |
| **File Upload** | AWS S3 |
| **SMS/OTP** | Twilio |
| **Documentation** | Swagger UI / ReDoc |

---

## 📁 Project Structure

```
backend/
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app initialization
│   │
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   └── config.py             # Settings & environment variables
│   │
│   ├── db/                       # Database setup
│   │   ├── __init__.py
│   │   └── session.py            # SQLAlchemy engine & sessions
│   │
│   ├── models/                   # Database models (ORM)
│   │   ├── __init__.py
│   │   └── models.py             # All database table definitions
│   │
│   ├── schemas/                  # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   └── schemas.py            # Request/response models
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   └── services.py           # Service classes (logic)
│   │
│   ├── api/                      # API routes
│   │   ├── __init__.py
│   │   └── routes.py             # All API endpoints
│   │
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py            # Helper functions (hashing, JWT, etc.)
│
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (local)
├── .env.example                  # Example environment variables
└── README.md                     # This file
```

### File Purposes

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, middleware setup |
| `config.py` | Load settings from .env file |
| `session.py` | Database connection setup |
| `models.py` | Database table definitions (9 tables) |
| `schemas.py` | Request/response validation models |
| `services.py` | Business logic for each entity |
| `routes.py` | All API endpoints (~32 endpoints) |
| `helpers.py` | Utility functions (password, JWT, OTP, etc.) |

---

## 💾 Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip or conda

### Step 1: Clone Repository

```bash
git clone https://github.com/neuralways/Runestateback.git
cd Runestateback/backend
```

### Step 2: Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create .env File

```bash
# Copy example to actual .env
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your editor
```

### Step 5: Initialize Database

```bash
# Database tables are created automatically when app starts
# But first, create the PostgreSQL database

# Using psql:
psql -U postgres
CREATE DATABASE runestate_db;
\q
```

---

## ⚙️ Configuration

### .env File Explained

```env
# ============================================
# DATABASE
# ============================================
# Format: postgresql://username:password@host:port/dbname
DATABASE_URL=postgresql://postgres:password@localhost:5432/runestate_db

# ============================================
# JWT SECURITY
# ============================================
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-min-32-chars-change-in-production

# JWT token expiration (days)
JWT_EXPIRATION_DAYS=30

# ============================================
# SERVER
# ============================================
ENVIRONMENT=development  # or production
DEBUG=True               # Never True in production!

# ============================================
# FRONTEND
# ============================================
# URL where React app is running
FRONTEND_URL=http://localhost:3000

# ============================================
# AWS S3 (File Uploads)
# ============================================
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=runestate-bucket
AWS_REGION=us-east-1

# ============================================
# TWILIO (SMS/OTP)
# ============================================
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# ============================================
# OPENAI (Whisper/GPT)
# ============================================
OPENAI_API_KEY=sk-your-key-here

# ============================================
# EMAIL (SMTP)
# ============================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Docker Compose (Optional)

For easierPostgreSQL setup:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: runestate_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with: `docker-compose up -d`

---

## 🗄️ Database Setup

### Database Schema (9 Tables)

```sql
-- 1. USERS - Store user information
CREATE TABLE users {
    id PRIMARY KEY,
    name, email, phone,
    password (hashed), role,
    is_phone_verified, is_email_verified
}

-- 2. OTP_VERIFICATIONS - Phone OTP codes
CREATE TABLE otp_verifications {
    id PRIMARY KEY,
    phone, otp, expires_at, is_used
}

-- 3. SITES - Construction projects
CREATE TABLE sites {
    id PRIMARY KEY,
    name, location, budget, builder_id
}

-- 4. SITE_MANAGERS - Many-to-many (Sites ↔ Managers)
CREATE TABLE site_managers {
    id PRIMARY KEY,
    site_id, user_id
}

-- 5. UPDATES - Progress updates
CREATE TABLE updates {
    id PRIMARY KEY,
    site_id, created_by,
    worker_count, notes, voice_text
}

-- 6. UPDATE_FILES - Photos/audio attached to updates
CREATE TABLE update_files {
    id PRIMARY KEY,
    update_id, file_url, file_type
}

-- 7. EXPENSES - Cost tracking
CREATE TABLE expenses {
    id PRIMARY KEY,
    site_id, added_by,
    amount, category, note
}

-- 8. ALERTS - Warnings/notifications
CREATE TABLE alerts {
    id PRIMARY KEY,
    site_id, type, message, is_read
}

-- 9. MESSAGES - Team chat
CREATE TABLE messages {
    id PRIMARY KEY,
    site_id, sender_id, message
}
```

### Relationships Diagram

```
Users (1) ──────── (∞) Sites
           builder_id

Users (∞) ─────── (∞) Sites
   \           /
    Site_Managers
    (junction table)

Sites (1) ────── (∞) Updates
       site_id

Updates (1) ───── (∞) UpdateFiles
       update_id

Sites (1) ────── (∞) Expenses
     site_id

Sites (1) ────── (∞) Alerts
     site_id

Sites (1) ────── (∞) Messages
     site_id
```

### Database Migrations (Future)

For production, use Alembic:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head
```

---

## 🚀 Running the Server

### Development (with hot reload)

```bash
# Activate virtual environment first
source venv/bin/activate  # on macOS/Linux
# or
venv\Scripts\activate  # on Windows

# Run with auto-reload on code changes
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

### Production (with Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Docker

```bash
# Build image
docker build -t runestate-api .

# Run container
docker run -p 8000:8000 --env-file .env runestate-api
```

---

## 📚 API Documentation

### Interactive Documentation

Once server is running, visit:

- **Swagger UI** (Interactive Testing): http://localhost:8000/docs
- **ReDoc** (Clean Docs): http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

These are **auto-generated** from your code!

### Documentation Include

✅ All endpoints with descriptions  
✅ Request/response examples  
✅ Data type validation  
✅ Error responses  
✅ Try-it-out functionality  
✅ Authentication options  

---

## 🔌 API Endpoints

### Overview

Total endpoints: **~32 endpoints across 9 categories**

### Authentication Endpoints (5)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login-email` | Login with email + password |
| POST | `/auth/send-otp` | Request OTP for phone login |
| POST | `/auth/verify-otp` | Verify OTP and login |
| GET | `/auth/me` | Get current user profile |

**Example:**

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass@123",
    "role": "builder"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass@123"
  }'
```

### User Management Endpoints (4)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/users` | List all users |
| GET | `/users/{user_id}` | Get user details |
| POST | `/users/assign-site` | Assign site manager |
| PUT | `/users/{user_id}` | Update user |

### Site Management Endpoints (5)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/sites` | Create new site |
| GET | `/sites` | List all sites |
| GET | `/sites/{site_id}` | Get site details |
| PUT | `/sites/{site_id}` | Update site |
| DELETE | `/sites/{site_id}` | Delete site |

### Progress Updates Endpoints (5)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/updates` | Create progress update |
| GET | `/updates` | List all updates |
| GET | `/updates/{update_id}` | Get update details |
| DELETE | `/updates/{update_id}` | Delete update |
| GET | `/sites/{site_id}/timeline` | Get site timeline |

### Expense Tracking Endpoints (5)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/expenses` | Record expense |
| GET | `/expenses` | List expenses |
| GET | `/expenses/{expense_id}` | Get expense details |
| PUT | `/expenses/{expense_id}` | Update expense |
| DELETE | `/expenses/{expense_id}` | Delete expense |

### Alert Endpoints (2)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/alerts` | List alerts |
| PUT | `/alerts/{alert_id}/read` | Mark alert read |

### Chat Endpoints (3)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/chat/send` | Send message |
| GET | `/chat/{site_id}` | Get messages |
| DELETE | `/chat/{message_id}` | Delete message |

### Dashboard Endpoints (2)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/dashboard/{site_id}` | Site dashboard |
| GET | `/dashboard/overview` | Overview dashboard |

### AI Endpoints (1)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ai/transcribe` | Transcribe audio |

### Health Check (1)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | API status |

---

## 🔐 Authentication

### How JWT Authentication Works

```
1. User Login
   ├─ Send email + password
   ├─ Server verifies credentials
   └─ Server generates JWT token
        │
        └─ Token = Header.Payload.Signature
           - Header: Algorithm (HS256)
           - Payload: User data + expiration
           - Signature: HMAC(Header.Payload, SECRET_KEY)

2. User Makes Requests
   ├─ Send JWT in Authorization header
   ├─ Authorization: Bearer <token>
   └─ Server verifies signature
        │
        └─ If valid: Process request
           If invalid: Reject request

3. Token Expiration
   ├─ Tokens expire after 30 days
   ├─ User must login again for new token
   └─ Prevents long-lived compromised tokens
```

### Implementation Details

**Login:**

```python
# In routes.py
@router.post("/auth/login-email")
def login_email(credentials: UserLoginEmail, db: Session):
    # Find user
    user = AuthService.login_with_email(db, credentials.email, credentials.password)
    
    # Create JWT token
    token = create_access_token({"sub": str(user.id)})
    
    return {"access_token": token, "user": user}
```

**Protected Route:**

```python
# In routes.py
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    # Automatic authentication via dependency
    return current_user
```

**Dependency:**

```python
# In routes.py
def get_current_user(authorization: str, db: Session):
    # Extract token
    token = authorization.split(" ")[1]
    
    # Verify signature & expiration
    payload = decode_access_token(token)
    
    # Get user from database
    user = UserService.get_user_by_id(db, payload["sub"])
    
    return user
```

### Login Methods

**1. Email + Password (Email Login)**

```bash
POST /auth/login-email
{
    "email": "user@example.com",
    "password": "SecurePass@123"
}
```

**2. Phone + OTP (Phone Login)**

```bash
# Step 1: Request OTP
POST /auth/send-otp
{"phone": "+919876543210"}

# Step 2: Verify OTP
POST /auth/verify-otp
{
    "phone": "+919876543210",
    "otp": "427839"
}
```

### Token Storage (Frontend)

```javascript
// After login, store token
localStorage.setItem('token', response.access_token);

// Use token in requests
fetch('/api/v1/profile', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});

// Clear on logout
localStorage.removeItem('token');
```

---

## 📖 Code Explanations

### 1. Password Hashing (Security)

**Problem**: Storing passwords in plain text is dangerous

**Solution**: Hash passwords using BCrypt

```python
# helpers.py
def hash_password(password: str) -> str:
    """Hash plain text password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password matches hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

**How It Works:**

```
User enters: "MyPassword123"
                    ↓
            PWD_CONTEXT.HASH()
                    ↓
Hash result: "$2b$12$abcdef..."  (never same twice due to salt)
                    ↓
            Store in database

Next login:
User enters: "MyPassword123"
                    ↓
Database has: "$2b$12$abcdef..."
                    ↓
        PWD_CONTEXT.VERIFY() compares
                    ↓
        Match? Login success!
        No match? Login fails
```

### 2. ORM Relationships (Database)

**Problem**: Accessing related data (user's sites)

**Solution**: Define relationships in models

```python
# models.py
class User(Base):
    sites = relationship("Site", back_populates="builder")

class Site(Base):
    builder = relationship("User", back_populates="sites")

# Usage in code:
user = db.query(User).filter_by(id=1).first()
user_sites = user.sites  # Auto-loaded from database!
```

### 3. Dependency Injection (Clean Code)

**Problem**: Passing database session to every function

**Solution**: FastAPI dependencies

```python
# routes.py
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    # db is automatically passed!
    return UserService.get_all_users(db)

# In templates/multiple routes:
@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Multiple dependencies!
    return ...
```

### 4. Request/Response Validation (Data Safety)

**Problem**: Receiving invalid data from frontend

**Solution**: Pydantic schemas

```python
# schemas.py
class UserLoginEmail(BaseModel):
    email: EmailStr  # Must be valid email
    password: str = Field(..., min_length=8)  # At least 8 chars

# Usage in routes:
@router.post("/login")
def login(credentials: UserLoginEmail):  # Pydantic auto-validates!
    # By here, email is valid format
    # password is min 8 chars
    ...
```

### 5. SQL Queries (Database)

**Problem**: Writing raw SQL is error-prone

**Solution**: SQLAlchemy ORM

```python
# RAW SQL (Avoid!)
user = db.execute(
    "SELECT * FROM users WHERE email=:email",
    {"email": "john@example.com"}
)

# SQLAlchemy ORM (Better!)
user = db.query(User).filter(User.email == "john@example.com").first()

# Complex queries:
expensive_sites = db.query(Site).filter(
    Site.budget > 1000000
).join(User).filter(
    User.role == "builder"
).all()
```

### 6. Pagination (Handle Large Data)

**Problem**: Your site has 10,000 expenses, loading all is slow

**Solution**: Pagination

```python
# routes.py
@router.get("/expenses")
def get_expenses(
    skip: int = Query(0),  # Records to skip
    limit: int = Query(10)  # Records to return
):
    expenses = db.query(Expense).offset(skip).limit(limit).all()
    # Returns only 10 records at a time
    return expenses

# Frontend:
# Page 1: ?skip=0&limit=10   (records 1-10)
# Page 2: ?skip=10&limit=10  (records 11-20)
# Page 3: ?skip=20&limit=10  (records 21-30)
```

---

## 🌐 Deployment

### Option 1: Heroku

```bash
# Install Heroku CLI
# Then:
heroku login
heroku create runestate-api
git push heroku main

# Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=...

# View logs
heroku logs --tail
```

### Option 2: AWS

```bash
# Using Elastic Beanstalk
eb init
eb create runestate-env
eb deploy

# Or use EC2 + Gunicorn + Nginx
```

### Option 3: DigitalOcean

```bash
# Using App Platform
doctl apps create --spec app.yaml

# Or using Droplets
# SSH into droplet
# Install Python, PostgreSQL
# Clone repo & run Gunicorn
```

### Option 4: Azure

```bash
# Using App Service
az webapp up --name runestate-api --runtime python
```

### Production Checklist

- [ ] DEBUG=False in .env
- [ ] Strong SECRET_KEY (min 32 chars)
- [ ] Database backups enabled
- [ ] CORS restricted to your frontend domain
- [ ] HTTPS enabled
- [ ] Rate limiting enabled
- [ ] Logging enabled
- [ ] Database indexes created
- [ ] Environment variables secured
- [ ] Error monitoring (Sentry, etc.)
- [ ] Performance monitoring
- [ ] Load balancer configured

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Run from backend directory
cd backend

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: "Database connection refused"

**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres  # Should connect

# Check .env DATABASE_URL
# Format: postgresql://user:password@localhost:5432/dbname

# Create database if not exists
createdb runestate_db
```

### Issue: "ORM model not found"

**Solution:**
```python
# Make sure to import in app/main.py
from app.models.models import Base

# Create tables
Base.metadata.create_all(bind=engine)
```

### Issue: "JWT token invalid"

**Solution:**
```bash
# Check SECRET_KEY in .env
# Is it consistent between requests?

# Check token expiration
# Token expires every 30 days

# Check Authorization header
# Format: Authorization: Bearer <token>
```

### Issue: "CORS error from frontend"

**Solution:**
```python
# Check ALLOWED_ORIGINS in config.py
# Make sure frontend URL is included

# Example:
# Frontend: http://localhost:3000
# Backend: FRONTEND_URL=http://localhost:3000
```

### Issue: "Email validation failing"

**Solution:**
```bash
# Install email-validator
pip install email-validator

# Check pydantic version
pip list | grep pydantic
```

### Logs and Debugging

```bash
# View application logs
# Set DEBUG=True in .env

# Or enable SQL query logging
# In config.py: echo=True in engine

# Using logging module
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📞 API Request Examples

### cURL Examples

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com","password":"Pass@123","role":"builder"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login-email \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Pass@123"}'

# Protected request
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Create site
curl -X POST http://localhost:8000/api/v1/sites \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Office Complex","location":"123 Main St","budget":5000000}'
```

### Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass@123",
    "role": "builder"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login-email", json={
    "email": "john@example.com",
    "password": "SecurePass@123"
})
token = response.json()["access_token"]

# Protected request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(response.json())
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Register
const register = async () => {
    const response = await fetch(`${BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: 'John Doe',
            email: 'john@example.com',
            password: 'SecurePass@123',
            role: 'builder'
        })
    });
    return response.json();
};

// Login
const login = async () => {
    const response = await fetch(`${BASE_URL}/auth/login-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: 'john@example.com',
            password: 'SecurePass@123'
        })
    });
    const data = response.json();
    localStorage.setItem('token', data.access_token);
    return data;
};

// Protected request
const getProfile = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch(`${BASE_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
};
```

---

## 📚 Additional Resources

### FastAPI Documentation

- [FastAPI Official Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Pydantic Validation](https://docs.pydantic.dev)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

### Video Tutorials

- [FastAPI Full Course](https://www.youtube.com/results?search_query=fastapi+full+course)
- [SQLAlchemy ORM Tutorial](https://www.youtube.com/results?search_query=sqlalchemy+orm+tutorial)
- [JWT Authentication](https://www.youtube.com/results?search_query=jwt+authentication+fastapi)

### Best Practices

- Use virtual environments
- Never commit `.env` files
- Validate all inputs
- Use HTTPS in production
- Enable CORS carefully
- Log errors properly
- Use database indexes for frequent queries
- Implement rate limiting
- Monitor performance
- Keep dependencies updated

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Create a pull request

---

## 📄 License

MIT License - See LICENSE file

---

## 📧 Support

- Email: support@runestate.com
- Issues: [GitHub Issues](https://github.com/neuralways/Runestateback/issues)
- Documentation: [Full Docs](https://docs.runestate.com)

---

## 🎉 Next Steps

1. ✅ Set up `.env` file
2. ✅ Create PostgreSQL database
3. ✅ Run `pip install -r requirements.txt`
4. ✅ Run `uvicorn app.main:app --reload`
5. ✅ Visit `http://localhost:8000/docs`
6. ✅ Try the API endpoints
7. ✅ Build frontend (React)
8. ✅ Connect frontend to backend
9. ✅ Test full workflow
10. ✅ Deploy to production

---

**Happy Building! 🚀**
