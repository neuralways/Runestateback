"""
=============================================================================
🗄️ MODELS.PY - DATABASE TABLE DEFINITIONS
=============================================================================
Purpose:
    Defines all database tables using SQLAlchemy ORM.
    Each class represents a table in PostgreSQL.
    
Key Concepts:
    - Column: Database column definition
    - Relationship: Define relationships between tables (1-to-many, many-to-many)
    - ForeignKey: Reference to another table's primary key
    - Index: Speed up database queries
    
SQLAlchemy Type Mapping:
    Integer → SQL INT
    String → SQL VARCHAR
    Text → SQL TEXT
    DateTime → SQL TIMESTAMP
    Boolean → SQL BOOLEAN
    
Why This Structure:
    ✅ Type-safe database operations
    ✅ Automatic validation
    ✅ Easy to query with ORM
    ✅ Auto-generates SQL
=============================================================================
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.session import Base


# =============================================================================
# 1. USERS TABLE - Core user information
# =============================================================================
class User(Base):
    """
    USER MODEL
    
    Stores user information (builders, site managers)
    
    Fields Explanation:
    - id: Unique identifier (Primary Key)
    - name: User's full name
    - phone: Phone number (unique for OTP login)
    - email: Email address (unique for email login)
    - password: Hashed password (nullable if using OTP only)
    - role: 'builder' or 'site_manager' (determines permissions)
    - is_phone_verified: Whether phone number is verified
    - is_email_verified: Whether email is verified
    - created_at: When user account was created
    
    Constraints:
    - At least one of phone or email must exist (enforced in service)
    - phone and email are unique (can't use same phone twice)
    
    Relationships:
    - sites: Sites created by this builder
    - managed_sites: Sites managed by this site_manager
    - updates: Updates created by this user
    - expenses: Expenses added by this user
    """
    __tablename__ = "users"
    
    # Primary Key - Unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    name = Column(String(100), nullable=False)
    
    # Authentication Fields
    phone = Column(String(15), unique=True, nullable=True, index=True)  # Index for fast phone lookup
    email = Column(String(150), unique=True, nullable=True, index=True)  # Index for fast email lookup
    password = Column(Text, nullable=True)  # Hashed password (not plain text!)
    
    # User Type/Role
    role = Column(String(20), nullable=False)  # 'builder' or 'site_manager'
    
    # Verification Flags
    is_phone_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (For easy access in code)
    sites = relationship("Site", back_populates="builder", foreign_keys="Site.builder_id")
    managed_sites = relationship("Site", secondary="site_managers", back_populates="managers")
    updates = relationship("Update", back_populates="created_by")
    expenses = relationship("Expense", back_populates="added_by")
    messages = relationship("Message", back_populates="sender")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, phone={self.phone}, role={self.role})>"


# =============================================================================
# 2. OTP VERIFICATIONS TABLE - For phone OTP login
# =============================================================================
class OTPVerification(Base):
    """
    OTP VERIFICATION MODEL
    
    Stores temporary OTP codes for phone number verification.
    Each OTP expires after a certain time.
    
    Flow:
    1. User enters phone number
    2. Send OTP via SMS (Twilio)
    3. Store OTP in this table with expiration time
    4. User enters OTP
    5. Verify OTP matches and hasn't expired
    6. Set is_phone_verified=True on User
    
    Fields Explanation:
    - id: Unique identifier
    - phone: Phone number OTP was sent to
    - otp: The 6-digit code
    - expires_at: When OTP becomes invalid
    - is_used: Whether OTP was already used
    - created_at: When OTP was generated
    
    Security Notes:
    - OTPs should expire in 10 minutes
    - After successful use, mark is_used=True
    - Old OTPs should be deleted periodically
    """
    __tablename__ = "otp_verifications"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Phone number for this OTP
    phone = Column(String(15), nullable=False, index=True)
    
    # The OTP code (typically 6 digits)
    otp = Column(String(6), nullable=False)
    
    # When this OTP expires (typically 10 minutes from creation)
    expires_at = Column(DateTime, nullable=False)
    
    # Whether this OTP has been used
    is_used = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<OTPVerification(phone={self.phone}, expires_at={self.expires_at})>"


# =============================================================================
# 3. SITES TABLE - Construction projects
# =============================================================================
class Site(Base):
    """
    SITE MODEL
    
    Represents a construction project/site.
    Created by builders, managed by site managers.
    
    Fields Explanation:
    - id: Unique site identifier
    - name: Project name
    - location: Project location/address
    - budget: Total project budget (in paise/cents)
    - builder_id: User who created this site
    - created_at: When project was created
    
    Relationships:
    - builder: User who owns this site
    - managers: Site managers assigned to this site
    - updates: Progress updates for this site
    - expenses: Expenses for this site
    - alerts: Alerts/issues for this site
    - messages: Chat messages for this site
    
    Note:
    - Budget is stored as BigInteger for precision (no decimal issues)
    - To display: budget / 100 to get amount in rupees
    """
    __tablename__ = "sites"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Site Information
    name = Column(String(150), nullable=False)
    location = Column(Text, nullable=False)
    budget = Column(BigInteger, nullable=False)  # In paise (cents)
    
    # Permission: Who created this site
    builder_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    builder = relationship("User", back_populates="sites", foreign_keys=[builder_id])
    managers = relationship("User", secondary="site_managers", back_populates="managed_sites")
    updates = relationship("Update", back_populates="site", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="site", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="site", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="site", cascade="all, delete-orphan")
    
    # Index for fast queries by builder
    __table_args__ = (Index('idx_sites_builder', 'builder_id'),)
    
    def __repr__(self):
        return f"<Site(id={self.id}, name={self.name}, location={self.location})>"


# =============================================================================
# 4. SITE MANAGERS TABLE - Many-to-many relationship (Sites ↔ Managers)
# =============================================================================
class SiteManager(Base):
    """
    SITE MANAGER MODEL
    
    Maps site managers to sites they manage.
    One site can have multiple managers.
    One manager can manage multiple sites.
    
    This is a junction table for many-to-many relationship.
    
    Fields Explanation:
    - id: Unique identifier for this assignment
    - site_id: Which site is being managed
    - user_id: Which user is managing it
    - assigned_at: When manager was assigned
    
    Example:
    - Site 1 has managers: User 5, User 7
    - Site 2 has managers: User 5, User 9
    - User 5 manages: Site 1, Site 2
    """
    __tablename__ = "site_managers"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for fast lookups
    __table_args__ = (Index('idx_site_managers_site', 'site_id'),
                      Index('idx_site_managers_user', 'user_id'),)
    
    def __repr__(self):
        return f"<SiteManager(site_id={self.site_id}, user_id={self.user_id})>"


# =============================================================================
# 5. UPDATES TABLE - Site progress updates
# =============================================================================
class Update(Base):
    """
    UPDATE MODEL
    
    Progress updates submitted by site managers.
    Can include: worker count, notes, voice transcription.
    Related files (photos, audio) stored in update_files table.
    
    Fields Explanation:
    - id: Unique update identifier
    - site_id: Which site this update is about
    - created_by: Which user submitted this update
    - worker_count: Number of workers at site
    - notes: Text description of progress
    - voice_text: Transcription of voice note (from Whisper)
    - created_at: When update was submitted
    
    Relationships:
    - site: Which site this is for
    - created_by: User who submitted update
    - files: Photos/audio/documents linked to update
    
    Typical Flow:
    1. Site manager opens app
    2. Takes photos, records voice note
    3. Submits with worker count
    4. Voice converted to text via Whisper AI
    5. Builder sees update in timeline
    """
    __tablename__ = "updates"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Data
    worker_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    voice_text = Column(Text, nullable=True)  # Transcription from Whisper
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    site = relationship("Site", back_populates="updates")
    created_by_user = relationship("User", back_populates="updates", foreign_keys=[created_by])
    files = relationship("UpdateFile", back_populates="update", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (Index('idx_updates_site', 'site_id'),
                      Index('idx_updates_created_by', 'created_by'),)
    
    def __repr__(self):
        return f"<Update(id={self.id}, site_id={self.site_id}, worker_count={self.worker_count})>"


# =============================================================================
# 6. UPDATE FILES TABLE - Files linked to updates (photos, audio)
# =============================================================================
class UpdateFile(Base):
    """
    UPDATE FILE MODEL
    
    Stores metadata for files (photos, audio) attached to updates.
    Examples:
    - Photos of construction progress
    - Audio files (voice notes)
    - Documents/PDFs
    
    Fields Explanation:
    - id: Unique file identifier
    - update_id: Which update this file belongs to
    - file_url: URL to file in S3/cloud storage
    - file_type: 'image', 'audio', or 'document'
    - created_at: When file was uploaded
    
    Storage:
    - Files stored in AWS S3 bucket
    - file_url = "https://s3.amazonaws.com/bucket/path/to/file"
    - Only metadata stored in database
    
    Note:
    - Files are NOT stored in database (too large)
    - Only URLs and metadata stored
    - Actual files in S3/cloud
    """
    __tablename__ = "update_files"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    update_id = Column(Integer, ForeignKey("updates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File Metadata
    file_url = Column(Text, nullable=False)  # URL to file in S3
    file_type = Column(String(20), nullable=False)  # 'image', 'audio', 'document'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    update = relationship("Update", back_populates="files")
    
    def __repr__(self):
        return f"<UpdateFile(id={self.id}, file_type={self.file_type})>"


# =============================================================================
# 7. EXPENSES TABLE - Project expenses/costs
# =============================================================================
class Expense(Base):
    """
    EXPENSE MODEL
    
    Tracks all expenses for a site (materials, labor, equipment, etc.)
    Used for budget tracking and cost analysis.
    
    Fields Explanation:
    - id: Unique expense identifier
    - site_id: Which site this expense is for
    - added_by: User who recorded this expense
    - amount: Cost amount (in paise/cents)
    - category: Type of expense (cement, labor, equipment, etc.)
    - note: Description of expense
    - created_at: When expense was recorded
    
    Example:
    - amount = 50000 (paise) = ₹500
    - category = "cement"
    - note = "100 bags of cement for foundation"
    
    Usage:
    - Builders track total costs
    - Compare actual vs budgeted
    - Identify cost overruns
    """
    __tablename__ = "expenses"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Expense Data
    amount = Column(BigInteger, nullable=False)  # In paise/cents
    category = Column(String(100), nullable=False)
    note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    site = relationship("Site", back_populates="expenses")
    added_by_user = relationship("User", back_populates="expenses", foreign_keys=[added_by])
    
    # Indexes
    __table_args__ = (Index('idx_expenses_site', 'site_id'),)
    
    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, category={self.category})>"


# =============================================================================
# 8. ALERTS TABLE - Warnings/issues detected
# =============================================================================
class Alert(Base):
    """
    ALERT MODEL
    
    Stores alerts/warnings for a site.
    Examples:
    - Budget exceeded
    - Safety concerns
    - Schedule delays
    - Anomalies detected by AI
    
    Fields Explanation:
    - id: Unique alert identifier
    - site_id: Which site this alert is about
    - type: Alert category (budget, safety, schedule, etc.)
    - message: Alert description
    - is_read: Whether builder has seen it
    - created_at: When alert was created
    
    Usage:
    - AI model generates alerts
    - Site manager sees notifications
    - Builder can mark as read
    """
    __tablename__ = "alerts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert Data
    type = Column(String(50), nullable=False)  # 'budget', 'safety', 'schedule', etc.
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    site = relationship("Site", back_populates="alerts")
    
    # Index
    __table_args__ = (Index('idx_alerts_site', 'site_id'),)
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.type}, is_read={self.is_read})>"


# =============================================================================
# 9. MESSAGES TABLE - Chat/Communication
# =============================================================================
class Message(Base):
    """
    MESSAGE MODEL
    
    Stores messages/chat for each site.
    Used for real-time communication between builders and site managers.
    
    Fields Explanation:
    - id: Unique message identifier
    - site_id: Which site this message is about
    - sender_id: User who sent message
    - message: Message text
    - created_at: When sent
    
    Optional MVP+ feature (not in initial backend).
    Can be skipped if not needed now.
    
    Future Enhancements:
    - Real-time updates (WebSocket)
    - Message read receipts
    - Message editing/deletion
    - Attachments (photos, documents)
    """
    __tablename__ = "messages"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Message Data
    message = Column(Text, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    site = relationship("Site", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    
    # Indexes
    __table_args__ = (Index('idx_messages_site', 'site_id'),)
    
    def __repr__(self):
        return f"<Message(id={self.id}, site_id={self.site_id})>"


# =============================================================================
# CREATE ALL TABLES
# =============================================================================
# This function is called when app starts to create all tables
# def create_tables():
#     """Create all tables in database"""
#     Base.metadata.create_all(bind=engine)
