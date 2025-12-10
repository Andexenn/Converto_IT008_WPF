"""
user entity
"""

from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from Database.connection import Base 

if TYPE_CHECKING:
    from Entities.tasks import Tasks
    from Entities.user_preferences import UserPreferences
    from Entities.user_otp import UserOTP
class User(Base):
    __tablename__ = "USER"

    UserID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    FirstName: Mapped[Optional[str]] = mapped_column(String(255), default="John")
    LastName: Mapped[Optional[str]] = mapped_column(String(255), default="Doe")
    Address: Mapped[Optional[str]] = mapped_column(String(500))
    PhoneNumber: Mapped[Optional[str]] = mapped_column(String(20))
    DateOfBirth: Mapped[Optional[datetime]] = mapped_column(DateTime)
    City: Mapped[Optional[str]] = mapped_column(String(100))
    ProfilePictureURL: Mapped[Optional[str]] = mapped_column(String(100))
    MemberSince: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable
    Email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    HashedPassword: Mapped[str] = mapped_column(String(255))
    LastLogin: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable

    #Relationship
    UserTasks: Mapped[List["Tasks"]] = relationship(back_populates="User", cascade="all, delete-orphan")
    Preferences: Mapped["UserPreferences"] = relationship(back_populates="User", cascade="all, delete-orphan")
    UserOTP: Mapped["UserOTP"] = relationship(back_populates="User", cascade="all, delete-orphan")
