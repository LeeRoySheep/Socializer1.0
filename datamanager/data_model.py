import datetime
from os import path
from pathlib import Path
from typing import Generator, Optional, List, Dict, Any

from sqlalchemy import (
    Integer,
    String,
    JSON,
    Float,
    Date,
    DateTime,
    ForeignKey,
    create_engine,
    UniqueConstraint,
    text,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

# Define Base for SQLAlchemy ORM first
class Base(DeclarativeBase):
    pass

class TokenBlacklist(Base):
    """Model for storing blacklisted JWT tokens."""
    __tablename__ = "token_blacklist"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationship with User
    user: Mapped[Optional["User"]] = relationship("User", back_populates="blacklisted_tokens")
    
    def __repr__(self) -> str:
        return f"<TokenBlacklist(id={self.id}, expires_at={self.expires_at})>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # User account status
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)  # JSON for user preferences
    hashed_name: Mapped[str] = mapped_column(String, default="")  # Hashed name for privacy
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    hashed_email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    member_since: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today)
    messages: Mapped[int] = mapped_column(Integer, default=0)  # Track number of messages sent
    
    # Memory and encryption fields
    encryption_key: Mapped[str] = mapped_column(String, nullable=True)  # User-specific encryption key
    conversation_memory: Mapped[str] = mapped_column(Text, nullable=True)  # Encrypted conversation memory
    
    # LLM Configuration fields - Allow users to configure custom local LLM endpoints
    llm_provider: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)  # e.g., 'lm_studio', 'ollama', 'openai'
    llm_endpoint: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)  # e.g., 'http://192.168.1.100:1234'
    llm_model: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)  # e.g., 'llama-3.2', 'local-model'
    
    # Relationships
    user_skills: Mapped[list["UserSkill"]] = relationship(
        "UserSkill", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    trainings: Mapped[list["Training"]] = relationship("Training", backref="user")
    user_preferences: Mapped[list["UserPreference"]] = relationship("UserPreference", backref="user")
    error_logs: Mapped[list["ErrorLog"]] = relationship(
        "ErrorLog", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Relationship with blacklisted tokens
    blacklisted_tokens: Mapped[list["TokenBlacklist"]] = relationship(
        "TokenBlacklist",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, role={self.role})"

    def __str__(self):
        return f"User {self.username} (ID: {self.id})"


class Skill(Base):
    __tablename__ = "skills"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_name: Mapped[str] = mapped_column(String, unique=True, nullable=True)

    # Relationships
    user_skills: Mapped[list["UserSkill"]] = relationship(
        "UserSkill", 
        back_populates="skill", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Skill(id={self.id}, skill_name={self.skill_name})"

    def __str__(self) -> str:
        return f"{self.skill_name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Skill):
            return False
        return self.skill_name == other.skill_name


class UserSkill(Base):
    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint('user_id', 'skill_id', name='_user_skill_uc'),
        {'sqlite_autoincrement': True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("skills.id", ondelete="CASCADE"), 
        nullable=False
    )
    level: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills")

    def __repr__(self) -> str:
        return f"UserSkill(user_id={self.user_id}, skill_id={self.skill_id}, level={self.level})"

    def __str__(self) -> str:
        skill_name = self.skill.skill_name if self.skill else "Unknown Skill"
        return f"User {self.user_id} - {skill_name} (Level: {self.level})"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.skill_name if self.skill else None,
            "level": self.level,
        }


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    preference_type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'communication_style', 'interests', 'goals'
    preference_key: Mapped[str] = mapped_column(String, nullable=False)    # Specific preference name
    preference_value: Mapped[dict] = mapped_column(JSON, nullable=False)   # The actual preference value
    confidence: Mapped[float] = mapped_column(Float, default=1.0)          # Confidence score (0-1)
    last_updated: Mapped[datetime.date] = mapped_column(
        Date, 
        default=datetime.date.today, 
        onupdate=datetime.date.today
    )
    
    # Add a composite unique constraint on user_id, preference_type, and preference_key
    __table_args__ = (
        UniqueConstraint('user_id', 'preference_type', 'preference_key'),
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self) -> str:
        return (
            f"UserPreference(id={self.id}, user_id={self.user_id}, "
            f"type={self.preference_type}, key={self.preference_key})"
        )

    def to_dict(self) -> dict:
        """Convert the UserPreference object to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preference_type": self.preference_type,
            "preference_key": self.preference_key,
            "preference_value": self.preference_value,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


class ErrorLog(Base):
    """Model for tracking errors in the application."""
    __tablename__ = "error_logs"
    
    # Maximum length for error_type field
    ERROR_TYPE_MAX_LENGTH = 100
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    error_type: Mapped[str] = mapped_column(String(ERROR_TYPE_MAX_LENGTH), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __init__(self, **kwargs):
        # Truncate error_type if it exceeds the maximum length
        if 'error_type' in kwargs and len(kwargs['error_type']) > self.ERROR_TYPE_MAX_LENGTH:
            kwargs['error_type'] = kwargs['error_type'][:self.ERROR_TYPE_MAX_LENGTH]
        super().__init__(**kwargs)
    
    # Relationship to User (optional)
    user: Mapped[Optional["User"]] = relationship("User", back_populates="error_logs")
    
    def __repr__(self):
        return f"<ErrorLog(id={self.id}, error_type='{self.error_type}', timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert the ErrorLog object to a dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "context": self.context
        }


class Training(Base):
    """
    Training record linking a user to a skill they are training.
    
    Tracks the progress of a user's training on a specific skill,
    including status, progress percentage, and timestamps.
    
    Attributes:
        user_id: Foreign key to users table (composite primary key)
        skill_id: Foreign key to skills table (composite primary key)
        status: Training status ('pending', 'active', 'paused', 'completed')
        progress: Progress as float 0.0-1.0 (0-100%)
        started_at: Date training was started
        completed_at: Date training was completed (if applicable)
        notes: Optional notes about the training
        
    Relationships:
        - Belongs to User (via user_id)
        - Belongs to Skill (via skill_id)
        - Has one TrainingSchedule (optional)
    """
    __tablename__ = "training"

    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("skills.id", ondelete="CASCADE"), 
        primary_key=True
    )
    status: Mapped[str] = mapped_column(String, default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[datetime.date] = mapped_column(
        Date, 
        default=datetime.date.today
    )
    completed_at: Mapped[datetime.date | None] = mapped_column(
        Date, 
        default=None
    )
    notes: Mapped[str | None] = mapped_column(String, default=None)

    def __repr__(self) -> str:
        return (
            f"<Training(user_id={self.user_id}, skill_id={self.skill_id}, "
            f"status={self.status}, progress={self.progress})>"
        )

    def __str__(self) -> str:
        return (
            f"Training for user {self.user_id} on skill {self.skill_id}: "
            f"{self.status} ({self.progress*100:.1f}%)"
        )

    def to_dict(self) -> dict:
        """Convert the Training object to a dictionary."""
        return {
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
        }


class TrainingSchedule(Base):
    """
    User-configurable training schedule for a specific training.
    
    Allows users to customize when and how often they train,
    with support for pausing (max 2 weeks) and automatic reactivation.
    
    Features:
        - Configurable training days (Monday-Sunday)
        - Preferred training time
        - Pause functionality with 2-week maximum
        - Automatic reactivation after pause expires
        - Basic training always stays active (is_basic=True)
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        skill_id: Foreign key to skills table
        is_basic: If True, this is a core training that cannot be disabled
        is_active: Whether training is currently active
        paused_at: When training was paused (if applicable)
        pause_until: When pause expires (max 2 weeks from paused_at)
        preferred_days: JSON list of preferred training days (0=Mon, 6=Sun)
        preferred_time: Preferred time of day for training reminders
        frequency: How often to train ('daily', 'every_other_day', 'weekly')
        last_trained_at: Last time user actively trained this skill
        created_at: When schedule was created
        updated_at: When schedule was last updated
        
    Business Rules:
        - Basic trainings (is_basic=True) cannot be paused for more than 2 weeks
        - After pause_until expires, training automatically reactivates
        - Users can customize preferred_days and preferred_time
        
    Example:
        >>> schedule = TrainingSchedule(
        ...     user_id=1,
        ...     skill_id=1,
        ...     is_basic=True,
        ...     preferred_days=[0, 2, 4],  # Mon, Wed, Fri
        ...     preferred_time=datetime.time(9, 0),  # 9:00 AM
        ...     frequency='every_other_day'
        ... )
    """
    __tablename__ = "training_schedules"
    __table_args__ = (
        UniqueConstraint('user_id', 'skill_id', name='_user_skill_schedule_uc'),
    )
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys (composite reference to Training)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Core training flag - basic trainings always stay active
    is_basic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Active/Pause state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    paused_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    pause_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    # Schedule preferences
    preferred_days: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        default=lambda: [0, 1, 2, 3, 4, 5, 6],  # All days by default
        nullable=True
    )
    preferred_time: Mapped[Optional[datetime.time]] = mapped_column(
        DateTime,  # Store as datetime, extract time
        nullable=True
    )
    frequency: Mapped[str] = mapped_column(
        String, 
        default="daily",  # 'daily', 'every_other_day', 'weekly'
        nullable=False
    )
    
    # Tracking
    last_trained_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    
    # Constants
    MAX_PAUSE_DAYS: int = 14  # Maximum 2 weeks pause
    
    def __repr__(self) -> str:
        return (
            f"<TrainingSchedule(user_id={self.user_id}, skill_id={self.skill_id}, "
            f"is_active={self.is_active}, is_basic={self.is_basic})>"
        )
    
    def __str__(self) -> str:
        status = "active" if self.is_active else f"paused until {self.pause_until}"
        return f"Schedule for user {self.user_id}, skill {self.skill_id}: {status}"
    
    def pause(self, days: int = 7) -> bool:
        """
        Pause the training for specified number of days.
        
        Args:
            days: Number of days to pause (max 14 for basic trainings)
            
        Returns:
            True if pause was successful, False if not allowed
            
        Raises:
            ValueError: If days exceeds MAX_PAUSE_DAYS for basic trainings
        """
        # Basic trainings can only be paused for max 2 weeks
        if self.is_basic and days > self.MAX_PAUSE_DAYS:
            days = self.MAX_PAUSE_DAYS
        
        self.is_active = False
        self.paused_at = datetime.datetime.utcnow()
        self.pause_until = self.paused_at + datetime.timedelta(days=days)
        self.updated_at = datetime.datetime.utcnow()
        
        return True
    
    def resume(self) -> bool:
        """
        Resume a paused training.
        
        Returns:
            True if resume was successful
        """
        self.is_active = True
        self.paused_at = None
        self.pause_until = None
        self.updated_at = datetime.datetime.utcnow()
        
        return True
    
    def check_auto_reactivate(self) -> bool:
        """
        Check if pause has expired and auto-reactivate if needed.
        
        This should be called on login or periodically to ensure
        basic trainings are reactivated after pause expires.
        
        Returns:
            True if training was reactivated, False otherwise
        """
        if not self.is_active and self.pause_until:
            if datetime.datetime.utcnow() >= self.pause_until:
                self.resume()
                return True
        return False
    
    def should_train_today(self) -> bool:
        """
        Check if user should train this skill today based on schedule.
        
        Returns:
            True if today is a training day, False otherwise
        """
        if not self.is_active:
            return False
        
        today = datetime.date.today().weekday()  # 0=Monday, 6=Sunday
        
        if self.preferred_days:
            return today in self.preferred_days
        
        return True  # Default: train every day
    
    def to_dict(self) -> dict:
        """Convert the TrainingSchedule object to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "is_basic": self.is_basic,
            "is_active": self.is_active,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "pause_until": self.pause_until.isoformat() if self.pause_until else None,
            "preferred_days": self.preferred_days,
            "frequency": self.frequency,
            "last_trained_at": self.last_trained_at.isoformat() if self.last_trained_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatRoom(Base):
    """
    Private chat room that can contain multiple users + AI.
    Supports both 1-on-1 and group conversations.
    """
    __tablename__ = "chat_rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Optional custom name
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    room_type: Mapped[str] = mapped_column(String, default="group", nullable=False)  # 'direct', 'group', 'private'
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Optional password for room protection
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # False = hidden (invite-only), True = discoverable
    
    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[creator_id])
    members: Mapped[list["RoomMember"]] = relationship(
        "RoomMember", 
        back_populates="room",
        cascade="all, delete-orphan"
    )
    messages: Mapped[list["RoomMessage"]] = relationship(
        "RoomMessage",
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="RoomMessage.created_at"
    )
    invites: Mapped[list["RoomInvite"]] = relationship(
        "RoomInvite",
        back_populates="room",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ChatRoom(id={self.id}, name={self.name}, creator_id={self.creator_id})>"
    
    def get_auto_name(self, db_session) -> str:
        """
        Generate automatic room name based on members.
        Returns: "Chat with Alice, Bob" or "Chat with Alice" for 1-on-1
        """
        active_members = [m for m in self.members if m.is_active and m.role != 'ai']
        member_names = []
        for member in active_members:
            if member.user_id != self.creator_id:
                user = db_session.query(User).filter(User.id == member.user_id).first()
                if user:
                    member_names.append(user.username)
        
        if not member_names:
            return "Private Room"
        return f"Chat with {', '.join(member_names)}"


class RoomMember(Base):
    """
    Association table tracking which users are members of which rooms.
    """
    __tablename__ = "room_members"
    __table_args__ = (
        UniqueConstraint('room_id', 'user_id', name='_room_user_uc'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for AI
    joined_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    role: Mapped[str] = mapped_column(String, default="member", nullable=False)  # 'creator', 'member', 'ai'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_read_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="members")
    user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<RoomMember(room_id={self.room_id}, user_id={self.user_id}, role={self.role})>"


class RoomMessage(Base):
    """
    Messages sent in private chat rooms.
    """
    __tablename__ = "room_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for AI
    sender_type: Mapped[str] = mapped_column(String, default="user", nullable=False)  # 'user', 'ai', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String, default="text", nullable=False)  # 'text', 'invite', 'system'
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # For invite buttons, etc.
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )
    edited_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="messages")
    sender: Mapped[Optional["User"]] = relationship("User", foreign_keys=[sender_id])
    
    def __repr__(self) -> str:
        return f"<RoomMessage(id={self.id}, room_id={self.room_id}, sender_type={self.sender_type})>"


class GeneralChatMessage(Base):
    """
    Messages sent in the general chat room.
    Persisted to maintain chat history across server restarts.
    """
    __tablename__ = "general_chat_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )
    
    # Relationships
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    
    def __repr__(self) -> str:
        return f"<GeneralChatMessage(id={self.id}, sender_id={self.sender_id})>"


class RoomInvite(Base):
    """
    Invitations to join private chat rooms.
    Appears as a message in the invitee's main chat.
    """
    __tablename__ = "room_invites"
    __table_args__ = (
        UniqueConstraint('room_id', 'invitee_id', name='_room_invitee_uc'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    inviter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # 'pending', 'accepted', 'declined'
    message_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("room_messages.id"), nullable=True
    )  # Reference to invite message shown in main chat
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    responded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    room: Mapped["ChatRoom"] = relationship("ChatRoom", back_populates="invites")
    inviter: Mapped["User"] = relationship("User", foreign_keys=[inviter_id])
    invitee: Mapped["User"] = relationship("User", foreign_keys=[invitee_id])
    
    def __repr__(self) -> str:
        return f"<RoomInvite(id={self.id}, room_id={self.room_id}, invitee_id={self.invitee_id}, status={self.status})>"


class DataModel:
    """
    Database management class for the application.
    Uses SQLAlchemy 2.0 style with type hints and async support.
    """
    def __init__(self, sqlite_file_name: str = "data.sqlite.db") -> None:
        """Initialize the database connection and session factory.
        
        Args:
            sqlite_file_name: Name of the SQLite database file
        """
        self.sqlite_file_name = sqlite_file_name
        self.sqlite_url = f"sqlite:///{self.sqlite_file_name}"
        self.engine = create_engine(
            self.sqlite_url, 
            echo=False, 
            future=True,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine,
            class_=Session,
            expire_on_commit=False
        )

    def create_db_and_tables(self) -> None:
        """Create all database tables defined in the models."""
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        """
        Get a database session.
        
        Yields:
            Session: A SQLAlchemy database session
            
        Example:
            ```python
            data_model = DataModel()
            with data_model.get_db() as db:
                # Use the database session
                user = db.query(User).first()
            ```
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_user_preferences(self, user_id: int, preference_type: Optional[str] = None) -> dict:
        """
        Get user preferences from database.
        
        Args:
            user_id: ID of the user
            preference_type: Optional filter by preference type
            
        Returns:
            Dictionary mapping "type.key" to value (extracted from JSON)
        """
        db = self.SessionLocal()
        try:
            query = db.query(UserPreference).filter(UserPreference.user_id == user_id)
            
            if preference_type:
                query = query.filter(UserPreference.preference_type == preference_type)
            
            preferences = query.all()
            
            # Return as dict: "type.key" -> value
            result = {}
            for pref in preferences:
                key = f"{pref.preference_type}.{pref.preference_key}"
                # Extract value from JSON format
                if isinstance(pref.preference_value, dict) and "value" in pref.preference_value:
                    result[key] = pref.preference_value["value"]
                else:
                    result[key] = pref.preference_value
            
            return result
        finally:
            db.close()
    
    def set_user_preference(self, user_id: int, preference_type: str, 
                           preference_key: str, preference_value: Any, 
                           confidence: float = 1.0) -> bool:
        """
        Set a user preference in database.
        
        Args:
            user_id: ID of the user
            preference_type: Type of preference (e.g., 'personal_info', 'interests')
            preference_key: Key for the preference
            preference_value: Value to store (will be stored as JSON)
            confidence: Confidence score for this preference (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        db = self.SessionLocal()
        try:
            # Convert value to dict if it's a string (for JSON storage)
            if isinstance(preference_value, str):
                json_value = {"value": preference_value}
            elif isinstance(preference_value, dict):
                json_value = preference_value
            else:
                json_value = {"value": str(preference_value)}
            
            # Check if preference already exists
            existing = db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == preference_type,
                UserPreference.preference_key == preference_key
            ).first()
            
            if existing:
                # Update existing
                existing.preference_value = json_value
                existing.confidence = confidence
            else:
                # Create new
                new_pref = UserPreference(
                    user_id=user_id,
                    preference_type=preference_type,
                    preference_key=preference_key,
                    preference_value=json_value,
                    confidence=confidence
                )
                db.add(new_pref)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error setting user preference: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
    
    def delete_user_preference(self, user_id: int, preference_type: str, 
                              preference_key: str) -> bool:
        """
        Delete a user preference from database.
        
        Args:
            user_id: ID of the user
            preference_type: Type of preference
            preference_key: Key for the preference
            
        Returns:
            True if successful, False otherwise
        """
        db = self.SessionLocal()
        try:
            preference = db.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.preference_type == preference_type,
                UserPreference.preference_key == preference_key
            ).first()
            
            if preference:
                db.delete(preference)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            print(f"Error deleting user preference: {e}")
            return False
        finally:
            db.close()


if __name__ == "__main__":
    # Example usage:
    data = DataModel()
    print(f"Initializing database at {data.sqlite_url}...")
    if Path(data.sqlite_file_name).exists():
        print("Database already exists, skipping...")
    else:
        data.create_db_and_tables()
        print("Database created.")
