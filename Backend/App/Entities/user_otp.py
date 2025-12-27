"""User otp"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

# 1. Thêm ForeignKey vào import
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from Entities.user import User
    
class UserOTP(Base):
    __tablename__ = "USEROTP"

    __table_args__ = {'extend_existing': True}

    UserID: Mapped[int] = mapped_column(Integer, ForeignKey("USER.UserID", ondelete="CASCADE"), primary_key=True)
    
    OTPCode: Mapped[Optional[str]] = mapped_column(String(30))
    OTPExpiry: Mapped[Optional[datetime]] = mapped_column(DateTime)
    OTPAttempts: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    # relationship
    User: Mapped["User"] = relationship("Entities.user.User", back_populates="UserOtp")