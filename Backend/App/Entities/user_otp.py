"""User otp"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

# 1. Thêm ForeignKey vào import
from sqlalchemy import BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base

if TYPE_CHECKING:
    from Entities.user import User
    
class UserOTP(Base):
    __tablename__ = "USEROTP"

    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("USER.UserID", ondelete="CASCADE"), primary_key=True)
    
    OTPCode: Mapped[Optional[str]] = mapped_column(String(30))
    OTPExpiry: Mapped[Optional[datetime]] = mapped_column(DateTime)
    OTPAttempts: Mapped[Optional[int]] = mapped_column(BigInteger, default=0)

    # relationship
    User: Mapped["User"] = relationship("User", back_populates="UserOTP")