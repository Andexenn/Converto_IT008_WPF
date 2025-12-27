"""
user entity
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, func, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped
from Database.connection import Base 

if TYPE_CHECKING:
    from Entities.tasks import Tasks
    from Entities.user_preferences import UserPreferences
    from Entities.user_otp import UserOTP

class User(Base):
    __tablename__ = "USER"

    __table_args__ = {'extend_existing': True}

    UserID: Mapped[int] = mapped_column(Integer, primary_key=True)
    FirstName: Mapped[Optional[str]] = mapped_column(String(255), default="John")
    LastName: Mapped[Optional[str]] = mapped_column(String(255), default="Doe")
    Address: Mapped[Optional[str]] = mapped_column(String(500))
    PhoneNumber: Mapped[Optional[str]] = mapped_column(String(20))
    DateOfBirth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    City: Mapped[Optional[str]] = mapped_column(String(100))
    ProfilePictureURL: Mapped[Optional[str]] = mapped_column(String(100))
    MemberSince: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    Email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    HashedPassword: Mapped[str] = mapped_column(String(255))
    LastLogin: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    # Use class references instead of strings
    UserTasks: Mapped[List["Tasks"]] = relationship(
        back_populates="User", 
        cascade="all, delete-orphan"
    )
    
    Preferences: Mapped["UserPreferences"] = relationship(
        back_populates="User", 
        cascade="all, delete-orphan"
    )
    
    UserOtp: Mapped["UserOTP"] = relationship(
        back_populates="User", 
        cascade="all, delete-orphan"
    )