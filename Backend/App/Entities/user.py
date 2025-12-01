"""
user entity
"""

from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from Database.connection import Base 

if TYPE_CHECKING:

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
    MemberSince: Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable
    Email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    HashedPassword: Mapped[str] = mapped_column(String(255))
    LastLogin: Mapped[datetime] = mapped_column(DateTime)

    #Relationship
