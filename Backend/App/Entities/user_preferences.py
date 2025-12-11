"""
User preferences entity
"""

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from Database.connection import Base 

if TYPE_CHECKING:
    from Entities.user import User 

class UserPreferences(Base):
    """Define UserPreferences Entity"""
    __tablename__ = 'USERPREFERENCES'

    PreferenceID: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    UserID: Mapped[int] = mapped_column(BigInteger, ForeignKey("USER.UserID", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    DefaultOutputFolder: Mapped[str] = mapped_column(String(255), default='C:/Downloads', nullable=False)
    Language: Mapped[str] = mapped_column(String(100), default='English', nullable=False)
    Theme: Mapped[str] = mapped_column(String(100), default='dark')

    CreatedAt:Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable
    UpdatedAt:Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) #pylint: disable=not-callable

    #relationships:
    User: Mapped["User"] = relationship(back_populates="Preferences", lazy="joined")
