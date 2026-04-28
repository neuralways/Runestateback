"""
=============================================================================
🌐 ROUTES.PY - API ENDPOINTS
=============================================================================
Purpose:
    Defines all HTTP API endpoints (routes).
    Each endpoint handles a specific request and returns a response.
    
Architecture:
    Request → Route → Validate → Service → Database → Response
    
Naming Convention:
    GET /resource → Fetch data
    POST /resource → Create data
    PUT /resource/{id} → Update data
    DELETE /resource/{id} → Delete data
    
Status Codes:
    200 OK - Request successful
    201 Created - Resource created
    400 Bad Request - Invalid data
    401 Unauthorized - Not logged in
    403 Forbidden - Not allowed
    404 Not Found - Resource not found
    500 Server Error
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.schemas import (
    UserRegister, UserResponse, TokenResponse, UserLoginEmail, UserVerifyOTP,
    UserLoginPhone, AssignSiteManager, SiteCreate, SiteResponse, SiteUpdate,
    UpdateCreate, UpdateResponse, ExpenseCreate, ExpenseResponse, ExpenseUpdate,
    AlertResponse, AlertUpdate, MessageCreate, MessageResponse,
    DashboardStats, SiteDashboard, OverviewDashboard, TranscribeRequest, TranscribeResponse
)
from app.services.services import (
    AuthService, UserService, SiteService, UpdateService,
    ExpenseService, AlertService, MessageService
)
from app.utils.helpers import (
    create_access_token, decode_access_token, format_currency
)
from app.models.models import User
from app.core.config import settings

# Create router for API endpoints
router = APIRouter(prefix="/api/v1", tags=["API"])


# =============================================================================
# ============= DEPENDENCY: GET CURRENT USER =============
# =============================================================================

def get_current_user(
    authorization: str = None,
    db: Session = Depends(get_db)
) -> User:
    """
    DEPENDENCY: Get current authenticated user
    
    Used in protected routes like:
    @router.get("/profile")
    def get_profile(current_user: User = Depends(get_current_user)):
        return current_user
    
    Extracts JWT token from Authorization header:
    Authorization: Bearer <token>
    
    Args:
        authorization: Authorization header
        db: Database session
    
    Returns:
        User: Currently authenticated user
    
    Raises:
        HTTPException: If not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = UserService.get_user_by_id(db, int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# =============================================================================
# ============= AUTH ENDPOINTS =============
# =============================================================================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    REGISTER NEW USER
    
    Endpoint: POST /auth/register
    
    Register as a new builder or site manager.
    
    Request:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "password": "SecurePass@123",
        "role": "builder"
    }
    
    Response (200):
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "role": "builder",
        "is_phone_verified": false,
        "is_email_verified": false,
        "created_at": "2024-01-15T10:30:00Z"
    }
    
    Errors:
    - 400: Invalid data or email/phone already exists
    - 422: Validation error
    """
    try:
        user = AuthService.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auth/login-email", response_model=TokenResponse)
def login_email(credentials: UserLoginEmail, db: Session = Depends(get_db)):
    """
    LOGIN WITH EMAIL + PASSWORD
    
    Endpoint: POST /auth/login-email
    
    Authenticate with email and password.
    Returns JWT token for future requests.
    
    Request:
    {
        "email": "john@example.com",
        "password": "SecurePass@123"
    }
    
    Response (200):
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {...},
        "expires_in": 2592000
    }
    
    Errors:
    - 401: Invalid email or password
    - 422: Validation error
    """
    user = AuthService.login_with_email(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "expires_in": settings.JWT_EXPIRATION_DAYS * 86400
    }


@router.post("/auth/send-otp", status_code=status.HTTP_200_OK)
def send_otp(request: UserLoginPhone, db: Session = Depends(get_db)):
    """
    SEND OTP - Request OTP for phone login
    
    Endpoint: POST /auth/send-otp
    
    Send 6-digit OTP to phone number.
    OTP valid for 10 minutes.
    
    Request:
    {
        "phone": "+919876543210"
    }
    
    Response (200):
    {
        "message": "OTP sent to your phone",
        "expires_in": 600
    }
    
    In Production:
    - SMS sent via Twilio
    - Only logs in tests/development
    
    Errors:
    - 400: Invalid phone format
    - 422: Validation error
    """
    try:
        otp = AuthService.send_otp(db, request.phone)
        
        # In production: Send SMS via Twilio
        # twilio_client.messages.create(
        #     to=request.phone,
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     body=f"Your Runestate OTP: {otp.otp}"
        # )
        
        return {
            "message": "OTP sent to your phone",
            "expires_in": 600  # 10 minutes
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auth/verify-otp", response_model=TokenResponse)
def verify_otp(request: UserVerifyOTP, db: Session = Depends(get_db)):
    """
    VERIFY OTP - Authenticate with OTP
    
    Endpoint: POST /auth/verify-otp
    
    Verify 6-digit OTP sent to phone.
    Returns JWT token if valid.
    Creates user if first login.
    
    Request:
    {
        "phone": "+919876543210",
        "otp": "427839"
    }
    
    Response (200):
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {...},
        "expires_in": 2592000
    }
    
    Errors:
    - 401: Invalid OTP or expired
    - 422: Validation error
    """
    user = AuthService.verify_otp(db, request.phone, request.otp)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
        "expires_in": settings.JWT_EXPIRATION_DAYS * 86400
    }


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    GET CURRENT USER - Fetch authenticated user profile
    
    Endpoint: GET /auth/me
    
    Returns profile of currently authenticated user.
    Used to verify token and get user details.
    
    Headers:
    Authorization: Bearer <jwt_token>
    
    Response (200):
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+919876543210",
        "role": "builder",
        ...
    }
    
    Errors:
    - 401: Not authenticated
    - 404: User not found
    """
    return current_user


# =============================================================================
# ============= USER ENDPOINTS =============
# =============================================================================

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET ALL USERS - List all users (paginated)
    
    Endpoint: GET /users
    
    Fetch list of users with pagination.
    
    Query Parameters:
    - skip: Records to skip (default: 0)
    - limit: Records to return (default: 10, max: 100)
    
    Response (200):
    [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+919876543210",
            "role": "builder",
            ...
        },
        ...
    ]
    
    Errors:
    - 401: Not authenticated
    """
    users = UserService.get_all_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET USER BY ID - Fetch specific user details
    
    Endpoint: GET /users/{user_id}
    
    Path Parameters:
    - user_id: User ID to fetch
    
    Response (200):
    {
        "id": 1,
        "name": "John Doe",
        ...
    }
    
    Errors:
    - 401: Not authenticated
    - 404: User not found
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/users/assign-site", status_code=status.HTTP_200_OK)
def assign_site_manager(
    data: AssignSiteManager,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ASSIGN SITE MANAGER - Assign manager to site
    
    Endpoint: POST /users/assign-site
    
    Builder assigns a site manager to manage their site.
    
    Request:
    {
        "site_id": 5,
        "user_id": 10
    }
    
    Response (200):
    {
        "message": "Site manager assigned successfully",
        "site_id": 5,
        "user_id": 10
    }
    
    Errors:
    - 401: Not authenticated
    - 403: Not allowed (must be builder)
    - 404: Site or user not found
    """
    manager = UserService.assign_site_manager(db, data.site_id, data.user_id)
    
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not assign site manager"
        )
    
    return {
        "message": "Site manager assigned successfully",
        "site_id": data.site_id,
        "user_id": data.user_id
    }


# =============================================================================
# ============= SITE ENDPOINTS =============
# =============================================================================

@router.post("/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CREATE SITE - Create new construction project
    
    Endpoint: POST /sites
    
    Create new site/project (builder only).
    
    Request:
    {
        "name": "Downtown Office Complex",
        "location": "123 Main St, Downtown",
        "budget": 5000000
    }
    
    Response (201):
    {
        "id": 1,
        "name": "Downtown Office Complex",
        "location": "123 Main St, Downtown",
        "budget": 5000000,
        "builder_id": 5,
        "created_at": "2024-01-15T10:30:00Z",
        ...
    }
    
    Errors:
    - 401: Not authenticated
    - 422: Validation error
    """
    site = SiteService.create_site(db, site_data, current_user.id)
    return site


@router.get("/sites", response_model=List[SiteResponse])
def get_all_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET ALL SITES - List all sites (paginated)
    
    Endpoint: GET /sites
    """
    sites = SiteService.get_all_sites(db, skip=skip, limit=limit)
    return sites


@router.get("/sites/{site_id}", response_model=SiteResponse)
def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET SITE BY ID - Fetch specific site details
    
    Endpoint: GET /sites/{site_id}
    """
    site = SiteService.get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    return site


@router.put("/sites/{site_id}", response_model=SiteResponse)
def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    UPDATE SITE - Modify site details
    
    Endpoint: PUT /sites/{site_id}
    """
    site = SiteService.update_site(db, site_id, **site_data.dict(exclude_unset=True))
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    return site


@router.delete("/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DELETE SITE - Remove site
    
    Endpoint: DELETE /sites/{site_id}
    """
    success = SiteService.delete_site(db, site_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )


# =============================================================================
# ============= UPDATE ENDPOINTS =============
# =============================================================================

@router.post("/updates", response_model=UpdateResponse, status_code=status.HTTP_201_CREATED)
def create_update(
    update_data: UpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CREATE UPDATE - Submit progress update
    
    Endpoint: POST /updates
    
    Site manager submits progress update with photos/audio.
    
    Request:
    {
        "site_id": 1,
        "worker_count": 15,
        "notes": "Foundation poured today"
    }
    
    Response (201):
    {
        "id": 1,
        "site_id": 1,
        "created_by": 5,
        "worker_count": 15,
        "notes": "Foundation poured today",
        "created_at": "2024-01-15T10:30:00Z",
        "files": []
    }
    """
    update = UpdateService.create_update(db, update_data, current_user.id)
    return update


@router.get("/updates", response_model=List[UpdateResponse])
def get_all_updates(
    site_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET ALL UPDATES - List updates
    
    Endpoint: GET /updates?site_id=1
    
    Filter by site_id if provided.
    """
    if site_id:
        updates = UpdateService.get_updates_by_site(db, site_id)
    else:
        # Get all updates
        updates = db.query(Update).offset(skip).limit(limit).all()
    
    return updates


@router.get("/updates/{update_id}", response_model=UpdateResponse)
def get_update(
    update_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET UPDATE BY ID
    
    Endpoint: GET /updates/{update_id}
    """
    update = UpdateService.get_update_by_id(db, update_id)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
    return update


@router.delete("/updates/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_update(
    update_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DELETE UPDATE
    
    Endpoint: DELETE /updates/{update_id}
    """
    success = UpdateService.delete_update(db, update_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )


@router.get("/sites/{site_id}/timeline", response_model=List[UpdateResponse])
def get_site_timeline(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET SITE TIMELINE - Get all updates for a site
    
    Endpoint: GET /sites/{site_id}/timeline
    
    Returns chronological list of updates for site.
    """
    updates = UpdateService.get_updates_by_site(db, site_id)
    return updates


# =============================================================================
# ============= EXPENSE ENDPOINTS =============
# =============================================================================

@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CREATE EXPENSE - Record new expense
    
    Endpoint: POST /expenses
    """
    expense = ExpenseService.create_expense(db, expense_data, current_user.id)
    return expense


@router.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(
    site_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET EXPENSES - List expenses
    
    Endpoint: GET /expenses?site_id=1
    """
    if site_id:
        expenses = ExpenseService.get_expenses_by_site(db, site_id)
    else:
        expenses = db.query(Expense).offset(skip).limit(limit).all()
    
    return expenses


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET EXPENSE BY ID
    
    Endpoint: GET /expenses/{expense_id}
    """
    expense = ExpenseService.get_expense_by_id(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    UPDATE EXPENSE
    
    Endpoint: PUT /expenses/{expense_id}
    """
    expense = ExpenseService.update_expense(db, expense_id, **expense_data.dict(exclude_unset=True))
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DELETE EXPENSE
    
    Endpoint: DELETE /expenses/{expense_id}
    """
    success = ExpenseService.delete_expense(db, expense_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )


# =============================================================================
# ============= ALERT ENDPOINTS =============
# =============================================================================

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    site_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET ALERTS - List alerts
    
    Endpoint: GET /alerts?site_id=1
    """
    if site_id:
        alerts = AlertService.get_alerts_by_site(db, site_id)
    else:
        alerts = db.query(Alert).all()
    
    return alerts


@router.put("/alerts/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    MARK ALERT READ - Mark alert as read/unread
    
    Endpoint: PUT /alerts/{alert_id}/read
    """
    alert = AlertService.mark_alert_read(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return alert


# =============================================================================
# ============= MESSAGE ENDPOINTS =============
# =============================================================================

@router.post("/chat/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    SEND MESSAGE - Send chat message
    
    Endpoint: POST /chat/send
    """
    message = MessageService.create_message(db, message_data, current_user.id)
    return message


@router.get("/chat/{site_id}", response_model=List[MessageResponse])
def get_messages(
    site_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET MESSAGES - Get chat messages for site
    
    Endpoint: GET /chat/{site_id}
    """
    messages = MessageService.get_messages_by_site(db, site_id)
    return messages


@router.delete("/chat/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DELETE MESSAGE
    
    Endpoint: DELETE /chat/{message_id}
    """
    success = MessageService.delete_message(db, message_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )


# =============================================================================
# ============= DASHBOARD ENDPOINTS =============
# =============================================================================

@router.get("/dashboard/{site_id}")
def get_site_dashboard(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET SITE DASHBOARD - Complete site dashboard
    
    Endpoint: GET /dashboard/{site_id}
    
    Returns all data needed for site details page.
    """
    site = SiteService.get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Calculate stats
    total_expenses = ExpenseService.get_total_expenses(db, site_id)
    total_workers = sum(u.worker_count or 0 for u in UpdateService.get_updates_by_site(db, site_id))
    
    stats = {
        "total_workers": total_workers,
        "total_expenses": total_expenses,
        "budget": site.budget,
        "expense_percentage": (total_expenses / site.budget * 100) if site.budget > 0 else 0,
        "total_alerts": len(AlertService.get_alerts_by_site(db, site_id)),
        "unread_alerts": len([a for a in AlertService.get_alerts_by_site(db, site_id) if not a.is_read]),
        "total_updates": len(UpdateService.get_updates_by_site(db, site_id)),
        "recent_updates": UpdateService.get_updates_by_site(db, site_id)[:5]
    }
    
    return {
        "site": site,
        "stats": stats,
        "managers": site.managers,
        "recent_expenses": ExpenseService.get_expenses_by_site(db, site_id)[:5]
    }


@router.get("/dashboard/overview")
def get_overview_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET OVERVIEW DASHBOARD - Overview of all sites
    
    Endpoint: GET /dashboard/overview
    
    Returns high-level statistics across all sites.
    """
    sites = SiteService.get_sites_by_builder(db, current_user.id)
    
    total_budget = sum(s.budget for s in sites)
    total_expenses = sum(ExpenseService.get_total_expenses(db, s.id) for s in sites)
    
    return {
        "total_sites": len(sites),
        "total_workers": 0,  # Calculate from all updates
        "total_expenses": total_expenses,
        "total_budget": total_budget,
        "sites": sites
    }


# =============================================================================
# ============= AI ENDPOINTS =============
# =============================================================================

@router.post("/ai/transcribe", response_model=TranscribeResponse)
def transcribe_audio(
    request: TranscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    TRANSCRIBE AUDIO - Convert audio to text using Whisper
    
    Endpoint: POST /ai/transcribe
    
    Send audio file URL to be transcribed.
    Uses OpenAI Whisper API.
    
    Request:
    {
        "audio_url": "https://s3.amazonaws.com/bucket/audio.mp3"
    }
    
    Response (200):
    {
        "text": "Foundation concrete poured today. Workers on track.",
        "duration": 15.5,
        "language": "en"
    }
    
    In Production:
    - Call OpenAI API with settings.OPENAI_API_KEY
    - Handle errors gracefully
    - Cache results if needed
    """
    try:
        # In production:
        # import openai
        # response = openai.Audio.transcribe(
        #     model="whisper-1",
        #     audio=request.audio_url,
        #     language="en"
        # )
        # return TranscribeResponse(text=response["text"])
        
        # For testing:
        return {
            "text": "Sample transcribed text from audio",
            "duration": 15.5,
            "language": "en"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transcription failed: {str(e)}"
        )


# =============================================================================
# ============= HEALTH CHECK ENDPOINT =============
# =============================================================================

@router.get("/health")
def health_check():
    """
    HEALTH CHECK - API status
    
    Endpoint: GET /health
    
    Used by monitoring tools to check if API is running.
    
    Response (200):
    {
        "status": "healthy",
        "version": "1.0.0"
    }
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }
