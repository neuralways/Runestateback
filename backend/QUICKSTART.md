# 🚀 QUICK START GUIDE

Get the Runestate Backend running in 5 minutes!

## Option 1: Docker (Easiest - Recommended)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

```bash
# 1. Navigate to backend directory
cd backend

# 2. Start everything (PostgreSQL + API)
docker-compose up -d

# 3. Wait for services to be healthy (~10 seconds)
docker-compose ps

# 4. API is running!
# Visit: http://localhost:8000/docs
```

**Connected!** ✅

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Database: localhost:5432

### Stop Services

```bash
docker-compose down
```

---

## Option 2: Local Python Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Steps

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit .env with your PostgreSQL details
nano .env
# Change: DATABASE_URL=postgresql://postgres:password@localhost:5432/runestate_db

# 6. Create database (in another terminal)
createdb runestate_db

# 7. Run server
uvicorn app.main:app --reload
```

**Connected!** ✅

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Testing the API

### 1. Visit Interactive Docs

http://localhost:8000/docs

### 2. Try Example Requests

**Register User:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass@123",
    "role": "builder"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass@123"
  }'
```

**Get Current User (use token from login):**
```bash
TOKEN="<copy_access_token_from_login>"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## File Structure

```
backend/
├── app/
│   ├── main.py              # 🚀 FastAPI app
│   ├── core/config.py       # ⚙️  Settings
│   ├── db/session.py        # 🗄️  Database
│   ├── models/models.py     # 📊 Tables
│   ├── schemas/schemas.py   # ✓ Validation
│   ├── services/services.py # ⚙️  Logic
│   ├── api/routes.py        # 🌐 Endpoints
│   └── utils/helpers.py     # 🔧 Utilities
├── requirements.txt         # 📦 Dependencies
├── .env.example            # 🔐 Config template
├── Dockerfile              # 🐳 Container
├── docker-compose.yml      # 🐳 Multi-container
└── README.md               # 📚 Full docs
```

---

## Common Issues

### "Connection refused" (Database)

**Solution:**
```bash
# Make sure PostgreSQL is running
# Docker: docker-compose up -d postgres
# Local: brew services start postgresql (macOS) or service postgresql start (Linux)
```

### "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# And virtual environment is activated
source venv/bin/activate  # macOS/Linux
```

### "CORS error" (Frontend can't connect)

**Solution:**
Edit `.env`:
```
FRONTEND_URL=http://localhost:3000
```

### JWT Token not working

**Solution:**
1. Check you're using Bearer prefix:
   ```
   Authorization: Bearer <token>
   ```
2. Token might be expired (30 days default)
3. SECRET_KEY might have changed between requests

---

## Next Steps

### 1. Read Full Documentation
See `README.md` for comprehensive guide

### 2. Explore API  
Visit `http://localhost:8000/docs` for interactive testing

### 3. Build Frontend  
Connect React to your API

### 4. Deploy  
Use Docker on production server

---

## Architecture at a Glance

```
Request Flow:
User → Frontend → HTTP Request → FastAPI Routes
                                    ↓
                              Validate (Pydantic)
                                    ↓
                              Call Service Logic
                                    ↓
                              Query Database (ORM)
                                    ↓
                              Return Data → JSON Response
```

---

## Important Files Explained

| File | Purpose |
|------|---------|
| `main.py` | Starts FastAPI, adds middleware, defines events |
| `config.py` | Loads all settings from .env file |
| `session.py` | Creates database connection & sessions |
| `models.py` | Defines 9 database tables with relationships |
| `schemas.py` | Validates incoming/outgoing data |
| `services.py` | Contains all business logic |
| `routes.py` | Defines ~32 API endpoints |
| `helpers.py` | Password hashing, JWT, OTP functions |

---

## API Endpoints Cheat Sheet

```
Auth:
  POST   /auth/register        - Register
  POST   /auth/login-email     - Email login
  POST   /auth/send-otp        - Request OTP
  POST   /auth/verify-otp      - Phone login
  GET    /auth/me              - Get profile

Users:
  GET    /users                - List users
  GET    /users/{id}           - Get user
  POST   /users/assign-site    - Assign manager

Sites:
  POST   /sites                - Create
  GET    /sites                - List
  GET    /sites/{id}           - Get
  PUT    /sites/{id}           - Update
  DELETE /sites/{id}           - Delete

Updates:
  POST   /updates              - Create
  GET    /updates              - List
  GET    /updates/{id}         - Get
  DELETE /updates/{id}         - Delete
  GET    /sites/{id}/timeline  - Timeline

Expenses:
  POST   /expenses             - Create
  GET    /expenses             - List
  GET    /expenses/{id}        - Get
  PUT    /expenses/{id}        - Update
  DELETE /expenses/{id}        - Delete

Alerts:
  GET    /alerts               - List
  PUT    /alerts/{id}/read     - Mark read

Chat:
  POST   /chat/send            - Send
  GET    /chat/{site_id}       - Get
  DELETE /chat/{id}            - Delete

Dashboard:
  GET    /dashboard/{site_id}  - Site dashboard
  GET    /dashboard/overview   - Overview

AI:
  POST   /ai/transcribe        - Transcribe audio

Health:
  GET    /health               - Status
```

---

## Monitoring & Logs

### Docker Logs

```bash
# View backend logs
docker-compose logs -f backend

# View database logs
docker-compose logs -f postgres

# View specific service
docker-compose logs -f backend | grep ERROR
```

### Local Logs

```bash
# Terminal shows logs when running with --reload
uvicorn app.main:app --reload

# Or write to file
uvicorn app.main:app --log-config logging_config.ini
```

---

## Performance Tips

1. **Use indexes on frequently queried fields**
   - Already set on: phone, email, site_id

2. **Enable query result caching**
   - Cache user profile after login

3. **Pagination**
   - Always use limit on list endpoints

4. **Connection pooling**
   - Database already configured: pool_size=5

5. **Use CDN for file uploads**
   - Store files in S3, serve via CloudFront

---

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS (not HTTP)
- [ ] Restrict CORS to your frontend domain
- [ ] Enable rate limiting
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Implement request throttling
- [ ] Validate all inputs

---

## Support

- **Documentation**: See `README.md`
- **Issues**: Check GitHub Issues
- **Questions**: Open a discussion
- **Deployment Help**: See Deployment section in README

---

## What Next?

1. ✅ API is running
2. ✅ Test endpoints at `/docs`
3. Create React frontend (connect to API)
4. Deploy to production
5. Scale and optimize

---

**Happy Building! 🚀**
