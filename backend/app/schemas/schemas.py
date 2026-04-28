"""
=============================================================================
📝 SCHEMAS.PY - REQUEST/RESPONSE DATA MODELS
=============================================================================
Purpose:
    Defines Pydantic models for request validation and response serialization.
    
Key Concepts:
    - Schemas = Data validation blueprints
    - Separate from DB Models for flexibility
    - Automatic validation, serialization, documentation
    - Generate OpenAPI docs automatically
    
Types of Schemas:
    - Create*: For POST/PUT requests (input)
    - *Response: For API responses (output)
    - *Base: Common fields used in both
    
Why Separate from Models:
    - DB models might have sensitive fields (password, tokens)
    - API doesn't always return all fields
    - Easy to change API without changing DB
    - Can validate data before storing
=============================================================================
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# =============================================================================
# ============= AUTH SCHEMAS ============= 
# =============================================================================

class UserLoginPhone(BaseModel):
    """
    REQUEST: Phone login
    Endpoint: POST /auth/login-phone
    
    User provides phone number to request OTP.
    
    Fields:
    - phone: Phone number (with country code)
    
    Example:
    {
        "phone": "+919876543210"
    }
    """
    phone: str = Field(..., min_length=10, max_length=15)
    
    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        # Remove common formatting characters
        v = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        # Should contain only digits and optional + at start
        if not v.replace('+', '').isdigit():
            raise ValueError('Phone must contain only digits')
        return v


class UserLoginEmail(BaseModel):
    """
    REQUEST: Email login
    Endpoint: POST /auth/login-email
    
    User provides email and password.
    
    Fields:
    - email: Email address
    - password: Plain text password (validated against hash in DB)
    
    Example:
    {
        "email": "user@example.com",
        "password": "SecurePass@123"
    }
    """
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserVerifyOTP(BaseModel):
    """
    REQUEST: Verify OTP
    Endpoint: POST /auth/verify-otp
    
    User provides phone and OTP code to verify.
    
    Fields:
    - phone: Phone number that received OTP
    - otp: 6-digit OTP code
    
    Example:
    {
        "phone": "+919876543210",
        "otp": "123456"
    }
    """
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)


class UserRegister(BaseModel):
    """
    REQUEST: User registration
    Endpoint: POST /auth/register
    
    User registers as new builder or site manager.
    
    Fields:
    - name: Full name
    - email: Email (optional if phone provided)
    - phone: Phone (optional if email provided)
    - password: Password (optional if using OTP)
    - role: 'builder' or 'site_manager'
    
    Rules:
    - At least one of email or phone required
    - Password required if using email
    
    Example:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "password": "SecurePass@123",
        "role": "builder"
    }
    """
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    role: str = Field(..., pattern="^(builder|site_manager)$")


class TokenResponse(BaseModel):
    """
    RESPONSE: Token after successful login
    
    Returned after successful login:
    - POST /auth/login-email
    - POST /auth/verify-otp
    
    Fields:
    - access_token: JWT token for authentication
    - token_type: Type of token (usually "bearer")
    - user: User details
    - expires_in: Time until expiration (seconds)
    
    Example:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {...},
        "expires_in": 2592000
    }
    """
    access_token: str
    token_type: str = "bearer"
    user: 'UserResponse'
    expires_in: int


# =============================================================================
# ============= USER SCHEMAS ============= 
# =============================================================================

class UserBase(BaseModel):
    """
    BASE: Common user fields
    Used in Create and Response schemas.
    """
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str


class UserCreate(UserBase):
    """
    REQUEST: Create user
    Endpoint: POST /users
    """
    password: str


class UserUpdate(BaseModel):
    """
    REQUEST: Update user
    Endpoint: PUT /users/{user_id}
    
    All fields optional (update only what's provided).
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """
    RESPONSE: User details
    
    Used in:
    - GET /users
    - GET /users/{user_id}
    - Token response
    
    Note: Password NOT included in response.
    
    Example:
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "role": "builder",
        "is_phone_verified": true,
        "is_email_verified": true,
        "created_at": "2024-01-15T10:30:00Z"
    }
    """
    id: int
    is_phone_verified: bool
    is_email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allow reading from ORM models


class AssignSiteManager(BaseModel):
    """
    REQUEST: Assign site manager to site
    Endpoint: POST /users/assign-site
    
    Builder assigns a site manager to manage their site.
    
    Fields:
    - site_id: Which site
    - user_id: Which user (site manager) to assign
    
    Example:
    {
        "site_id": 5,
        "user_id": 10
    }
    """
    site_id: int
    user_id: int


# =============================================================================
# ============= SITE SCHEMAS ============= 
# =============================================================================

class SiteBase(BaseModel):
    """
    BASE: Common site fields
    """
    name: str = Field(..., min_length=1, max_length=150)
    location: str = Field(..., min_length=1)
    budget: int = Field(..., gt=0)  # Must be > 0


class SiteCreate(SiteBase):
    """
    REQUEST: Create site
    Endpoint: POST /sites
    
    Example:
    {
        "name": "Downtown Office Complex",
        "location": "123 Main St, Downtown",
        "budget": 5000000  # ₹50,000
    }
    """
    pass


class SiteUpdate(BaseModel):
    """
    REQUEST: Update site
    Endpoint: PUT /sites/{site_id}
    """
    name: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[int] = None


class SiteResponse(SiteBase):
    """
    RESPONSE: Site details
    
    Used in:
    - GET /sites
    - GET /sites/{site_id}
    - POST /sites (creation response)
    
    Example:
    {
        "id": 1,
        "name": "Downtown Office Complex",
        "location": "123 Main St, Downtown",
        "budget": 5000000,
        "builder_id": 5,
        "created_at": "2024-01-15T10:30:00Z",
        "managers": [...]
    }
    """
    id: int
    builder_id: int
    created_at: datetime
    updated_at: datetime
    managers: Optional[List[UserResponse]] = []
    
    class Config:
        from_attributes = True


# =============================================================================
# ============= UPDATE SCHEMAS ============= 
# =============================================================================

class UpdateFileResponse(BaseModel):
    """
    RESPONSE: File metadata
    
    Used in Update responses to show attached files.
    """
    id: int
    file_url: str
    file_type: str  # 'image', 'audio', 'document'
    created_at: datetime
    
    class Config:
        from_attributes = True


class UpdateBase(BaseModel):
    """
    BASE: Common update fields
    """
    worker_count: Optional[int] = None
    notes: Optional[str] = None


class UpdateCreate(UpdateBase):
    """
    REQUEST: Create update
    Endpoint: POST /updates
    
    Site manager submits progress update.
    Files uploaded separately.
    
    Example:
    {
        "site_id": 1,
        "worker_count": 15,
        "notes": "Foundation concrete poured today. Workers on track."
    }
    """
    site_id: int


class UpdateResponse(UpdateBase):
    """
    RESPONSE: Update details
    
    Used in:
    - GET /updates
    - GET /updates/{update_id}
    - GET /sites/{site_id}/timeline
    
    Example:
    {
        "id": 1,
        "site_id": 1,
        "created_by": 5,
        "worker_count": 15,
        "notes": "Foundation concrete poured today.",
        "voice_text": "Transcription of voice note...",
        "created_at": "2024-01-15T10:30:00Z",
        "files": [...]
    }
    """
    id: int
    site_id: int
    created_by: int
    voice_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    files: Optional[List[UpdateFileResponse]] = []
    
    class Config:
        from_attributes = True


# =============================================================================
# ============= EXPENSE SCHEMAS ============= 
# =============================================================================

class ExpenseBase(BaseModel):
    """
    BASE: Common expense fields
    """
    amount: int = Field(..., gt=0)
    category: str
    note: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """
    REQUEST: Create expense
    Endpoint: POST /expenses
    
    Example:
    {
        "site_id": 1,
        "amount": 100000,  # ₹1000
        "category": "cement",
        "note": "100 bags of cement"
    }
    """
    site_id: int


class ExpenseUpdate(BaseModel):
    """
    REQUEST: Update expense
    Endpoint: PUT /expenses/{expense_id}
    """
    amount: Optional[int] = None
    category: Optional[str] = None
    note: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    """
    RESPONSE: Expense details
    
    Used in:
    - GET /expenses
    - GET /expenses?site_id=1
    
    Example:
    {
        "id": 1,
        "site_id": 1,
        "added_by": 5,
        "amount": 100000,
        "category": "cement",
        "note": "100 bags of cement",
        "created_at": "2024-01-15T10:30:00Z"
    }
    """
    id: int
    site_id: int
    added_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# ============= ALERT SCHEMAS ============= 
# =============================================================================

class AlertBase(BaseModel):
    """
    BASE: Common alert fields
    """
    type: str
    message: str


class AlertResponse(AlertBase):
    """
    RESPONSE: Alert details
    
    Used in:
    - GET /alerts
    - GET /alerts?site_id=1
    
    Example:
    {
        "id": 1,
        "site_id": 1,
        "type": "budget",
        "message": "Budget exceeded by 10%",
        "is_read": false,
        "created_at": "2024-01-15T10:30:00Z"
    }
    """
    id: int
    site_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """
    REQUEST: Update alert (mark as read)
    Endpoint: PUT /alerts/{alert_id}
    """
    is_read: bool


# =============================================================================
# ============= MESSAGE SCHEMAS ============= 
# =============================================================================

class MessageBase(BaseModel):
    """
    BASE: Common message fields
    """
    message: str


class MessageCreate(MessageBase):
    """
    REQUEST: Send message
    Endpoint: POST /chat/send
    
    Example:
    {
        "site_id": 1,
        "message": "Can we start the next phase?"
    }
    """
    site_id: int


class MessageResponse(MessageBase):
    """
    RESPONSE: Message details
    
    Used in:
    - GET /chat/{site_id}
    
    Example:
    {
        "id": 1,
        "site_id": 1,
        "sender_id": 5,
        "message": "Can we start next phase?",
        "created_at": "2024-01-15T10:30:00Z"
    }
    """
    id: int
    site_id: int
    sender_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# ============= DASHBOARD SCHEMAS ============= 
# =============================================================================

class DashboardStats(BaseModel):
    """
    RESPONSE: Dashboard statistics
    
    Used in:
    - GET /dashboard/{site_id}
    - GET /dashboard/overview
    
    Contains aggregated data about:
    - Worker counts
    - Expenses vs budget
    - Number of alerts
    - Recent updates
    """
    total_workers: int
    total_expenses: int
    budget: int
    expense_percentage: float  # 0-100
    total_alerts: int
    unread_alerts: int
    total_updates: int
    recent_updates: List[UpdateResponse]


class SiteDashboard(BaseModel):
    """
    RESPONSE: Complete site dashboard
    
    Returned by:
    - GET /dashboard/{site_id}
    
    Contains all info needed for site details page.
    """
    site: SiteResponse
    stats: DashboardStats
    managers: List[UserResponse]
    recent_expenses: List[ExpenseResponse]


class OverviewDashboard(BaseModel):
    """
    RESPONSE: Overview dashboard (all sites)
    
    Returned by:
    - GET /dashboard/overview
    
    High-level stats across all sites.
    """
    total_sites: int
    total_workers: int
    total_expenses: int
    total_budget: int
    sites: List[SiteResponse]


# =============================================================================
# ============= AI SCHEMAS ============= 
# =============================================================================

class TranscribeRequest(BaseModel):
    """
    REQUEST: Transcribe audio
    Endpoint: POST /ai/transcribe
    
    Send audio file URL to be transcribed using Whisper.
    
    Example:
    {
        "audio_url": "https://s3.amazonaws.com/bucket/audio.mp3"
    }
    """
    audio_url: str


class TranscribeResponse(BaseModel):
    """
    RESPONSE: Transcription result
    
    Contains transcribed text from audio.
    
    Example:
    {
        "text": "Foundation concrete poured today. Workers on track.",
        "duration": 15.5,
        "language": "en"
    }
    """
    text: str
    duration: Optional[float] = None
    language: Optional[str] = "en"


# =============================================================================
# ============= ERROR SCHEMAS ============= 
# =============================================================================

class ErrorResponse(BaseModel):
    """
    RESPONSE: Error response
    
    Returned on any API error.
    
    Example:
    {
        "detail": "User not found",
        "status_code": 404
    }
    """
    detail: str
    status_code: int


class ValidationError(BaseModel):
    """
    RESPONSE: Validation error
    
    Returned when request validation fails.
    
    Example:
    {
        "detail": [
            {
                "loc": ["body", "email"],
                "msg": "Not a valid email",
                "type": "value_error.email"
            }
        ]
    }
    """
    detail: List[dict]
