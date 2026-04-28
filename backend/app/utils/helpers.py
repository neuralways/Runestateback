"""
=============================================================================
🔧 HELPERS.PY - UTILITY FUNCTIONS
=============================================================================
Purpose:
    Common helper functions used throughout the application:
    - Password hashing & verification
    - JWT token creation & validation
    - Email/OTP sending
    - Date/time utilities
    
Why Separate File:
    ✅ DRY (Don't Repeat Yourself)
    ✅ Reusable across services
    ✅ Easier testing
    ✅ Cleaner code
=============================================================================
"""

import jwt
import random
import string
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional, Dict, Any

from app.core.config import settings


# =============================================================================
# PASSWORD HASHING
# =============================================================================

# CryptContext = Password hashing configuration
# scheme="bcrypt": Use BCrypt algorithm (most secure)
# Other options: "argon2", "scrypt"
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"  # Auto upgrade hash if algorithm changes
)


def hash_password(password: str) -> str:
    """
    HASH PASSWORD - Securely hash plain text password
    
    Uses BCrypt algorithm:
    - One-way hashing (can't reverse)
    - Adds random salt (prevents rainbow tables)
    - Slow algorithm (prevents brute force)
    
    Args:
        password (str): Plain text password from user
    
    Returns:
        str: Hashed password (can be stored in DB)
    
    Example:
        hashed = hash_password("MyPassword123")
        # Output: $2b$12$abcdef...
        # Store hashed version in database
    
    Security:
        ✅ Never store plain passwords
        ✅ Hash before saving to DB
        ✅ Same password = different hash (due to salt)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    VERIFY PASSWORD - Check if plain password matches hash
    
    During login:
    1. User enters password
    2. Hash the input
    3. Compare with stored hash
    4. Match = correct password
    
    Args:
        plain_password (str): Password entered by user
        hashed_password (str): Hashed password from database
    
    Returns:
        bool: True if passwords match, False otherwise
    
    Example:
        db_hash = user.password  # "$2b$12$abcdef..."
        user_input = "MyPassword123"
        if verify_password(user_input, db_hash):
            # Password correct - login user
            return create_token(user.id)
    
    Security:
        ✅ Uses constant-time comparison (prevents timing attacks)
        ✅ Safe to compare sensitive data
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    CREATE JWT TOKEN - Generate authentication token
    
    JWT (JSON Web Token) flow:
    1. User logs in with credentials
    2. Server creates JWT with user data
    3. Client stores JWT and sends with each request
    4. Server verifies JWT signature
    5. If valid, process request; if invalid, reject
    
    Args:
        data (dict): Data to encode in token (e.g., {"sub": user_id})
        expires_delta (timedelta, optional): Token expiration time
                                            Defaults to 30 days
    
    Returns:
        str: Encoded JWT token
    
    Example:
        user_id = 5
        token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(days=7)
        )
        # Client receives token and stores for future requests
    
    JWT Structure:
        Token = Header.Payload.Signature
        Header: Algorithm (HS256)
        Payload: User data + expiration
        Signature: HMAC-SHA256(Header.Payload, SECRET_KEY)
        
    Security:
        ✅ Signature proves token not tampered
        ✅ Expiration prevents long-lived tokens
        ✅ User data encoded (but NOT encrypted)
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default: JWT_EXPIRATION_DAYS from config
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)
    
    # Add expiration to token data
    to_encode.update({"exp": expire})
    
    # Encode: Create JWT token signature
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    DECODE JWT TOKEN - Verify and extract data from token
    
    Called on each request:
    1. Extract token from Authorization header
    2. Verify signature using SECRET_KEY
    3. Check if expired
    4. Return payload if valid, None if invalid
    
    Args:
        token (str): JWT token from client
    
    Returns:
        dict: Token payload if valid
        None: If token invalid/expired
    
    Example:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            # User authenticated - process request
        else:
            # Invalid token - reject request
    
    Raises:
        jwt.InvalidTokenError: If signature invalid or tampered
        jwt.ExpiredSignatureError: If token expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token expired
        return None
    except jwt.InvalidTokenError:
        # Signature invalid / tampered token
        return None


# =============================================================================
# OTP GENERATION
# =============================================================================

def generate_otp(length: int = 6) -> str:
    """
    GENERATE OTP - Create random OTP code
    
    Used for phone number verification.
    
    Args:
        length (int): Length of OTP (default 6 digits)
    
    Returns:
        str: Random OTP code
    
    Example:
        otp = generate_otp()
        # Output: "427839"
        # Send via SMS to user
        # Store in database with expiration
    
    Security:
        ✅ Random generation (not sequential)
        ✅ Expires in 10 minutes
        ✅ Can only be used once
    """
    # Generate random digits
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp


def is_otp_valid(expires_at: datetime) -> bool:
    """
    CHECK IF OTP EXPIRED - Verify OTP hasn't expired
    
    Args:
        expires_at (datetime): When OTP expires
    
    Returns:
        bool: True if not expired, False if expired
    
    Example:
        otp = OTPVerification(
            phone="+919876543210",
            otp="427839",
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        
        if is_otp_valid(otp.expires_at):
            # OTP still valid
        else:
            # OTP expired - ask user to request new one
    """
    return datetime.utcnow() < expires_at


# =============================================================================
# DATE/TIME UTILITIES
# =============================================================================

def get_current_utc() -> datetime:
    """
    GET CURRENT UTC TIME
    
    Always use UTC internally for consistency.
    Convert to local timezone on frontend.
    
    Returns:
        datetime: Current time in UTC
    """
    return datetime.utcnow()


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """
    ADD MINUTES TO DATETIME
    
    Used for OTP expiration:
    expires_at = add_minutes(datetime.utcnow(), 10)
    
    Args:
        dt (datetime): Starting datetime
        minutes (int): Minutes to add
    
    Returns:
        datetime: Result datetime
    """
    return dt + timedelta(minutes=minutes)


# =============================================================================
# STRING UTILITIES
# =============================================================================

def format_currency(amount: int) -> str:
    """
    FORMAT CURRENCY - Convert paise to rupees
    
    Database stores amounts as integers (paise/cents) to avoid decimals.
    For display: paise / 100 = rupees
    
    Args:
        amount (int): Amount in paise
    
    Returns:
        str: Formatted string with rupees
    
    Example:
        amount = 50000  # paise
        formatted = format_currency(amount)
        # Output: "₹500.00"
    """
    rupees = amount / 100
    return f"₹{rupees:,.2f}"


def is_valid_phone(phone: str) -> bool:
    """
    VALIDATE PHONE NUMBER - Check if phone is valid
    
    Args:
        phone (str): Phone number (with or without country code)
    
    Returns:
        bool: True if valid format
    
    Example:
        is_valid_phone("+919876543210")  # True
        is_valid_phone("9876543210")     # True
        is_valid_phone("abc")            # False
    """
    # Remove common formatting
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    # Should be digits and optional + at start
    if clean_phone.startswith('+'):
        clean_phone = clean_phone[1:]
    return clean_phone.isdigit() and 10 <= len(clean_phone) <= 15


# =============================================================================
# PAGINATION UTILITIES
# =============================================================================

def get_offset_limit(page: int, limit: int) -> tuple:
    """
    CALCULATE OFFSET & LIMIT FOR PAGINATION
    
    For database queries:
    - offset: Record to start at
    - limit: Number of records
    
    Args:
        page (int): Page number (1-indexed)
        limit (int): Records per page
    
    Returns:
        tuple: (offset, limit)
    
    Example:
        offset, limit = get_offset_limit(page=2, limit=10)
        # offset=10, limit=10
        # Get records 11-20
        
        users = db.query(User).offset(offset).limit(limit).all()
    """
    offset = (page - 1) * limit
    return offset, limit
