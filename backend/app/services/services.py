"""
=============================================================================
⚙️ SERVICES.PY - BUSINESS LOGIC LAYER
=============================================================================
Purpose:
    Contains all business logic (independent of database/HTTP framework).
    Services handle:
    - Querying database
    - Validating business rules
    - Transforming data
    - Calling external APIs
    
Architecture:
    Routes (HTTP) → Services (Logic) → Database
    - Routes: Handle HTTP requests/responses
    - Services: Business logic
    - Database: Data persistence
    
Why This Layer:
    ✅ Clean separation of concerns
    ✅ Easy to test
    ✅ Reusable business logic
    ✅ Easy to maintain and extend
    
Naming Convention:
    create_* → Create new record
    get_* → Fetch existing record(s)
    update_* → Modify record
    delete_* → Remove record
    verify_* → Check/validate
=============================================================================
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.models import (
    User, OTPVerification, Site, SiteManager, Update, UpdateFile,
    Expense, Alert, Message
)
from app.schemas.schemas import (
    UserRegister, UserCreate, SiteCreate, UpdateCreate,
    ExpenseCreate, MessageCreate
)
from app.utils.helpers import (
    hash_password, verify_password, create_access_token,
    generate_otp, add_minutes, is_otp_valid
)


# =============================================================================
# ========================= AUTH SERVICE =========================
# =============================================================================

class AuthService:
    """
    AUTH SERVICE - Handle authentication operations
    
    Responsible for:
    - User registration
    - Email login
    - Phone OTP login
    - Token generation
    """
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """
        REGISTER NEW USER
        
        Steps:
        1. Validate at least one of email or phone exists
        2. Hash password if provided
        3. Create user record
        4. Return user object
        
        Args:
            db: Database session
            user_data: Registration data (Pydantic schema)
        
        Returns:
            User: Created user object
        
        Raises:
            ValueError: If validation fails
        
        Example:
            user_data = UserRegister(
                name="John Doe",
                email="john@example.com",
                password="SecurePass123",
                role="builder"
            )
            user = AuthService.register_user(db, user_data)
        """
        # Validation: At least one contact method required
        if not user_data.email and not user_data.phone:
            raise ValueError("Either email or phone must be provided")
        
        # Validation: Email must have password
        if user_data.email and not user_data.password:
            raise ValueError("Password required for email login")
        
        # Hash password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = hash_password(user_data.password)
        
        # Create user object
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password=hashed_password,
            role=user_data.role,
            is_email_verified=False,
            is_phone_verified=False
        )
        
        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def login_with_email(db: Session, email: str, password: str) -> Optional[User]:
        """
        LOGIN WITH EMAIL + PASSWORD
        
        Steps:
        1. Find user by email
        2. Verify password matches
        3. Return user if match
        
        Args:
            db: Database session
            email: User's email
            password: User's plain text password
        
        Returns:
            User if credentials valid
            None if invalid
        
        Example:
            user = AuthService.login_with_email(db, "john@example.com", "password123")
            if user:
                token = create_access_token({"sub": str(user.id)})
        """
        # Query user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None  # User not found
        
        # Verify password
        if not verify_password(password, user.password):
            return None  # Wrong password
        
        return user
    
    @staticmethod
    def send_otp(db: Session, phone: str) -> OTPVerification:
        """
        SEND OTP - Generate and store OTP
        
        Steps:
        1. Generate random 6-digit code
        2. Set expiration (10 minutes)
        3. Store in database
        4. Return OTP record (to send via SMS)
        
        In production:
        - Call Twilio API to send SMS
        - Only store OTP for verification, don't log
        
        Args:
            db: Database session
            phone: Phone number to send OTP to
        
        Returns:
            OTPVerification: OTP record with code
        
        Example:
            otp = AuthService.send_otp(db, "+919876543210")
            # In production: send_sms(phone, f"Your OTP: {otp.otp}")
        """
        # Generate 6-digit OTP
        otp_code = generate_otp(length=6)
        
        # Set expiration (10 minutes from now)
        expires_at = add_minutes(datetime.utcnow(), 10)
        
        # Create OTP record
        otp_record = OTPVerification(
            phone=phone,
            otp=otp_code,
            expires_at=expires_at
        )
        
        # Save to database
        db.add(otp_record)
        db.commit()
        db.refresh(otp_record)
        
        return otp_record
    
    @staticmethod
    def verify_otp(db: Session, phone: str, otp: str) -> Optional[User]:
        """
        VERIFY OTP - Check OTP and authenticate user
        
        Steps:
        1. Find OTP record
        2. Verify code matches
        3. Verify not expired
        4. Mark as used
        5. Create or update user
        6. Mark phone verified
        7. Return user
        
        Args:
            db: Database session
            phone: Phone number
            otp: OTP code entered by user
        
        Returns:
            User if OTP valid
            None if invalid or expired
        
        Example:
            user = AuthService.verify_otp(db, "+919876543210", "427839")
            if user:
                token = create_access_token({"sub": str(user.id)})
        """
        # Find most recent OTP for this phone
        otp_record = db.query(OTPVerification).filter(
            and_(
                OTPVerification.phone == phone,
                OTPVerification.is_used == False
            )
        ).order_by(OTPVerification.created_at.desc()).first()
        
        if not otp_record:
            return None  # No OTP found
        
        # Check if OTP code matches
        if otp_record.otp != otp:
            return None  # Wrong OTP
        
        # Check if expired
        if not is_otp_valid(otp_record.expires_at):
            return None  # Expired
        
        # Mark OTP as used
        otp_record.is_used = True
        db.commit()
        
        # Find or create user by phone
        user = db.query(User).filter(User.phone == phone).first()
        
        if not user:
            # Create new user (first time login with OTP)
            user = User(
                name="User",  # Will be updated by user
                phone=phone,
                role="site_manager",
                is_phone_verified=True,
                is_email_verified=False
            )
            db.add(user)
        else:
            # Mark phone as verified
            user.is_phone_verified = True
        
        db.commit()
        db.refresh(user)
        
        return user


# =============================================================================
# ========================= USER SERVICE =========================
# =============================================================================

class UserService:
    """
    USER SERVICE - User management operations
    """
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> List[User]:
        """
        GET ALL USERS - Fetch list of users
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Number of records to return
        
        Returns:
            List of User objects
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        GET USER BY ID
        
        Args:
            db: Database session
            user_id: User ID to fetch
        
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """
        UPDATE USER - Modify user details
        
        Args:
            db: Database session
            user_id: User to update
            **kwargs: Fields to update
        
        Returns:
            Updated User object
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                # Hash password if being updated
                if key == 'password' and value:
                    value = hash_password(value)
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        DELETE USER - Remove user from database
        
        Args:
            db: Database session
            user_id: User to delete
        
        Returns:
            bool: True if deleted, False if not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def assign_site_manager(db: Session, site_id: int, user_id: int) -> Optional[SiteManager]:
        """
        ASSIGN SITE MANAGER - Assign manager to site
        
        Args:
            db: Database session
            site_id: Site to assign to
            user_id: Manager user to assign
        
        Returns:
            SiteManager record or None
        """
        # Check if already assigned
        existing = db.query(SiteManager).filter(
            and_(SiteManager.site_id == site_id, SiteManager.user_id == user_id)
        ).first()
        
        if existing:
            return existing  # Already assigned
        
        # Create new assignment
        manager = SiteManager(site_id=site_id, user_id=user_id)
        db.add(manager)
        db.commit()
        db.refresh(manager)
        return manager


# =============================================================================
# ========================= SITE SERVICE =========================
# =============================================================================

class SiteService:
    """
    SITE SERVICE - Site/project management operations
    """
    
    @staticmethod
    def create_site(db: Session, site_data: SiteCreate, builder_id: int) -> Site:
        """
        CREATE SITE - Create new construction project
        
        Args:
            db: Database session
            site_data: Site creation data
            builder_id: User creating the site
        
        Returns:
            Created Site object
        """
        site = Site(
            name=site_data.name,
            location=site_data.location,
            budget=site_data.budget,
            builder_id=builder_id
        )
        db.add(site)
        db.commit()
        db.refresh(site)
        return site
    
    @staticmethod
    def get_all_sites(db: Session, skip: int = 0, limit: int = 10) -> List[Site]:
        """
        GET ALL SITES
        """
        return db.query(Site).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_sites_by_builder(db: Session, builder_id: int) -> List[Site]:
        """
        GET SITES BY BUILDER - Get sites created by specific builder
        """
        return db.query(Site).filter(Site.builder_id == builder_id).all()
    
    @staticmethod
    def get_site_by_id(db: Session, site_id: int) -> Optional[Site]:
        """
        GET SITE BY ID
        """
        return db.query(Site).filter(Site.id == site_id).first()
    
    @staticmethod
    def update_site(db: Session, site_id: int, **kwargs) -> Optional[Site]:
        """
        UPDATE SITE
        """
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(site, key):
                setattr(site, key, value)
        
        db.commit()
        db.refresh(site)
        return site
    
    @staticmethod
    def delete_site(db: Session, site_id: int) -> bool:
        """
        DELETE SITE
        """
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return False
        
        db.delete(site)
        db.commit()
        return True


# =============================================================================
# ========================= UPDATE SERVICE =========================
# =============================================================================

class UpdateService:
    """
    UPDATE SERVICE - Progress update operations
    """
    
    @staticmethod
    def create_update(db: Session, update_data: UpdateCreate, user_id: int) -> Update:
        """
        CREATE UPDATE - Submit progress update
        """
        update = Update(
            site_id=update_data.site_id,
            created_by=user_id,
            worker_count=update_data.worker_count,
            notes=update_data.notes
        )
        db.add(update)
        db.commit()
        db.refresh(update)
        return update
    
    @staticmethod
    def add_file_to_update(db: Session, update_id: int, file_url: str, file_type: str) -> UpdateFile:
        """
        ADD FILE TO UPDATE - Attach photo/audio to update
        """
        file_record = UpdateFile(
            update_id=update_id,
            file_url=file_url,
            file_type=file_type
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record
    
    @staticmethod
    def get_update_by_id(db: Session, update_id: int) -> Optional[Update]:
        """
        GET UPDATE BY ID
        """
        return db.query(Update).filter(Update.id == update_id).first()
    
    @staticmethod
    def get_updates_by_site(db: Session, site_id: int) -> List[Update]:
        """
        GET UPDATES BY SITE - Get all updates for a site (timeline)
        """
        return db.query(Update).filter(Update.site_id == site_id).order_by(Update.created_at.desc()).all()
    
    @staticmethod
    def delete_update(db: Session, update_id: int) -> bool:
        """
        DELETE UPDATE
        """
        update = db.query(Update).filter(Update.id == update_id).first()
        if not update:
            return False
        
        db.delete(update)
        db.commit()
        return True


# =============================================================================
# ========================= EXPENSE SERVICE =========================
# =============================================================================

class ExpenseService:
    """
    EXPENSE SERVICE - Expense tracking operations
    """
    
    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate, user_id: int) -> Expense:
        """
        CREATE EXPENSE - Record new expense
        """
        expense = Expense(
            site_id=expense_data.site_id,
            added_by=user_id,
            amount=expense_data.amount,
            category=expense_data.category,
            note=expense_data.note
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense
    
    @staticmethod
    def get_expenses_by_site(db: Session, site_id: int) -> List[Expense]:
        """
        GET EXPENSES BY SITE - Get all expenses for a site
        """
        return db.query(Expense).filter(Expense.site_id == site_id).all()
    
    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """
        GET EXPENSE BY ID
        """
        return db.query(Expense).filter(Expense.id == expense_id).first()
    
    @staticmethod
    def update_expense(db: Session, expense_id: int, **kwargs) -> Optional[Expense]:
        """
        UPDATE EXPENSE
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(expense, key):
                setattr(expense, key, value)
        
        db.commit()
        db.refresh(expense)
        return expense
    
    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> bool:
        """
        DELETE EXPENSE
        """
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            return False
        
        db.delete(expense)
        db.commit()
        return True
    
    @staticmethod
    def get_total_expenses(db: Session, site_id: int) -> int:
        """
        GET TOTAL EXPENSES - Calculate total spent for a site
        """
        result = db.query(Expense).filter(Expense.site_id == site_id).all()
        return sum(e.amount for e in result)


# =============================================================================
# ========================= ALERT SERVICE =========================
# =============================================================================

class AlertService:
    """
    ALERT SERVICE - Alert/notification operations
    """
    
    @staticmethod
    def create_alert(db: Session, site_id: int, alert_type: str, message: str) -> Alert:
        """
        CREATE ALERT - Generate new alert
        """
        alert = Alert(
            site_id=site_id,
            type=alert_type,
            message=message
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    
    @staticmethod
    def get_alerts_by_site(db: Session, site_id: int) -> List[Alert]:
        """
        GET ALERTS BY SITE
        """
        return db.query(Alert).filter(Alert.site_id == site_id).all()
    
    @staticmethod
    def mark_alert_read(db: Session, alert_id: int) -> Optional[Alert]:
        """
        MARK ALERT AS READ
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.is_read = True
        db.commit()
        db.refresh(alert)
        return alert


# =============================================================================
# ========================= MESSAGE SERVICE =========================
# =============================================================================

class MessageService:
    """
    MESSAGE SERVICE - Chat/messaging operations
    """
    
    @staticmethod
    def create_message(db: Session, message_data: MessageCreate, user_id: int) -> Message:
        """
        CREATE MESSAGE - Send chat message
        """
        message = Message(
            site_id=message_data.site_id,
            sender_id=user_id,
            message=message_data.message
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_messages_by_site(db: Session, site_id: int) -> List[Message]:
        """
        GET MESSAGES BY SITE - Get all messages for a site
        """
        return db.query(Message).filter(Message.site_id == site_id).order_by(Message.created_at.asc()).all()
    
    @staticmethod
    def delete_message(db: Session, message_id: int) -> bool:
        """
        DELETE MESSAGE
        """
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return False
        
        db.delete(message)
        db.commit()
        return True
